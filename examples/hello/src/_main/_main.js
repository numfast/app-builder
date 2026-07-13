"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PUBLIC = void 0;
// _main — точка входа HelloApp
function hello_fn(who) {
    return "Hello, " + who + "!";
}
function default_fn() {
    return "Hello, World!";
}
exports.PUBLIC = { hello_fn, default_fn };
