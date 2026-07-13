// build-pkg.js — Build calculator as npm package with Kernel structure
// Usage: node scripts/build-pkg.js
//
// Produces: packages/calculator/
//   index.js     (Kernel + extensions + alias registration)
//   package.json
//   README.md

const path = require("path");
const fs = require("fs");
const { MAIN } = require("../builder-js/dist/index");

const HERE = __dirname;
const APP_DIR = path.resolve(HERE, "../examples/calculator");
const PKG_DIR = path.resolve(HERE, "../packages/calculator");

console.log("1. Building calculator to resolve order");

// Используем builder для разрешения порядка
const kernel = MAIN["build"](APP_DIR);

// Получаем данные для генерации из Kernel и файловой системы
const appDir = APP_DIR;
const manifestPath = path.join(appDir, "full.toml");

// Читаем манифест
const loadAppManifest = MAIN["loadAppManifest"];
const app = loadAppManifest(manifestPath);

// Собираем расширения с их манифестами и JS-файлами
const extensions = [];
for (const extCfg of app.extensions) {
  const extName = extCfg.name;
  const relPath = extCfg.path;
  if (!relPath) continue;

  const extDir = path.resolve(appDir, relPath);
  const baseName = path.basename(extDir);
  const tomlPath = path.join(extDir, `${baseName}.toml`);
  const jsPath = path.join(extDir, `${baseName}.js`);

  if (!fs.existsSync(tomlPath)) continue;
  if (!fs.existsSync(jsPath)) continue;

  const loadExtManifest = MAIN["loadExtensionManifest"];
  const em = loadExtManifest(tomlPath);

  // Извлекаем список доступных PUBLIC функций из JS
  const jsCode = fs.readFileSync(jsPath, "utf-8");
  const publicMatch = jsCode.match(/exports\.PUBLIC\s*=\s*\{([^}]+)\}/);
  const publicFns = new Set();
  if (publicMatch) {
    for (const part of publicMatch[1].split(",")) {
      const trimmed = part.trim();
      if (trimmed) publicFns.add(trimmed);
    }
  }

  extensions.push({
    name: extName,
    jsPath,
    jsCode,
    manifest: em,
    publicFns,
    order: app.extensions.indexOf(extCfg),
  });
}

// Сортируем по порядку из манифеста
extensions.sort((a, b) => a.order - b.order);

// Определяем variables
const variables = kernel.variables; // Set<string>

console.log("2. Generating index.js");

let lines = [
  "//",
  "// @numfast/calculator -- built by App Builder",
  "//",
  "(function(global) {",
  '  "use strict";',
  "",
  "  // ==== Kernel ====",
  "  function Kernel(name) {",
  "    this.alias = {};",
  "    this._owner = {};",
  "    this.metadata = { _kernel: { name: name } };",
  "    this.variables = {};",
  "  }",
  "  Kernel.prototype.register = function(aliasName, func, owner) {",
  "    this.alias[aliasName] = func;",
  "    if (owner) {",
  "      this._owner[aliasName] = owner;",
  '      this.alias["_" + owner + "_" + aliasName] = func;',
  "    }",
  "  };",
  "  Kernel.prototype.call = function(name) {",
  "    var fn = this.alias[name];",
  "    if (!fn) throw new Error('Alias \"' + name + '\" not found');",
  "    if (this.variables[name]) return fn();",
  "    var args = Array.prototype.slice.call(arguments, 1);",
  "    return fn.apply(null, args);",
  "  };",
  "",
  "  // ==== Extensions ====",
  "",
];

// Конкатенируем JS-файлы расширений
for (const ext of extensions) {
  const relPath = path.relative(HERE, ext.jsPath);
  lines.push("  // ---- " + relPath + " ----");

  let code = ext.jsCode;

  // Убираем use strict (будет в UMD обёртке)
  code = code.replace(/^"use strict";\s*/m, "");

  // Убираем exports.__esModule = true
  code = code.replace(/Object\.defineProperty\(exports.*?__esModule.*?\);\s*/g, "");

  // Убираем exports.PUBLIC = {...} — регистрация будет отдельно
  code = code.replace(/exports\.PUBLIC\s*=\s*\{[^}]*\};\s*/g, "");

  // Убираем Object.defineProperty(exports, "PUBLIC"...)
  code = code.replace(/Object\.defineProperty\(exports,\s*"PUBLIC".*?\);\s*/g, "");

  lines.push(code.trim());
  lines.push("");
}

// Строим приложение
lines.push("  // ==== Build app ====");
lines.push('  var app = new Kernel("Calc");');
lines.push("");

for (const ext of extensions) {
  const em = ext.manifest;
  const extName = em.name;
  const aliases = em.alias || [];
  const mods = em.mods || [];
  const extVars = em.variables || [];

  for (let i = 0; i < aliases.length; i++) {
    const aliasName = aliases[i];
    const modName = mods[i];
    // Пропускаем, если функция не экспортирована (как Loader)
    if (!ext.publicFns.has(modName)) continue;
    lines.push('  app.register("' + aliasName + '", ' + modName + ', "' + extName + '");');
  }

  for (const v of extVars) {
    if (variables.has(v)) {
      lines.push('  app.variables["' + v + '"] = true;');
    }
  }
}

lines.push("");

// Помечаем переменные — при вызове call() вернёт fn() без аргументов
for (const v of variables || []) {
  if (kernel.alias[v]) {
    lines.push('  app.variables["' + v + '"] = true;');
  }
}

lines.push("");
lines.push("  // CommonJS export");
lines.push('  if (typeof module !== "undefined" && module.exports) {');
lines.push("    module.exports = app;");
lines.push("  }");
lines.push("");
lines.push("  // Browser global");
lines.push("  global.Calc = app;");
lines.push('})(typeof window !== "undefined" ? window : this);');
lines.push("");

const indexJs = lines.join("\n");
fs.writeFileSync(path.join(PKG_DIR, "index.js"), indexJs, "utf-8");
console.log("   Written:", indexJs.length + " bytes");

// ============================================================
// Generate package.json
// ============================================================
console.log("3. Generating package.json");

const pkgJson = {
  name: "@numfast/calculator",
  version: "1.0.0",
  description: "Calculator built by App Builder from examples/calculator/",
  main: "index.js",
  files: ["index.js", "README.md"],
  license: "MIT",
};

fs.writeFileSync(
  path.join(PKG_DIR, "package.json"),
  JSON.stringify(pkgJson, null, 2) + "\n",
  "utf-8"
);
console.log("   Written");

// ============================================================
// Generate README.md
// ============================================================
console.log("4. Generating README.md");

const aliases = Object.keys(kernel.alias).filter(a => !a.startsWith("_")).sort();
const readme = [
  "# @numfast/calculator",
  "",
  "Calculator built by **App Builder** from `examples/calculator/`.",
  "",
  "## Usage (Node.js)",
  "",
  "```js",
  "const Calc = require('@numfast/calculator');",
  "console.log(Calc.call('add', 2, 3));   // 5",
  "console.log(Calc.call('sin', 0));      // 0",
  "console.log(Calc.alias['pi']);         // 3.141592653589793",
  "```",
  "",
  "## Usage (Browser)",
  "",
  "```html",
  '<script src="node_modules/@numfast/calculator/index.js"></script>',
  "<script>",
  "  console.log(Calc.call('add', 2, 3));",
  "</script>",
  "```",
  "",
  "## Available functions",
  "",
  aliases.map(a => "  - `" + a + "`").join("\n"),
  "",
  "## Build",
  "",
  "```",
  "node scripts/build-pkg.js",
  "```",
  "",
].join("\n");

fs.writeFileSync(path.join(PKG_DIR, "README.md"), readme, "utf-8");
console.log("   Written");

// Summary
console.log("");
console.log("=== Package created ===");
console.log("Dir:", PKG_DIR);
console.log("Files:", fs.readdirSync(PKG_DIR).join(", "));
console.log("");

// Verify
const Calc = require(path.join(PKG_DIR, "index.js"));
console.log("Verification:");
console.log("  Calc.call('add', 2, 3):", Calc.call("add", 2, 3));
console.log("  Calc.call('sin', 1):", Calc.call("sin", 1));
console.log("  Calc.call('pi'):", Calc.call("pi"));
console.log("  Calc.alias['_Math_add']:", typeof Calc.alias["_Math_add"]);
