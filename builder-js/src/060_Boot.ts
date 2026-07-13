// Copyright (c) 2026 NumFast
// SPDX-License-Identifier: AGPL-3.0-only

/**
 * Bootloader — собирает Registry из PUBLIC всех файлов builder'а.
 * Читает все .js файлы в директории dist/, require() каждый,
 * собирает PUBLIC в единый словарь MAIN.
 */
import * as fs from "fs";
import * as path from "path";

export function boot(builderDir?: string): Record<string, any> {
  const dir = builderDir ?? __dirname;

  const MAIN: Record<string, any> = {};

  // Размещаем MAIN в globalThis до require, чтобы модули
  // могли захватить ссылку через const MAIN = (globalThis as any).__MAIN__
  (globalThis as any).__MAIN__ = MAIN;

  // Сортируем файлы по имени (010_, 020_, ...)
  const jsFiles = fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".js") && !f.startsWith("_") && f !== "index.js")
    .sort();

  for (const file of jsFiles) {
    const filePath = path.join(dir, file);
    // Очищаем кэш чтобы при повторном boot() модули перезахватили новый MAIN
    delete require.cache[filePath];
    try {
      const mod = require(filePath);
      if (mod.PUBLIC) {
        for (const [key, value] of Object.entries(mod.PUBLIC)) {
          if (key in MAIN) {
            throw new Error(
              `Duplicate PUBLIC key '${key}' in ${file} ` +
              `(already defined in another file)`
            );
          }
          (MAIN as any)[key] = value;
        }
      }
    } catch (e: any) {
      throw new Error(`Boot failed loading ${file}: ${e.message}`);
    }
  }

  return MAIN;
}

export const PUBLIC = { boot };
