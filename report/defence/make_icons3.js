// Violet / amber icon set for deck v3.
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const path = require("path");
const fa6 = require("react-icons/fa6");

const OUT = path.join(__dirname, "figs");
const VIOLET = "#43307A";
const AMBER = "#D98A1F";
const CORAL = "#D9534F";
const WHITE = "#F5F2FC";

const wanted = [
  ["FaLungs", "v_lungs", VIOLET],
  ["FaWaveSquare", "v_wave", VIOLET],
  ["FaCommentDots", "v_mouth", VIOLET],
  ["FaMicrophone", "v_mic", VIOLET],
  ["FaBolt", "v_bolt", VIOLET],
  ["FaTableCells", "v_grid", VIOLET],
  ["FaFileAudio", "v_wavfile", VIOLET],
  ["FaDatabase", "v_db", VIOLET],
  ["FaBroom", "v_broom", VIOLET],
  ["FaArrowsLeftRight", "v_arrows", VIOLET],
  ["FaScissors", "v_scissors", VIOLET],
  ["FaGaugeHigh", "v_gauge", VIOLET],
  ["FaRobot", "v_robot", VIOLET],
  ["FaTree", "v_tree", VIOLET],
  ["FaEarListen", "v_ear", VIOLET],
  ["FaClock", "v_clock", VIOLET],
  ["FaCircleCheck", "v_check", VIOLET],
  ["FaPersonWalking", "v_person", VIOLET],
  ["FaVolumeHigh", "v_volume", VIOLET],
  ["FaScaleBalanced", "v_scale", VIOLET],
  ["FaBan", "c_ban", CORAL],
  ["FaMicrophone", "w_mic", WHITE],
  ["FaGraduationCap", "v_grad", VIOLET],
];

(async () => {
  for (const [name, file, color] of wanted) {
    const Comp = fa6[name];
    if (!Comp) { console.log("MISSING", name); continue; }
    const svg = ReactDOMServer.renderToStaticMarkup(
      React.createElement(Comp, { color, size: 256 })
    );
    await sharp(Buffer.from(svg)).resize(256, 256).png()
      .toFile(path.join(OUT, file + ".png"));
  }
  console.log("icons v3 done");
})();
