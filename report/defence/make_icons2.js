// Teal / coral icon set for the light lecture deck (v2).
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const path = require("path");
const fa6 = require("react-icons/fa6");

const OUT = path.join(__dirname, "figs");
const TEAL = "#028090";
const CORAL = "#E85A5A";
const SLATE = "#16324A";

const wanted = [
  ["FaLungs", "t_lungs", TEAL],
  ["FaWaveSquare", "t_wave", TEAL],
  ["FaCommentDots", "t_mouth", TEAL],
  ["FaMicrophone", "t_mic", TEAL],
  ["FaBolt", "t_bolt", TEAL],
  ["FaFileAudio", "t_wavfile", TEAL],
  ["FaDatabase", "t_db", TEAL],
  ["FaBroom", "t_broom", TEAL],
  ["FaRobot", "t_robot", TEAL],
  ["FaTree", "t_tree", TEAL],
  ["FaScaleBalanced", "t_scale", TEAL],
  ["FaBullseye", "t_target", TEAL],
  ["FaCircleCheck", "t_check", TEAL],
  ["FaBan", "t_ban", CORAL],
  ["FaEarListen", "t_ear", TEAL],
  ["FaClock", "t_clock", TEAL],
  ["FaDollarSign", "t_dollar", TEAL],
  ["FaTableCells", "t_grid", TEAL],
  ["FaPersonWalking", "t_person", TEAL],
  ["FaHeartPulse", "t_pulse", CORAL],
  ["FaMusic", "t_music", TEAL],
  ["FaVolumeHigh", "t_volume", TEAL],
  ["FaScissors", "t_trim", TEAL],
  ["FaArrowsLeftRight", "t_resample", TEAL],
  ["FaSliders", "t_normalize", TEAL],
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
  console.log("icons v2 done");
})();
