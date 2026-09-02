// Render react-icons to PNG for the deck (light blue on transparent).
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const path = require("path");
const icons = require("react-icons/fa6");

const OUT = path.join(__dirname, "figs");
const COLOR = "#5AB4F0";
const ICE = "#E8EEF7";
const WRONG = "#FF8C42";

const wanted = [
  ["FaBrain", "ic_brain", COLOR],
  ["FaMicrophone", "ic_mic", COLOR],
  ["FaWaveSquare", "ic_wave", COLOR],
  ["FaClock", "ic_clock", COLOR],
  ["FaDollarSign", "ic_dollar", COLOR],
  ["FaScaleBalanced", "ic_scale", COLOR],
  ["FaShieldHalved", "ic_shield", COLOR],
  ["FaMagnifyingGlass", "ic_search", COLOR],
  ["FaFlaskVial", "ic_flask", COLOR],
  ["FaBan", "ic_ban", WRONG],
  ["FaTriangleExclamation", "ic_warn", WRONG],
  ["FaCircleCheck", "ic_check", COLOR],
  ["FaEarListen", "ic_ear", COLOR],
  ["FaGaugeHigh", "ic_gauge", COLOR],
  ["FaLock", "ic_lock", COLOR],
  ["FaItalic", "ic_unused", COLOR],
  ["FaPersonWalking", "ic_person", COLOR],
  ["FaChartLine", "ic_chart", COLOR],
  ["FaQuestion", "ic_question", ICE],
];

(async () => {
  for (const [name, file, color] of wanted) {
    const Comp = icons[name];
    if (!Comp) { console.log("MISSING", name); continue; }
    const svg = ReactDOMServer.renderToStaticMarkup(
      React.createElement(Comp, { color, size: 256 })
    );
    await sharp(Buffer.from(svg)).resize(256, 256).png()
      .toFile(path.join(OUT, file + ".png"));
  }
  console.log("icons done");
})();
