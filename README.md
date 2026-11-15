# Dot runner

A small project for learning [Preact Signals](https://github.com/preactjs/signals) and [lit-html](https://lit.dev/docs/libraries/standalone-templates/). A red dot moves on a 16×8 grid in the last arrow direction you pressed, and a readout shows its position as one hex byte. There is no npm and no build step: the browser loads both libraries as ES modules straight from `vendor/`.

## Run

<details>
<summary>Start command, why a server, network exposure, README viewer</summary>
<br>

```bash
uv run --no-project python -m http.server 8000
```

Open <http://localhost:8000>. Arrow keys move the dot, Space stops it. Ctrl+C stops the server.

- **Why a server:** Chrome refuses to load ES modules (`<script type="module">`) from a `file://` page, so opening `index.html` directly gives an empty page.
- **Why `--no-project`:** uv skips looking for a `pyproject.toml` and creates no venv. It just runs Python's built-in file server.
- **Network exposure:** `http.server` listens on every network interface, so other machines on your network can browse this folder, `.git/` included. Add `--bind 127.0.0.1` to keep it to this machine.
- **README viewer:** <http://localhost:8000/README.html> shows this file rendered, with `[ expand all ]` and `[ collapse all ]` pinned at the top. It looks like VS Code's Markdown preview with the Dark 2026 theme (Light 2026 when your system is in light mode), using [marked](https://github.com/markedjs/marked), [highlight.js](https://highlightjs.org/) and VS Code's own preview stylesheets from `.readme-vendor/`. It needs the server too: a `file://` page cannot `fetch` README.md.

</details>

## How it works

### Files

<details>
<summary>Model, view, controller, main loop; what each file holds</summary>
<br>

The code is split the way an embedded C program often is: a model (state plus the rule that changes it), a view (draws the state), a controller (reads the keys), and a main loop that feeds the controller's input to the model on a timer. Comments in the code name the C counterpart of each piece (`model_t`, `model_update()`, `view_update()`, `controller_read()`).

| File | Role |
|------|------|
| `index.html` | Page shell: the import map, the grid's CSS, and the empty `#app` container. |
| `model.js` | State and update rule: `row` and `col` signals, a `hex` computed, `update(cmd)`. No DOM. |
| `view.js` | `view(m)`: a lit-html template for the 16×8 table and the hex readout. Reads signals, writes none. |
| `controller.js` | Input: `controllerKeydown(e)` latches a key in `pending`; `controllerRead()` hands the tick the latest key and clears it. |
| `main.js` | Wiring: `keydown` → `controllerKeydown`, a 150 ms timer → `m.update(controllerRead())`, `effect` → `render`. |
| `vendor/` | lit-html 3.3.3 (`lit-html.js`) and @preact/signals-core 1.14.5 (`dist/signals-core.mjs`), the published files used as-is. |

</details>

### Terms

<details>
<summary>semantic HTML, DOM, import map, arrow keys, div, table, Object.freeze, signal, computed, effect, html, container, render</summary>
<br>

- **semantic HTML**: choosing the element whose name says what the content is, such as `<p>` for a paragraph, `<table>` for rows and columns, or `<output>` for a computed result, rather than a generic box made to look right. Screen readers, search engines and browser features rely on that meaning; the look comes from CSS either way.
  ***
- **DOM** (browser): the tree of elements the browser builds from the HTML and draws on screen. JavaScript changes the page by changing this tree, and the browser redraws to match.
- **import map** (browser): a JSON block in the page that tells the browser which file a bare module name such as `lit-html` means. In an npm project a bundler does this job.
- **ArrowUp, ArrowDown, ArrowLeft, ArrowRight** (browser): the values the browser puts in a key event's `key` field when an arrow key is pressed. `controller.js` uses them as the keys of its `KEYMAP` table.
  ***
- **div** (HTML): a generic box with no meaning of its own, the opposite of semantic. It groups things or gives CSS and JavaScript something to find.
- **table, tr, td** (HTML): a table, a row in it (*table row*), and a cell in a row (*table data*). Here 8 `<tr>` of 16 `<td>` each make the grid.
  ***
- **Object.freeze** (JS): a function built into JavaScript that locks an object: afterwards its fields cannot be changed, added or deleted, and it cannot be unfrozen. It is shallow (an object stored in a field stays changeable) and does not fix the variable name, which is `const`'s job. In a module, which always runs in *strict mode*, a write to a frozen object throws a `TypeError`; in older non-module code the same write silently does nothing.
  ***
- **signal** (Preact): a box holding one value. Code that reads `.value` inside a `computed` or `effect` is subscribed to it; writing a *different* value to `.value` notifies the subscribers. Writing the same value notifies nobody.
- **computed** (Preact): a read-only signal whose value is a function of other signals. `model.js` hands out `computed` wrappers around `row` and `col`, so code outside the model can read them but not write them.
- **effect** (Preact): a function that runs immediately, then again whenever a signal it read on its last run changes.
  ***
- **html** (lit-html): a tagged template literal. It returns a description of the DOM and does not touch the page.
- **container** (lit-html): the element that `render` draws into, here `<div id="app">`. The rest of the page is untouched.
- **render** (lit-html): writes that description into a container. On later calls it reuses the DOM it built and goes slot by slot (each `${…}`, walking into nested templates and arrays), updating only the slots whose value changed.

</details>

### One tick, step by step

<details>
<summary>Key press, tick, write, redraw, hex packing</summary>
<br>

1. **Key press.** The browser calls `controllerKeydown` (in `controller.js`, registered in `main.js`), which stores the command in `pending`. The browser pushes events rather than waiting to be polled, so the key waits in `pending` until the next tick reads it. If two keys arrive within one tick, the last one wins.
2. **Tick.** Every 150 ms (about 6.7 steps per second) `setInterval` calls `m.update(controllerRead())`; `controllerRead` returns `pending` and clears it. `update` remembers the last real command in a plain variable `cmd`, so the dot keeps moving with no key held. `cmd` is not a signal because nothing on screen shows it. Edges wrap: from column 15, RIGHT goes to column 0.
3. **Write.** `update` writes a new value to `col` or `row`. After Space, it writes nothing, so nothing re-renders.
4. **Redraw.** On its last run the effect in `main.js` read `row`, `col` and `hex` (through `view`), so it re-runs `render(view(m), #app)`. `view(m)` rebuilds the whole description: 128 cells. `render` then changes only what differs, which for one step is the `class` of two `<td>` cells and the `<output>` text. The saving is in DOM work, not in JavaScript work.

The readout packs the position into one byte: `hex = (row << 4) | col`. Column 0–15 fills the low 4 bits and row 0–7 the next 3, so the range is `00`–`7F`. Example: the start position, row 4 and column 7, gives `(4 << 4) | 7 = 0x40 | 0x07 = 0x47`, shown as `47`.

</details>

## Code walkthrough

Each file in full, cut into short parts, each part followed by its notes. The notes cover the HTML, CSS and JavaScript as well as the two libraries, so knowing C is enough to follow them. Each file's notes open with the library names it uses, tagged (Preact) or (lit-html), and those names are bold wherever they appear; everything else is plain HTML, CSS or JavaScript. [How it works](#how-it-works) defines the terms.

### `index.html`

<details>
<summary>Page tree, import map, CSS rules, module script</summary>
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
- `<script type="importmap">` is the import map from [How it works](#how-it-works). Its paths are relative to the page, so `./vendor/lit-html.js` means `http://localhost:8000/vendor/lit-html.js`. It must come before the module script: browsers apply the map only to imports resolved after they have read it.

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
- `output` is the hex readout: a fixed-width font at `2em`, twice the surrounding text size (32 px at the usual 16 px default).

```html
</head>
<body>
  <p>Arrow keys move, Space stops.</p>
  <div id="app"></div>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

- `<p>` is a paragraph of text: the instruction line.
- `<div id="app">` is an empty `<div>`, the container. `id` gives an element a name unique in the page, and `#app` is the CSS selector for it. JavaScript draws everything under the instruction line into this box.
- `<script type="module" src="./main.js">` loads `main.js` as a module: a file with its own scope, which shares only the names it `export`s and gets other files' names with `import`. That is close to a C file where everything is `static` except what it exports, but there is no linker: the browser fetches each imported file by URL while loading. A module script also waits until the whole page is parsed, so `#app` exists by the time `main.js` runs. The imports in `main.js` pull in `model.js`, `view.js`, `controller.js` and both libraries.

</details>

### `model.js`

<details>
<summary>Imports, command table, private signals, read-only computeds, update, wrap-around math</summary>
<br>

Library names: **`signal`**, **`computed`** and **`.value`** (Preact).

```js
import { signal, computed } from '@preact/signals-core';
```

- `import { signal, computed } from '@preact/signals-core'` takes two exported names from a module. A bare name like `@preact/signals-core` goes through the import map to a file in `vendor/`.
- The model is built from these two Preact functions alone. Nothing in this file touches the page.
- @preact/signals-core 1.14.5 exports more: **`effect`** (used in `main.js`); **`batch`**, which groups several writes so that effects run once, at the end; **`untracked`**, which reads signals without subscribing; **`action`**, which wraps a function so that each call runs batched and untracked; and **`createModel`**, a helper for building models out of signals. That last one is unrelated to this project's own `createModel`, a plain function of the same name. It also exports the classes `Signal`, `Computed` and `Effect`, which `signal()`, `computed()` and `effect()` create. The [signals-core 1.14.5 README](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#guide--api) documents all of the functions except `action`, which it mentions only under `createModel`.

```js
export const WIDTH = 16, HEIGHT = 8;
export const Cmd = Object.freeze({ NONE: 0, STOP: 1, LEFT: 2, RIGHT: 3, UP: 4, DOWN: 5 });
```

- `export const WIDTH = 16, HEIGHT = 8` makes the grid size visible to other modules. `view.js` imports it, so the size is set in one place. `const` declares a name that cannot be reassigned, like `T * const p` in C: when the value is an object, the name always refers to that object, but the object itself could still be changed, unless it is frozen like `Cmd` below.
- `Cmd = Object.freeze({ NONE: 0, … })` stands in for a C `enum`, which JavaScript lacks. `{ NONE: 0, … }` is an object literal: a table of named fields, each with a value. It is frozen (see [Terms](#terms)), so `Cmd.UP = 9` throws a `TypeError`. The numbers only need to be distinct.

```js
export function createModel() {
  const row = signal(4), col = signal(7);   // private, like fields of model_t
  let cmd = Cmd.STOP;                       // not shown on screen, so plain variable
  return {
    row: computed(() => row.value),         // read-only to outsiders: const model_t *
    col: computed(() => col.value),
    hex: computed(() => (row.value << 4) | col.value),
```

- `export function createModel()` is a factory: each call builds a fresh model and returns it.
- `const row = signal(4), col = signal(7)` creates two **`signal`** boxes holding the start position. They are local to `createModel`, yet the functions created inside it keep using them after it returns. That is a closure: a function keeps access to the local variables of the function it was created in. Nothing else can reach `row` and `col`, so they are private. Think of a struct that only these functions hold a pointer to, allocated afresh by each `createModel()` call; the garbage collector frees it once nothing refers to the model, so there is no `free`.
- `let cmd = Cmd.STOP` declares a variable that can be reassigned, here holding the last direction; [How it works](#how-it-works), step 2, explains why it is a plain variable and not a signal.
- `return {` starts an object literal, the model handed back to the caller: three read-only fields here and `update` in the next part.
- `row: computed(() => row.value)` hands out a read-only **`computed`** view of `row`. `() => row.value` is an arrow function: an unnamed function, here taking no arguments and returning `row.value`. A computed has a getter for **`.value`** but no setter, so `m.row.value = 3` throws a `TypeError`. It is like returning a `const model_t *`, except that C rejects the write at compile time and JavaScript only at run time. A computed is also lazy and cached: it recalculates only when read after one of its inputs changed.
- `hex: computed(() => (row.value << 4) | col.value)` packs the position into one byte ([How it works](#how-it-works) has the worked example). JavaScript has one number type, a 64-bit float, but `<<` and `|` convert to 32-bit integers first, so the result matches C for these small values.

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

- `update(c) { … }` is the model's one entry point for change, called by the tick in `main.js` as `m.update(controllerRead())`; `c` is the new command, or `Cmd.NONE` if no key came this tick. **The syntax is shorthand for `update: function (c) { … }`**, a field whose value is a function, much like a function pointer in a C struct. The difference: this function carries the variables it closed over, the names it uses but does not declare, found in `createModel`: `row`, `col` and `cmd`. So it needs no context argument, and it is the only code that writes them.
- `if (c !== Cmd.NONE) cmd = c`: `!==` compares without converting types. Loose `!=` converts first, so `'1' != 1` is `false`; the strict form avoids such surprises.
- `switch (cmd)` works as in C, `break` included, and a value that matches no `case` does nothing, also as in C.
- STOP has no `case`, on purpose. Space puts `Cmd.STOP` in `pending`. On the next tick `update(Cmd.STOP)` stores it in `cmd`, since it is not `NONE`. The `switch` then finds no match, so `update` writes neither signal: the effect in `main.js` is not notified and the page is not redrawn. On the ticks after that `c` is `NONE`, so `cmd` stays `STOP` and the dot stays put until an arrow key replaces it.
- `(col.value + WIDTH - 1) % WIDTH` steps left with wrap-around. JavaScript's `%` takes the sign of the left operand, as in C99, so a plain `(0 - 1) % 16` gives `-1`, not 15. Adding `WIDTH` first keeps the left side non-negative: `(0 + 16 - 1) % 16 = 15`, and `(5 + 16 - 1) % 16 = 4`. Writing a new number to **`.value`** is what notifies the effect in `main.js`.
- The last three lines close `update`, the returned object and `createModel`.

</details>

### `view.js`

<details>
<summary>Imports, range helper, tagged templates, rows and cells, class slot, hex text</summary>
<br>

Library names: **`html`** (lit-html), **`.value`** (Preact). Inside an **`html`** template, each `${…}` is a slot that lit-html fills.

```js
import { html } from 'lit-html';
import { WIDTH, HEIGHT } from './model.js';
```

- **`html`** is lit-html's template tag, explained below. `WIDTH` and `HEIGHT` come from `./model.js`: a path starting with `./` is relative to this file.
- lit-html 3.3.3 exports more: **`render`** (used in `main.js`); **`svg`** and **`mathml`**, template tags like `html` for SVG graphics and MathML math markup; **`nothing`**, a value that renders as empty; and **`noChange`**, a value that leaves a slot as it was, used mostly when writing directives (add-ons that control how a slot updates). It also exports `_$LH`, which is internal to Lit's own packages. The [Templates API page](https://lit.dev/docs/api/templates/) documents `html`, `svg`, `render` and `nothing`; the [lit-html 3.3.3 declaration file](https://cdn.jsdelivr.net/npm/lit-html@3.3.3/lit-html.d.ts) lists every export, types included. lit.dev writes imports as `from 'lit'`; the `lit` package re-exports `lit-html`, so the names are the same. Ready-made directives such as `repeat` live in separate `lit-html/directives/…` files, which this project has not vendored.

```js
const range = n => [...Array(n).keys()];
```

- `const range = n => [...Array(n).keys()]` returns `[0, 1, …, n−1]`. `Array(n)` makes an array of `n` empty places, `.keys()` walks its indexes, and `[...]` collects them into a new array. Example: `range(3)` is `[0, 1, 2]`.

```js
export const view = m => html`
  <table class="matrix">
    ${range(HEIGHT).map(r => html`<tr>
      ${range(WIDTH).map(c => html`<td class=${r === m.row.value && c === m.col.value ? 'on' : ''}></td>`)}
    </tr>`)}
  </table>
  <output>${m.hex.value.toString(16).toUpperCase().padStart(2, '0')}</output>`;
```

- `` export const view = m => html`…` `` is a function from the model to a description of the page. It reads signals and writes none.
- `` html`…` `` is a tagged template literal. A template literal is a string in backticks where `${expr}` inserts the value of any JavaScript expression. With a function name in front, the tag, JavaScript builds no string: it calls the function with the fixed text pieces and the `${…}` values separately. **`html`** keeps the pieces as the template and each value as a slot. The pieces array is the same object each time a given template in the source runs, which is how **`render`** in `main.js` recognizes the last frame's template and fills its slots instead of rebuilding it.
- `` range(HEIGHT).map(r => html`<tr>…</tr>`) ``: `.map` calls the function on each element and returns a new array of the results, here 8 row templates of 16 cell templates each. An array in a slot renders its items in order, matched to the last frame's items by position. The counts never change, so every cell is reused.
- `class=${r === m.row.value && c === m.col.value ? 'on' : ''}` is an attribute slot: it sets the cell's `class` to `on` or to nothing, and the `.matrix td.on` rule in `index.html` paints it red. `===` is strict equality, and `? :` is the same as in C. These **`.value`** reads are what subscribe the effect in `main.js`.
- `<output>${m.hex.value.toString(16).toUpperCase().padStart(2, '0')}</output>`: `<output>` is the semantic element for a computed result. The chain does what `printf("%02X", hex)` does in C: base-16 text, upper case, padded to two characters with `0`. Example: row 0, column 10 gives 10 → `a` → `A` → `0A`.

</details>

### `controller.js`

<details>
<summary>Command import, key table, pending key, controllerKeydown, controllerRead</summary>
<br>

Library names: none.

```js
import { Cmd } from './model.js';
```

- The commands are the message from the controller to the model, so they are defined once, in `model.js`, and imported here.

```js
const KEYMAP = { ArrowUp: Cmd.UP, ArrowDown: Cmd.DOWN, ArrowLeft: Cmd.LEFT,
                 ArrowRight: Cmd.RIGHT, ' ': Cmd.STOP };
```

- `const KEYMAP = { ArrowUp: Cmd.UP, … }` is a table from key names to commands, looked up as `KEYMAP[e.key]`. The keys are the names the browser gives keys; Space is `' '`.

```js
let pending = Cmd.NONE;                      // latched key, like KEYPAD bit 7
```

- `let pending = Cmd.NONE` is a one-slot mailbox from the keyboard to the timer; [How it works](#how-it-works), step 1, explains why a key waits here. It is not exported, so no other file can touch it, like a file-scope `static` in C.

```js
export function controllerKeydown(e) {       // the keypad latching a key
  if (e.key in KEYMAP) { pending = KEYMAP[e.key]; e.preventDefault(); }
}
```

- `export function controllerKeydown(e)` is the function `main.js` hands to the browser for key presses. `e` is the key event object, and `e.key` names the key.
- `e.key in KEYMAP` is true when the table has that key. `e.preventDefault()` cancels the browser's own action for the key; arrows and Space would otherwise scroll the page. It runs only for mapped keys, so shortcuts such as F5 still work.

```js
export function controllerRead() {           // controller_read(): the latched key, or NONE
  const c = pending;
  pending = Cmd.NONE;
  return c;
}
```

- `controllerRead()` returns the latched command and empties the latch, so each key press reaches the model once; on a tick with no new key it returns `Cmd.NONE`. The tick in `main.js` calls it as `m.update(controllerRead())`.
- The browser runs JavaScript on one thread, from a queue of events such as key presses and timer ticks, and each callback finishes before the next starts. So `controllerKeydown` and the tick never interrupt each other, and the read-then-clear in `controllerRead` needs no lock, `volatile` or disabled interrupts, unlike a variable shared with an interrupt handler.

</details>

### `main.js`

<details>
<summary>Imports, the model, key listener, timer tick, redraw effect</summary>
<br>

Library names: **`effect`** (Preact), **`render`** (lit-html).

```js
import { effect } from '@preact/signals-core';
import { render } from 'lit-html';
```

- **`effect`** and **`render`** come from the two libraries, imported by bare name as in `model.js` and `view.js`.

```js
import { createModel } from './model.js';
import { view } from './view.js';
import { controllerKeydown, controllerRead } from './controller.js';
```

- This project's own pieces, all covered above: `createModel` from `model.js`, `view` from `view.js`, and `controllerKeydown` and `controllerRead` from `controller.js`.

```js
const m = createModel();
```

- `const m = createModel()` builds the one model.

```js
window.addEventListener('keydown', controllerKeydown);  // the browser calls it on each key press
```

- `window.addEventListener('keydown', controllerKeydown)` asks the browser to call `controllerKeydown` on every key press, passing it the key event. The function is passed by name, the way C passes a function pointer. This file makes every connection to the browser (key events, the timer, drawing); the other files only define things.

```js
setInterval(() => {                          // the NMI tick
  m.update(controllerRead());
}, 150);
```

- `setInterval(() => { … }, 150)` queues a tick every 150 ms. Each tick asks the controller for the latest key and hands it to the model. The timer cannot preempt: if other code is running, the tick waits its turn. Browsers also slow timers in a hidden tab to at most once per second, so the dot crawls while you look at another tab.

```js
effect(() => render(view(m), document.querySelector('#app')));  // view_update(), only on change
```

- `effect(() => render(view(m), document.querySelector('#app')))` ties it together. **`effect`** runs its function once straight away, which draws the first frame. `view(m)` reads `row`, `col` and `hex`, so the effect is now subscribed to them. **`render`** writes the description into the element that `document.querySelector('#app')` finds with the CSS selector `#app`. Later, a write such as `col.value = …` inside `update` re-runs the effect before the assignment completes, so the page is already redrawn when `update` returns.

</details>

## Claude Code setup

<details>
<summary>Settings, the /wrapup skill, project instructions, handoff file</summary>
<br>

| File | Purpose |
|------|---------|
| `.claude/CLAUDE.md` | Project instructions Claude Code loads every session: code principles, explanation style, conventions, environment. |
| `.claude/settings.json` | Claude Code settings (`model: opus`, `effortLevel: xhigh`), a permission allowlist, and a `SessionStart` hook that prints `.claude/PROGRESS.md` into context. |
| `.claude/skills/wrapup/SKILL.md` | `/wrapup` rewrites `.claude/PROGRESS.md` as a handoff for the work since the previous one, then commits. It runs only when you type it. |
| `.claude/rules/markdown.md` | How to write README.md and docs/: which `##` sections fold. Claude Code loads it when working on those files. |
| `.claude/PROGRESS.md` | Latest session handoff, maintained by `/wrapup`; earlier ones: `git log -p --follow -- .claude/PROGRESS.md`. |
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
sudo apt install -y git gh python3 python3-dev build-essential curl jq wget
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
