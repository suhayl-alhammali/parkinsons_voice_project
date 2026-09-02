// Premium dark PowerPoint version of the defence deck.
// Run:  node report/defence/gen_deck.js   (from project root)
const pptxgen = require("pptxgenjs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const FIGS = path.join(ROOT, "report", "defence", "figs");
const RFIG = path.join(ROOT, "report", "figures");

// ---------- palette ----------
const BG = "0B1526";        // deep navy (dominant)
const PANEL = "13233B";     // card fill
const PANEL2 = "182B47";    // slightly lighter card
const STROKE = "2A3D58";    // card outline
const ICE = "E8EEF7";       // primary text
const MUTED = "9DB0C7";     // secondary text
const HONEST = "5AB4F0";    // blue  = honest / correct / measured
const WRONG = "FF8C42";     // vermillion = inflated / wrong / leaked
const WHITE = "FFFFFF";

const HEAD = "Cambria";
const BODY = "Calibri";

const W = 13.33, H = 7.5;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Suhail Mohamed Alhammali";
pres.title = "Voice Signal Analysis Using Machine Learning for Early Detection of Parkinson's Disease";

// ---------- helpers ----------
function bg(s, hero) {
  s.background = { path: path.join(FIGS, hero ? "bg_hero.png" : "bg_main.png") };
}
function heroWave(s, yTop, h) {
  s.addImage({ path: path.join(FIGS, "wave_hero.png"), x: 0, y: yTop, w: W, h: h });
}
function iconCircle(s, x, y, d, icon, ringColor) {
  s.addShape("ellipse", {
    x, y, w: d, h: d,
    fill: { color: PANEL2 }, line: { color: ringColor || HONEST, width: 1.25 },
    shadow: { type: "outer", color: "000000", opacity: 0.35, blur: 7, offset: 2, angle: 90 },
  });
  const pad = d * 0.26;
  s.addImage({ path: path.join(FIGS, icon + ".png"), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad });
}
function chip(s, n) {
  s.addText(String(n), {
    x: W - 0.62, y: H - 0.52, w: 0.42, h: 0.34, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10, color: MUTED, align: "right",
  });
}
// deterministic waveform strip
function waveform(s, yTop, height, color) {
  const n = 74; // one bar per feature — a quiet nod
  const barW = 0.075, gap = (W - n * barW) / (n + 1);
  for (let i = 0; i < n; i++) {
    const t = Math.abs(Math.sin(i * 0.53) * 0.65 + Math.sin(i * 0.19) * 0.35);
    const h = 0.10 + t * (height - 0.10);
    s.addShape("roundRect", {
      x: gap + i * (barW + gap), y: yTop + (height - h),
      w: barW, h: h, rectRadius: 0.03,
      fill: { color: color || HONEST, transparency: 55 + Math.round((1 - t) * 30) },
      line: { type: "none" },
    });
  }
}
function headline(s, text, opts) {
  s.addText(text, Object.assign({
    x: 0.55, y: 0.32, w: W - 1.1, h: 0.75, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 30, bold: true, color: ICE, align: "left",
  }, opts || {}));
}
const STAGES = ["raw audio", "clean-up", "10-s chunks", "74 measures", "model", "indication"];
function pipeStrip(s, active) {
  const bw = 1.62, bh = 0.44, gap = 0.30;
  const total = STAGES.length * bw + (STAGES.length - 1) * gap;
  let x = (W - total) / 2;
  const y = 1.18;
  for (let i = 0; i < STAGES.length; i++) {
    const on = i === active;
    s.addShape("roundRect", {
      x, y, w: bw, h: bh, rectRadius: 0.07,
      fill: { color: on ? HONEST : PANEL, transparency: on ? 72 : 0 },
      line: { color: on ? HONEST : STROKE, width: on ? 1.5 : 0.75 },
    });
    s.addText(STAGES[i], {
      x, y: y + 0.02, w: bw, h: bh - 0.04, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 10.5, color: on ? ICE : MUTED,
      align: "center", valign: "middle", bold: on,
    });
    if (i < STAGES.length - 1) {
      s.addText("›", {
        x: x + bw + 0.02, y: y + 0.01, w: gap - 0.04, h: bh, isTextBox: true, margin: 0,
        fontFace: BODY, fontSize: 14, color: MUTED, align: "center", valign: "middle",
      });
    }
    x += bw + gap;
  }
}
function card(s, x, y, w, h, fill) {
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.09,
    fill: { color: fill || PANEL },
    line: { color: STROKE, width: 0.75 },
    shadow: { type: "outer", color: "000000", opacity: 0.35, blur: 8, offset: 3, angle: 90 },
  });
}

// =================================================================
// 1 — TITLE
// =================================================================
let s = pres.addSlide();
bg(s, true);
heroWave(s, 5.75, 1.75);
s.addText([
  { text: "Voice Signal Analysis Using Machine Learning\n", options: { fontSize: 33 } },
  { text: "for Early Detection of Parkinson's Disease", options: { fontSize: 33 } },
], {
  x: 0.9, y: 1.15, w: W - 1.8, h: 1.7, isTextBox: true, margin: 0,
  fontFace: HEAD, bold: true, color: ICE, align: "center",
});
s.addText("Suhail Mohamed Alhammali", {
  x: 0.9, y: 3.0, w: W - 1.8, h: 0.45, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 20, bold: true, color: HONEST, align: "center",
});
s.addText("ID 2200208522      Supervisor: Dr. Adel Adyaf", {
  x: 0.9, y: 3.47, w: W - 1.8, h: 0.38, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 14, color: MUTED, align: "center",
});
s.addText("Control and Instrumentation Division  •  Department of Biomedical Engineering\nFaculty of Engineering, University of Tripoli  •  Spring 2026", {
  x: 0.9, y: 4.0, w: W - 1.8, h: 0.75, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, color: MUTED, align: "center",
});
s.addNotes("Good morning. My name is Suhail. This is my graduation project. It asks one question: can the voice help us notice Parkinson's disease earlier?");

// =================================================================
// 2 — CAUSAL CHAIN
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "A movement disease reaches the voice");
chip(s, 2);
const chain = ["dopamine\nloss", "impaired\nmotor control", "hypokinetic\ndysarthria", "measurable\nacoustic change"];
{
  const bw = 2.5, bh = 1.25, gap = 0.62;
  const total = chain.length * bw + (chain.length - 1) * gap;
  let x = (W - total) / 2, y = 2.35;
  chain.forEach((label, i) => {
    const last = i === chain.length - 1;
    card(s, x, y, bw, bh, last ? PANEL2 : PANEL);
    if (last) s.addShape("roundRect", { x, y, w: bw, h: bh, rectRadius: 0.09, fill: { color: HONEST, transparency: 82 }, line: { color: HONEST, width: 1.5 } });
    s.addText(label, {
      x, y, w: bw, h: bh, isTextBox: true, margin: 0.05,
      fontFace: BODY, fontSize: 15.5, bold: last, color: last ? ICE : ICE,
      align: "center", valign: "middle",
    });
    if (i < chain.length - 1) s.addShape("rightArrow", {
      x: x + bw + 0.10, y: y + bh / 2 - 0.11, w: 0.42, h: 0.22,
      fill: { color: MUTED, transparency: 35 }, line: { type: "none" },
    });
    x += bw + gap;
  });
}
s.addText("every muscle — breathing, larynx, articulation", {
  x: 0.9, y: 3.9, w: W - 1.8, h: 0.4, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, italic: true, color: MUTED, align: "center",
});
s.addText("The weakness that shakes a hand also moves the voice.", {
  x: 0.9, y: 4.85, w: W - 1.8, h: 0.55, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 20, italic: true, color: ICE, align: "center",
});
s.addNotes("Parkinson's disease reduces dopamine. That impairs motor control. Every muscle is affected. Also the small muscles of speech. The result is a speech disorder we can measure. The weakness that shakes a hand also moves the voice.");

// =================================================================
// 3 — THREE STATS
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "The voice is a cheap, early window");
chip(s, 3);
const stats = [
  ["ic_ear", "~90%", "of patients show\nspeech changes"],
  ["ic_clock", "5 yr", "before diagnosis,\nin one documented case"],
  ["ic_mic", "$", "a microphone:\nnon-invasive, repeatable"],
];
{
  const cw = 3.55, chh = 3.15, gap = 0.7;
  const total = stats.length * cw + (stats.length - 1) * gap;
  let x = (W - total) / 2, y = 1.85;
  stats.forEach(([icon, big, small]) => {
    card(s, x, y, cw, chh);
    iconCircle(s, x + cw / 2 - 0.42, y - 0.42, 0.84, icon);
    s.addText(big, {
      x, y: y + 0.75, w: cw, h: 1.15, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 54, bold: true, color: HONEST, align: "center",
    });
    s.addText(small, {
      x: x + 0.2, y: y + 2.05, w: cw - 0.4, h: 0.85, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 14, color: MUTED, align: "center",
    });
    x += cw + gap;
  });
}
s.addText("Not a diagnosis — a reason to see a doctor earlier.", {
  x: 0.9, y: 5.3, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 18, italic: true, color: ICE, align: "center",
});
s.addNotes("About ninety percent of patients show speech changes. In one documented case, changes appeared five years before diagnosis. A microphone is cheap and non-invasive. This is not a diagnosis. It is a reason to see a doctor earlier.");

// =================================================================
// 4 — RESEARCH QUESTION (statement)
// =================================================================
s = pres.addSlide();
bg(s, true);
heroWave(s, 6.3, 1.2);
chip(s, 4);
s.addText([
  { text: "Can a computer measure a voice recording\nand tell whether its pattern resembles\n", options: { color: ICE } },
  { text: "Parkinson's patients", options: { color: ICE, bold: true } },
  { text: " — or ", options: { color: ICE } },
  { text: "healthy speakers", options: { color: ICE, bold: true } },
  { text: "?", options: { color: ICE } },
], {
  x: 1.0, y: 2.3, w: W - 2.0, h: 2.4, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 28, align: "center", lineSpacing: 44,
});
s.addNotes("This is the research question. Read it slowly. Can a computer tell if a voice pattern resembles patients, or healthy speakers?");

// =================================================================
// 5 — PIPELINE
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "Six stages, one shared implementation");
chip(s, 5);
{
  const bw = 1.85, bh = 1.05, gap = 0.24;
  const total = STAGES.length * bw + (STAGES.length - 1) * gap;
  let x = (W - total) / 2, y = 2.6;
  const labels = ["raw WAV\naudio", "clean-up\n5 steps", "10-second\nchunks", "74 measure-\nments / chunk", "model\n(Random Forest)", "cautious\nindication"];
  labels.forEach((label, i) => {
    card(s, x, y, bw, bh, i === 3 ? PANEL2 : PANEL);
    s.addText(label, {
      x, y, w: bw, h: bh, isTextBox: true, margin: 0.04,
      fontFace: BODY, fontSize: 12.5, color: ICE, align: "center", valign: "middle",
    });
    if (i < labels.length - 1) s.addShape("rightArrow", {
      x: x + bw + 0.02, y: y + bh / 2 - 0.09, w: 0.2, h: 0.18,
      fill: { color: MUTED, transparency: 35 }, line: { type: "none" },
    });
    x += bw + gap;
  });
}
s.addText([
  { text: "The same code runs in training, testing, and prediction — ", options: { color: ICE } },
  { text: "enforced, not promised.", options: { color: HONEST, bold: true } },
], {
  x: 0.9, y: 4.35, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 18, italic: true, align: "center",
});
s.addNotes("The system has six stages. Audio comes in. We clean it. We cut it into ten-second chunks. We take seventy-four measurements per chunk. A model judges. The output is cautious. One key point: the same code runs everywhere. The program checks this before every prediction.");

// =================================================================
// 6 — PHYSIOLOGY MAPPING
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "Every measurement points at physiology");
chip(s, 6);
pipeStrip(s, 3);
const maps = [
  ["monotone speech", "pitch variation"],
  ["unstable vocal-fold control", "jitter, shimmer"],
  ["incomplete glottal closure", "HNR, CPPS"],
  ["disturbed timing", "pause statistics"],
  ["imprecise articulation", "MFCC dynamics"],
];
{
  let y = 2.15;
  maps.forEach(([phys, meas]) => {
    s.addText(phys, {
      x: 1.3, y, w: 4.7, h: 0.42, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 16, color: ICE, align: "right", valign: "middle",
    });
    s.addShape("rightArrow", {
      x: 6.25, y: y + 0.11, w: 0.55, h: 0.2,
      fill: { color: MUTED, transparency: 40 }, line: { type: "none" },
    });
    s.addText(meas, {
      x: 7.05, y, w: 4.9, h: 0.42, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 16, bold: true, color: HONEST, align: "left", valign: "middle",
    });
    y += 0.62;
  });
}
s.addText([
  { text: "All 74 measurements implemented in this project — ", options: { color: ICE } },
  { text: "none downloaded.", options: { color: HONEST, bold: true } },
], {
  x: 0.9, y: 5.65, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 17, italic: true, align: "center",
});
s.addNotes("Each measurement family points at physiology. Monotone speech shows in pitch variation. Unstable vocal folds show in jitter and shimmer. Incomplete closure shows in HNR and CPPS. Timing problems show in pauses. Imprecise articulation shows in MFCC dynamics. We implemented all seventy-four measurements ourselves.");

// =================================================================
// 7 — NO DENOISING
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, [{ text: "We chose ", options: {} }, { text: "not", options: { italic: true } }, { text: " to clean the sound", options: {} }]);
chip(s, 7);
pipeStrip(s, 1);
iconCircle(s, W / 2 - 0.55, 1.95, 1.1, "ic_ban", WRONG);
s.addText([
  { text: "Denoising suppresses irregularity.\n", options: { color: ICE } },
  { text: "Irregularity ", options: { color: ICE } },
  { text: "is", options: { color: ICE, italic: true } },
  { text: " the evidence.", options: { color: ICE } },
], {
  x: 1.6, y: 3.2, w: W - 3.2, h: 1.2, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 26, align: "center", lineSpacing: 40,
});
card(s, 2.4, 4.5, W - 4.8, 0.85, PANEL2);
s.addText("Cleaning would make a disordered voice look artificially healthy.", {
  x: 2.4, y: 4.5, w: W - 4.8, h: 0.85, isTextBox: true, margin: 0.1,
  fontFace: BODY, fontSize: 17, bold: true, color: WRONG, align: "center", valign: "middle",
});
s.addNotes("One decision matters here. We did not remove noise. Denoising software removes irregularity. But irregularity is the medical evidence. Cleaning the sound would make a sick voice look healthy.");

// =================================================================
// 8 — DATA LEAKAGE
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "A student with the exam questions proves nothing");
chip(s, 8);
// person container with two stacked recordings
s.addShape("roundRect", { x: 1.3, y: 1.95, w: 2.3, h: 3.0, rectRadius: 0.08, fill: { color: PANEL, transparency: 60 }, line: { color: STROKE, width: 1.25 } });
s.addText("one person", { x: 1.3, y: 2.05, w: 2.3, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, italic: true, color: MUTED, align: "center" });
card(s, 1.55, 2.5, 1.8, 0.85, PANEL);
s.addText("recording 1", { x: 1.55, y: 2.5, w: 1.8, h: 0.85, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: ICE, align: "center", valign: "middle" });
card(s, 1.55, 3.7, 1.8, 0.85, PANEL);
s.addText("recording 2", { x: 1.55, y: 3.7, w: 1.8, h: 0.85, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: ICE, align: "center", valign: "middle" });
// destination boxes
card(s, 7.3, 2.2, 1.9, 0.8, PANEL2);
s.addText("training", { x: 7.3, y: 2.2, w: 1.9, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 15, bold: true, color: WRONG, align: "center", valign: "middle" });
card(s, 7.3, 3.55, 1.9, 0.8, PANEL2);
s.addText("test", { x: 7.3, y: 3.55, w: 1.9, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 15, bold: true, color: WRONG, align: "center", valign: "middle" });
// arrows: recording 1 -> training, recording 2 -> test (no crossing)
s.addShape("line", { x: 3.35, y: 2.60, w: 3.95, h: 0.33, flipV: true, line: { color: WRONG, width: 2.2, endArrowType: "arrow" } });
s.addShape("line", { x: 3.35, y: 3.95, w: 3.95, h: 0.18, flipV: true, line: { color: WRONG, width: 2.2, endArrowType: "arrow" } });
s.addText([
  { text: "the model can win by\nrecognising the ", options: { color: ICE } },
  { text: "person", options: { color: WRONG, italic: true, bold: true } },
], {
  x: 9.6, y: 2.15, w: 3.2, h: 1.1, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 16, align: "left",
});
s.addText([
  { text: "This is ", options: { color: ICE } },
  { text: "data leakage", options: { color: WRONG, bold: true } },
  { text: ".  Our program halts if it ever happens.", options: { color: ICE } },
], {
  x: 0.9, y: 5.0, w: W - 1.8, h: 0.55, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 19, align: "center",
});
s.addNotes("Here is the danger. Each person gave two recordings. Put one in training and one in test. The model can then win by recognising the person. Not the disease. This is data leakage. Our program stops itself if it ever happens.");

// =================================================================
// 9 — THE IMPRESSIVE NUMBER
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "Validation design decides the number");
chip(s, 9);
s.addText("0.909", {
  x: 0.9, y: 2.0, w: W - 1.8, h: 2.0, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 110, bold: true, color: ICE, align: "center",
});
s.addText("balanced accuracy", {
  x: 0.9, y: 4.15, w: W - 1.8, h: 0.45, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 16, color: MUTED, align: "center",
});
s.addText("an impressive result?", {
  x: 0.9, y: 4.85, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 19, italic: true, color: MUTED, align: "center",
});
s.addNotes("Look at this number. 0.909. It looks like an excellent result. [Pause. Next slide.]");

// =================================================================
// 10 — THE REVEAL
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "Validation design decides the number");
chip(s, 10);
// left: the two numbers
s.addText("0.909", {
  x: 0.8, y: 1.55, w: 4.6, h: 1.15, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 60, bold: true, color: WRONG, align: "center",
});
s.addText("deliberately wrong split — demonstration only", {
  x: 0.8, y: 2.7, w: 4.6, h: 0.4, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, bold: true, color: WRONG, align: "center",
});
s.addText("0.775", {
  x: 0.8, y: 3.35, w: 4.6, h: 1.15, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 60, bold: true, color: HONEST, align: "center",
});
s.addText("correct split, same model", {
  x: 0.8, y: 4.5, w: 4.6, h: 0.4, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, color: HONEST, align: "center",
});
// right: native bar comparison
{
  const bx = 6.6, by = 1.7, bw = 1.7, maxH = 3.0, gap2 = 1.4;
  const base = by + maxH;
  // chance line at 0.5
  s.addShape("line", { x: bx - 0.35, y: base - 0.5 * maxH, w: bw * 2 + gap2 + 0.7, h: 0, line: { color: MUTED, width: 1, dashType: "dash" } });
  const bars = [
    ["0.775", 0.775, HONEST, "correct split\ngrouped by subject"],
    ["0.909", 0.909, WRONG, "wrong split\nchunks cross sides"],
  ];
  bars.forEach(([label, v, color, cap], i) => {
    const bh2 = (v / 1.0) * maxH;
    const x = bx + i * (bw + gap2);
    s.addShape("roundRect", {
      x, y: base - bh2, w: bw, h: bh2, rectRadius: 0.05,
      fill: { color, transparency: 15 }, line: { type: "none" },
    });
    s.addText(label, {
      x: x - 0.2, y: base - bh2 - 0.5, w: bw + 0.4, h: 0.45, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 21, bold: true, color, align: "center",
    });
    s.addText(cap, {
      x: x - 0.45, y: base + 0.12, w: bw + 0.9, h: 0.65, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 11.5, color: MUTED, align: "center",
    });
  });
}
s.addText([
  { text: "The difference is ", options: { color: ICE } },
  { text: "memorisation", options: { color: WRONG, bold: true } },
  { text: ", not detection — and it is why 95%+ results exist.", options: { color: ICE } },
], {
  x: 0.9, y: 6.2, w: W - 1.8, h: 0.55, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 18, align: "center",
});
s.addNotes("Now the truth. That number came from a deliberately wrong split. Chunks of the same recording were on both sides. The honest split gives 0.775. Same data. Same model. Only the split changed. The difference is memorisation, not detection. This is why many papers report ninety-five percent or more. Orange means inflated. Blue means honest. Remember these two colours.");

// =================================================================
// 11 — RULES FIXED BEFORE
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "The rules were fixed before the experiments");
chip(s, 11);
const rules = [
  ["ic_scale", "identical splits for every variant"],
  ["ic_chart", "adoption margin: +0.02"],
  ["ic_warn", "any result ≥ 0.95: stop, investigate"],
  ["ic_check", "all 19 configurations reported"],
];
{
  const cw = 5.6, chh = 0.95, gapx = 0.6, gapy = 0.5;
  let idx = 0;
  for (let r = 0; r < 2; r++) for (let c = 0; c < 2; c++) {
    const x = (W - 2 * cw - gapx) / 2 + c * (cw + gapx);
    const y = 1.8 + r * (chh + gapy);
    card(s, x, y, cw, chh);
    const [icon, label] = rules[idx];
    iconCircle(s, x + 0.18, y + chh / 2 - 0.29, 0.58, icon,
               icon === "ic_warn" ? WRONG : HONEST);
    s.addText(label, {
      x: x + 0.95, y, w: cw - 1.15, h: chh, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 15, color: ICE, align: "left", valign: "middle",
    });
    idx++;
  }
}
card(s, 2.2, 4.6, W - 4.4, 1.15, PANEL2);
s.addText([
  { text: "Best score ", options: { color: ICE } },
  { text: "0.840", options: { color: WRONG, bold: true } },
  { text: " — ", options: { color: ICE } },
  { text: "rejected.", options: { color: ICE, bold: true } },
  { text: "  It won by 0.018: less than the noise.", options: { color: MUTED } },
], {
  x: 2.2, y: 4.6, w: W - 4.4, h: 1.15, isTextBox: true, margin: 0.15,
  fontFace: HEAD, fontSize: 20, align: "center", valign: "middle",
});
s.addNotes("We fixed the rules before running anything. Same splits for every variant. A complex variant must win by more than 0.02. Anything above 0.95 stops the study. All nineteen configurations are reported. The best score was 0.840. We rejected it. It won by only 0.018. That is smaller than the noise.");

// =================================================================
// 12 — MODEL SELECTION LEADERBOARD
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "Nineteen configurations — the winner chosen by rule");
chip(s, 12);
{
  const x0 = 5.0, x1 = 12.15, v0 = 0.74, v1 = 0.88;
  const X = (v) => x0 + ((v - v0) / (v1 - v0)) * (x1 - x0);
  const rows = [
    ["baseline phase — SVM (V0)", 0.780, MUTED, ""],
    ["chunk features — SVM (V1)", 0.816, MUTED, ""],
    ["chunk features — tuned RF (V4)", 0.814, MUTED, ""],
    ["mean+std features — SVM (V6)", 0.824, MUTED, ""],
    ["tuned SVM+RF ensemble (V5)", 0.840, WRONG, "rejected (+0.018)"],
    ["chunk features — Random Forest (V1)", 0.822, HONEST, "selected"],
  ];
  const yTop = 2.05, rowH = 0.72;
  const bx = X(0.822), bw2 = X(0.842) - X(0.822);
  s.addShape("rect", { x: bx, y: yTop - 0.28, w: bw2, h: rows.length * rowH + 0.5, fill: { color: HONEST, transparency: 88 }, line: { type: "none" } });
  s.addText("adoption margin +0.02", { x: bx - 0.55, y: yTop - 0.62, w: bw2 + 1.1, h: 0.3, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 10.5, color: MUTED, align: "center" });
  rows.forEach(([label, v, color, tag], i) => {
    const y = yTop + i * rowH;
    const big = color === HONEST;
    s.addText(label, { x: 0.6, y: y - 0.02, w: 4.25, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: big ? 13.5 : 12.5, bold: big, color: big ? ICE : MUTED, align: "right", valign: "middle" });
    s.addShape("line", { x: x0, y: y + 0.18, w: X(v) - x0, h: 0, line: { color: color, width: big ? 2.6 : 1.4 } });
    s.addShape("ellipse", { x: X(v) - 0.09, y: y + 0.09, w: 0.18, h: 0.18, fill: { color: color }, line: { type: "none" } });
    s.addText(v.toFixed(3), { x: X(v) + 0.14, y: y - 0.03, w: 0.85, h: 0.42, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: big ? 16 : 13, bold: true, color: color, valign: "middle" });
    if (tag) s.addText(tag, { x: X(v) + 0.95, y: y - 0.03, w: 2.05, h: 0.42, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11, italic: true, color: color, valign: "middle" });
  });
  [0.75, 0.80, 0.85].forEach((tk) => {
    s.addShape("line", { x: X(tk), y: yTop + rows.length * rowH + 0.16, w: 0.001, h: 0.12, line: { color: MUTED, width: 1 } });
    s.addText(tk.toFixed(2), { x: X(tk) - 0.4, y: yTop + rows.length * rowH + 0.3, w: 0.8, h: 0.3, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11, color: MUTED, align: "center" });
  });
  s.addText("subject-level balanced accuracy, 3-seed mean — six of the 19 configurations shown; all are reported", { x: 0.9, y: yTop + rows.length * rowH + 0.74, w: W - 1.8, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, italic: true, color: MUTED, align: "center" });
}
s.addNotes("Nineteen configurations were compared under identical splits. Here are the leaders. The ensemble scored highest, 0.840. But it beat the Random Forest by only 0.018, inside the pre-declared margin and inside the noise. So the rule rejected it. The Random Forest at 0.822 was selected. The rule chose the winner, not our preference.");

// =================================================================
// 13 — FINAL PERFORMANCE
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "Judged on people it has never heard");
chip(s, 13);
pipeStrip(s, 4);
// left tiles
s.addText([
  { text: "0.822", options: { fontSize: 52, bold: true, color: HONEST } },
  { text: "  ± 0.032", options: { fontSize: 22, color: MUTED } },
], {
  x: 0.8, y: 2.1, w: 5.3, h: 1.0, isTextBox: true, margin: 0,
  fontFace: HEAD, align: "left",
});
s.addText("balanced accuracy, per subject", {
  x: 0.8, y: 3.05, w: 5.3, h: 0.38, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, color: MUTED,
});
const tiles = [["0.771", "sensitivity"], ["0.873", "specificity"], ["0.864", "AUC"]];
{
  const tw = 1.62, th = 1.05, gap3 = 0.22;
  let x = 0.8; const y = 3.7;
  tiles.forEach(([v, lab]) => {
    card(s, x, y, tw, th);
    s.addText(v, { x, y: y + 0.08, w: tw, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 22, bold: true, color: ICE, align: "center" });
    s.addText(lab, { x, y: y + 0.6, w: tw, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11.5, color: MUTED, align: "center" });
    x += tw + gap3;
  });
}
s.addText("“always healthy” scores 0.575 accuracy, finds nobody — balanced accuracy 0.500.", {
  x: 0.8, y: 5.15, w: 5.5, h: 0.75, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, italic: true, color: MUTED,
});
card(s, 6.7, 1.95, 6.0, 5.0, PANEL);
s.addImage({ path: path.join(FIGS, "roc_dark.png"), x: 6.95, y: 2.15, w: 5.5, h: 4.6 });
s.addNotes("The final model is a Random Forest on the seventy-four measurements. Balanced accuracy 0.822, plus or minus 0.032. Sensitivity 0.771. Specificity 0.873. AUC 0.864. All measured on people the model never heard. Why balanced accuracy? A model that always says healthy gets 0.575 accuracy and finds nobody. Balanced accuracy gives it 0.5 and exposes it.");

// =================================================================
// 13 — CLINICAL SIGN
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "It rediscovered a known clinical sign");
chip(s, 14);
pipeStrip(s, 4);
s.addText([
  { text: "Top measurement:\n", options: { fontSize: 17, color: MUTED } },
  { text: "pitch range\n\n", options: { fontSize: 30, bold: true, color: HONEST } },
  { text: "the acoustic correlate of monotone speech — described by clinicians for decades.", options: { fontSize: 15, color: ICE } },
], {
  x: 0.8, y: 2.4, w: 4.4, h: 3.4, isTextBox: true, margin: 0,
  fontFace: HEAD, align: "left", lineSpacing: 26,
});
card(s, 5.5, 1.95, 7.2, 5.0, PANEL);
s.addImage({ path: path.join(FIGS, "importance_dark.png"), x: 5.75, y: 2.2, w: 6.7, h: 4.5 });
s.addNotes("We asked the model which measurement mattered most. The answer: pitch range. That is monotone speech. Clinicians have described it for decades. A system with no medical knowledge rediscovered a known clinical sign.");

// =================================================================
// 14 — ITALY
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "Italy: a frozen model, a trap, and a puzzle");
chip(s, 15);
pipeStrip(s, 4);
const italy = [
  [["Trap caught: ", WRONG], ["every 44.1 kHz file was a patient. Band-limited all audio to 16 kHz.", ICE]],
  [["Result: ", HONEST], ["AUC 0.701, balanced accuracy 0.629.", ICE]],
  [["Puzzle: ", WRONG], ["healthy young 0.626 > patients 0.566. Why?", ICE]],
];
{
  let y = 2.15;
  italy.forEach(([a, b]) => {
    s.addText([
      { text: a[0], options: { bold: true, color: a[1] } },
      { text: b[0], options: { color: b[1] } },
    ], {
      x: 0.8, y, w: 4.3, h: 1.35, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 15, align: "left",
    });
    y += 1.5;
  });
}
card(s, 5.4, 1.95, 7.35, 4.9, PANEL);
s.addImage({ path: path.join(FIGS, "external_dark.png"), x: 5.65, y: 2.3, w: 6.85, h: 4.2 });
s.addNotes("We froze the model and tested it on an Italian corpus. Sixty-one speakers. Another language. First, a trap: every 44.1 kilohertz file was a patient. The model could have detected microphones, not disease. We band-limited everything to 16 kilohertz. Result: AUC 0.701. Now the puzzle. Healthy young speakers scored higher than patients. Why? [Pause. Let them think.] It is medically impossible. So it proves the score follows the recording channel out of domain. That is exactly why our interface is cautious.");

// =================================================================
// 15 — REFUSES TO GUESS
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "A system that refuses to guess");
chip(s, 16);
// screenshot on white card (aspect ratio 1486x1018 = 1.46)
card(s, 0.8, 1.85, 6.3, 4.8, WHITE);
s.addImage({ path: path.join(RFIG, "app_result.png"), x: 1.05, y: 2.1, w: 5.8, h: 5.8 / 1.4597 });
const guess = [
  [{ text: "scores 0.35–0.65 ⇒ ", options: { color: ICE } }, { text: "“inconclusive”", options: { color: ICE, bold: true } }],
  [{ text: "100% of elderly healthy Italian speakers", options: { color: HONEST, bold: true } }, { text: " landed there", options: { color: ICE } }],
  [{ text: "declining to answer is a ", options: { color: ICE } }, { text: "feature", options: { color: HONEST, bold: true } }],
];
{
  let y = 2.7;
  guess.forEach((runs) => {
    s.addText([{ text: "▪  ", options: { color: HONEST } }].concat(runs), {
      x: 7.2, y, w: 5.4, h: 0.8, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 17, align: "left",
    });
    y += 1.05;
  });
}
s.addNotes("The prototype never guesses near the boundary. Scores between 0.35 and 0.65 are reported as inconclusive. In the Italian test, all elderly healthy speakers landed there. The system refused to mislabel them. Declining to answer is a feature.");

// =================================================================
// 16 — DEMO
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "Optional: live demonstration", { color: MUTED });
chip(s, 17);
const demo = [
  "safest demo: a corpus recording, command line",
  "analysis takes about one minute",
  "fallback: the screenshots on the previous slide carry the same content",
];
// terminal card (exact lines from a real run, verified)
card(s, 0.8, 1.95, 5.9, 3.6, "081018");
s.addText([
  { text: "$ python scripts/predict_file.py ID07_pd_2_0_0.wav\n\n", options: { color: MUTED } },
  { text: "RESEARCH MODEL RESULT (non-diagnostic)\n", options: { color: ICE, bold: true } },
  { text: "Duration: 147.7 s, original sample rate 44100 Hz\n\n", options: { color: MUTED } },
  { text: "The acoustic pattern was classified by the\nresearch model as closer to the PD class.\n", options: { color: ICE } },
  { text: "Model score for the PD class: 0.96", options: { color: HONEST, bold: true } },
], {
  x: 1.1, y: 2.2, w: 5.4, h: 3.2, isTextBox: true, margin: 0,
  fontFace: "Consolas", fontSize: 12.5, align: "left", lineSpacing: 19,
});
{
  let y = 2.45;
  demo.forEach((d) => {
    s.addText([{ text: "▪  ", options: { color: HONEST } }, { text: d, options: { color: ICE } }], {
      x: 7.1, y, w: 5.5, h: 0.85, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 16, align: "left",
    });
    y += 0.95;
  });
}
s.addText("skip this slide if time is short", {
  x: 0.9, y: 5.9, w: W - 1.8, h: 0.4, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, italic: true, color: MUTED, align: "center",
});
s.addNotes("If time allows, run the live demo now. Start the analysis, then keep talking. If anything misbehaves, the previous slide shows the same content.");

// =================================================================
// 18 — LIMITATIONS
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "The limits, stated plainly");
chip(s, 18);
{
  const lims = [
    ["ic_person", "37 subjects — one device, one language", "the dominant limitation; every result is reported with its spread"],
    ["ic_mic", "vowel-defined measures on continuous speech", "jitter, shimmer and HNR are noisier here; CPPS compensates only partly"],
    ["ic_gauge", "scores are not calibrated probabilities", "0.7 does not mean a 70% chance of disease — the wording enforces this"],
    ["ic_search", "one external corpus — one data point", "0.701 AUC measures generalisation once; it does not characterise it"],
  ];
  const cw = 5.75, chh = 1.55, gapx = 0.5, gapy = 0.45;
  lims.forEach(([icon, head, sub], idx) => {
    const c = idx % 2, r = Math.floor(idx / 2);
    const x = (W - 2 * cw - gapx) / 2 + c * (cw + gapx);
    const y = 1.85 + r * (chh + gapy);
    card(s, x, y, cw, chh);
    iconCircle(s, x + 0.2, y + 0.24, 0.55, icon, MUTED);
    s.addText(head, { x: x + 0.95, y: y + 0.14, w: cw - 1.15, h: 0.55, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15, bold: true, color: ICE, align: "left", valign: "middle" });
    s.addText(sub, { x: x + 0.95, y: y + 0.72, w: cw - 1.15, h: 0.75, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: MUTED, align: "left" });
  });
}
s.addText("Every limitation above is stated in the report itself — none is left for an examiner to discover.", {
  x: 0.9, y: 5.75, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 16, italic: true, color: ICE, align: "center",
});
s.addNotes("Before I close: the limits, stated plainly. Thirty-seven subjects, one device, one language. The classic voice measures were designed for vowels, not continuous speech. The scores are not probabilities. And one external corpus is one data point about generalisation. All of this is written in the report itself.");

// =================================================================
// 19 — CLOSING THESIS
// =================================================================
s = pres.addSlide();
bg(s);
headline(s, "What this is — and is not");
chip(s, 19);
{
  const nots = [
    "not a diagnostic tool; many conditions change a voice",
    "37 subjects, one language, one device",
  ];
  let y = 1.7;
  nots.forEach((d) => {
    s.addText([{ text: "▪  ", options: { color: MUTED } }, { text: d, options: { color: MUTED } }], {
      x: 2.6, y, w: 8.6, h: 0.45, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 15, align: "left",
    });
    y += 0.55;
  });
}
s.addText("Validation design moves the number\nmore than model engineering does.", {
  x: 0.9, y: 3.25, w: W - 1.8, h: 1.4, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 30, bold: true, color: ICE, align: "center", lineSpacing: 42,
});
s.addText([
  { text: "An honest ", options: { color: MUTED } },
  { text: "0.822", options: { color: HONEST, bold: true } },
  { text: " is worth more than an inflated one.", options: { color: MUTED } },
], {
  x: 0.9, y: 4.85, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 19, italic: true, align: "center",
});
heroWave(s, 6.35, 1.15);
s.addNotes("To close. This is not a diagnostic tool. Thirty-seven subjects is small. But the central lesson is this. Validation design moves the number more than model engineering does. An honest 0.822 is worth more than an inflated one.");

// =================================================================
// 18 — THANK YOU
// =================================================================
s = pres.addSlide();
bg(s, true);
heroWave(s, 5.95, 1.55);
s.addText("Thank you", {
  x: 0.9, y: 2.5, w: W - 1.8, h: 1.0, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 44, bold: true, color: ICE, align: "center",
});
s.addText("Questions welcome.", {
  x: 0.9, y: 3.7, w: W - 1.8, h: 0.5, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 17, color: MUTED, align: "center",
});
s.addNotes("Thank you. I welcome your questions.");

// =================================================================
// BACKUPS (19-26)
// =================================================================
const backups = [
  ["Why 82% and not 95%?", [
    "published 95%+ figures usually split recordings or windows, not people",
    "our own pipeline: 0.909 leaky vs 0.775 honest — same model",
    "0.822 is measured on people the model never heard",
  ]],
  ["Why not deep learning?", [
    "37 subjects is far below what deep networks need",
    "examiners can ask this model which measurements it used",
    "our small neural network collapsed in the confounder test (0.671 → 0.526)",
  ]],
  ["Why balanced accuracy?", [
    "classes are imbalanced: 42 HC vs 31 PD recordings",
    "“always healthy” scores 0.575 accuracy and finds zero patients",
    "balanced accuracy gives that model 0.500 — correctly exposing it",
  ]],
  ["Why reject the 0.840 ensemble?", [
    "the +0.02 adoption margin was fixed before the experiments",
    "0.018 is smaller than the seed-to-seed noise (~0.03): a statistical tie",
    "we report 0.840 openly — we just did not let it drive the decision",
  ]],
  ["Can it diagnose Parkinson's?", [
    "no — and it is not designed to",
    "colds, laryngitis, ageing, smoking also change the voice",
    "a non-diagnostic disclaimer appears before and after every result",
  ]],
  ["Is 37 subjects too few?", [
    "yes — it is the main limitation, stated in every report",
    "we report variability, repeat with 3 seeds, use grouped validation",
    "and we tested externally on a second corpus of 61 speakers",
  ]],
  ["Is it just detecting male vs female voices?", [
    "we tested it: removed all absolute-pitch features and re-ran everything",
    "the selected model held: 0.768 → 0.780",
    "the small neural network collapsed — and was excluded",
  ]],
  ["Hardest technical problem?", [
    "in the Italian corpus, every 44.1 kHz file belonged to the patient group",
    "a model could “detect Parkinson's” by detecting microphone bandwidth",
    "caught at inspection; all audio band-limited to 16 kHz before evaluation",
  ]],
];
backups.forEach(([q, bullets], bi) => {
  const sb = pres.addSlide();
  bg(sb);
  sb.addText([
    { text: "Backup  ", options: { color: MUTED, fontSize: 16 } },
    { text: q, options: { color: ICE, fontSize: 26, bold: true } },
  ], {
    x: 0.55, y: 0.4, w: W - 1.1, h: 0.8, isTextBox: true, margin: 0, fontFace: HEAD,
  });
  chip(sb, 21 + bi);
  let y = 2.2;
  bullets.forEach((b) => {
    sb.addText([{ text: "▪  ", options: { color: HONEST } }, { text: b, options: { color: ICE } }], {
      x: 1.6, y, w: 10.5, h: 0.6, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 17, align: "left",
    });
    y += 0.85;
  });
});

// ---------- write ----------
const out = path.join(ROOT, "report", "defence", "slides_premium.pptx");
pres.writeFile({ fileName: out }).then(() => console.log("wrote", out));
