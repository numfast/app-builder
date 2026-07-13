// Copyright (c) 2026 NumFast
// SPDX-License-Identifier: AGPL-3.0-only

/**
 * CLI — командная строка.
 *
 * Прямой запуск:
 *   node dist/070_CLI.js build <app-dir>
 *   node dist/070_CLI.js list
 *
 * Через boot():
 *   MAIN["main"](MAIN)
 */

function main(MAIN: Record<string, any>): void {
  const build = MAIN["build"];

  const args = process.argv.slice(2);
  if (!args.length) {
    console.error("Usage: node 070_CLI.js build <app-dir>");
    console.error("       node 070_CLI.js list");
    process.exit(1);
  }

  const command = args[0];

  if (command === "build") {
    const appDir = args[1] || ".";
    const kernel = build(appDir);
    console.log(`Built: ${kernel.metadata._kernel.name}`);
    console.log(`Aliases: ${Object.keys(kernel.alias).length}`);

    const defaultFn = kernel.get("_default");
    if (defaultFn) {
      const result = defaultFn();
      if (result != null) console.log(result);
    }
  } else if (command === "list") {
    console.log("MAIN Registry components:");
    for (const name of Object.keys(MAIN).sort()) {
      console.log(`  ${name}`);
    }
  } else if (command === "test") {
    const appDir = args[1] || ".";
    const kernel = build(appDir);
    const tests = kernel.metadata._tests ?? {};
    const testKeys = Object.keys(tests);
    if (!testKeys.length) {
      console.log("No tests found in manifest.");
      return;
    }
    let failed = 0;
    for (const tname of testKeys) {
      const tspec = tests[tname];
      const modName = tspec.mod;
      const argsList = tspec.args ?? [];
      const expected = tspec.expected;
      const expr = tspec.expr;

      let result: string;
      if (expr) {
        result = String(eval(expr));
      } else if (modName) {
        const fn = kernel.get(modName);
        if (!fn) {
          console.log(`  FAIL ${tname}: alias '${modName}' not found`);
          failed++;
          continue;
        }
        result = String(fn(...argsList));
      } else {
        console.log(`  FAIL ${tname}: no mod or expr`);
        failed++;
        continue;
      }

      if (result === expected) {
        console.log(`  OK  ${tname}`);
      } else {
        console.log(`  FAIL ${tname}: got '${result}', expected '${expected}'`);
        failed++;
      }
    }

    if (failed) {
      console.log(`FAILED: ${failed} of ${testKeys.length}`);
      process.exit(1);
    } else {
      console.log(`ALL OK: ${testKeys.length} tests passed`);
    }
  } else {
    console.error(`Unknown command: ${command}`);
    process.exit(1);
  }
}

// Self-boot: node dist/070_CLI.js ...
// Этот блок НЕ выполняется, когда файл загружен через boot() (require.main !== module)
if (require.main === module) {
  const boot = require("./060_Boot").boot;
  const MAIN = boot(__dirname);
  main(MAIN);
}

export const PUBLIC = { main };
