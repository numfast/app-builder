//
// @numfast/calculator -- built by App Builder
//
(function(global) {
  "use strict";

  // ==== Kernel ====
  function Kernel(name) {
    this.alias = {};
    this._owner = {};
    this.metadata = { _kernel: { name: name } };
    this.variables = {};
  }
  Kernel.prototype.register = function(aliasName, func, owner) {
    this.alias[aliasName] = func;
    if (owner) {
      this._owner[aliasName] = owner;
      this.alias["_" + owner + "_" + aliasName] = func;
    }
  };
  Kernel.prototype.call = function(name) {
    var fn = this.alias[name];
    if (!fn) throw new Error('Alias "' + name + '" not found');
    if (this.variables[name]) return fn();
    var args = Array.prototype.slice.call(arguments, 1);
    return fn.apply(null, args);
  };

  // ==== Extensions ====

  // ---- ..\examples\calculator\src\_main\_main.js ----
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

  // ---- ..\examples\calculator\src\Math\Math.js ----
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

  // ---- ..\examples\calculator\src\Trig\Trig.js ----
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

  // ==== Build app ====
  var app = new Kernel("Calc");

  app.register("calc", calc_fn, "_main");
  app.register("help", help_fn, "_main");
  app.register("_default", default_fn, "_main");
  app.register("add", add_fn, "Math");
  app.register("sub", sub_fn, "Math");
  app.register("mul", mul_fn, "Math");
  app.register("div", div_fn, "Math");
  app.register("pow", pow_fn, "Math");
  app.register("sin", sin_fn, "Trig");
  app.register("cos", cos_fn, "Trig");
  app.register("tan", tan_fn, "Trig");
  app.register("pi", pi_fn, "Trig");
  app.variables["pi"] = true;

  app.variables["pi"] = true;

  // CommonJS export
  if (typeof module !== "undefined" && module.exports) {
    module.exports = app;
  }

  // Browser global
  global.Calc = app;
})(typeof window !== "undefined" ? window : this);
