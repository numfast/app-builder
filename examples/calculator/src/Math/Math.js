"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PUBLIC = void 0;
// Math — арифметические операции
function add_fn(a, b) { return a + b; }
function sub_fn(a, b) { return a - b; }
function mul_fn(a, b) { return a * b; }
function div_fn(a, b) {
    if (b === 0)
        return "Error: division by zero";
    return a / b;
}
function pow_fn(a, b) { return a ** b; }
exports.PUBLIC = { add_fn, sub_fn, mul_fn, div_fn, pow_fn };
