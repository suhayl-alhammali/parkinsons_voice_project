// Light-theme "lecture" deck (v2) — simple English, concept-first order.
// Run:  node report/defence/gen_deck2.js   (from project root)
const pptxgen = require("pptxgenjs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const FIGS = path.join(ROOT, "report", "defence", "figs");

// ---------- palette (light medical) ----------
const INK = "16324A";      // deep slate text
const MUTED = "5B7286";    // secondary text
const TEAL = "028090";     // primary
const TEALD = "026873";    // deep teal
const CORAL = "E85A5A";    // warm accent / errors / PD
const CARD = "FFFFFF";
const EDGE = "D9E5EE";
const TINT = "EAF4F5";     // pale teal tint

const HEAD = "Cambria";
const BODY = "Calibri";
const W = 13.33, H = 7.5;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Suhail Mohamed Alhammali";
pres.title = "Voice Signal Analysis Using Machine Learning for Early Detection of Parkinson's Disease";

function bg(s, hero) {
  s.background = { path: path.join(FIGS, hero ? "bg2_hero.png" : "bg2_main.png") };
}
function chip(s, n) {
  s.addText(String(n), {
    x: W - 0.62, y: H - 0.52, w: 0.42, h: 0.34, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10, color: MUTED, align: "right",
  });
}
function wave(s, yTop, h) {
  s.addImage({ path: path.join(FIGS, "wave_teal.png"), x: 0, y: yTop, w: W, h });
}
function headline(s, text, opts) {
  s.addText(text, Object.assign({
    x: 0.55, y: 0.32, w: W - 1.1, h: 0.75, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 30, bold: true, color: INK, align: "left",
  }, opts || {}));
}
function card(s, x, y, w, h, fill) {
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.1,
    fill: { color: fill || CARD },
    line: { color: EDGE, width: 1 },
    shadow: { type: "outer", color: "9FB4C4", opacity: 0.35, blur: 9, offset: 3, angle: 90 },
  });
}
function iconDot(s, x, y, d, icon, ring) {
  s.addShape("ellipse", {
    x, y, w: d, h: d,
    fill: { color: TINT }, line: { color: ring || TEAL, width: 1.4 },
    shadow: { type: "outer", color: "9FB4C4", opacity: 0.3, blur: 6, offset: 2, angle: 90 },
  });
  const pad = d * 0.26;
  s.addImage({ path: path.join(FIGS, icon + ".png"), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad });
}

// =========================== 1 TITLE ===========================
let s = pres.addSlide();
bg(s, true);
wave(s, 5.85, 1.65);
s.addText("Voice Signal Analysis Using Machine Learning\nfor Early Detection of Parkinson's Disease", {
  x: 0.9, y: 1.2, w: W - 1.8, h: 1.7, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 32, bold: true, color: INK, align: "center", lineSpacing: 42,
});
s.addText("Suhail Mohamed Alhammali", {
  x: 0.9, y: 3.05, w: W - 1.8, h: 0.45, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 20, bold: true, color: TEAL, align: "center",
});
s.addText("ID 2200208522      Supervisor: Dr. Adel Adyaf", {
  x: 0.9, y: 3.52, w: W - 1.8, h: 0.38, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 14, color: MUTED, align: "center",
});
s.addText("Department of Biomedical Engineering  •  Faculty of Engineering\nUniversity of Tripoli  •  Spring 2026", {
  x: 0.9, y: 4.05, w: W - 1.8, h: 0.7, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, color: MUTED, align: "center",
});
s.addNotes("Good morning. My name is Suhail. This is my graduation project about the voice and Parkinson's disease.");

// =========================== 2 WHAT IS THIS PROJECT ===========================
s = pres.addSlide();
bg(s);
headline(s, "What is this project?");
chip(s, 2);
card(s, 1.3, 1.6, W - 2.6, 1.9, CARD);
s.addText([
  { text: "A computer program that listens to a voice recording\nand answers one question: ", options: { color: INK } },
  { text: "does this voice pattern look more like\nParkinson's patients — or like healthy people?", options: { color: TEALD, bold: true } },
], {
  x: 1.3, y: 1.6, w: W - 2.6, h: 1.9, isTextBox: true, margin: 0.2,
  fontFace: HEAD, fontSize: 21, align: "center", valign: "middle", lineSpacing: 32,
});
const facts2 = [
  ["t_person", "37 people", "in the study data"],
  ["t_wave", "74 measurements", "from every recording"],
  ["t_check", "not a diagnosis", "a research screening idea"],
];
{
  const cw = 3.5, chh = 1.9, gap = 0.65;
  let x = (W - 3 * cw - 2 * gap) / 2, y = 4.15;
  facts2.forEach(([icon, big, small]) => {
    card(s, x, y, cw, chh);
    iconDot(s, x + cw / 2 - 0.37, y - 0.37, 0.74, icon);
    s.addText(big, { x, y: y + 0.55, w: cw, h: 0.55, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 21, bold: true, color: TEAL, align: "center" });
    s.addText(small, { x, y: y + 1.15, w: cw, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: MUTED, align: "center" });
    x += cw + gap;
  });
}
s.addNotes("In one sentence: the program listens to a recording. It answers one question. Does this voice pattern look more like patients, or like healthy people? It is not a diagnosis. It is a research screening idea.");

// =========================== 3 WHY THE VOICE ===========================
s = pres.addSlide();
bg(s);
headline(s, "Why the voice?");
chip(s, 3);
const why3 = [
  ["t_ear", "~90%", "of patients get\nvoice changes"],
  ["t_clock", "early", "changes can start years\nbefore diagnosis"],
  ["t_mic", "easy", "a microphone is cheap\nand painless"],
];
{
  const cw = 3.55, chh = 3.0, gap = 0.7;
  let x = (W - 3 * cw - 2 * gap) / 2, y = 1.95;
  why3.forEach(([icon, big, small]) => {
    card(s, x, y, cw, chh);
    iconDot(s, x + cw / 2 - 0.42, y - 0.42, 0.84, icon);
    s.addText(big, { x, y: y + 0.7, w: cw, h: 1.0, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 44, bold: true, color: TEAL, align: "center" });
    s.addText(small, { x: x + 0.2, y: y + 1.85, w: cw - 0.4, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: MUTED, align: "center" });
    x += cw + gap;
  });
}
s.addText("Parkinson's weakens every muscle — also the small muscles of speech.", {
  x: 0.9, y: 5.35, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 17, italic: true, color: INK, align: "center",
});
s.addNotes("Why the voice? Ninety percent of patients get voice changes. The changes can start early. And a microphone is cheap and painless. Parkinson's weakens every muscle. Also the small muscles of speech.");

// =========================== 4 VOICE IN 3 STAGES ===========================
s = pres.addSlide();
bg(s);
headline(s, "How the voice is made — three stages");
chip(s, 4);
const stages4 = [
  ["t_lungs", "1. Lungs", "push the air", "the power"],
  ["t_wave", "2. Vocal folds", "vibrate very fast", "the sound  (pitch)"],
  ["t_mouth", "3. Mouth & tongue", "shape the sound", "the letters"],
];
{
  const cw = 3.6, chh = 2.9, gap = 0.62;
  let x = (W - 3 * cw - 2 * gap) / 2, y = 1.95;
  stages4.forEach(([icon, t1, t2, t3], i) => {
    card(s, x, y, cw, chh);
    iconDot(s, x + cw / 2 - 0.42, y - 0.42, 0.84, icon);
    s.addText(t1, { x, y: y + 0.6, w: cw, h: 0.55, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 22, bold: true, color: INK, align: "center" });
    s.addText(t2, { x, y: y + 1.25, w: cw, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 15, color: MUTED, align: "center" });
    s.addText(t3, { x, y: y + 1.95, w: cw, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 17, italic: true, bold: true, color: TEAL, align: "center" });
    if (i < 2) s.addShape("rightArrow", {
      x: x + cw + 0.08, y: y + chh / 2 - 0.12, w: 0.44, h: 0.24,
      fill: { color: MUTED, transparency: 45 }, line: { type: "none" },
    });
    x += cw + gap;
  });
}
s.addText("Like a musical instrument: air, a vibrating part, and a shape around it.", {
  x: 0.9, y: 5.3, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 17, italic: true, color: INK, align: "center",
});
s.addNotes("The voice is made in three stages. The lungs push the air. The vocal folds vibrate very fast. That vibration is the pitch. The mouth and tongue shape the sound into letters. Like a musical instrument.");

// =========================== 5 WHAT WE MEASURE ===========================
s = pres.addSlide();
bg(s);
headline(s, "What we measure — 74 numbers per recording");
chip(s, 5);
const meas5 = [
  ["Is the pitch flat or lively?", "pitch range", "monotone speech is a classic sign"],
  ["Is the vibration steady?", "jitter & shimmer", "shaky muscle control makes it uneven"],
  ["Is the voice clear or breathy?", "noise ratio (HNR)", "weak folds let air leak through"],
  ["Are there many pauses?", "pause statistics", "starting speech becomes harder"],
  ["How fast does the mouth move?", "spectrum (MFCC)", "slow, small movements blur the letters"],
];
{
  let y = 1.5;
  meas5.forEach(([q, m, whyTxt]) => {
    card(s, 0.9, y, W - 1.8, 0.92, CARD);
    s.addText(q, {
      x: 1.2, y, w: 4.6, h: 0.92, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 15.5, bold: true, color: INK, align: "left", valign: "middle",
    });
    s.addText(m, {
      x: 6.0, y, w: 2.9, h: 0.92, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 15.5, bold: true, color: TEAL, align: "left", valign: "middle",
    });
    s.addText(whyTxt, {
      x: 9.0, y, w: 3.3, h: 0.92, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12.5, italic: true, color: MUTED, align: "left", valign: "middle",
    });
    y += 1.08;
  });
}
s.addNotes("We turn every recording into seventy-four numbers. Each number answers a simple question. Is the pitch flat or lively? Is the vibration steady? Is the voice clear or breathy? Are there many pauses? How fast does the mouth move? Every number has a medical reason.");

// =========================== 6 ADC ===========================
s = pres.addSlide();
bg(s);
headline(s, "How sound becomes numbers");
chip(s, 6);
// chain: mic -> bolt -> ADC -> numbers
const chain6 = [
  ["t_mic", "microphone", "sound wave hits it"],
  ["t_bolt", "electricity", "the wave becomes a signal"],
  ["t_grid", "ADC", "measures it 44,100 times\nevery second"],
];
{
  const cw = 3.35, chh = 1.75, gap = 0.9;
  let x = (W - 3 * cw - 2 * gap) / 2, y = 1.5;
  chain6.forEach(([icon, t1, t2], i) => {
    card(s, x, y, cw, chh);
    iconDot(s, x + 0.22, y + chh / 2 - 0.35, 0.7, icon);
    s.addText(t1, { x: x + 1.05, y: y + 0.22, w: cw - 1.2, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 18, bold: true, color: INK });
    s.addText(t2, { x: x + 1.05, y: y + 0.75, w: cw - 1.2, h: 0.85, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: MUTED });
    if (i < 2) s.addShape("rightArrow", {
      x: x + cw + 0.16, y: y + chh / 2 - 0.12, w: 0.5, h: 0.24,
      fill: { color: MUTED, transparency: 45 }, line: { type: "none" },
    });
    x += cw + gap;
  });
}
s.addImage({ path: path.join(FIGS, "adc_wave.png"), x: 2.2, y: 3.6, w: 8.9, h: 3.56 * 0.75 });
s.addText([
  { text: "analog wave", options: { color: TEAL, bold: true } },
  { text: "        →        ", options: { color: MUTED } },
  { text: "samples: one number each", options: { color: CORAL, bold: true } },
], {
  x: 0.9, y: 6.45, w: W - 1.8, h: 0.45, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 15, align: "center",
});
s.addNotes("How does sound become numbers? The sound wave hits the microphone. It becomes an electrical signal. Then a converter called ADC measures this signal 44,100 times every second. Each measurement is one number, called a sample. A two-minute recording is about five million numbers.");

// =========================== 7 MONO & WAV ===========================
s = pres.addSlide();
bg(s);
headline(s, "One channel, no compression");
chip(s, 7);
{
  const cw = 5.55, chh = 2.6, gap = 0.7;
  let x = (W - 2 * cw - gap) / 2, y = 1.9;
  // mono card
  card(s, x, y, cw, chh);
  iconDot(s, x + cw / 2 - 0.42, y - 0.42, 0.84, "t_volume");
  s.addText("Mono", { x, y: y + 0.6, w: cw, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 26, bold: true, color: INK, align: "center" });
  s.addText("one channel = one list of numbers.\nWe study one voice, so one list is enough.", {
    x: x + 0.35, y: y + 1.35, w: cw - 0.7, h: 1.0, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14.5, color: MUTED, align: "center",
  });
  // wav card
  const x2 = x + cw + gap;
  card(s, x2, y, cw, chh);
  iconDot(s, x2 + cw / 2 - 0.42, y - 0.42, 0.84, "t_wavfile");
  s.addText("WAV file", { x: x2, y: y + 0.6, w: cw, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 26, bold: true, color: INK, align: "center" });
  s.addText("keeps every number exactly as recorded.\nNothing is deleted, nothing is lost.", {
    x: x2 + 0.35, y: y + 1.35, w: cw - 0.7, h: 1.0, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14.5, color: MUTED, align: "center",
  });
}
card(s, 2.0, 5.0, W - 4.0, 1.0, TINT);
s.addText([
  { text: "MP3 deletes small details to save space — and small details are ", options: { color: INK } },
  { text: "exactly what we measure.", options: { color: TEALD, bold: true } },
], {
  x: 2.0, y: 5.0, w: W - 4.0, h: 1.0, isTextBox: true, margin: 0.15,
  fontFace: BODY, fontSize: 16, align: "center", valign: "middle",
});
s.addNotes("Two small technical points. Mono means one channel. One list of numbers. That is enough for one voice. And we use WAV files. WAV keeps every number. MP3 deletes small details to save space. But small details are exactly what we measure. So no MP3.");

// =========================== 8 DATASET ===========================
s = pres.addSlide();
bg(s);
headline(s, "The data: real voices, checked first");
chip(s, 8);
const data8 = [
  ["37", "people"],
  ["21 / 16", "healthy / Parkinson's"],
  ["73", "recordings"],
  ["~2 min", "each, on a phone"],
];
{
  const cw = 2.75, chh = 1.7, gap = 0.55;
  let x = (W - 4 * cw - 3 * gap) / 2, y = 1.8;
  data8.forEach(([big, small]) => {
    card(s, x, y, cw, chh);
    s.addText(big, { x, y: y + 0.2, w: cw, h: 0.8, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 34, bold: true, color: TEAL, align: "center" });
    s.addText(small, { x, y: y + 1.05, w: cw, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13.5, color: MUTED, align: "center" });
    x += cw + gap;
  });
}
iconDot(s, 1.35, 4.25, 0.7, "t_db");
s.addText([
  { text: "MDVR-KCL", options: { bold: true, color: INK } },
  { text: " — a public research dataset recorded at King's College London.\nEvery file was checked before training: labels, speaker identity, no duplicates, no damage.", options: { color: MUTED } },
], {
  x: 2.3, y: 4.15, w: W - 3.4, h: 1.0, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 15, align: "left",
});
card(s, 2.0, 5.55, W - 4.0, 0.95, TINT);
s.addText("Each person reads a text and has a free conversation — normal speech, not sounds.", {
  x: 2.0, y: 5.55, w: W - 4.0, h: 0.95, isTextBox: true, margin: 0.15,
  fontFace: BODY, fontSize: 15, italic: true, color: TEALD, align: "center", valign: "middle",
});
s.addNotes("Our data is called MDVR-KCL. It is a public research dataset from King's College London. Thirty-seven people. Twenty-one healthy, sixteen with Parkinson's. Seventy-three recordings, about two minutes each, on a phone. We checked every file before training. Labels, speaker identity, no duplicates.");

// =========================== 9 PREPROCESSING ===========================
s = pres.addSlide();
bg(s);
headline(s, "Cleaning up — five careful steps");
chip(s, 9);
const prep9 = [
  ["t_volume", "mono", "one channel"],
  ["t_resample", "44.1 kHz", "same clock\nfor all"],
  ["t_broom", "remove offset", "center the wave"],
  ["t_trim", "trim silence", "only at the edges"],
  ["t_normalize", "same loudness", "fair comparison"],
];
{
  const cw = 2.2, chh = 2.05, gap = 0.35;
  let x = (W - 5 * cw - 4 * gap) / 2, y = 1.75;
  prep9.forEach(([icon, t1, t2], i) => {
    card(s, x, y, cw, chh);
    iconDot(s, x + cw / 2 - 0.33, y - 0.33, 0.66, icon);
    s.addText(t1, { x, y: y + 0.5, w: cw, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16.5, bold: true, color: INK, align: "center" });
    s.addText(t2, { x: x + 0.1, y: y + 1.05, w: cw - 0.2, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: MUTED, align: "center" });
    x += cw + gap;
  });
}
iconDot(s, 2.35, 4.55, 0.8, "t_ban", CORAL);
card(s, 3.4, 4.55, W - 5.4, 1.35, CARD);
s.addText([
  { text: "One thing we did NOT do: remove noise.\n", options: { bold: true, color: CORAL, fontSize: 17 } },
  { text: "Noise-removal software smooths away irregularities — and the irregularities are the medical evidence.", options: { color: INK, fontSize: 14.5 } },
], {
  x: 3.4, y: 4.55, w: W - 5.4, h: 1.35, isTextBox: true, margin: 0.15,
  fontFace: BODY, align: "left", valign: "middle",
});
s.addNotes("Before measuring, we clean up. Five careful steps. One channel. One fixed clock, 44.1 kilohertz. Center the wave. Trim the silence at the edges. Same loudness for all. And one thing we did not do: remove noise. Noise removal smooths away irregularities. But the irregularities are the medical evidence.");

// =========================== 10 MACHINE LEARNING ===========================
s = pres.addSlide();
bg(s);
headline(s, "How the computer learns");
chip(s, 10);
{
  const cw = 5.55, chh = 2.5, gap = 0.7;
  let x = (W - 2 * cw - gap) / 2, y = 1.9;
  card(s, x, y, cw, chh);
  s.addText("TRAINING", { x, y: y + 0.25, w: cw, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 20, bold: true, color: TEAL, align: "center" });
  s.addText("show the computer many recordings\nWITH the answers\n→ it finds the pattern", {
    x: x + 0.3, y: y + 0.9, w: cw - 0.6, h: 1.4, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 15.5, color: INK, align: "center",
  });
  const x2 = x + cw + gap;
  card(s, x2, y, cw, chh);
  s.addText("TESTING", { x: x2, y: y + 0.25, w: cw, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 20, bold: true, color: CORAL, align: "center" });
  s.addText("new recordings, NO answers,\nfrom people it has never heard\n→ can it still tell?", {
    x: x2 + 0.3, y: y + 0.9, w: cw - 0.6, h: 1.4, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 15.5, color: INK, align: "center",
  });
}
card(s, 2.0, 4.95, W - 4.0, 1.1, TINT);
s.addText([
  { text: "Golden rule: ", options: { bold: true, color: TEALD } },
  { text: "never test on a person the computer trained on —\nlike a student who saw the exam questions before the exam.", options: { color: INK } },
], {
  x: 2.0, y: 4.95, w: W - 4.0, h: 1.1, isTextBox: true, margin: 0.15,
  fontFace: BODY, fontSize: 15.5, align: "center", valign: "middle",
});
s.addNotes("How does the computer learn? Two phases. Training: we show it many recordings with the answers. It finds the pattern. Testing: new recordings, no answers, from people it never heard. Can it still tell? One golden rule. Never test on a person the computer trained on. Like a student who saw the exam questions before the exam.");

// =========================== 11 OUR MODEL ===========================
s = pres.addSlide();
bg(s);
headline(s, "Our model: a forest of 300 small decisions");
chip(s, 11);
// three tree icons voting
{
  const d = 1.0, gap = 0.5;
  let x = (W - 3 * d - 2 * gap) / 2;
  for (let i = 0; i < 3; i++) {
    iconDot(s, x, 1.6, d, "t_tree");
    x += d + gap;
  }
}
s.addText("Random Forest", {
  x: 0.9, y: 2.85, w: W - 1.8, h: 0.6, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 28, bold: true, color: TEAL, align: "center",
});
s.addText("300 small decision trees, each looking at the numbers differently — then they vote.", {
  x: 0.9, y: 3.5, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 16, color: INK, align: "center",
});
{
  const cw = 5.55, chh = 1.55, gap = 0.7;
  let x = (W - 2 * cw - gap) / 2, y = 4.35;
  card(s, x, y, cw, chh);
  s.addText([
    { text: "Why this one?  ", options: { bold: true, color: INK } },
    { text: "We can ask it which\nmeasurements it used — it is explainable.", options: { color: MUTED } },
  ], { x, y, w: cw, h: chh, isTextBox: true, margin: 0.15, fontFace: BODY, fontSize: 14.5, align: "left", valign: "middle" });
  const x2 = x + cw + gap;
  card(s, x2, y, cw, chh);
  s.addText([
    { text: "Its favourite measurement?  ", options: { bold: true, color: INK } },
    { text: "Pitch range —\nthe monotone-speech sign doctors know.", options: { color: TEALD, bold: true } },
  ], { x: x2, y, w: cw, h: chh, isTextBox: true, margin: 0.15, fontFace: BODY, fontSize: 14.5, align: "left", valign: "middle" });
}
s.addText("We compared four models under the same fair test — this one won.", {
  x: 0.9, y: 6.2, w: W - 1.8, h: 0.45, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13.5, italic: true, color: MUTED, align: "center",
});
s.addNotes("Our model is called Random Forest. Three hundred small decision trees. Each looks at the numbers differently. Then they vote. Why this model? Because we can ask it which measurements it used. Its favourite is pitch range. That is the monotone speech sign doctors already know. We compared four models. This one won.");

// =========================== 12 METRICS ===========================
s = pres.addSlide();
bg(s);
headline(s, "How good is it? — in plain words");
chip(s, 12);
const met12 = [
  ["0.822", "balanced accuracy", "the overall fair score\n(on people it never heard)"],
  ["77%", "sensitivity", "of all true patients,\nhow many did we catch?"],
  ["87%", "specificity", "of all healthy people,\nhow many did we clear?"],
];
{
  const cw = 3.55, chh = 2.9, gap = 0.7;
  let x = (W - 3 * cw - 2 * gap) / 2, y = 1.9;
  met12.forEach(([big, name, small]) => {
    card(s, x, y, cw, chh);
    s.addText(big, { x, y: y + 0.3, w: cw, h: 1.0, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 46, bold: true, color: TEAL, align: "center" });
    s.addText(name, { x, y: y + 1.35, w: cw, h: 0.45, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: INK, align: "center" });
    s.addText(small, { x: x + 0.2, y: y + 1.85, w: cw - 0.4, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: MUTED, align: "center" });
    x += cw + gap;
  });
}
card(s, 2.0, 5.3, W - 4.0, 1.0, TINT);
s.addText([
  { text: "Why not plain accuracy? A lazy model that always says “healthy” scores 57.5% —\nand finds ", options: { color: INK } },
  { text: "zero patients.", options: { color: CORAL, bold: true } },
], {
  x: 2.0, y: 5.3, w: W - 4.0, h: 1.0, isTextBox: true, margin: 0.12,
  fontFace: BODY, fontSize: 14.5, align: "center", valign: "middle",
});
s.addNotes("How good is it? Balanced accuracy 0.822 on people it never heard. Sensitivity 77 percent. Of all true patients, how many did we catch? Specificity 87 percent. Of all healthy people, how many did we clear? Why not plain accuracy? A lazy model that always says healthy scores 57.5 percent and finds zero patients. That is why we use the fair score.");

// =========================== 13 CONFUSION MATRIX ===========================
s = pres.addSlide();
bg(s);
headline(s, "The confusion matrix — every recording, counted");
chip(s, 13);
{
  const cx = 3.4, cy = 2.15, cell = 1.9, gap = 0.16;
  // column headers
  s.addText("model says:\nhealthy", { x: cx, y: cy - 0.85, w: cell, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, bold: true, color: MUTED, align: "center" });
  s.addText("model says:\nParkinson's", { x: cx + cell + gap, y: cy - 0.85, w: cell, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, bold: true, color: MUTED, align: "center" });
  // row headers
  s.addText("really\nhealthy", { x: cx - 1.5, y: cy + 0.4, w: 1.35, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, bold: true, color: MUTED, align: "right" });
  s.addText("really\nParkinson's", { x: cx - 1.5, y: cy + cell + gap + 0.4, w: 1.35, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, bold: true, color: MUTED, align: "right" });
  const cells = [
    [0, 0, "36", "correct", TEAL],
    [1, 0, "6", "false alarm", CORAL],
    [0, 1, "7", "missed", CORAL],
    [1, 1, "24", "caught", TEAL],
  ];
  cells.forEach(([cxi, cyi, v, lab, color]) => {
    const x = cx + cxi * (cell + gap), y = cy + cyi * (cell + gap);
    s.addShape("roundRect", {
      x, y, w: cell, h: cell, rectRadius: 0.1,
      fill: { color, transparency: color === TEAL ? 82 : 80 },
      line: { color, width: 1.5 },
    });
    s.addText(v, { x, y: y + 0.3, w: cell, h: 0.85, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 40, bold: true, color, align: "center" });
    s.addText(lab, { x, y: y + 1.25, w: cell, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: INK, align: "center" });
  });
}
s.addText([
  { text: "Out of 73 recordings:  ", options: { color: INK } },
  { text: "60 correct", options: { color: TEAL, bold: true } },
  { text: "  •  ", options: { color: MUTED } },
  { text: "13 mistakes", options: { color: CORAL, bold: true } },
  { text: " — and we say so openly.", options: { color: INK } },
], {
  x: 7.7, y: 3.2, w: 5.2, h: 1.6, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 17, align: "left", lineSpacing: 26,
});
s.addNotes("This table counts every recording. Really healthy, and the model says healthy: 36 correct. Six false alarms. Seven missed patients. Twenty-four caught. Out of 73 recordings, 60 correct, 13 mistakes. And we say so openly. Every screening system makes mistakes. Honest systems count them.");

// =========================== 14 REMEMBER ===========================
s = pres.addSlide();
bg(s, true);
headline(s, "Three things to remember");
chip(s, 14);
const rem14 = [
  ["1", "The voice carries a real, measurable signal of Parkinson's."],
  ["2", "We tested honestly — only on people the computer never heard."],
  ["3", "It is a screening helper, not a diagnosis — a doctor decides."],
];
{
  let y = 1.9;
  rem14.forEach(([n, t]) => {
    card(s, 1.7, y, W - 3.4, 1.15, CARD);
    s.addShape("ellipse", { x: 2.0, y: y + 0.28, w: 0.6, h: 0.6, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(n, { x: 2.0, y: y + 0.28, w: 0.6, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 20, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    s.addText(t, { x: 2.85, y, w: W - 4.8, h: 1.15, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 17.5, color: INK, align: "left", valign: "middle" });
    y += 1.4;
  });
}
s.addNotes("Three things to remember. One: the voice carries a real, measurable signal. Two: we tested honestly, only on people the computer never heard. Three: it is a screening helper, not a diagnosis. A doctor decides.");

// =========================== 15 THANK YOU ===========================
s = pres.addSlide();
bg(s, true);
wave(s, 5.95, 1.55);
s.addText("Thank you", {
  x: 0.9, y: 2.6, w: W - 1.8, h: 1.0, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 46, bold: true, color: INK, align: "center",
});
s.addText("Questions are welcome.", {
  x: 0.9, y: 3.8, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 17, color: MUTED, align: "center",
});
s.addNotes("Thank you. I welcome your questions.");

// ---------- write ----------
const out = path.join(ROOT, "report", "defence", "slides_v2.pptx");
pres.writeFile({ fileName: out }).then(() => console.log("wrote", out));
