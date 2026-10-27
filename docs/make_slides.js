const pptxgen = require("pptxgenjs");

const INK = "12181A", PAPER = "E6EAE5", WHITE = "FFFFFF";
const GREEN = "0B6E4F", AMBER = "B8830C", RED = "A32A1F", SLATE = "3A6E8F";
const MUTED = "6B7671", RULE = "C7CDC6", SOFT = "F4F6F3";
const SANS = "Arial", MONO = "Courier New";

const p = new pptxgen();
p.layout = "LAYOUT_WIDE";          // 13.3 x 7.5
p.author = "Fatima Naseer";
p.title = "Which language model should answer our customers first";

const W = 13.3, H = 7.5, M = 0.85;

function eyebrow(s, text, color) {
  s.addText(text.toUpperCase().split("").join(" "), {
    x: M, y: 0.44, w: W - M * 2, h: 0.3,
    fontFace: MONO, fontSize: 9, color: color || MUTED, charSpacing: 1, margin: 0,
  });
}

function title(s, text, color) {
  s.addText(text, {
    x: M, y: 0.82, w: W - M * 2, h: 1.0,
    fontFace: SANS, fontSize: 30, bold: true, color: color || INK, margin: 0, valign: "top",
  });
}

function light(num, head) {
  const s = p.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, num);
  title(s, head);
  return s;
}

function card(s, x, y, w, h, fill) {
  s.addShape(p.ShapeType.rect, {
    x, y, w, h, fill: { color: fill || SOFT },
    line: { color: RULE, width: 0.5 },
  });
}

function note(s, text) { s.addNotes(text); }

/* ------------------------------------------------------------------ 1 */
{
  const s = p.addSlide();
  s.background = { color: INK };
  s.addText("S A F E X   S O L U T I O N S      W E E K   4      G R O U P   5 7", {
    x: M, y: 0.9, w: W - M * 2, h: 0.3, fontFace: MONO, fontSize: 10, color: "8FA096", margin: 0,
  });
  s.addText("Which language model\nshould answer our\ncustomers first?", {
    x: M, y: 1.5, w: 9.2, h: 2.9, fontFace: SANS, fontSize: 40, bold: true,
    color: WHITE, lineSpacing: 46, margin: 0, valign: "top",
  });
  s.addText("A vendor evaluation for a courier operation. Three providers, one prompt,\nthirty hand-labelled cases, one weighted recommendation.", {
    x: M, y: 4.6, w: 8.6, h: 0.9, fontFace: SANS, fontSize: 14, color: "9DAEA3", margin: 0,
  });
  s.addText("Fatima Naseer   /   Institute of Space Technology, Islamabad", {
    x: M, y: 6.4, w: 8, h: 0.3, fontFace: MONO, fontSize: 10, color: "7E9089", margin: 0,
  });
  note(s, "Open on the question, not on the vendors. The audience is an operations lead, not an engineer.");
}

/* ------------------------------------------------------------------ 2 */
{
  const s = light("01", "The decision on the table");
  s.addText("A courier operation takes tens of thousands of support messages a month, most of them on WhatsApp, most of them in Roman Urdu or a mix of Urdu and English. Every one has to be read, labelled, routed, and answered.", {
    x: M, y: 1.95, w: 6.2, h: 1.4, fontFace: SANS, fontSize: 14, color: "2A3639", margin: 0,
  });
  s.addText("The question is which model reads them first. That is a build decision with a monthly invoice attached, so it deserves a measurement rather than a preference.", {
    x: M, y: 3.5, w: 6.2, h: 1.2, fontFace: SANS, fontSize: 14, color: "2A3639", margin: 0,
  });

  const facts = [
    ["42,000", "inbound contacts a month"],
    ["3", "languages in one inbox: English, Roman Urdu, and the mix"],
    ["1", "wrong reply is all it takes to lose a customer's trust"],
  ];
  facts.forEach(([big, small], i) => {
    const y = 1.95 + i * 1.5;
    card(s, 7.6, y, 4.85, 1.25);
    s.addText(big, { x: 7.85, y: y + 0.12, w: 1.7, h: 0.7, fontFace: SANS, fontSize: 30, bold: true, color: INK, margin: 0 });
    s.addText(small, { x: 7.85, y: y + 0.75, w: 4.3, h: 0.42, fontFace: SANS, fontSize: 11.5, color: MUTED, margin: 0 });
  });
  note(s, "Say the volume number out loud. It is what makes cost per call matter.");
}

/* ------------------------------------------------------------------ 3 */
{
  const s = light("02", "What the model is actually asked to do");
  s.addText("One customer message in. One JSON object out. The JSON goes to the ticketing system, the reply goes to the customer. Both halves matter and they fail differently.", {
    x: M, y: 1.9, w: 5.4, h: 1.3, fontFace: SANS, fontSize: 14, color: "2A3639", margin: 0,
  });
  const fails = [
    ["Wrong intent", "creates a ticket in the wrong queue. Costs staff time.", AMBER],
    ["Invented fact", "reaches the customer. Costs trust, and you find out from a complaint.", RED],
  ];
  fails.forEach(([h, t, c], i) => {
    const y = 3.5 + i * 1.35;
    s.addText(h, { x: M, y, w: 5.4, h: 0.32, fontFace: SANS, fontSize: 14, bold: true, color: c, margin: 0 });
    s.addText(t, { x: M, y: y + 0.36, w: 5.4, h: 0.6, fontFace: SANS, fontSize: 12.5, color: "2A3639", margin: 0 });
  });

  card(s, 6.85, 1.85, 5.6, 4.4, INK);
  s.addText([
    { text: "{\n", options: { color: "8FA096" } },
    { text: '  "intent":         "delayed_delivery",\n', options: { color: "E9EDE8" } },
    { text: '  "tracking_id":    "RGX8830115",\n', options: { color: "E9EDE8" } },
    { text: '  "city":           null,\n', options: { color: "E9EDE8" } },
    { text: '  "cod_amount_pkr": null,\n', options: { color: "E9EDE8" } },
    { text: '  "action":         "create_ticket",\n', options: { color: "E9EDE8" } },
    { text: '  "reply":          "Aap ka parcel check\n', options: { color: "E9EDE8" } },
    { text: '                     kar rahe hain, isi\n', options: { color: "E9EDE8" } },
    { text: '                     chat par bata denge."\n', options: { color: "E9EDE8" } },
    { text: "}", options: { color: "8FA096" } },
  ], { x: 7.15, y: 2.15, w: 5.05, h: 3.8, fontFace: MONO, fontSize: 11.5, lineSpacing: 17, margin: 0, valign: "top" });
  note(s, "Show the schema, do not read it. The point is that the output is machine-readable and customer-facing at the same time.");
}

/* ------------------------------------------------------------------ 4 */
{
  const s = light("03", "The test set is the whole argument");
  s.addText("Thirty cases, written the way people actually type on WhatsApp, and labelled by hand before a single model ran.", {
    x: M, y: 1.9, w: 11.6, h: 0.5, fontFace: SANS, fontSize: 14, color: "2A3639", margin: 0,
  });

  card(s, M, 2.65, 6.0, 1.5, INK);
  s.addText('"bhai mera parcel kahan hai 3 din ho gaye RGX8830115"', {
    x: M + 0.3, y: 2.95, w: 5.4, h: 0.9, fontFace: SANS, fontSize: 15, italic: true, color: WHITE, margin: 0,
  });

  const bits = [
    ["Gold labels", "intent, tracking number, city, COD amount, routing action", SLATE],
    ["Required facts", "what the reply has to contain, in English or Roman Urdu", GREEN],
    ["Banned inventions", "what it must not say, per case. A delivery date on a tracking query. An approved refund on a damage claim.", RED],
  ];
  bits.forEach(([h, t, c], i) => {
    const y = 4.5 + i * 0.82;
    s.addText(h, { x: M, y, w: 2.3, h: 0.3, fontFace: SANS, fontSize: 12.5, bold: true, color: c, margin: 0 });
    s.addText(t, { x: M + 2.35, y, w: 9.2, h: 0.62, fontFace: SANS, fontSize: 12, color: "2A3639", margin: 0 });
  });

  const stats = [["9", "Roman Urdu"], ["6", "mixed"], ["15", "English"], ["6", "adversarial"]];
  stats.forEach(([n, l], i) => {
    const x = 7.3 + i * 1.32;
    s.addText(n, { x, y: 2.7, w: 1.2, h: 0.55, fontFace: SANS, fontSize: 26, bold: true, color: INK, margin: 0 });
    s.addText(l, { x, y: 3.3, w: 1.25, h: 0.5, fontFace: SANS, fontSize: 10, color: MUTED, margin: 0 });
  });
  note(s, "Read the Urdu message out loud. It lands better than describing it.");
}

/* ------------------------------------------------------------------ 5 */
{
  const s = light("04", "Accuracy is six things, not one");
  const rows = [
    ["Schema valid", "20%", "Parses, and every field sits inside its enum"],
    ["Intent exact", "25%", "Exact match against the hand-set label"],
    ["Entity F1", "20%", "Tracking number, city, cash-on-delivery amount"],
    ["Action exact", "15%", "The routing decision, which decides who sees the ticket"],
    ["Grounding", "10%", "Zero if the reply contains anything from that case's banned list"],
    ["Policy facts", "10%", "Share of required facts present, matched across both languages"],
  ];
  const table = [[
    { text: "Component", options: { bold: true, color: WHITE, fill: { color: INK } } },
    { text: "Weight", options: { bold: true, color: WHITE, fill: { color: INK } } },
    { text: "What it measures", options: { bold: true, color: WHITE, fill: { color: INK } } },
  ]].concat(rows.map(r => r.map((c, i) => ({
    text: c, options: { color: i === 0 ? INK : "2A3639", bold: i === 0 },
  }))));
  s.addTable(table, {
    x: M, y: 1.95, w: 7.6, colW: [2.0, 0.95, 4.65],
    fontFace: SANS, fontSize: 11.5, border: { type: "solid", color: RULE, pt: 0.5 },
    rowH: 0.42, valign: "middle", margin: 6,
  });
  card(s, 8.8, 1.95, 3.65, 2.5, SOFT);
  s.addText("A reply that does not parse scores zero on all six.", {
    x: 9.05, y: 2.2, w: 3.15, h: 0.7, fontFace: SANS, fontSize: 14, bold: true, color: INK, margin: 0,
  });
  s.addText("In production the ticketing system drops it silently, and a dropped ticket is worse than a wrong one because nobody knows it happened.", {
    x: 9.05, y: 2.95, w: 3.15, h: 1.4, fontFace: SANS, fontSize: 11.5, color: "2A3639", margin: 0,
  });
  s.addText("Grounding is only ten percent of the composite, which understates it. It is reported on its own line for that reason, and any vendor that invents facts gets discussed on that basis whatever its total says.", {
    x: 8.8, y: 4.75, w: 3.65, h: 1.6, fontFace: SANS, fontSize: 11.5, color: MUTED, margin: 0,
  });
  note(s, "This slide is where the method earns its keep. Do not rush it.");
}

/* ------------------------------------------------------------------ 6 */
{
  const s = light("05", "Keeping it a fair fight");
  const items = [
    ["One prompt file", "Read once, hashed, sent byte for byte to all three. The hash prints on the report so nobody has to take it on trust."],
    ["Raw HTTP, not vendor SDKs", "Some SDKs retry internally and some do not. A vendor that retries silently posts better latency for a reason unrelated to its model."],
    ["Matched on tier, not on brand", "All three are each vendor's small and fast tier. Comparing a frontier model against a budget one produces a number that looks like a finding and means nothing."],
    ["Temperature zero, three repeats", "Run-to-run variance shows up as a stability number instead of disappearing into an average."],
  ];
  items.forEach(([h, t], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * 6.0, y = 2.0 + row * 2.2;
    card(s, x, y, 5.6, 1.85);
    s.addText(h, { x: x + 0.3, y: y + 0.22, w: 5.0, h: 0.35, fontFace: SANS, fontSize: 14, bold: true, color: INK, margin: 0 });
    s.addText(t, { x: x + 0.3, y: y + 0.62, w: 5.0, h: 1.1, fontFace: SANS, fontSize: 11.5, color: "2A3639", margin: 0 });
  });
  note(s, "If anyone challenges the result, this is the slide you go back to.");
}

/* ------------------------------------------------------------------ 7 */
{
  const s = light("06", "Four axes, and the weights are arguable");
  s.addChart(p.ChartType.bar, [{
    name: "Weight",
    labels: ["Accuracy", "Cost", "Latency", "Integration"],
    values: [40, 25, 20, 15],
  }], {
    x: M, y: 2.0, w: 6.0, h: 3.9,
    barDir: "bar", chartColors: [SLATE, GREEN, AMBER, MUTED], varyColors: true,
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: INK,
    dataLabelFontFace: SANS, dataLabelFontSize: 12, dataLabelFormatCode: '0"%"',
    showLegend: false, showTitle: false,
    catAxisLabelColor: INK, catAxisLabelFontFace: SANS, catAxisLabelFontSize: 12,
    valAxisLabelColor: MUTED, valAxisLabelFontSize: 10, valAxisMaxVal: 50,
    valGridLine: { color: "E4E8E2", size: 0.5 }, catGridLine: { style: "none" },
    barGapWidthPct: 60,
  });
  s.addText("Anyone can object that the weights were chosen to produce a preferred answer. So the ranking gets recomputed under five profiles.", {
    x: 7.3, y: 2.0, w: 5.15, h: 0.9, fontFace: SANS, fontSize: 13.5, color: "2A3639", margin: 0,
  });
  const profiles = ["As specified", "Accuracy first", "Cost first", "Speed first", "Equal weights"];
  profiles.forEach((t, i) => {
    s.addText(t, { x: 7.3, y: 3.15 + i * 0.44, w: 5.15, h: 0.38, fontFace: MONO, fontSize: 12, color: INK, margin: 0 });
  });
  s.addText("If the same vendor wins all five, the recommendation survives disagreement about priorities. If it does not, the memo names the assumption the decision rests on instead of hiding it.", {
    x: 7.3, y: 5.5, w: 5.15, h: 1.1, fontFace: SANS, fontSize: 11.5, color: MUTED, margin: 0,
  });
  note(s, "The weights are the softest part of any scorecard. Owning that is more persuasive than defending them.");
}

/* ------------------------------------------------------------------ 8 */
{
  const s = p.addSlide();
  s.background = { color: INK };
  eyebrow(s, "07", "8FA096");
  title(s, "Results, pending the live run", WHITE);
  s.addText("The harness, the test set, the scoring, the dashboard, and the memo are built and tested. The benchmark itself needs live keys on all three vendor accounts, and that run has not happened yet.", {
    x: M, y: 2.0, w: 6.4, h: 1.4, fontFace: SANS, fontSize: 14, color: "9DAEA3", margin: 0,
  });
  s.addText("I did not fill the gap with invented numbers. A report that looks finished and is not measured is worth less than one that says so.", {
    x: M, y: 3.6, w: 6.4, h: 1.0, fontFace: SANS, fontSize: 14, bold: true, color: WHITE, margin: 0,
  });
  const pending = [
    "Comparison table, twenty rows",
    "Sample outputs, all three side by side",
    "Latency percentiles and cost per thousand calls",
    "Failure log, by failure type",
    "Integration rubric, scored by hand",
  ];
  card(s, 7.5, 1.95, 4.95, 3.4, "1F2C2F");
  s.addText("Fills automatically from one run", {
    x: 7.8, y: 2.2, w: 4.4, h: 0.35, fontFace: MONO, fontSize: 11, color: "8FA096", margin: 0,
  });
  pending.forEach((t, i) => {
    s.addText(t, { x: 7.8, y: 2.72 + i * 0.5, w: 4.4, h: 0.44, fontFace: SANS, fontSize: 12, color: "E9EDE8", margin: 0 });
  });
  s.addText("And a caveat that stays true whatever the numbers say: thirty cases gives a confidence interval about fifteen points wide. Two vendors within ten points of each other are a tie, and no decimal places change that.", {
    x: M, y: 5.7, w: 11.6, h: 1.0, fontFace: SANS, fontSize: 12.5, color: "9DAEA3", margin: 0,
  });
  note(s, "Do not apologise for this slide. Saying it plainly is the reason the rest of the deck is believable.");
}

/* ------------------------------------------------------------------ 9 */
{
  const s = light("08", "What went wrong, and what I did about it");
  const probs = [
    ["English keyword matching failed Roman Urdu replies", "Every required fact became a set of acceptable surface forms across both languages."],
    ["Entity scoring rewarded returning nothing but nulls", "Slots empty in both gold and prediction are now excluded from the F1 entirely."],
    ["Free-tier rate limits on a 270-request run", "Backoff on 429 only, per-vendor runs that merge into one file, and a nine-request smoke test first."],
    ["Models wrapped valid JSON in a code fence", "Split into two measures: schema validity, and a separate clean-JSON rate."],
  ];
  probs.forEach(([a, b], i) => {
    const y = 1.95 + i * 1.2;
    s.addText(a, { x: M, y, w: 5.6, h: 0.75, fontFace: SANS, fontSize: 12.5, bold: true, color: RED, margin: 0 });
    s.addText(b, { x: M + 5.9, y, w: 5.7, h: 0.9, fontFace: SANS, fontSize: 12, color: GREEN, margin: 0 });
    if (i < 3) s.addShape(p.ShapeType.line, { x: M, y: y + 1.02, w: 11.6, h: 0, line: { color: "E4E8E2", width: 0.75 } });
  });
  s.addText("Four of eight. The rest are in the progress report.", {
    x: M, y: 6.7, w: 11.6, h: 0.35, fontFace: MONO, fontSize: 10.5, color: MUTED, margin: 0,
  });
  note(s, "This is the slide interviewers remember. Pick one and tell the story properly.");
}

/* ------------------------------------------------------------------ 10 */
{
  const s = light("09", "Who I approached, and how");
  const orgs = [
    ["PostEx", "Courier plus payments for e-commerce sellers, so support carries both delivery and money questions."],
    ["Rider", "Karachi last-mile built around online shippers. Volume high enough for per-contact support cost to be a real line item."],
    ["Unity Retail", "Fulfilment software for merchants, so their support conversations are with sellers rather than consumers."],
  ];
  orgs.forEach(([n, why], i) => {
    const x = M + i * 4.0;
    card(s, x, 1.95, 3.7, 2.5);
    s.addText(n, { x: x + 0.28, y: 2.2, w: 3.1, h: 0.4, fontFace: SANS, fontSize: 17, bold: true, color: INK, margin: 0 });
    s.addText(why, { x: x + 0.28, y: 2.72, w: 3.15, h: 1.5, fontFace: SANS, fontSize: 11.5, color: "2A3639", margin: 0 });
  });
  s.addText("Rules I held to", {
    x: M, y: 4.8, w: 11.6, h: 0.35, fontFace: SANS, fontSize: 14, bold: true, color: INK, margin: 0,
  });
  const rules = [
    "One message per organisation, written and sent by hand. No automation, no list send.",
    "The message says plainly that I am an intern and that I am not selling anything.",
    "No claim to have studied their operation, because I have not. The offer is to show the method and ask where the test cases are wrong.",
    "A not-interested reply closes the row the day it arrives, with no follow-up later.",
  ];
  s.addText(rules.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < rules.length - 1 } })), {
    x: M, y: 5.25, w: 11.6, h: 1.5, fontFace: SANS, fontSize: 12, color: "2A3639", paraSpaceAfter: 5, margin: 0,
  });
  note(s, "If asked about the commission: any real engagement goes through SafeX, and I say so during the call rather than after it.");
}

/* ------------------------------------------------------------------ 11 */
{
  const s = light("10", "Next week");
  const items = [
    ["1", "Run the full benchmark on live keys, one vendor at a time if rate limits bite", SLATE],
    ["2", "Score the integration rubric by hand after writing client code against each API", SLATE],
    ["3", "Rebuild the dashboard and memo, record the walkthrough video", SLATE],
    ["4", "Send the three messages and log every response, including silence", SLATE],
    ["5", "Expand the test set toward a hundred cases, with a second labeller on a sample", GREEN],
    ["6", "Add prompt injection cases, because a customer message is untrusted input", RED],
  ];
  items.forEach(([n, t, c], i) => {
    const y = 1.9 + i * 0.78;
    s.addText(n, { x: M, y, w: 0.5, h: 0.4, fontFace: MONO, fontSize: 15, bold: true, color: c, margin: 0 });
    s.addText(t, { x: M + 0.6, y, w: 11.0, h: 0.5, fontFace: SANS, fontSize: 14, color: "2A3639", margin: 0 });
  });
  s.addText("Five and six are the ones that would change the quality of the answer rather than its presentation. Thirty cases is enough to rule a vendor out and not enough to sign a contract, and untested prompt injection on a channel where strangers write the input is the largest open risk in this work.", {
    x: M, y: 6.4 - 0.15, w: 11.6, h: 0.9, fontFace: SANS, fontSize: 12, color: MUTED, margin: 0,
  });
  note(s, "End on the two items that are about rigour, not polish.");
}

/* ------------------------------------------------------------------ 12 */
{
  const s = p.addSlide();
  s.background = { color: INK };
  s.addText("The recommendation is one line.\nThe method is the deliverable.", {
    x: M, y: 2.5, w: 10.5, h: 1.9, fontFace: SANS, fontSize: 30, bold: true, color: WHITE, lineSpacing: 40, margin: 0,
  });
  s.addText("Repo, dashboard, memo, methodology, and the full failure log are in the submission.", {
    x: M, y: 4.7, w: 10.5, h: 0.5, fontFace: SANS, fontSize: 14, color: "9DAEA3", margin: 0,
  });
  s.addText("Fatima Naseer   /   SafeX Solutions   /   Group 57", {
    x: M, y: 6.4, w: 8, h: 0.3, fontFace: MONO, fontSize: 10, color: "7E9089", margin: 0,
  });
  note(s, "Stop here and take questions.");
}

p.writeFile({ fileName: "/home/claude/w4/docs/Week4_Presentation.pptx" })
  .then(f => console.log("wrote", f));
