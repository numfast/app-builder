# @numfast/calculator

Calculator built by **App Builder** from `examples/calculator/`.

## Usage (Node.js)

```js
const Calc = require('@numfast/calculator');
console.log(Calc.call('add', 2, 3));   // 5
console.log(Calc.call('sin', 0));      // 0
console.log(Calc.alias['pi']);         // 3.141592653589793
```

## Usage (Browser)

```html
<script src="node_modules/@numfast/calculator/index.js"></script>
<script>
  console.log(Calc.call('add', 2, 3));
</script>
```

## Available functions

  - `add`
  - `calc`
  - `cos`
  - `div`
  - `help`
  - `mul`
  - `pi`
  - `pow`
  - `sin`
  - `sub`
  - `tan`

## Build

```
node scripts/build-pkg.js
```
