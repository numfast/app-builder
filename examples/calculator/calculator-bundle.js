//
// NumFast Calculator — built by App Builder
// Source: examples/calculator/
//
(function(global) {
  var Calc = {};

  Calc.add = function add_fn(a, b) { return a + b; };

  Calc.sub = function sub_fn(a, b) { return a - b; };

  Calc.mul = function mul_fn(a, b) { return a * b; };

  Calc.div = function div_fn(a, b) {
    if (b === 0)
        return "Error: division by zero";
    return a / b;
};

  Calc.pow = function pow_fn(a, b) { return a ** b; };

  Calc.sin = function sin_fn(x) {
    let term = x;
    let result = term;
    for (let n = 1; n < 10; n++) {
        term = -term * x * x / ((2 * n) * (2 * n + 1));
        result += term;
    }
    return result;
};

  Calc.cos = function cos_fn(x) {
    let term = 1.0;
    let result = term;
    for (let n = 1; n < 10; n++) {
        term = -term * x * x / ((2 * n - 1) * (2 * n));
        result += term;
    }
    return result;
};

  Calc.tan = function tan_fn(x) {
    const s = sin_fn(x);
    const c = cos_fn(x);
    if (Math.abs(c) < 1e-15)
        return "Error: tan undefined";
    return s / c;
};

  Calc.pi = function pi_fn() { return 3.141592653589793; };

  Calc.calc = function calc_fn(expr) {
    const e = String(expr).trim();
    try {
        return String(Function('"use strict"; return (' + e + ')')());
    }
    catch (err) {
        return "Error: " + err.message;
    }
};

  Calc.help = function help_fn() {
    return "Calc usage: calc('2+2*3') -> '8'";
};

  global.Calc = Calc;
})(window);
