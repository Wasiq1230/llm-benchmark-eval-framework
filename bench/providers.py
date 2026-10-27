"""
One thin client per vendor, written against the raw HTTP APIs rather than the
official SDKs.

Two reasons for that choice, and both are part of the evaluation:

  1. SDK versions drift. If OpenAI's SDK retries internally and Anthropic's does
     not, the latency numbers stop being comparable. Raw HTTP means every vendor
     gets the same timeout, the same retry policy, and the same clock.
  2. Writing these three functions is the integration exercise. Differences in
     auth headers, message shape, token accounting, and error bodies are what the
     integration score in the report is actually measuring.

Every function returns the same tuple so the runner does not care who answered.
"""

import json
import os
import time

import requests


class ProviderError(RuntimeError):
    def __init__(self, status, body):
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {str(body)[:300]}")


class RateLimited(ProviderError):
    pass


def _post(url, headers, payload, timeout_s):
    """Send the request and time only the network round trip."""
    t0 = time.perf_counter()
    r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    if r.status_code == 429:
        raise RateLimited(r.status_code, r.text)
    if r.status_code >= 400:
        raise ProviderError(r.status_code, r.text)
    return r.json(), elapsed_ms


def _key(env_name):
    v = os.environ.get(env_name)
    if not v:
        raise RuntimeError(
            f"{env_name} is not set. Copy .env.example to .env, fill it in, "
            f"and run with: set -a && source .env && set +a"
        )
    return v


def call_openai_compatible(cfg, system_prompt, user_message, run_cfg):
    """
    Covers OpenAI itself, Google's OpenAI-compatible Gemini endpoint, and a
    LiteLLM gateway. Same wire format for all three.
    """
    url = cfg["base_url"].rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {_key(cfg['api_key_env'])}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg["model"],
        "temperature": run_cfg["temperature"],
        "max_tokens": run_cfg["max_tokens"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }
    data, elapsed_ms = _post(url, headers, payload, run_cfg["timeout_s"])
    text = data["choices"][0]["message"]["content"] or ""
    usage = data.get("usage") or {}
    return {
        "text": text,
        "latency_ms": elapsed_ms,
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
        "raw_finish": data["choices"][0].get("finish_reason"),
    }


def call_anthropic(cfg, system_prompt, user_message, run_cfg):
    """
    Anthropic keeps the system prompt out of the messages array and uses its own
    auth header. Token counts come back under different names.
    """
    url = cfg["base_url"].rstrip("/") + "/messages"
    headers = {
        "x-api-key": _key(cfg["api_key_env"]),
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg["model"],
        "system": system_prompt,
        "temperature": run_cfg["temperature"],
        "max_tokens": run_cfg["max_tokens"],
        "messages": [{"role": "user", "content": user_message}],
    }
    data, elapsed_ms = _post(url, headers, payload, run_cfg["timeout_s"])
    parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
    usage = data.get("usage") or {}
    return {
        "text": "".join(parts),
        "latency_ms": elapsed_ms,
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "raw_finish": data.get("stop_reason"),
    }


def build_caller(provider_cfg, gateway_cfg):
    """
    Return a function that takes (system_prompt, user_message, run_cfg).

    If the gateway is on, everything goes through one OpenAI-compatible endpoint
    and the per-vendor differences disappear. That is convenient, and it is also
    a finding worth putting in the memo: a gateway removes lock-in at the code
    level but adds a hop that shows up in the latency numbers.
    """
    if gateway_cfg.get("enabled"):
        alias = gateway_cfg["aliases"][provider_cfg["key"]]
        shim = {
            "model": alias,
            "base_url": gateway_cfg["base_url"],
            "api_key_env": gateway_cfg["api_key_env"],
        }
        return lambda sp, um, rc: call_openai_compatible(shim, sp, um, rc)

    if provider_cfg["key"] == "anthropic":
        return lambda sp, um, rc: call_anthropic(provider_cfg, sp, um, rc)
    return lambda sp, um, rc: call_openai_compatible(provider_cfg, sp, um, rc)


def extract_json(text):
    """
    Pull the JSON object out of a reply. Returns (obj, was_clean).

    was_clean is False when the model wrapped its answer in a code fence or put
    prose around it. That is a real integration cost, so the report tracks it
    separately from outright invalid JSON.
    """
    s = (text or "").strip()
    try:
        return json.loads(s), True
    except Exception:
        pass

    if s.startswith("```"):
        s2 = s.strip("`")
        if s2.lower().startswith("json"):
            s2 = s2[4:]
        try:
            return json.loads(s2.strip()), False
        except Exception:
            pass

    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(s[start:end + 1]), False
        except Exception:
            pass
    return None, False
