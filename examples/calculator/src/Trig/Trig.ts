// Trig — тригонометрические функции (Taylor series)
function sin_fn(x: number): number {
  let term = x;
  let result = term;
  for (let n = 1; n < 10; n++) {
    term = -term * x * x / ((2 * n) * (2 * n + 1));
    result += term;
  }
  return result;
}
function cos_fn(x: number): number {
  let term = 1.0;
  let result = term;
  for (let n = 1; n < 10; n++) {
    term = -term * x * x / ((2 * n - 1) * (2 * n));
    result += term;
  }
  return result;
}
function tan_fn(x: number): number | string {
  const s = sin_fn(x);
  const c = cos_fn(x);
  if (Math.abs(c) < 1e-15) return "Error: tan undefined";
  return s / c;
}
function pi_fn(): number { return 3.141592653589793; }
export const PUBLIC = { sin_fn, cos_fn, tan_fn, pi_fn };
