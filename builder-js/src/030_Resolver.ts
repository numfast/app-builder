// Copyright (c) 2026 NumFast
// SPDX-License-Identifier: AGPL-3.0-only

/**
 * Resolver — топологическая сортировка расширений (Kahn's algorithm).
 */

export interface ExtRef {
  name: string;
  path?: string;
  depends: string[];
}

export function resolveOrder(extensions: ExtRef[]): ExtRef[] {
  if (!extensions.length) return [];

  const depsMap: Record<string, string[]> = {};
  const nameToExt: Record<string, ExtRef> = {};

  for (const ext of extensions) {
    const name = ext.name;
    if (!name) continue;
    nameToExt[name] = ext;
    depsMap[name] = [...(ext.depends ?? [])];
  }

  const allNames = new Set(Object.keys(depsMap));

  // Check missing dependencies
  for (const [name, deps] of Object.entries(depsMap)) {
    for (const dep of deps) {
      if (!allNames.has(dep)) {
        throw new Error(
          `Extension '${name}' depends on '${dep}', ` +
          `but '${dep}' is not in the extension list`
        );
      }
    }
  }

  // Kahn's algorithm
  const inDegree: Record<string, number> = {};
  const dependents: Record<string, string[]> = {};

  for (const name of allNames) {
    inDegree[name] = depsMap[name].length;
    dependents[name] = [];
  }
  for (const [name, deps] of Object.entries(depsMap)) {
    for (const dep of deps) {
      dependents[dep].push(name);
    }
  }

  const queue: string[] = [];
  for (const [name, deg] of Object.entries(inDegree)) {
    if (deg === 0) queue.push(name);
  }

  const sorted: string[] = [];
  while (queue.length) {
    queue.sort();
    const name = queue.shift()!;
    sorted.push(name);
    for (const dep of dependents[name]) {
      inDegree[dep]--;
      if (inDegree[dep] === 0) queue.push(dep);
    }
  }

  if (sorted.length !== allNames.size) {
    const cycle = [...allNames].filter((n) => !sorted.includes(n));
    throw new Error(`Circular dependency detected: ${cycle.join(", ")}`);
  }

  return sorted.map((n) => nameToExt[n]);
}

export const PUBLIC = { resolveOrder };
