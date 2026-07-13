// _main — точка входа HelloApp
function hello_fn(who: string): string {
  return "Hello, " + who + "!";
}
function default_fn(): string {
  return "Hello, World!";
}
export const PUBLIC = { hello_fn, default_fn };
