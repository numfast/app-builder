// Copyright (c) 2026 NumFast
// SPDX-License-Identifier: AGPL-3.0-only

/**
 * Loader — require() загрузчик расширений для Node.js.
 * Ищет {Name}.toml или {Name}.json для манифеста.
 * Загружает {Name}.js через require().
 */

import * as fs from "fs";
import * as path from "path";

const MAIN: Record<string, any> = (globalThis as any).__MAIN__;

export function loadExtension(
  kernel: any,
  extDir: string,
  overrideMetadata?: Record<string, any>
): void {
  const resolvedDir = path.resolve(extDir);
  const extName = path.basename(resolvedDir);

  // Ищем манифест: {Name}.toml или {Name}.json
  let manifestPath: string | null = null;
  for (const mn of [`${extName}.toml`, `${extName}.json`]) {
    const fp = path.join(resolvedDir, mn);
    if (fs.existsSync(fp)) { manifestPath = fp; break; }
  }
  if (!manifestPath) {
    throw new Error(`Extension manifest not found: ${resolvedDir}`);
  }

  const loadExtensionManifest = MAIN["loadExtensionManifest"];
  const em = loadExtensionManifest(manifestPath);

  // Мерж метаданных
  const metaSection = em.name;
  if (!kernel.metadata[metaSection]) kernel.metadata[metaSection] = {};
  Object.assign(kernel.metadata[metaSection], em.metadata);
  if (overrideMetadata) {
    Object.assign(kernel.metadata[metaSection], overrideMetadata);
  }

  // Версия
  if (!kernel.metadata._versions) kernel.metadata._versions = {};
  kernel.metadata._versions[em.name] = em.version;

  if (!em.mods.length) return;

  // Загружаем .js через require()
  const jsPath = path.join(resolvedDir, `${extName}.js`);
  if (!fs.existsSync(jsPath)) {
    throw new Error(`Extension module not found: ${jsPath}`);
  }

  // Проверка на require/import (грубая, через строки)
  const source = fs.readFileSync(jsPath, "utf-8");
  for (const rawLine of source.split("\n")) {
    const stripped = rawLine.trim();
    if (stripped.startsWith("require(") || stripped.startsWith("import ")) {
      throw new Error(
        `ImportError: ${path.basename(jsPath)} has '${stripped}'. ` +
        `Extensions must NOT have imports.`
      );
    }
  }

  // Загружаем модуль
  let extModule: any;
  try {
    extModule = require(jsPath);
  } catch (e: any) {
    throw new Error(`Failed to load extension ${extName}: ${e.message}`);
  }

  const extPublic = extModule.PUBLIC;
  if (!extPublic) {
    throw new Error(`${path.basename(jsPath)} has no PUBLIC export`);
  }

  // Регистрируем алиасы
  const aliasList = em.alias;
  const modsList = em.mods;
  for (let i = 0; i < aliasList.length; i++) {
    const aliasName = aliasList[i];
    const modName = modsList[i];
    const func = extPublic[modName];
    if (!func) continue;
    kernel.register(aliasName, func, em.name);
    if (em.variables.includes(aliasName)) {
      kernel.variables.add(aliasName);
    }
  }

  // Очищаем require cache для перезагрузки
  delete require.cache[require.resolve(jsPath)];
}

export const PUBLIC = { loadExtension };
