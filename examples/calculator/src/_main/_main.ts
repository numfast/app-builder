// _main — точка входа Calculator
function calc_fn(expr: string): string {
  const e = String(expr).trim();
  try {
    return String(Function('"use strict"; return (' + e + ')')());
  } catch (err: any) {
    return "Error: " + err.message;
  }
}
function help_fn(): string {
  return "Calc usage: calc('2+2*3') -> '8'";
}
function default_fn(): string {
  return help_fn();
}
export const PUBLIC = { calc_fn, help_fn, default_fn };
