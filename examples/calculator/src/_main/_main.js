"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PUBLIC = void 0;
// _main — точка входа Calculator
function calc_fn(expr) {
    const e = String(expr).trim();
    try {
        return String(Function('"use strict"; return (' + e + ')')());
    }
    catch (err) {
        return "Error: " + err.message;
    }
}
function help_fn() {
    return "Calc usage: calc('2+2*3') -> '8'";
}
function default_fn() {
    return help_fn();
}
exports.PUBLIC = { calc_fn, help_fn, default_fn };
