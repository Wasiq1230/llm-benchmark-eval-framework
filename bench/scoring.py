"""
Scoring. Every function here is deterministic, so two people running the same
results file get the same numbers. Nothing is scored by asking a model what it
thinks of another model's answer.

Six components. The weights live in config.yaml, not here, so the sensitivity
analysis in the report can move them without touching this file.
"""

import re
import unicodedata

INTENTS = {
    "track_status", "delayed_delivery", "cod_query", "address_change",
    "damaged_parcel", "pickup_request", "refund_return", "rate_query",
    "out_of_scope",
}
ACTIONS = {"resolve_with_info", "create_ticket", "escalate_human", "refund_request", "none"}


def _norm(v):
    if v is None:
        return None
    s = unicodedata.normalize("NFKC", str(v)).strip().lower()
    s = re.sub(r"[\s\-_/]", "", s)
    return s or None


def _norm_amount(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    digits = re.sub(r"[^\d.]", "", str(v))
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


def score_intent(pred, gold):
    return 1.0 if _norm(pred.get("intent")) == _norm(gold["intent"]) else 0.0


def score_action(pred, gold):
    return 1.0 if _norm(pred.get("action")) == _norm(gold["action"]) else 0.0


def score_entities(pred, gold):
    """
    Micro-F1 over three slots. A slot that is null in the gold and null in the
    prediction is a true negative and is left out of the F1 entirely, so a model
    is not rewarded for a page of nulls.
    """
    tp = fp = fn = 0
    for slot in ("tracking_id", "city", "cod_amount_pkr"):
        g = gold.get(slot)
        p = pred.get(slot)
        if slot == "cod_amount_pkr":
            g, p = _norm_amount(g), _norm_amount(p)
        else:
            g, p = _norm(g), _norm(p)

        if g is None and p is None:
            continue
        if g is None and p is not None:
            fp += 1
        elif g is not None and p is None:
            fn += 1
        elif g == p:
            tp += 1
        else:
            fp += 1
            fn += 1

    if tp == 0 and fp == 0 and fn == 0:
        return 1.0
    if tp == 0:
        return 0.0
    prec = tp / (tp + fp)
    rec = tp / (tp + fn)
    return 2 * prec * rec / (prec + rec)


def score_grounding(pred, case):
    """
    1.0 if the reply invents nothing, 0.0 if it does.

    The must_not_contain list per case holds the specific inventions that matter
    for that message: a delivery date nobody knows, a fee nobody quoted, a refund
    nobody approved. This is the component that separates a model you can put in
    front of customers from one you cannot.
    """
    reply = (pred.get("reply") or "").lower()
    for banned in case.get("must_not_contain", []):
        if banned.lower() in reply:
            return 0.0
    return 1.0


def score_policy(pred, case):
    """
    Fraction of required facts present. Each required fact is a list of
    acceptable surface forms, so a Roman Urdu reply and an English reply can both
    get full marks for saying the same thing.
    """
    groups = case.get("policy_points") or []
    if not groups:
        return 1.0
    reply = (pred.get("reply") or "").lower()
    hits = sum(1 for group in groups if any(alt.lower() in reply for alt in group))
    return hits / len(groups)


def score_reply_length(pred, limit_words=45):
    words = len((pred.get("reply") or "").split())
    if words == 0:
        return 0.0
    return 1.0 if words <= limit_words else max(0.0, 1.0 - (words - limit_words) / limit_words)


def schema_penalties(pred):
    """Values outside the enum are a schema failure even when the JSON parses."""
    bad = []
    if _norm(pred.get("intent")) not in {_norm(i) for i in INTENTS}:
        bad.append("intent_out_of_enum")
    if _norm(pred.get("action")) not in {_norm(a) for a in ACTIONS}:
        bad.append("action_out_of_enum")
    for k in ("intent", "tracking_id", "city", "cod_amount_pkr", "action", "reply"):
        if k not in pred:
            bad.append(f"missing_{k}")
    return bad


def score_case(pred, was_clean, case, comp_weights):
    """
    Score one model reply against one gold case.

    A reply that does not parse gets zero on every component. That is deliberate.
    In production the ticketing system would have dropped it, and a dropped
    ticket is worse than a wrong one because nobody knows it happened.
    """
    if pred is None:
        return {
            "json_valid": 0.0, "intent_exact": 0.0, "entities_f1": 0.0,
            "action_exact": 0.0, "grounding": 0.0, "policy_points": 0.0,
            "reply_length": 0.0, "clean_json": 0.0,
            "schema_issues": ["unparseable"], "accuracy": 0.0,
        }

    issues = schema_penalties(pred)
    parts = {
        "json_valid": 0.0 if issues else 1.0,
        "intent_exact": score_intent(pred, case["gold"]),
        "entities_f1": score_entities(pred, case["gold"]),
        "action_exact": score_action(pred, case["gold"]),
        "grounding": score_grounding(pred, case),
        "policy_points": score_policy(pred, case),
    }
    accuracy = sum(parts[k] * comp_weights[k] for k in comp_weights)
    parts.update({
        "reply_length": score_reply_length(pred),
        "clean_json": 1.0 if was_clean else 0.0,
        "schema_issues": issues,
        "accuracy": accuracy,
    })
    return parts


def percentile(values, p):
    if not values:
        return 0.0
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    k = (len(xs) - 1) * (p / 100.0)
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return float(xs[lo] + (xs[hi] - xs[lo]) * (k - lo))


def wilson_interval(successes, n, z=1.96):
    """
    95% confidence interval on a proportion. Thirty cases is a small set and the
    memo has to say so honestly rather than reporting a bare percentage.
    """
    if n == 0:
        return (0.0, 0.0)
    phat = successes / n
    denom = 1 + z * z / n
    centre = (phat + z * z / (2 * n)) / denom
    margin = z * ((phat * (1 - phat) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))
