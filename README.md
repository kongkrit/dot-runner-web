# Dot runner

A small project for learning [Preact Signals](https://github.com/preactjs/signals) and [lit-html](https://lit.dev/docs/libraries/standalone-templates/). A red dot moves on a 16×8 grid in the last arrow direction you pressed, and a readout shows its position as one hex byte. The page runs this app twice, built two ways so you can compare them: a **singleton** version, where each part exists once and keeps its state at file level, and a **factory** version, where `main.js` creates the parts. There is no npm and no build step: the browser loads both libraries as ES modules straight from `vendor/`.

## Run

<details>
<summary>Start command, why a server, network exposure, README viewer</summary>
<br>

```bash
uv run --no-project python -m http.server 8000
```

Open <http://localhost:8000>. Arrow keys move both dots, Space stops them. Ctrl+C stops the server.

- **Why a server:** Chrome refuses to load ES modules (`<script type="module">`) from a `file://` page, so opening `index.html` directly shows the headings but no grids.
- **Why `--no-project`:** uv skips looking for a `pyproject.toml` and creates no venv. It just runs Python's built-in file server.
- **Network exposure:** `http.server` listens on every network interface, so other machines on your network can browse this folder, `.git/` included. Add `--bind 127.0.0.1` to keep it to this machine.
- **README viewer:** <http://localhost:8000/README.html> shows this file rendered, with `[ expand all ]` and `[ collapse all ]` pinned at the top. It looks like VS Code's Markdown preview with the Dark 2026 theme (Light 2026 when your system is in light mode), using [marked](https://github.com/markedjs/marked), [highlight.js](https://highlightjs.org/) and VS Code's own preview stylesheets from `.readme-vendor/`. It needs the server too: a `file://` page cannot `fetch` README.md.

</details>

## How it works

### Files

<details>
<summary>Model, view, controller, main loop; what each file holds</summary>
<br>

The code is split the way an embedded C program often is: a model (state plus the rule that changes it), a view (draws the state), a controller (reads the keys), and a main loop that feeds the controller's input to the model on a timer. Comments in the code name the C counterpart of each piece (`model_t`, `model_update()`, `view_update()`, `controller_read()`). The model, controller and main exist twice, in `singleton/` and `factory/`, with the same file names; both versions share `model-controller-common.js` and `view.js`.

| File | Role |
|------|------|
| `index.html` | Page shell: the import map, the grid's CSS, the empty `#app-singleton` and `#app-factory` containers, and one module script per version. |
| `model-controller-common.js` | The `Cmd` table: the message the controller sends to the model, shared by those two only, like the C `command` enum. |
| `view.js` | `viewUpdate(m, container)`: renders a lit-html template of the model's grid (its `width` × `height`) and the hex readout into the container. Reads signals, writes none. Imports nothing from either version, so both share it. |
| `singleton/model.js` | Grid size, state and update rule: `WIDTH`, `HEIGHT`, the `row` and `col` signals and `cmd` at file level, and the one `model` object with `width`, `height`, read-only `row`, `col` and `hex` computeds, and `update(c)`. No DOM. |
| `singleton/controller.js` | Input: a file-level `pending` latch, and the one `controller` object with `keydown(e)`, which latches a key, and `read()`, which hands the tick the latest key and clears it. |
| `singleton/main.js` | Wiring: `keydown` → `controller.keydown`, a 150 ms timer → `model.update(controller.read())`, `effect` → `viewUpdate` into `#app-singleton`. |
| `factory/model.js` | The same model built by `createModel()`, so each call gives a new, independent one. |
| `factory/controller.js` | The same controller built by `createController()`, each with its own latch. |
| `factory/main.js` | The same wiring, after creating one model and one controller; draws into `#app-factory`. |
| `vendor/` | lit-html 3.3.3 (`lit-html.js`) and @preact/signals-core 1.14.5 (`signals-core.mjs`, the package's `dist/signals-core.mjs`), the published files used as-is. |

</details>

### Terms

<details>
<summary>semantic HTML, singleton, factory, DOM, import map, arrow keys, div, table, Object.freeze, signal, computed, effect, html, container, render</summary>
<br>

- **semantic HTML**: choosing the element whose name says what the content is, such as `<p>` for a paragraph, `<table>` for rows and columns, or `<output>` for a computed result, rather than a generic box made to look right. Screen readers, search engines and browser features rely on that meaning; the look comes from CSS either way.
- **singleton**: a part that exists exactly once, built when its file loads, with its state in file-level variables, like `static` variables in a C file. Like a block hard-wired into a chip at a fixed address.
- **factory**: a function that builds and returns a new instance each time it is called, such as `createModel()`, so `main.js` decides how many there are. Like a Verilog module that the top level instantiates, each instance with its own flip-flops; unlike hardware, instances are made while the program runs and freed automatically when nothing uses them.
  ***
- **DOM** (browser): the tree of elements the browser builds from the HTML and draws on screen. JavaScript changes the page by changing this tree, and the browser redraws to match.
- **import map** (browser): a JSON block in the page that tells the browser which file a bare module name such as `lit-html` means. In an npm project a bundler does this job.
- **ArrowUp, ArrowDown, ArrowLeft, ArrowRight** (browser): the values the browser puts in a key event's `key` field when an arrow key is pressed. `controller.js` uses them as the keys of its `KEYMAP` table.
  ***
- **div** (HTML): a generic box with no meaning of its own, the opposite of semantic. It groups things or gives CSS and JavaScript something to find.
- **table, tr, td** (HTML): a table, a row in it (*table row*), and a cell in a row (*table data*). Here 8 `<tr>` of 16 `<td>` each make the grid.
  ***
- **Object.freeze** (JS): a function built into JavaScript that locks an object: afterwards its fields cannot be changed, added or deleted, and it cannot be unfrozen. It is shallow (an object stored in a field stays changeable) and does not stop the variable from being pointed at another object; declaring it with `const` does that. In a module (a file loaded with `import` or `<script type="module">`), which always runs in *strict mode*, the mode that turns silent failures into errors, a write to a frozen object throws a `TypeError`; in a classic script without `"use strict"` the same write silently does nothing.
  ***
- **signal** (Preact): a box holding one value. Code that reads `.value` inside a `computed` or `effect` is subscribed to it; writing a *different* value to `.value` notifies the subscribers. Writing the same value notifies nobody.
- **computed** (Preact): a read-only signal whose value is a function of other signals. `model.js` hands out `computed` wrappers around `row` and `col`, so code outside the model can read them but not write them.
- **effect** (Preact): a function that runs immediately, then again whenever a signal it read on its last run changes.
  ***
- **html** (lit-html): a tag written in front of a backtick string, a *tagged template literal* (see the `view.js` walkthrough). It returns a description of the DOM and does not touch the page.
- **container** (lit-html): the element that `render` draws into, here `<div id="app-singleton">` or `<div id="app-factory">`. The rest of the page is untouched.
- **render** (lit-html): writes that description into a container. On later calls it reuses the DOM it built and goes slot by slot (each `${…}`, walking into nested templates and arrays), updating only the slots whose value changed.

</details>

### One tick, step by step

<details>
<summary>Key press, tick, write, redraw, hex packing</summary>
<br>

Both apps run this same sequence, each with its own controller, model and tick.

1. **Key press.** The browser calls `controller.keydown` (the controller's method, registered in `main.js`), which stores the command in the controller's `pending` latch. The browser pushes events rather than waiting to be polled, so the key waits in `pending` until the next tick reads it. If two keys arrive within one tick, the last one wins.
2. **Tick.** Every 150 ms (about 6.7 steps per second) `setInterval` calls `model.update(controller.read())`; `read` returns `pending` and clears it. `update` remembers the last real command in a plain variable `cmd`, so the dot keeps moving with no key held. `cmd` is not a signal because nothing on screen shows it. Edges wrap: from column 15, RIGHT goes to column 0.
3. **Write.** `update` writes a new value to `col` or `row`. After Space, it writes nothing, so nothing re-renders.
4. **Redraw.** On its last run the effect in `main.js` read `row`, `col` and `hex` (through `viewUpdate`), so it re-runs `viewUpdate(model, container)`. Its `template(m)` rebuilds the whole description: 128 cells. `render` then changes only what differs, which for one step is the `class` of two `<td>` cells and the `<output>` text. The saving is in DOM work, not in JavaScript work.

The readout packs the position into one byte: `hex = (row << 4) | col`. Column 0–15 fills the low 4 bits and row 0–7 the next 3, so the range is `00`–`7F`. Example: the start position, row 4 and column 7, gives `(4 << 4) | 7 = 0x40 | 0x07 = 0x47`, shown as `47`.

</details>

## Code walkthrough

Each file in full, cut into short parts, each part followed by its notes. The shared files come first, then the singleton version, then the factory version, whose notes explain only what differs. The notes cover the HTML, CSS and JavaScript as well as the two libraries, so knowing C is enough to follow them. Each file's notes open with the library names it uses, tagged (Preact) or (lit-html), and those names are bold where the notes explain them; everything else is plain HTML, CSS or JavaScript. [How it works](#how-it-works) defines the terms.

### `index.html`

<details>
<summary>Page tree, import map, CSS rules, two containers, two module scripts</summary>
<br>

Library names: none. The import map only tells the browser where the two libraries live.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dot runner</title>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
```

- `<!doctype html>` asks for standard rendering instead of a legacy compatibility mode.
- `<html lang="en">` opens the root element. `lang="en"` is an attribute, a `name="value"` setting written inside a tag. It marks the page's text as English, so screen readers use English pronunciation and browsers know the language when they offer to translate.
- Tags nest into a tree that the browser parses into the DOM: `<html>` holds `<head>` (setup, never drawn) and `<body>` (what you see, in the last part). `<meta charset="utf-8">` says how to decode the file's bytes into text, and `<title>` names the browser tab.
- `<script type="importmap">` is the import map from [How it works](#how-it-works). Its paths are relative to the page, so `./vendor/lit-html.js` means `http://localhost:8000/vendor/lit-html.js`. It must come before the module scripts: browsers apply the map only to imports resolved after they have read it.

```html
  <style>
    body { background: #333; color: #eee; }
    .matrix { border-collapse: collapse; background: #111; }
    .matrix td { width: 20px; height: 20px; border: 1px solid #333; }
    .matrix td.on { background: #f33; }
    output { font: 2em monospace; }
  </style>
```

- `<style>` holds CSS rules of the form `selector { property: value; }`. The selector picks the elements a rule applies to.
- `body` is the `<body>` element: dark gray background, light gray text. Colors are hex RGB, and three digits are shorthand for six: `#f33` means `#ff3333` (red 255, green 51, blue 51).
- `.matrix` is any element with `class="matrix"`, here the table. `border-collapse: collapse` makes neighboring cells share one border line instead of each drawing its own with a gap between.
- `.matrix td` is every `<td>` inside it: 20 × 20 px, with a 1 px border in the page's color, so the grid lines look like gaps.
- `.matrix td.on` is a cell that also has class `on`. This rule alone makes the dot red: the view never sets a color, it only puts `on` in one cell's class. Looks live in CSS, structure in the template.
- `output` is the hex readout: a fixed-width font at `2em`. With the family given only as `monospace`, browsers start from their monospace default, 13 px in Chrome, so this comes out at 26 px rather than twice the 16 px body text.

```html
</head>
<body>
  <p>Arrow keys move, Space stops.</p>
  <h2>singleton</h2>
  <div id="app-singleton"></div>
  <h2>factory</h2>
  <div id="app-factory"></div>
  <script type="module" src="./singleton/main.js"></script>
  <script type="module" src="./factory/main.js"></script>
</body>
</html>
```

- `<p>` is a paragraph of text: the instruction line. `<h2>` is a second-level heading, here the label above each app.
- `<div id="app-singleton">` and `<div id="app-factory">` are empty `<div>`s, the two containers. `id` gives an element a name unique in the page, and `#app-singleton` is the CSS selector for it. JavaScript draws one app into each box.
- `<script type="module" src="./singleton/main.js">` loads `singleton/main.js` as a module: a file with its own scope, which shares only the names it `export`s and gets other files' names with `import`. That is close to a C file where everything is `static` except what it exports, but there is no linker: the browser fetches each imported file by URL while loading. A module script also waits until the whole page is parsed, so the containers exist by the time it runs. Each of the two scripts starts one app; its imports pull in that version's `model.js` and `controller.js`, the shared `view.js` and `model-controller-common.js`, and the libraries.

</details>

### `model-controller-common.js`

<details>
<summary>The command table, shared by model and controller</summary>
<br>

Library names: none.

```js
// The message from controller to model, shared by those two only, like the C `command` enum.
export const Cmd = Object.freeze({ NONE: 0, STOP: 1, LEFT: 2, RIGHT: 3, UP: 4, DOWN: 5 });
```

- `//` starts a comment that runs to the end of the line, as in C. This file holds only what the model and the controller both need: the commands, the message one sends to the other. Your C code marks its `command` enum the same way, as the MODEL-CONTROLLER message. The view never imports it.
- `export const Cmd` makes `Cmd` visible to other modules. `const` declares a name that cannot be reassigned, like `T * const p` in C: when the value is an object, the name always refers to that object, but the object itself could still be changed, unless it is frozen as `Cmd` is.
- `Object.freeze({ NONE: 0, … })` stands in for a C `enum`, which JavaScript lacks. `{ NONE: 0, … }` is an object literal: a table of named fields, each with a value. It is frozen (see [Terms](#terms)), so `Cmd.UP = 9` throws a `TypeError`. The numbers only need to be distinct.

</details>

### `view.js`

<details>
<summary>Imports, range helper, tagged templates, rows and cells, class slot, hex text, viewUpdate</summary>
<br>

Library names: **`html`** and **`render`** (lit-html), **`.value`** (Preact). Inside an **`html`** template, each `${…}` is a slot that lit-html fills.

```js
import { html, render } from 'lit-html';
```

- `import { html, render } from 'lit-html'` takes two exported names from a module. A bare name like `lit-html` goes through the import map to a file in `vendor/`. **`html`** is lit-html's template tag and **`render`** writes a template into the page; both are explained below. This is the only file that imports lit-html, and it imports nothing from either version: even the grid size comes from the model it is given.
- lit-html 3.3.3 exports more than `html` and `render`: **`svg`** and **`mathml`**, template tags like `html` for SVG graphics and MathML math markup; **`nothing`**, a value that renders as empty; and **`noChange`**, a value that leaves a slot as it was, used mostly when writing directives (add-ons that control how a slot updates). It also exports `_$LH`, which is internal to Lit's own packages. The [Templates API page](https://lit.dev/docs/api/templates/) documents `html`, `svg`, `render` and `nothing`; the [lit-html 3.3.3 declaration file](https://cdn.jsdelivr.net/npm/lit-html@3.3.3/lit-html.d.ts) lists every export, types included. lit.dev writes imports as `from 'lit'`; the `lit` package re-exports `lit-html`, so the names are the same. Ready-made directives such as `repeat` live in separate `lit-html/directives/…` files, which this project has not vendored.

```js
const range = n => [...Array(n).keys()];
```

- `const range = n => [...Array(n).keys()]` returns `[0, 1, …, n−1]`. `n => …` is an arrow function: an unnamed function, here taking `n` and returning the array. `Array(n)` makes an array of `n` empty places, `.keys()` walks its indexes, and `[...]` collects them into a new array. Example: `range(3)` is `[0, 1, 2]`.

```js
const template = m => html`
  <table class="matrix">
    ${range(m.height).map(r => html`<tr>
      ${range(m.width).map(c => html`<td class=${r === m.row.value && c === m.col.value ? 'on' : ''}></td>`)}
    </tr>`)}
  </table>
  <output>${m.hex.value.toString(16).toUpperCase().padStart(2, '0')}</output>`;
```

- `` const template = m => html`…` `` is a function from the model to a description of the page. It reads signals and writes none. It is not exported: other files draw through `viewUpdate` below.
- `` html`…` `` is a tagged template literal. A template literal is a string in backticks where `${expr}` inserts the value of any JavaScript expression. With a function name in front, the tag, JavaScript builds no string: it calls the function with the fixed text pieces and the `${…}` values separately. **`html`** keeps the pieces as the template and each value as a slot. The pieces array is the same object each time a given template in the source runs, which is how **`render`** (below) recognizes the last frame's template and fills its slots instead of rebuilding it.
- `` range(m.height).map(r => html`<tr>…</tr>`) ``: `.map` calls the function on each element and returns a new array of the results, here `m.height` row templates of `m.width` cell templates each, 8 × 16 with the model's numbers. An array in a slot renders its items in order, matched to the last frame's items by position. The counts never change, so every cell is reused.
- `class=${r === m.row.value && c === m.col.value ? 'on' : ''}` is an attribute slot: it sets the cell's `class` to `on` or to an empty string, and the `.matrix td.on` rule in `index.html` paints it red. `===` is strict equality, and `? :` is the same as in C. These **`.value`** reads are what subscribe the effect in each `main.js`, because `viewUpdate` runs inside it.
- `<output>${m.hex.value.toString(16).toUpperCase().padStart(2, '0')}</output>`: `<output>` is the semantic element for a computed result. The chain does what `printf("%02X", hex)` does in C: base-16 text, upper case, padded to two characters with `0`. Example: row 0, column 10 gives 10 → `a` → `A` → `0A`.

```js
export function viewUpdate(m, container) {   // view_update()
  render(template(m), container);
}
```

- `export function viewUpdate(m, container)` draws the model into `container` once and returns: **`render`** writes `template(m)` there, and on later calls changes only what differs from the last frame. It is the only name other files see, so lit-html stays a detail of this file. Redrawing on every change is not its job: each `main.js` calls it inside an `effect`.
- Both versions share this one view. It never imports a model; it only reads `m.width`, `m.height`, `m.row`, `m.col` and `m.hex` from whatever it is given, and both models have those five fields.

</details>

### `singleton/model.js`

<details>
<summary>Imports, file-level state, the one model, update, wrap-around math</summary>
<br>

Library names: **`signal`**, **`computed`** and **`.value`** (Preact).

```js
import { signal, computed } from '@preact/signals-core';
import { Cmd } from '../model-controller-common.js';
```

- `import { signal, computed } from '@preact/signals-core'` takes Preact's two building blocks, by bare name as in `view.js`. The model is built from these alone. Nothing in this file touches the page.
- `'../model-controller-common.js'` is a relative path, which starts with `./` (this file's folder) or `../` (the folder above). Here it is the shared file at the root, which provides `Cmd`.
- @preact/signals-core 1.14.5 exports more: **`effect`** (used in each `main.js`); **`batch`**, which groups several writes so that effects run once, at the end; **`untracked`**, which reads signals without subscribing; **`action`**, which wraps a function so that each call runs batched and untracked; and **`createModel`**, a helper for building models out of signals. That last one is unrelated to `factory/model.js`'s own `createModel`, a plain function of the same name. It also exports the classes `Signal`, `Computed` and `Effect`, which `signal()`, `computed()` and `effect()` create. The [signals-core 1.14.5 README](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#guide--api) documents all of the functions except `action`, which it mentions only under `createModel`.

```js
const WIDTH = 16, HEIGHT = 8;               // grid size, owned by the model
const row = signal(4), col = signal(7);     // file-level, like static variables in C
let cmd = Cmd.STOP;                         // not shown on screen, so plain variable
```

- `const WIDTH = 16, HEIGHT = 8` is the grid size. Only the models define it, and the factory version repeats these two numbers on purpose. The view learns them from the model it is given, through `width` and `height` below.
- `const row = signal(4), col = signal(7)` creates two **`signal`** boxes holding the start position. They sit at file level, outside any function, so they exist once, from the moment the file loads, like `static` variables in a C file. They are not exported, so nothing outside this file can reach them.
- `let cmd = Cmd.STOP` declares a variable that can be reassigned, here holding the last direction; [How it works](#how-it-works), step 2, explains why it is a plain variable and not a signal.

```js
export const model = {
  width: WIDTH, height: HEIGHT,             // the view draws whatever size the model says
  row: computed(() => row.value),           // read-only to outsiders: const model_t *
  col: computed(() => col.value),
  hex: computed(() => (row.value << 4) | col.value),
```

- `export const model = {` starts an object literal: the one model, built when the file loads. That is what makes this version a singleton: there is exactly one, and importing it is all `main.js` needs to do.
- `width: WIDTH, height: HEIGHT` are plain numbers that never change, there for the view to read, so the view draws whatever size the model says.
- `row: computed(() => row.value)` hands out a read-only **`computed`** view of `row`. A computed has a getter for **`.value`** but no setter, so `model.row.value = 3` throws a `TypeError`. It is like handing out a `const model_t *`, except that C rejects the write at compile time and JavaScript only at run time. A computed is also lazy and cached: it recalculates only when read after one of its inputs changed.
- `hex: computed(() => (row.value << 4) | col.value)` packs the position into one byte ([How it works](#how-it-works) has the worked example). Ordinary JavaScript numbers are 64-bit floats, but `<<` and `|` convert to 32-bit integers first, so the result matches C for these small values.

```js
  update(c) {                               // model_update()
    if (c !== Cmd.NONE) cmd = c;
    switch (cmd) {
      case Cmd.LEFT:  col.value = (col.value + WIDTH - 1) % WIDTH; break;
      case Cmd.RIGHT: col.value = (col.value + 1) % WIDTH;         break;
      case Cmd.UP:    row.value = (row.value + HEIGHT - 1) % HEIGHT; break;
      case Cmd.DOWN:  row.value = (row.value + 1) % HEIGHT;        break;
    }
  },
};
```

- `update(c) { … }` is the model's one entry point for change, called by the tick in `main.js` as `model.update(controller.read())`; `c` is the new command, or `Cmd.NONE` if no key came this tick. **The syntax is shorthand for `update: function (c) { … }`**, a field whose value is a function, much like a function pointer in a C struct. It uses `row`, `col` and `cmd` straight from the file level, the way a C function uses its file's `static` variables, and it is the only code that writes them.
- `if (c !== Cmd.NONE) cmd = c`: `!==` compares without converting types. Loose `!=` converts first, so `'1' != 1` is `false`; the strict form avoids such surprises.
- `switch (cmd)` works as in C, `break` included, and a value that matches no `case` does nothing, also as in C.
- STOP has no `case`, on purpose. Space puts `Cmd.STOP` in the controller's `pending` latch. On the next tick `update(Cmd.STOP)` stores it in `cmd`, since it is not `NONE`. The `switch` then finds no match, so `update` writes neither signal: the effect in `main.js` is not notified and the page is not redrawn. On the ticks after that `c` is `NONE`, so `cmd` stays `STOP` and the dot stays put until an arrow key replaces it.
- `(col.value + WIDTH - 1) % WIDTH` steps left with wrap-around. JavaScript's `%` takes the sign of the left operand, as in C99, so a plain `(0 - 1) % 16` gives `-1`, not 15. Adding `WIDTH` first keeps the left side non-negative: `(0 + 16 - 1) % 16 = 15`, and `(5 + 16 - 1) % 16 = 4`. Writing a new number to **`.value`** is what notifies the effect in `main.js`.
- The last two lines close `update` and the model object.

</details>

### `singleton/controller.js`

<details>
<summary>Command import, key table, file-level latch, keydown, read</summary>
<br>

Library names: none.

```js
import { Cmd } from '../model-controller-common.js';
```

- The commands are the message from the controller to the model, so they are defined once, in `model-controller-common.js`, which the two share, and imported here.

```js
const KEYMAP = Object.freeze({ ArrowUp: Cmd.UP, ArrowDown: Cmd.DOWN, ArrowLeft: Cmd.LEFT,
                               ArrowRight: Cmd.RIGHT, ' ': Cmd.STOP });
```

- `const KEYMAP = Object.freeze({ ArrowUp: Cmd.UP, … })` is a table from key names to commands, looked up as `KEYMAP[e.key]`, and frozen like `Cmd` because it never changes. The keys are the names the browser gives keys; Space is `' '`.

```js
let pending = Cmd.NONE;                      // latched key, like KEYPAD bit 7
```

- `let pending = Cmd.NONE` is a one-slot mailbox from the keyboard to the timer; [How it works](#how-it-works), step 1, explains why a key waits here. Like the model's signals it sits at file level, like a C `static`, and it is not exported, so only this file's functions touch it.

```js
export const controller = {
  keydown(e) {                               // the keypad latching a key
    if (e.key in KEYMAP) { pending = KEYMAP[e.key]; e.preventDefault(); }
  },
```

- `export const controller = {` is the one controller, built when the file loads.
- `keydown(e)` is the method `main.js` hands to the browser for key presses. `e` is the key event object, and `e.key` names the key. It uses `pending` from the file level, so it still works when handed over on its own, detached from the object, as `controller.keydown`.
- `e.key in KEYMAP` is true when the table has that key. `e.preventDefault()` cancels the browser's own action for the key; arrows and Space would otherwise scroll the page. It runs only for mapped keys, so shortcuts such as F5 still work.

```js
  read() {                                   // controller_read(): the latched key, or NONE
    const c = pending;
    pending = Cmd.NONE;
    return c;
  },
};
```

- `read()` returns the latched command and empties the latch, so each key press reaches the model once; on a tick with no new key it returns `Cmd.NONE`. The tick in `main.js` calls it as `model.update(controller.read())`. The last line closes the object.
- The browser runs JavaScript on one thread, from a queue of events such as key presses and timer ticks, and each callback finishes before the next starts. So `keydown` and the tick never interrupt each other, and the read-then-clear in `read` needs no lock, `volatile` or disabled interrupts, unlike a variable shared with an interrupt handler.

</details>

### `singleton/main.js`

<details>
<summary>Imports, key listener, timer tick, redraw effect</summary>
<br>

Library names: **`effect`** (Preact).

```js
import { effect } from '@preact/signals-core';
```

- **`effect`** comes from Preact, imported by bare name. lit-html is not imported here: drawing is `view.js`'s business.

```js
import { model } from './model.js';
import { viewUpdate } from '../view.js';
import { controller } from './controller.js';
```

- `model` and `controller` are the ready-made objects from this folder, and `viewUpdate` comes from the shared `../view.js`. Importing them is all it takes: the parts already exist.

```js
window.addEventListener('keydown', controller.keydown);  // the browser calls it on each key press
```

- `window.addEventListener('keydown', controller.keydown)` asks the browser to call the controller's `keydown` on every key press, passing it the key event. The function is passed by name, the way C passes a function pointer. `main.js` makes every connection to the browser (key events, the timer, the page element); the other files use no browser globals and get the key event or the container handed to them.

```js
setInterval(() => {                          // the NMI tick
  model.update(controller.read());
}, 150);
```

- `setInterval(() => { … }, 150)` queues a tick every 150 ms. Each tick asks the controller for the latest key (`controller.read()`) and hands it to the model. The timer cannot preempt: if other code is running, the tick waits its turn. Browsers also slow timers in a hidden tab to at most once per second, so the dot crawls while you look at another tab.

```js
effect(() => viewUpdate(model, document.querySelector('#app-singleton')));  // redraw only on change
```

- `effect(() => viewUpdate(model, document.querySelector('#app-singleton')))` ties it together. **`effect`** runs its function once straight away, so `viewUpdate` draws the first frame into the element that `document.querySelector('#app-singleton')` finds with the CSS selector `#app-singleton`. While drawing, the view reads `row`, `col` and `hex`, so the effect is now subscribed to them. Later, a write such as `col.value = …` inside `update` re-runs the effect before the assignment completes, so the page is already redrawn when `update` returns.

</details>

### `factory/model.js`

<details>
<summary>What changes from the singleton: createModel, closure, one model per call</summary>
<br>

Library names: **`signal`**, **`computed`** and **`.value`** (Preact). Only what differs from `singleton/model.js` is explained here.

```js
import { signal, computed } from '@preact/signals-core';
import { Cmd } from '../model-controller-common.js';
```

- The same imports as `singleton/model.js`.

```js
const WIDTH = 16, HEIGHT = 8;               // grid size, owned by the model
```

- The same grid size as the singleton's, repeated on purpose. A constant may sit at file level even in this version: it never changes, so every model can share it.

```js
export function createModel() {
  const row = signal(4), col = signal(7);   // private, like fields of model_t
  let cmd = Cmd.STOP;                       // not shown on screen, so plain variable
  return {
    width: WIDTH, height: HEIGHT,           // the view draws whatever size the model says
    row: computed(() => row.value),         // read-only to outsiders: const model_t *
    col: computed(() => col.value),
    hex: computed(() => (row.value << 4) | col.value),
```

- `export function createModel()` is a factory: each call builds a fresh model and returns it. The singleton's file-level state (`row`, `col`, `cmd`) moved inside this function, so nothing is created until someone calls it, and every call creates a new set.
- `row`, `col` and `cmd` are now local to `createModel`, yet the functions created inside it keep using them after it returns. That is a closure: a function keeps access to the local variables of the function it was created in. Think of a struct that only these functions hold a pointer to, allocated afresh by each `createModel()` call; the garbage collector frees it once nothing refers to the model, so there is no `free`.
- `return {` hands back an object literal with the same fields as the singleton's `model`, `width` and `height` included, which is why the shared view works with either.

```js
    update(c) {                             // model_update()
      if (c !== Cmd.NONE) cmd = c;
      switch (cmd) {
        case Cmd.LEFT:  col.value = (col.value + WIDTH - 1) % WIDTH; break;
        case Cmd.RIGHT: col.value = (col.value + 1) % WIDTH;         break;
        case Cmd.UP:    row.value = (row.value + HEIGHT - 1) % HEIGHT; break;
        case Cmd.DOWN:  row.value = (row.value + 1) % HEIGHT;        break;
      }
    },
  };
}
```

- `update(c)` is the same code as the singleton's. What changed is where `row`, `col` and `cmd` come from: they are the names it uses but does not declare, found in `createModel` through the closure, so each model's `update` changes only its own signals. The last three lines close `update`, the returned object and `createModel`.

</details>

### `factory/controller.js`

<details>
<summary>What changes from the singleton: createController, one latch per controller</summary>
<br>

Library names: none. Only what differs from `singleton/controller.js` is explained here.

```js
import { Cmd } from '../model-controller-common.js';
```

- The same import as `singleton/controller.js`.

```js
const KEYMAP = Object.freeze({ ArrowUp: Cmd.UP, ArrowDown: Cmd.DOWN, ArrowLeft: Cmd.LEFT,
                               ArrowRight: Cmd.RIGHT, ' ': Cmd.STOP });
```

- The same frozen `KEYMAP`. It stays at file level: it never changes, so every controller can share it.

```js
export function createController() {
  let pending = Cmd.NONE;                    // latched key, like KEYPAD bit 7
  return {
```

- `export function createController()` is a factory, like `createModel`: the `pending` latch moved inside it, so each controller gets its own, and two controllers never share one.

```js
    keydown(e) {                             // the keypad latching a key
      if (e.key in KEYMAP) { pending = KEYMAP[e.key]; e.preventDefault(); }
    },
```

- `keydown(e)` is the same code as the singleton's. It now reaches `pending` through the closure, so it still works when handed to the browser on its own, as `controller.keydown`.

```js
    read() {                                 // controller_read(): the latched key, or NONE
      const c = pending;
      pending = Cmd.NONE;
      return c;
    },
  };
}
```

- `read()` is the same code as the singleton's. The last two lines close the controller object and `createController`.

</details>

### `factory/main.js`

<details>
<summary>What changes from the singleton: creating the model and the controller</summary>
<br>

Library names: **`effect`** (Preact). Only what differs from `singleton/main.js` is explained here.

```js
import { effect } from '@preact/signals-core';
```

- The same import as `singleton/main.js`.

```js
import { createModel } from './model.js';
import { viewUpdate } from '../view.js';
import { createController } from './controller.js';
```

- This version imports the factories, `createModel` and `createController`, instead of ready-made objects.

```js
const model = createModel();
const controller = createController();
```

- `const model = createModel()` and `const controller = createController()` are the real difference from `singleton/main.js`: here this file decides that there is one of each. A second pair of calls would give a second, independent app.

```js
window.addEventListener('keydown', controller.keydown);  // the browser calls it on each key press
```

- The same listener as `singleton/main.js`.

```js
setInterval(() => {                          // the NMI tick
  model.update(controller.read());
}, 150);
```

- The same tick as `singleton/main.js`.

```js
effect(() => viewUpdate(model, document.querySelector('#app-factory')));  // redraw only on change
```

- The same redraw effect as `singleton/main.js`, drawing into `#app-factory` instead.

</details>

## Claude Code setup

<details>
<summary>Settings, the /wrapup skill, project instructions, handoff file</summary>
<br>

| File | Purpose |
|------|---------|
| `.claude/CLAUDE.md` | Project instructions Claude Code loads every session: code principles, explanation style, conventions, environment. |
| `.claude/settings.json` | Claude Code settings (`model: opus`, `effortLevel: xhigh`), a permission allowlist, a `SessionStart` hook that prints `.claude/PROGRESS.md` into context, a `PostToolUse` hook that runs `.checks/boundaries.py` after every edit, and a `Stop` hook that runs it again before Claude Code may finish a turn. |
| `.claude/skills/wrapup/SKILL.md` | `/wrapup` rewrites `.claude/PROGRESS.md` as a handoff for the work since the previous one, then commits. It runs only when you type it. |
| `.claude/rules/markdown.md` | How to write README.md and docs/: which `##` sections fold. Claude Code loads it when working on those files. |
| `.claude/PROGRESS.md` | Latest session handoff, maintained by `/wrapup`; earlier ones: `git log -p --follow -- .claude/PROGRESS.md`. |
| `.checks/boundaries.py` | Checks the MVC boundaries in CLAUDE.md's Architecture rules: who may import what; browser globals and `effect` only in `main.js`; signal writes only in `model.js`; `model.update` and `viewUpdate` used only from `main.js`; file-level changing state only in `singleton/`. Run `uv run --no-project python .checks/boundaries.py`. The `PostToolUse` hook runs it after every Edit or Write and tells Claude Code what it broke; it can't undo the edit, and shell edits skip it. |
| `.checks/stop-hook.sh` | The `Stop` hook: runs the same check when Claude Code tries to finish a turn and, on a violation, sends it back to fix the code first. If the violation survives one round, it lets the turn end but shows you a warning, so it can't loop forever. |
| `.gitignore` | OS cruft, Python/uv venv, editor files. |
| `.gitattributes` | LF line endings; binary file types; no line diffs for the minified `vendor/` and `.readme-vendor/` files. |

Personal overrides go in `.claude/settings.local.json`, which is gitignored ([settings docs](https://code.claude.com/docs/en/settings)).

</details>

## Development setup (Debian 13)

<details>
<summary>Base packages, uv, more tools, Python, Docker multi-arch</summary>
<br>

`docker` is assumed installed. Base toolchain:

```bash
sudo apt install -y git gh python3 python3-dev build-essential curl jq wget time
```

`python3-dev` and `build-essential` are only needed for Python packages built from source.

`uv` is not packaged for Debian; install it with the standalone installer (needs `curl` from above; [official instructions](https://docs.astral.sh/uv/getting-started/installation/)). It puts `uv` and `uvx` in `~/.local/bin`, which Debian's default `~/.profile` adds to `PATH` on next login:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify: `git --version && gh --version && curl --version && uv --version`.

**More tools.** `sudo` is passwordless, and Claude Code may install whatever a task needs:

```bash
sudo apt update && sudo apt install -y <package>
```

Use `apt` for system tools; keep Python packages in the project venv. Add any lasting dependency to the command above.

**Python.** Use `uv` for every venv and package install, not `pip` or `python3 -m venv` (Debian 13 also blocks system-wide `pip install`, PEP 668). One venv per project:

```bash
uv sync                                          # project with a pyproject.toml; add packages with: uv add <pkg>
uv venv && uv pip install -r requirements.txt    # project with only a requirements.txt
```

For a packaged CLI, `uv tool install .` avoids managing a venv by hand.

**Docker multi-arch (optional, one-time).** Cross-building `linux/amd64` + `linux/arm64` needs QEMU and a `docker-container` builder:

```bash
docker run --privileged --rm tonistiigi/binfmt --install all
docker buildx create --name multiarch --driver docker-container --bootstrap --use
```

On Apple Silicon with OrbStack, emulation is built in, so only the second line is needed.

**Not used.** `node`/`npm` (Python's `http.server` serves the page; see [Run](#run)) and the .NET SDK.

</details>
