"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PUBLIC = void 0;
// Trig — тригонометрические функции (Taylor series)
function sin_fn(x) {
    let term = x;
    let result = term;
    for (let n = 1; n < 10; n++) {
        term = -term * x * x / ((2 * n) * (2 * n + 1));
        result += term;
    }
    return result;
}
function cos_fn(x) {
    let term = 1.0;
    let result = term;
    for (let n = 1; n < 10; n++) {
        term = -term * x * x / ((2 * n - 1) * (2 * n));
        result += term;
    }
    return result;
}
function tan_fn(x) {
    const s = sin_fn(x);
    const c = cos_fn(x);
    if (Math.abs(c) < 1e-15)
        return "Error: tan undefined";
    return s / c;
}
function pi_fn() { return 3.141592653589793; }
exports.PUBLIC = { sin_fn, cos_fn, tan_fn, pi_fn };
