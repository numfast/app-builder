// Math — арифметические операции
function add_fn(a: number, b: number): number { return a + b; }
function sub_fn(a: number, b: number): number { return a - b; }
function mul_fn(a: number, b: number): number { return a * b; }
function div_fn(a: number, b: number): number | string {
  if (b === 0) return "Error: division by zero";
  return a / b;
}
function pow_fn(a: number, b: number): number { return a ** b; }
export const PUBLIC = { add_fn, sub_fn, mul_fn, div_fn, pow_fn };
