// Copyright (c) 2026 NumFast
// SPDX-License-Identifier: AGPL-3.0-only

/**
 * Kernel — ядро приложения. Плоское пространство имён для всех функций.
 */
export class Kernel {
  public alias: Record<string, Function> = {};
  private _owner: Record<string, string> = {};
  public metadata: Record<string, any> = {};
  public variables: Set<string> = new Set();

  constructor(name: string = "App", singleton: boolean = true) {
    this.metadata = { _kernel: { name, singleton } };
  }

  register(aliasName: string, func: Function, owner: string = ""): void {
    this.alias[aliasName] = func;
    if (owner) {
      this._owner[aliasName] = owner;
      const sysAlias = `_${owner}_${aliasName}`;
      this.alias[sysAlias] = func;
      this._owner[sysAlias] = owner;
    }
  }

  get(name: string): Function | undefined {
    return this.alias[name];
  }

  call(name: string, ...args: any[]): any {
    const fn = this.alias[name];
    if (!fn) throw new Error(`Alias '${name}' not found`);
    if (this.variables.has(name)) {
      return fn();
    }
    return fn(...args);
  }
}

export const PUBLIC = { Kernel };
