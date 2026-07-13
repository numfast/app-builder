// Copyright (c) 2026 NumFast
// SPDX-License-Identifier: AGPL-3.0-only

/**
 * App Builder JS — Zero Import Architecture.
 *
 * Использование:
 *   import { MAIN } from "@numfast/app-builder";
 *   MAIN["build"]("my-app/");
 */

import { boot } from "./060_Boot";

export const MAIN = boot();
export { boot } from "./060_Boot";
export { Kernel } from "./010_Kernel";
export { build } from "./050_Builder";
