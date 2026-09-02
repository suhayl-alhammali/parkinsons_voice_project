// Deck v3 — "sound ripples": violet + amber, chapter structure, simple English.
// Run:  node report/defence/gen_deck3.js   (from project root)
const pptxgen = require("pptxgenjs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const FIGS = path.join(ROOT, "report", "defence", "figs");

const INK = "241A45";
const MUTED = "6A6284";
const VIOLET = "43307A";
const AMBER = "D98A1F";     // amber for light slides (text-safe)
const AMBERB = "F2A93B";    // brighter amber for dark slides
const CORAL = "D9534F";
const CARD = "FFFFFF";
const EDGE = "E4DFF2";
const TINT = "F1EDFA";
const LTEXT = "F5F2FC";     // text on dark
const LMUTED = "B9B1D6";

const HEAD = "Bookman Old Style";
const BODY = "Calibri";
const W = 13.33, H = 7.5;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Suhail Mohamed Alhammali";
pres.title = "Voice Signal Analysis Using Machine Learning for Early Detection of Parkinson's Disease";

function bgL(s) { s.background = { path: path.join(FIGS, "bg3_light.png") }; }
function bgD(s) { s.background = { path: path.join(FIGS, "bg3_dark.png") }; }
function chip(s, n, dark) {
  s.addText(String(n), {
    x: W - 0.62, y: H - 0.5, w: 0.42, h: 0.32, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10, color: dark ? LMUTED : MUTED, align: "right",
  });
}
function tag(s, num, label) {
  s.addText([
    { text: num + "  ", options: { color: AMBER, bold: true } },
    { text: "·  " + label, options: { color: MUTED } },
  ], {
    x: 0.6, y: 0.34, w: 8.0, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, charSpacing: 2,
  });
}
function headline(s, text, opts) {
  s.addText(text, Object.assign({
    x: 0.6, y: 0.68, w: W - 1.2, h: 0.85, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 29, bold: true, color: INK, align: "left",
  }, opts || {}));
}
function card(s, x, y, w, h, fill) {
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.12,
    fill: { color: fill || CARD },
    line: { color: EDGE, width: 1 },
    shadow: { type: "outer", color: "B4A8D4", opacity: 0.4, blur: 10, offset: 3, angle: 90 },
  });
}
function dot(s, x, y, d, icon, ring) {
  s.addShape("ellipse", {
    x, y, w: d, h: d,
    fill: { color: TINT }, line: { color: ring || VIOLET, width: 1.4 },
    shadow: { type: "outer", color: "B4A8D4", opacity: 0.35, blur: 6, offset: 2, angle: 90 },
  });
  const pad = d * 0.26;
  s.addImage({ path: path.join(FIGS, icon + ".png"), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad });
}

// ============ 1 · TITLE (dark) ============
let s = pres.addSlide();
bgD(s);
s.addShape("ellipse", { x: W / 2 - 0.62, y: 0.85, w: 1.24, h: 1.24, fill: { color: VIOLET, transparency: 35 }, line: { color: AMBERB, width: 1.5 } });
s.addImage({ path: path.join(FIGS, "w_mic.png"), x: W / 2 - 0.31, y: 1.16, w: 0.62, h: 0.62 });
s.addText("Voice Signal Analysis Using Machine Learning\nfor Early Detection of Parkinson's Disease", {
  x: 0.9, y: 2.45, w: W - 1.8, h: 1.7, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 30, bold: true, color: LTEXT, align: "center", lineSpacing: 42,
});
s.addText("Suhail Mohamed Alhammali", {
  x: 0.9, y: 4.35, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 20, bold: true, color: AMBERB, align: "center",
});
s.addText("ID 2200208522      Supervisor: Dr. Adel Adyaf", {
  x: 0.9, y: 4.85, w: W - 1.8, h: 0.4, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 14, color: LMUTED, align: "center",
});
s.addText("Department of Biomedical Engineering  ·  Faculty of Engineering  ·  University of Tripoli  ·  Spring 2026", {
  x: 0.9, y: 5.45, w: W - 1.8, h: 0.4, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 12.5, color: LMUTED, align: "center",
});
s.addNotes("Good morning. My name is Suhail. This is my graduation project about the voice and Parkinson's disease.");

// ============ 2 · 01 THE QUESTION ============
s = pres.addSlide();
bgL(s);
tag(s, "01", "THE QUESTION");
headline(s, "One program, one question");
chip(s, 2);
card(s, 1.3, 1.85, W - 2.6, 1.85);
s.addText([
  { text: "Listen to a voice recording.  Does its pattern look more like\n", options: { color: INK } },
  { text: "Parkinson's patients", options: { color: AMBER, bold: true } },
  { text: " — or like ", options: { color: INK } },
  { text: "healthy people", options: { color: VIOLET, bold: true } },
  { text: "?", options: { color: INK } },
], {
  x: 1.3, y: 1.85, w: W - 2.6, h: 1.85, isTextBox: true, margin: 0.2,
  fontFace: HEAD, fontSize: 21, align: "center", valign: "middle", lineSpacing: 34,
});
const facts = [
  ["v_person", "37 people", "real study data"],
  ["v_wave", "74 numbers", "measured from every voice"],
  ["v_check", "not a diagnosis", "a screening helper"],
];
{
  const cw = 3.5, chh = 1.85, gap = 0.65;
  let x = (W - 3 * cw - 2 * gap) / 2, y = 4.45;
  facts.forEach(([icon, big, small]) => {
    card(s, x, y, cw, chh);
    dot(s, x + cw / 2 - 0.36, y - 0.36, 0.72, icon);
    s.addText(big, { x, y: y + 0.5, w: cw, h: 0.55, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 20, bold: true, color: VIOLET, align: "center" });
    s.addText(small, { x, y: y + 1.1, w: cw, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: MUTED, align: "center" });
    x += cw + gap;
  });
}
s.addNotes("One program, one question. Listen to a recording. Does its pattern look more like patients, or like healthy people? Thirty-seven people. Seventy-four numbers per voice. And it is not a diagnosis. It is a screening helper.");

// ============ 3 · 02 THE VOICE — disease reaches it ============
s = pres.addSlide();
bgL(s);
tag(s, "02", "THE VOICE");
headline(s, "Parkinson's reaches the voice");
chip(s, 3);
const chain3 = [["brain", "less dopamine"], ["muscles", "weaker control"], ["speech", "quieter, flatter,\nless steady"]];
{
  const cw = 3.3, chh = 1.7, gap = 0.85;
  let x = (W - 3 * cw - 2 * gap) / 2, y = 2.0;
  chain3.forEach(([t1, t2], i) => {
    card(s, x, y, cw, chh, i === 2 ? TINT : CARD);
    s.addText(t1, { x, y: y + 0.2, w: cw, h: 0.55, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 21, bold: true, color: i === 2 ? VIOLET : INK, align: "center" });
    s.addText(t2, { x, y: y + 0.78, w: cw, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: MUTED, align: "center" });
    if (i < 2) s.addShape("rightArrow", {
      x: x + cw + 0.18, y: y + chh / 2 - 0.12, w: 0.48, h: 0.24,
      fill: { color: AMBER, transparency: 20 }, line: { type: "none" },
    });
    x += cw + gap;
  });
}
s.addText([
  { text: "~90%", options: { fontFace: HEAD, fontSize: 40, bold: true, color: AMBER } },
  { text: "  of patients get voice changes — and they can start early.", options: { fontSize: 17, color: INK } },
], {
  x: 1.5, y: 4.35, w: W - 3.0, h: 0.8, isTextBox: true, margin: 0,
  fontFace: BODY, align: "center", valign: "middle",
});
s.addText("The weakness that shakes a hand also moves the voice.", {
  x: 0.9, y: 5.5, w: W - 1.8, h: 0.55, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 18, italic: true, color: VIOLET, align: "center",
});
s.addNotes("Parkinson's starts in the brain. Less dopamine. The muscles lose fine control. All muscles. Also the small muscles of speech. The voice becomes quieter, flatter, less steady. Ninety percent of patients get voice changes. And they can start early. The weakness that shakes a hand also moves the voice.");

// ============ 4 · 02 THE VOICE — three stages ============
s = pres.addSlide();
bgL(s);
tag(s, "02", "THE VOICE");
headline(s, "How a voice is made — three stages");
chip(s, 4);
const st4 = [
  ["v_lungs", "1 · Lungs", "push the air", "the power"],
  ["v_wave", "2 · Vocal folds", "vibrate very fast", "the sound (pitch)"],
  ["v_mouth", "3 · Mouth & tongue", "shape the sound", "the letters"],
];
{
  const cw = 3.6, chh = 2.8, gap = 0.62;
  let x = (W - 3 * cw - 2 * gap) / 2, y = 2.1;
  st4.forEach(([icon, t1, t2, t3], i) => {
    card(s, x, y, cw, chh);
    dot(s, x + cw / 2 - 0.42, y - 0.42, 0.84, icon);
    s.addText(t1, { x, y: y + 0.55, w: cw, h: 0.55, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 20, bold: true, color: INK, align: "center" });
    s.addText(t2, { x, y: y + 1.2, w: cw, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 15, color: MUTED, align: "center" });
    s.addText(t3, { x, y: y + 1.9, w: cw, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, italic: true, bold: true, color: AMBER, align: "center" });
    if (i < 2) s.addShape("rightArrow", {
      x: x + cw + 0.08, y: y + chh / 2 - 0.12, w: 0.44, h: 0.24,
      fill: { color: AMBER, transparency: 20 }, line: { type: "none" },
    });
    x += cw + gap;
  });
}
s.addText("Like a musical instrument: air, a vibrating part, and a shape around it.", {
  x: 0.9, y: 5.4, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 17, italic: true, color: VIOLET, align: "center",
});
s.addNotes("A voice is made in three stages. The lungs push the air. The vocal folds vibrate very fast. That vibration is the pitch. The mouth and tongue shape the sound into letters. Like a musical instrument. Parkinson's can disturb every one of these stages.");

// ============ 5 · 03 SOUND -> NUMBERS (ADC) ============
s = pres.addSlide();
bgL(s);
tag(s, "03", "SOUND BECOMES NUMBERS");
headline(s, "From air to electricity to numbers");
chip(s, 5);
const ch5 = [
  ["v_mic", "microphone", "the sound wave hits it"],
  ["v_bolt", "electricity", "the wave becomes a signal"],
  ["v_grid", "ADC", "measures it 44,100 times\nevery second"],
];
{
  const cw = 3.35, chh = 1.6, gap = 0.9;
  let x = (W - 3 * cw - 2 * gap) / 2, y = 1.7;
  ch5.forEach(([icon, t1, t2], i) => {
    card(s, x, y, cw, chh);
    dot(s, x + 0.22, y + chh / 2 - 0.33, 0.66, icon);
    s.addText(t1, { x: x + 1.0, y: y + 0.18, w: cw - 1.15, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 17, bold: true, color: INK });
    s.addText(t2, { x: x + 1.0, y: y + 0.68, w: cw - 1.15, h: 0.85, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: MUTED });
    if (i < 2) s.addShape("rightArrow", {
      x: x + cw + 0.16, y: y + chh / 2 - 0.12, w: 0.5, h: 0.24,
      fill: { color: AMBER, transparency: 20 }, line: { type: "none" },
    });
    x += cw + gap;
  });
}
s.addImage({ path: path.join(FIGS, "adc3.png"), x: 2.35, y: 3.65, w: 8.6, h: 8.6 * 620 / 1600 });
s.addText([
  { text: "one smooth wave", options: { color: VIOLET, bold: true } },
  { text: "      →      ", options: { color: MUTED } },
  { text: "44,100 numbers every second", options: { color: AMBER, bold: true } },
], {
  x: 0.9, y: 6.6, w: W - 1.8, h: 0.45, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 15.5, align: "center",
});
s.addNotes("How does a computer hear? The sound wave hits the microphone. It becomes an electrical signal. Then the ADC, the analog to digital converter, measures the signal 44,100 times every second. Each measurement is one number. A two-minute recording becomes about five million numbers.");

// ============ 6 · 03 Mono & WAV ============
s = pres.addSlide();
bgL(s);
tag(s, "03", "SOUND BECOMES NUMBERS");
headline(s, "One channel, nothing lost");
chip(s, 6);
{
  const cw = 5.55, chh = 2.4, gap = 0.7;
  let x = (W - 2 * cw - gap) / 2, y = 2.0;
  card(s, x, y, cw, chh);
  dot(s, x + cw / 2 - 0.4, y - 0.4, 0.8, "v_volume");
  s.addText("Mono", { x, y: y + 0.5, w: cw, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 24, bold: true, color: INK, align: "center" });
  s.addText("one channel = one list of numbers.\nOne voice needs only one list.", {
    x: x + 0.35, y: y + 1.2, w: cw - 0.7, h: 1.0, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14.5, color: MUTED, align: "center",
  });
  const x2 = x + cw + gap;
  card(s, x2, y, cw, chh);
  dot(s, x2 + cw / 2 - 0.4, y - 0.4, 0.8, "v_wavfile");
  s.addText("WAV file", { x: x2, y: y + 0.5, w: cw, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 24, bold: true, color: INK, align: "center" });
  s.addText("keeps every number exactly as recorded.\nNothing deleted, nothing lost.", {
    x: x2 + 0.35, y: y + 1.2, w: cw - 0.7, h: 1.0, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14.5, color: MUTED, align: "center",
  });
}
card(s, 2.0, 5.0, W - 4.0, 1.05, TINT);
s.addText([
  { text: "Why not MP3?  ", options: { bold: true, color: VIOLET } },
  { text: "MP3 deletes small details to save space — and the small details are exactly what we measure.", options: { color: INK } },
], {
  x: 2.0, y: 5.0, w: W - 4.0, h: 1.05, isTextBox: true, margin: 0.15,
  fontFace: BODY, fontSize: 15.5, align: "center", valign: "middle",
});
s.addNotes("Two small choices. Mono: one channel, one list of numbers. Enough for one voice. And WAV files. WAV keeps every number exactly as recorded. Why not MP3? MP3 deletes small details to save space. But the small details are exactly what we measure.");

// ============ 7 · 04 THE DATA ============
s = pres.addSlide();
bgL(s);
tag(s, "04", "THE DATA");
headline(s, "Real voices, checked before use");
chip(s, 7);
const d7 = [["37", "people"], ["21 / 16", "healthy / Parkinson's"], ["73", "recordings"], ["~2 min", "each, on a phone"]];
{
  const cw = 2.75, chh = 1.65, gap = 0.55;
  let x = (W - 4 * cw - 3 * gap) / 2, y = 1.85;
  d7.forEach(([big, small]) => {
    card(s, x, y, cw, chh);
    s.addText(big, { x, y: y + 0.18, w: cw, h: 0.8, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 30, bold: true, color: VIOLET, align: "center" });
    s.addText(small, { x, y: y + 1.02, w: cw, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: MUTED, align: "center" });
    x += cw + gap;
  });
}
dot(s, 1.35, 4.15, 0.7, "v_db");
s.addText([
  { text: "MDVR-KCL", options: { bold: true, color: INK } },
  { text: " — a public research dataset from King's College London.\nEveryone reads a text and has a free conversation — normal speech.", options: { color: MUTED } },
], {
  x: 2.3, y: 4.05, w: W - 3.4, h: 1.0, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 15,
});
card(s, 2.0, 5.45, W - 4.0, 1.0, TINT);
s.addText([
  { text: "Checked before training:  ", options: { bold: true, color: VIOLET } },
  { text: "labels, speaker identity, no duplicates, no damaged files.", options: { color: INK } },
], {
  x: 2.0, y: 5.45, w: W - 4.0, h: 1.0, isTextBox: true, margin: 0.15,
  fontFace: BODY, fontSize: 15, align: "center", valign: "middle",
});
s.addNotes("Our data is called MDVR-KCL. A public research dataset from King's College London. Thirty-seven people. Twenty-one healthy, sixteen with Parkinson's. Seventy-three recordings, about two minutes each, on a phone. Everyone reads a text and has a conversation. Normal speech. And we checked every file before training.");

// ============ 8 · 05 CLEANING ============
s = pres.addSlide();
bgL(s);
tag(s, "05", "GETTING READY");
headline(s, "Five careful cleaning steps — and one refusal");
chip(s, 8);
const p8 = [
  ["v_volume", "mono", "one channel"],
  ["v_arrows", "44.1 kHz", "same clock\nfor all"],
  ["v_broom", "remove offset", "center the wave"],
  ["v_scissors", "trim silence", "edges only"],
  ["v_gauge", "same loudness", "fair comparison"],
];
{
  const cw = 2.2, chh = 1.95, gap = 0.35;
  let x = (W - 5 * cw - 4 * gap) / 2, y = 1.85;
  p8.forEach(([icon, t1, t2]) => {
    card(s, x, y, cw, chh);
    dot(s, x + cw / 2 - 0.31, y - 0.31, 0.62, icon);
    s.addText(t1, { x, y: y + 0.42, w: cw, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15, bold: true, color: INK, align: "center" });
    s.addText(t2, { x: x + 0.1, y: y + 0.95, w: cw - 0.2, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: MUTED, align: "center" });
    x += cw + gap;
  });
}
dot(s, 2.35, 4.5, 0.8, "c_ban", CORAL);
card(s, 3.4, 4.5, W - 5.4, 1.4);
s.addText([
  { text: "We did NOT remove noise.\n", options: { bold: true, color: CORAL, fontSize: 17 } },
  { text: "Noise removal smooths away the small irregularities — and those irregularities are the medical evidence.", options: { color: INK, fontSize: 14.5 } },
], {
  x: 3.4, y: 4.5, w: W - 5.4, h: 1.4, isTextBox: true, margin: 0.15,
  fontFace: BODY, align: "left", valign: "middle",
});
s.addNotes("Before measuring, five careful cleaning steps. One channel. One clock for all recordings. Center the wave. Trim the silence at the edges only. Same loudness for everyone. And one refusal: we did not remove noise. Noise removal smooths away the small irregularities. But those irregularities are the medical evidence.");

// ============ 9 · 06 MEASURING ============
s = pres.addSlide();
bgL(s);
tag(s, "06", "MEASURING");
headline(s, "74 numbers — each answers a simple question");
chip(s, 9);
const m9 = [
  ["Is the pitch flat or lively?", "pitch range", "monotone speech is a classic sign"],
  ["Is the vibration steady?", "jitter & shimmer", "shaky control makes it uneven"],
  ["Is the voice clear or breathy?", "noise ratio (HNR)", "weak folds let air leak"],
  ["Are there many pauses?", "pause statistics", "starting speech becomes harder"],
  ["How fast does the mouth move?", "spectrum (MFCC)", "small slow movements blur letters"],
];
{
  let y = 1.6;
  m9.forEach(([q, m, whyTxt]) => {
    card(s, 0.9, y, W - 1.8, 0.9);
    s.addText(q, { x: 1.2, y, w: 4.6, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 15, bold: true, color: INK, valign: "middle" });
    s.addText(m, { x: 6.0, y, w: 2.9, h: 0.9, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 14.5, bold: true, color: VIOLET, valign: "middle" });
    s.addText(whyTxt, { x: 9.0, y, w: 3.3, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, italic: true, color: MUTED, valign: "middle" });
    y += 1.06;
  });
}
s.addNotes("From every recording we compute seventy-four numbers. Each answers a simple question. Is the pitch flat or lively? Is the vibration steady? Is the voice clear or breathy? Are there many pauses? How fast does the mouth move? Every number has a medical reason behind it.");

// ============ 10 · 07 TEACHING ============
s = pres.addSlide();
bgL(s);
tag(s, "07", "TEACHING THE COMPUTER");
headline(s, "Training, testing — and one golden rule");
chip(s, 10);
{
  const cw = 5.55, chh = 2.35, gap = 0.7;
  let x = (W - 2 * cw - gap) / 2, y = 1.85;
  card(s, x, y, cw, chh);
  s.addText("TRAINING", { x, y: y + 0.22, w: cw, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 19, bold: true, color: VIOLET, align: "center" });
  s.addText("show many recordings WITH answers\n→ the computer finds the pattern", {
    x: x + 0.3, y: y + 0.9, w: cw - 0.6, h: 1.2, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 15.5, color: INK, align: "center",
  });
  const x2 = x + cw + gap;
  card(s, x2, y, cw, chh);
  s.addText("TESTING", { x: x2, y: y + 0.22, w: cw, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 19, bold: true, color: AMBER, align: "center" });
  s.addText("new people, NO answers\n→ can it still tell?", {
    x: x2 + 0.3, y: y + 0.9, w: cw - 0.6, h: 1.2, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 15.5, color: INK, align: "center",
  });
}
card(s, 1.6, 4.75, W - 3.2, 1.35, TINT);
s.addText([
  { text: "Golden rule:  ", options: { bold: true, color: VIOLET } },
  { text: "never test on a person the computer trained on.\nA student who saw the exam questions proves nothing.", options: { color: INK } },
], {
  x: 1.6, y: 4.75, w: W - 3.2, h: 1.35, isTextBox: true, margin: 0.15,
  fontFace: BODY, fontSize: 16.5, align: "center", valign: "middle",
});
s.addNotes("How does the computer learn? Training: we show it many recordings with the answers. It finds the pattern. Testing: new people, no answers. Can it still tell? And one golden rule. Never test on a person the computer trained on. A student who saw the exam questions proves nothing. This rule is the heart of our project. The next slide shows why.");

// ============ 11 · DARK REVEAL — most important ============
s = pres.addSlide();
bgD(s);
chip(s, 11, true);
s.addText("The most important slide in this project", {
  x: 0.6, y: 0.5, w: W - 1.2, h: 0.7, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 26, bold: true, color: LTEXT, align: "left",
});
s.addText("Same data.  Same model.  Only the split changed.", {
  x: 0.6, y: 1.25, w: W - 1.2, h: 0.5, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 16, italic: true, color: LMUTED, align: "left",
});
// wrong side
s.addText("0.909", {
  x: 0.8, y: 2.2, w: 5.6, h: 1.6, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 84, bold: true, color: AMBERB, align: "center",
});
s.addText("the WRONG way: test on voices\nthe computer partly heard before", {
  x: 0.8, y: 3.9, w: 5.6, h: 0.85, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 15, color: AMBERB, align: "center",
});
// honest side (revealed on click)
s.addText("0.775", {
  x: 6.9, y: 2.2, w: 5.6, h: 1.6, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 84, bold: true, color: LTEXT, align: "center",
});
s.addText("the HONEST way: test only on people\nthe computer never heard", {
  x: 6.9, y: 3.9, w: 5.6, h: 0.85, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 15, color: LMUTED, align: "center",
});
s.addShape("line", { x: W / 2, y: 2.3, w: 0, h: 2.3, line: { color: LMUTED, width: 1, dashType: "dash" } });
s.addText([
  { text: "The difference is memorising people, not detecting disease.\n", options: { color: LTEXT, bold: true } },
  { text: "This is why many published 95%+ results are not what they seem — our number is honest.", options: { color: LMUTED } },
], {
  x: 1.2, y: 5.35, w: W - 2.4, h: 1.2, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 16.5, align: "center",
});
s.addNotes("This is the most important slide. Same data. Same model. Only the split changed. Tested the wrong way, on voices it partly heard before: 0.909. Looks amazing. [Click.] Tested the honest way, only on people it never heard: 0.775. The difference is memorising people. Not detecting disease. This is why many published 95 percent results are not what they seem. Our number is honest.");

// ============ 12 · 08 OUR MODEL ============
s = pres.addSlide();
bgL(s);
tag(s, "08", "OUR MODEL");
headline(s, "A forest of 300 small decisions");
chip(s, 12);
{
  const d = 0.95, gap = 0.45;
  let x = (W - 3 * d - 2 * gap) / 2;
  for (let i = 0; i < 3; i++) { dot(s, x, 1.75, d, "v_tree"); x += d + gap; }
}
s.addText("Random Forest", {
  x: 0.9, y: 2.95, w: W - 1.8, h: 0.6, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 26, bold: true, color: VIOLET, align: "center",
});
s.addText("300 small decision trees look at the 74 numbers — then they vote.", {
  x: 0.9, y: 3.55, w: W - 1.8, h: 0.45, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 16, color: INK, align: "center",
});
{
  const cw = 5.55, chh = 1.5, gap = 0.7;
  let x = (W - 2 * cw - gap) / 2, y = 4.3;
  card(s, x, y, cw, chh);
  s.addText([
    { text: "Why this model?\n", options: { bold: true, color: INK } },
    { text: "we can ask it which numbers it used — explainable", options: { color: MUTED } },
  ], { x, y, w: cw, h: chh, isTextBox: true, margin: 0.15, fontFace: BODY, fontSize: 14.5, valign: "middle" });
  const x2 = x + cw + gap;
  card(s, x2, y, cw, chh, TINT);
  s.addText([
    { text: "Its favourite number?\n", options: { bold: true, color: INK } },
    { text: "pitch range — the monotone sign doctors know", options: { color: VIOLET, bold: true } },
  ], { x: x2, y, w: cw, h: chh, isTextBox: true, margin: 0.15, fontFace: BODY, fontSize: 14.5, valign: "middle" });
}
s.addText("Four models competed under the same honest test — this one won.", {
  x: 0.9, y: 6.1, w: W - 1.8, h: 0.45, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13.5, italic: true, color: MUTED, align: "center",
});
s.addNotes("Our model is a Random Forest. Three hundred small decision trees look at the seventy-four numbers. Then they vote. Why this model? We can ask it which numbers it used. It is explainable. Its favourite number is pitch range. The monotone sign doctors already know. Four models competed. This one won.");

// ============ 13 · 09 RESULTS ============
s = pres.addSlide();
bgL(s);
tag(s, "09", "RESULTS");
headline(s, "How good is it — in plain words");
chip(s, 13);
const r13 = [
  ["0.822", "balanced accuracy", "the fair overall score, on\npeople it never heard"],
  ["77%", "sensitivity", "of all true patients,\nhow many did we catch?"],
  ["87%", "specificity", "of all healthy people,\nhow many did we clear?"],
];
{
  const cw = 3.55, chh = 2.8, gap = 0.7;
  let x = (W - 3 * cw - 2 * gap) / 2, y = 1.95;
  r13.forEach(([big, name, small]) => {
    card(s, x, y, cw, chh);
    s.addText(big, { x, y: y + 0.28, w: cw, h: 1.0, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 42, bold: true, color: VIOLET, align: "center" });
    s.addText(name, { x, y: y + 1.32, w: cw, h: 0.45, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15, bold: true, color: INK, align: "center" });
    s.addText(small, { x: x + 0.2, y: y + 1.8, w: cw - 0.4, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: MUTED, align: "center" });
    x += cw + gap;
  });
}
card(s, 2.0, 5.3, W - 4.0, 1.0, TINT);
s.addText([
  { text: "Why not plain accuracy?  ", options: { bold: true, color: VIOLET } },
  { text: "a lazy model that always says “healthy” scores 57.5% — and finds zero patients.", options: { color: INK } },
], {
  x: 2.0, y: 5.3, w: W - 4.0, h: 1.0, isTextBox: true, margin: 0.12,
  fontFace: BODY, fontSize: 14.5, align: "center", valign: "middle",
});
s.addNotes("How good is it? Balanced accuracy 0.822, on people it never heard. Sensitivity 77 percent: of all true patients, how many did we catch? Specificity 87 percent: of all healthy people, how many did we clear? Why not plain accuracy? A lazy model that always says healthy scores 57.5 percent and finds zero patients.");

// ============ 14 · 09 CONFUSION MATRIX ============
s = pres.addSlide();
bgL(s);
tag(s, "09", "RESULTS");
headline(s, "Every recording, counted honestly");
chip(s, 14);
{
  const cx = 3.3, cy = 2.3, cell = 1.85, gap = 0.16;
  s.addText("model says:\nhealthy", { x: cx, y: cy - 0.85, w: cell, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, bold: true, color: MUTED, align: "center" });
  s.addText("model says:\nParkinson's", { x: cx + cell + gap, y: cy - 0.85, w: cell, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, bold: true, color: MUTED, align: "center" });
  s.addText("really\nhealthy", { x: cx - 1.5, y: cy + 0.4, w: 1.35, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, bold: true, color: MUTED, align: "right" });
  s.addText("really\nParkinson's", { x: cx - 1.5, y: cy + cell + gap + 0.4, w: 1.35, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, bold: true, color: MUTED, align: "right" });
  const cells = [
    [0, 0, "36", "correct", VIOLET],
    [1, 0, "6", "false alarm", CORAL],
    [0, 1, "7", "missed", CORAL],
    [1, 1, "24", "caught", VIOLET],
  ];
  cells.forEach(([cxi, cyi, v, lab, color]) => {
    const x = cx + cxi * (cell + gap), y = cy + cyi * (cell + gap);
    s.addShape("roundRect", {
      x, y, w: cell, h: cell, rectRadius: 0.12,
      fill: { color, transparency: color === VIOLET ? 85 : 84 },
      line: { color, width: 1.5 },
    });
    s.addText(v, { x, y: y + 0.28, w: cell, h: 0.85, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 36, bold: true, color, align: "center" });
    s.addText(lab, { x, y: y + 1.2, w: cell, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: INK, align: "center" });
  });
}
s.addText([
  { text: "Out of 73 recordings:\n", options: { color: INK } },
  { text: "60 correct", options: { color: VIOLET, bold: true } },
  { text: "  ·  ", options: { color: MUTED } },
  { text: "13 mistakes", options: { color: CORAL, bold: true } },
  { text: "\n\nEvery screening tool makes mistakes.\nHonest tools count them.", options: { color: MUTED, italic: true } },
], {
  x: 7.8, y: 2.6, w: 5.0, h: 2.6, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 16.5, align: "left", lineSpacing: 26,
});
s.addNotes("This table counts every recording. Thirty-six healthy correctly cleared. Six false alarms. Seven patients missed. Twenty-four caught. Out of 73 recordings, 60 correct and 13 mistakes. Every screening tool makes mistakes. Honest tools count them.");

// ============ 15 · 10 THE HARD TEST ============
s = pres.addSlide();
bgL(s);
tag(s, "10", "THE HARD TEST");
headline(s, "A different country, a frozen model");
chip(s, 15);
const it15 = [
  ["61 Italian speakers", "different language, microphones, rooms — and the model was frozen: no re-training at all"],
  ["AUC 0.701", "given one patient and one healthy person, it still ranks the patient higher 70% of the time"],
  ["it refused to guess", "every elderly healthy speaker got “cannot tell” instead of a wrong confident answer"],
];
{
  let y = 1.75;
  it15.forEach(([t1, t2], i) => {
    card(s, 1.4, y, W - 2.8, 1.35, i === 2 ? TINT : CARD);
    s.addText(t1, { x: 1.75, y, w: 3.6, h: 1.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 18, bold: true, color: i === 2 ? VIOLET : INK, valign: "middle" });
    s.addText(t2, { x: 5.6, y, w: 7.0, h: 1.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14.5, color: MUTED, valign: "middle" });
    y += 1.6;
  });
}
s.addText("Knowing when to say “I don't know” is part of being honest.", {
  x: 0.9, y: 6.55, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 16, italic: true, color: VIOLET, align: "center",
});
s.addNotes("Then the hardest test. Sixty-one Italian speakers. Different language, microphones, rooms. And the model was frozen. No retraining. It still ranks a patient above a healthy person 70 percent of the time. And for every elderly healthy speaker, it said: cannot tell. It refused to guess. Knowing when to say I don't know is part of being honest.");

// ============ 16 · DARK REMEMBER ============
s = pres.addSlide();
bgD(s);
chip(s, 16, true);
s.addText("Three things to remember", {
  x: 0.6, y: 0.55, w: W - 1.2, h: 0.75, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 28, bold: true, color: LTEXT,
});
const rem = [
  "The voice carries a real, measurable signal of Parkinson's.",
  "We tested honestly — only on people the computer never heard.",
  "It is a screening helper, not a diagnosis — a doctor decides.",
];
{
  let y = 1.95;
  rem.forEach((t, i) => {
    s.addShape("ellipse", { x: 1.7, y: y + 0.18, w: 0.62, h: 0.62, fill: { color: AMBERB }, line: { type: "none" } });
    s.addText(String(i + 1), { x: 1.7, y: y + 0.18, w: 0.62, h: 0.62, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 20, bold: true, color: INK, align: "center", valign: "middle" });
    s.addText(t, { x: 2.65, y, w: W - 4.3, h: 1.0, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 19, color: LTEXT, valign: "middle" });
    y += 1.35;
  });
}
s.addText("An honest 0.822 is worth more than an inflated number.", {
  x: 0.9, y: 6.3, w: W - 1.8, h: 0.55, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 17, italic: true, color: AMBERB, align: "center",
});
s.addNotes("Three things to remember. One: the voice carries a real, measurable signal. Two: we tested honestly. Only on people the computer never heard. Three: it is a screening helper, not a diagnosis. A doctor decides. An honest 0.822 is worth more than an inflated number.");

// ============ 17 · THANK YOU (dark) ============
s = pres.addSlide();
bgD(s);
s.addText("Thank you", {
  x: 0.9, y: 2.9, w: W - 1.8, h: 1.0, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 48, bold: true, color: LTEXT, align: "center",
});
s.addText("Questions are welcome.", {
  x: 0.9, y: 4.1, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 17, color: LMUTED, align: "center",
});
s.addNotes("Thank you. I welcome your questions.");

const out = path.join(ROOT, "report", "defence", "slides_v3.pptx");
pres.writeFile({ fileName: out }).then(() => console.log("wrote", out));
