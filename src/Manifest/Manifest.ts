// Copyright (c) 2026 NumFast
// SPDX-License-Identifier: AGPL-3.0-only

/**
 * Manifest — парсер TOML/JSON манифестов.
 *
 * Содержит минимальный TOML-парсер для подмножества TOML,
 * используемого в манифестах App Builder.
 */

import * as fs from "fs";
import * as path from "path";

// ============================================================
// Minimal TOML parser (читает подмножество TOML для манифестов)
// ============================================================

function parseTomlValue(raw: string): any {
  const s = raw.trim();
  // Строка в кавычках
  if (s.startsWith('"') && s.endsWith('"')) {
    return s.slice(1, -1);
  }
  // Булевы
  if (s === "true") return true;
  if (s === "false") return false;
  // Число
  const n = Number(s);
  if (!isNaN(n) && s.length > 0) return n;
  return s;
}

function parseTomlArray(raw: string): any[] {
  // raw вида: [ "a", "b", "c" ]
  const inner = raw.trim().slice(1, -1).trim();
  if (!inner) return [];
  const items: any[] = [];
  let depth = 0;
  let current = "";
  let inString = false;
  for (const ch of inner) {
    if (ch === '"') inString = !inString;
    if (!inString) {
      if (ch === "[" || ch === "{") depth++;
      if (ch === "]" || ch === "}") depth--;
    }
    if (ch === "," && depth === 0 && !inString) {
      items.push(parseTomlValue(current.trim()));
      current = "";
    } else {
      current += ch;
    }
  }
  const last = current.trim();
  if (last) items.push(parseTomlValue(last));
  return items;
}

function parseToml(text: string): Record<string, any> {
  const result: Record<string, any> = {};
  let current: Record<string, any> = result;

  for (const rawLine of text.split("\n")) {
    const line = rawLine.trim();

    // Пустая строка или комментарий
    if (!line || line.startsWith("#")) continue;

    // [[array_of_tables]]
    const arrMatch = line.match(/^\[\[(.+?)\]\]$/);
    if (arrMatch) {
      const key = arrMatch[1].trim();
      if (!Array.isArray(result[key])) result[key] = [];
      const obj: Record<string, any> = {};
      result[key].push(obj);
      current = obj;
      continue;
    }

    // [table]
    const tableMatch = line.match(/^\[(.+?)\]$/);
    if (tableMatch) {
      const key = tableMatch[1].trim();
      if (!result[key] || typeof result[key] !== "object" || Array.isArray(result[key])) {
        result[key] = {};
      }
      current = result[key];
      continue;
    }

    // key = value
    const eqIdx = line.indexOf("=");
    if (eqIdx === -1) continue;

    const k = line.slice(0, eqIdx).trim();
    let v = line.slice(eqIdx + 1).trim();

    // Убираем inline-комментарий
    const commentIdx = v.indexOf(" #");
    if (commentIdx > 0) {
      // Проверяем, что # не внутри строки
      let inStr = false;
      let realIdx = -1;
      for (let i = 0; i < v.length; i++) {
        if (v[i] === '"') inStr = !inStr;
        if (v[i] === "#" && !inStr) { realIdx = i; break; }
      }
      if (realIdx > 0) v = v.slice(0, realIdx).trim();
    }

    if (v.startsWith("[") && (v.endsWith("]") || v.endsWith("],"))) {
      // Убираем trailing comma для одноместных массивов
      if (v.endsWith("],")) v = v.slice(0, -1);
      current[k] = parseTomlArray(v);
    } else {
      current[k] = parseTomlValue(v);
    }
  }

  return result;
}

// ============================================================
// Manifest loaders
// ============================================================

export interface ExtensionConfig {
  name: string;
  path?: string;
  exclude?: boolean;
  metadata?: Record<string, any>;
}

export interface AppManifest {
  kernel: { name: string; singleton: boolean };
  extensions: ExtensionConfig[];
  extensionsMeta?: Record<string, Record<string, any>>;
  tests?: Record<string, any>;
}

export interface ExtensionManifest {
  name: string;
  version: string;
  alias: string[];
  mods: string[];
  depends: string[];
  variables: string[];
  metadata: Record<string, any>;
}

function readManifest(filePath: string): Record<string, any> {
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved)) {
    throw new Error(`Manifest not found: ${resolved}`);
  }
  const text = fs.readFileSync(resolved, "utf-8");
  if (filePath.endsWith(".json")) {
    return JSON.parse(text);
  }
  return parseToml(text);
}

function findManifest(dir: string, name: string): { path: string; format: "toml" | "json" } | null {
  const tomlPath = path.join(dir, `${name}.toml`);
  if (fs.existsSync(tomlPath)) return { path: tomlPath, format: "toml" };
  const jsonPath = path.join(dir, `${name}.json`);
  if (fs.existsSync(jsonPath)) return { path: jsonPath, format: "json" };
  return null;
}

export function loadAppManifest(dirOrFile: string): AppManifest {
  // Support: path to directory (with full.toml/full.json inside)
  //          or path directly to manifest file
  let manifestPath: string;
  if (dirOrFile.endsWith(".toml") || dirOrFile.endsWith(".json")) {
    manifestPath = dirOrFile;
  } else {
    const found = findManifest(dirOrFile, "full");
    if (!found) throw new Error(`full.toml/full.json not found in ${dirOrFile}`);
    manifestPath = found.path;
  }

  const data = readManifest(manifestPath);

  // Kernel config
  const kData = data.kernel ?? {};
  const kernelName = typeof kData === "object" ? (kData.name ?? "App") : "App";
  const singleton = typeof kData === "object" ? (kData.singleton ?? true) : true;

  // Extensions
  const rawExts: any[] = data.extensions ?? [];
  const extensions: ExtensionConfig[] = rawExts.map((e: any) => ({
    name: e.name ?? "",
    path: e.path,
    exclude: e.exclude ?? false,
    metadata: e.metadata ?? {},
  }));

  return {
    kernel: { name: kernelName, singleton },
    extensions,
    extensionsMeta: data.extensions_meta ?? {},
    tests: data.tests ?? {},
  };
}

export function loadExtensionManifest(filePath: string): ExtensionManifest {
  const resolved = path.resolve(filePath);
  const data = readManifest(resolved);
  const extName = data.name ?? path.basename(path.dirname(resolved));

  return {
    name: extName,
    version: data.version ?? "0.1.0",
    alias: data.alias ?? [],
    mods: data.mods ?? [],
    depends: data.depends ?? [],
    variables: data.variables ?? [],
    metadata: data.metadata ?? {},
  };
}

export const PUBLIC = { loadAppManifest, loadExtensionManifest };
