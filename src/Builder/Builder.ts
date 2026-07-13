// Copyright (c) 2026 NumFast
// SPDX-License-Identifier: AGPL-3.0-only

/**
 * Builder — оркестратор сборки приложений.
 * Ноль импортов. Всё через MAIN (Registry).
 */

import * as fs from "fs";
import * as path from "path";

const MAIN: Record<string, any> = (globalThis as any).__MAIN__;

export function build(appDir: string): any {
  const Kernel = MAIN["Kernel"];
  const loadAppManifest = MAIN["loadAppManifest"];
  const loadExtensionManifest = MAIN["loadExtensionManifest"];
  const resolveOrder = MAIN["resolveOrder"];
  const loadExtension = MAIN["loadExtension"];

  const base = path.resolve(appDir);

  // Ищем full.toml или full.json
  let manifestPath: string | null = null;
  for (const name of ["full.toml", "full.json"]) {
    const fp = path.join(base, name);
    if (fs.existsSync(fp)) { manifestPath = fp; break; }
  }
  if (!manifestPath) throw new Error(`full.toml not found in ${base}`);

  // Парсим манифест
  const app = loadAppManifest(manifestPath);

  // Создаём Kernel
  const kernel = new Kernel(app.kernel.name, app.kernel.singleton);

  // Собираем extension refs с depends
  const extRefs: any[] = [];
  for (const extCfg of app.extensions) {
    const name = extCfg.name;
    const relPath = extCfg.path;
    if (!relPath) continue;

    const extDir = path.resolve(base, relPath);

    // Ищем манифест расширения: {Name}.toml или {Name}.json
    const extName = path.basename(extDir);
    let extManifestPath: string | null = null;
    for (const mn of [`${extName}.toml`, `${extName}.json`]) {
      const fp = path.join(extDir, mn);
      if (fs.existsSync(fp)) { extManifestPath = fp; break; }
    }

    let depends: string[] = [];
    if (extManifestPath) {
      const em = loadExtensionManifest(extManifestPath);
      depends = em.depends ?? [];
    }

    extRefs.push({
      name,
      path: extDir,
      depends,
      metadata: extCfg.metadata ?? {},
    });
  }

  // Топологическая сортировка
  const ordered = resolveOrder(extRefs);

  // Загрузка расширений по порядку
  for (const ref of ordered) {
    const overrideMeta: Record<string, any> = { ...ref.metadata };
    const metaSection = path.basename(ref.path);
    const appMeta = (app.extensionsMeta ?? {})[metaSection];
    if (appMeta) Object.assign(overrideMeta, appMeta);

    loadExtension(
      kernel,
      ref.path,
      Object.keys(overrideMeta).length ? overrideMeta : undefined
    );
  }

  return kernel;
}

export const PUBLIC = { build };
