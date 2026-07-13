// bundle-calculator.js — Build calculator and generate browser bundle
const path = require("path");
const fs = require("fs");
const { MAIN } = require("../builder-js/dist/index");

const HERE = __dirname;
const APP_DIR = path.resolve(HERE, "../examples/calculator");
const OUT = path.resolve(APP_DIR, "calculator-bundle.js");

console.log("Building calculator from:", APP_DIR);

const kernel = MAIN["build"](APP_DIR);
const aliases = Object.keys(kernel.alias).filter((a) => !a.startsWith("_"));

console.log("Aliases found:", aliases.join(", "));

let bundle = [
  "//",
  "// NumFast Calculator — built by App Builder",
  "// Source: examples/calculator/",
  "//",
  "(function(global) {",
  "  var Calc = {};",
  "",
];

for (const alias of aliases) {
  const fn = kernel.alias[alias];
  if (typeof fn !== "function") continue;
  // fn.toString() gives full function source
  const src = fn.toString();
  bundle.push("  Calc." + alias + " = " + src + ";");
  bundle.push("");
}

bundle.push("  global.Calc = Calc;");
bundle.push("})(window);");
bundle.push("");

const output = bundle.join("\n");
fs.writeFileSync(OUT, output, "utf-8");
console.log("Bundle written:", OUT);
console.log("Size:", output.length, "bytes");