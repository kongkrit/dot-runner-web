[README.md](README.md) · [STUDY_PLAN_1.md](STUDY_PLAN_1.md) · [STUDY_PLAN_2.md](STUDY_PLAN_2.md)

# How it works and code walkthrough

The companion to [README.md](README.md), which says what the app is and how to run it. This file explains how the app works, walks through every source file in full, compares the singleton, factory and class versions, and describes the Claude Code and Debian setup.

## How it works

### Files

<details>
<summary>Model, view, controller, main loop; what each file holds</summary>
<br>

The code is split the way an embedded C program often is: a model (state plus the rule that changes it), a view (draws the state), a controller (reads the keys), and a main loop that feeds the controller's input to the model on a timer. Comments in the code name the C counterpart of each piece (`model_t`, `model_update()`, `view_update()`, `controller_read()`). The app exists three times, in `singleton/`, `factory/` and `class/`. Each folder holds all five files under the same names and imports nothing from the others; only `vendor/` is shared.

| File | Role |
|------|------|
| `index.html` | Page shell: the import map, the Eruda console, the grid's CSS, the empty `#app-singleton`, `#app-factory` and `#app-class` containers, and one module script per version. |
| `singleton/model-controller-common.js` | The `Cmd` table: the message the controller sends to the model, shared by those two only, like the C `command` enum. |
| `singleton/model.js` | Grid size, state and update rule: `WIDTH`, `HEIGHT`, the `row` and `col` signals and `cmd` at file level, and the one `model` object with `width`, `height`, read-only `row`, `col` and `hex` computeds, and `update(c)`. No DOM. |
| `singleton/view.js` | `viewUpdate(m, container)`: renders a lit-html template of the model's grid (its `width` × `height`) and the hex readout into the container. Reads signals, writes none. |
| `singleton/controller.js` | Input: a file-level `pending` latch, and the one `controller` object with `keydown(e)`, which latches a key, and `read()`, which hands the tick the latest key and clears it. |
| `singleton/main.js` | Wiring: `keydown` → `controller.keydown`, a 150 ms timer → `model.update(controller.read())`, `effect` → `viewUpdate` into `#app-singleton`. |
| `factory/model-controller-common.js` | A byte-identical copy of `singleton/model-controller-common.js`, so the folders share no file. |
| `factory/model.js` | The same model built by `createModel()`, so each call gives a new, independent one. |
| `factory/view.js` | The same template, behind `createView(container)`: each view keeps the container it draws into, and `view.update(m)` draws. |
| `factory/controller.js` | The same controller built by `createController()`, each with its own latch. |
| `factory/main.js` | The same wiring, after creating one model, one view and one controller; draws into `#app-factory`. |
| `class/model-controller-common.js` | Another byte-identical copy of `singleton/model-controller-common.js`. |
| `class/model.js` | The same model as `class Model`: each `new Model()` gives a new, independent one, with its state in private `#` fields. |
| `class/view.js` | The same template, behind `class View`: `new View(container)` keeps the container in a private field, and `view.update(m)` draws. |
| `class/controller.js` | The same controller as `class Controller`, each with its own private `#pending` latch. |
| `class/main.js` | The same wiring, after creating one model, one view and one controller with `new`; wraps the key listener so that `keydown` keeps `this`; draws into `#app-class`. |
| `vendor/` | lit-html 3.3.3 (`lit-html.js`) and @preact/signals-core 1.14.5 (`signals-core.mjs`, the package's `dist/signals-core.mjs`), and Eruda 3.4.3 (`eruda.js`), an in-page console for debugging; the published files used as-is. |
| `C/` | The original bare-metal C program that the JavaScript ports, not loaded by the page: `dot_runner.c`, whose `model_t`, `model_update()`, `view_update()` and `controller_read()` the code comments name, and `baremetal_binary.h`, its `B8()` macro for binary literals. |

</details>

### Terms

<details open>
<summary>General, Browser, HTML, JS, Preact, lit-html</summary>
<br>

<details open>
<summary>General: semantic HTML, singleton, factory</summary>
<br>

- **semantic HTML**: choosing the element whose name says what the content is, such as `<p>` for a paragraph, `<table>` for rows and columns, or `<output>` for a computed result, rather than a generic box made to look right. Screen readers, search engines and browser features rely on that meaning; the look comes from CSS either way.
- **singleton**: a part that exists exactly once, built when its file loads, with its state in file-level variables, like `static` variables in a C file. Like a block hard-wired into a chip at a fixed address.
- **factory**: a function that builds and returns a new instance each time it is called, such as `createModel()`, so `main.js` decides how many there are. Like a Verilog module that the top level instantiates, each instance with its own flip-flops; unlike hardware, instances are made while the program runs and freed automatically when nothing uses them.

</details>

<details open>
<summary>Browser: DOM, querySelector, activeElement, addEventListener, import map, arrow keys</summary>
<br>

- **DOM**: the tree of elements the browser builds from the HTML and draws on screen. JavaScript changes the page by changing this tree, and the browser redraws to match.
- **querySelector** ([MDN](https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector), [W3Schools](https://www.w3schools.com/jsref/met_document_queryselector.asp)): `document.querySelector(selector)` returns the first element in the page that matches a CSS selector, or `null` if none does. `'#app-singleton'` matches the element with `id="app-singleton"`. Called on an element instead of `document`, it searches only inside that element. It returns the live element, not a copy: reading its fields reads the page, and writing them changes it. Each `main.js` uses it to find its app's container.
- **activeElement** ([MDN](https://developer.mozilla.org/en-US/docs/Web/API/Document/activeElement), [W3Schools](https://www.w3schools.com/jsref/prop_document_activeelement.asp)): `document.activeElement` is the element that has the keyboard focus, the one your key presses go to, such as the text box you are typing in. When nothing has it, it is `<body>`. Clicking into a text box, or pressing Tab, moves the focus. [STUDY_PLAN_1.md](STUDY_PLAN_1.md) uses it to leave a box alone while the user types in it.
- **addEventListener** ([MDN](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener), [W3Schools](https://www.w3schools.com/jsref/met_element_addeventlistener.asp)): `target.addEventListener('keydown', fn)` asks the browser to call `fn` each time that event happens on `target`, an element or `window` for the whole page. The browser passes `fn` an event object, `e`, that describes what happened, such as `e.key` for a key press. Your code never polls; it waits to be called, like an interrupt handler. Each `main.js` uses it for key presses; the [`class/` walkthrough](#class) shows how a method passed this way loses `this`.
- **import map**: a JSON block in the page that tells the browser which file a bare module name such as `lit-html` means. In an npm project a bundler does this job.
- **ArrowUp, ArrowDown, ArrowLeft, ArrowRight**: the values the browser puts in a key event's `key` field when an arrow key is pressed. `controller.js` uses them as the keys of its `KEYMAP` table.

</details>

<details open>
<summary>HTML: div, span, output, table, dl, dd, dt</summary>
<br>

- **div**: a generic box with no meaning of its own, the opposite of semantic. It groups things or gives CSS and JavaScript something to find. It is a *block* element: it starts on its own line, takes the full width, and may contain almost anything, tables included. The three app containers are `<div>`s.
- **span**: the *inline* counterpart of `div`, just as meaningless but flowing inside a line of text like a word. It may contain only text and other inline elements (`<b>`, `<code>`, `<output>`), never blocks such as `<div>` or `<table>`. Use a `div` to group blocks and a `span` to mark a few words or a value inside a line. lit-html's `render` can draw into either; the browser does not stop a `<table>` inside a `<span>`, but that is invalid HTML.
- **output** ([MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/output), [W3Schools](https://www.w3schools.com/tags/tag_output.asp)): an inline element, like `span`, that holds the result of a calculation or of something the user did. It is the semantic choice for such a value: it says "this text is computed" the way `<p>` says "this is a paragraph". Here it holds the hex readout. Browsers draw it like a `span`; its larger font comes from the `output` rule in `index.html`. Two things set it apart from a `span`. Many browsers treat it as a *live region* (an element whose changes a screen reader announces), so a blind user hears the new value without moving the keyboard focus to it. And it belongs to forms: an optional `for="a b"` attribute names, by `id`, the elements whose values went into the result. That only records the link; the browser computes nothing from it, and the output's value is not sent when a form is submitted. JavaScript writes it like any element, through `textContent` or, here, a lit-html slot.
- **table, tr, td** ([MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/table), [W3Schools](https://www.w3schools.com/tags/tag_table.asp)): a table, a row in it (*table row*), and a cell in a row (*table data*). Here 8 `<tr>` of 16 `<td>` each make the grid.
- **dl, dd, dt** ([MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dl), [W3Schools](https://www.w3schools.com/tags/tag_dl.asp)): a list of terms and their descriptions (*description list*), and one description in it (*description details*), which follows its term in a `<dt>` (*description term*). Browsers indent a `<dd>` by 40 px, and this file uses it only for that: in the [Code walkthrough](#code-walkthrough), a `<dl><dd>` around each folder's file folds indents them under the folder. A `<dd>` with no `<dt>` is invalid HTML, but browsers and GitHub draw it; it is used because GitHub strips `style` attributes, the usual way to indent.

</details>

<details open>
<summary>JS: => (arrow function), Object.freeze, closure, class, # (private member)</summary>
<br>

- **=> (arrow function)** ([MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions), [W3Schools](https://www.w3schools.com/js/js_arrow_function.asp)): a short way to write a function in place, often as an argument: the parameters go left of `=>`, the body right. `n => n + 1` takes `n` and returns `n + 1`; `() => …` takes nothing and `(a, b) => …` takes two. A body without braces is one expression, and its value is returned; a body in braces, as in `setInterval(() => { … }, 150)`, is a block of statements and returns a value only through `return`. It is written without a name; `const range = n => …` stores one in a variable so it can be called as `range(3)`. Unlike a function written with `function`, it has no `this` of its own and uses the `this` of the code around it, which is how `computed(() => this.#row.value)` in `class/model.js` reads its own model. C has no counterpart; the nearest is passing a pointer to a named function defined elsewhere, like `qsort`'s comparator.
- **Object.freeze**: a function built into JavaScript that locks an object: afterwards its fields cannot be changed, added or deleted, and it cannot be unfrozen. It is shallow (an object stored in a field stays changeable) and does not stop the variable from being pointed at another object; declaring it with `const` does that. In a module (a file loaded with `import` or `<script type="module">`), which always runs in *strict mode*, the mode that turns silent failures into errors, a write to a frozen object throws a `TypeError`; in a classic script without `"use strict"` the same write silently does nothing.
- **closure** ([MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures), [W3Schools](https://www.w3schools.com/js/js_function_closures.asp)): a function that keeps access to the local variables of the function it was created in, even after that outer function has returned. Think of a struct that only those inner functions hold a pointer to, allocated afresh each time the outer function runs; the garbage collector frees it once nothing refers to it, so there is no `free`. C has no closures. `factory/model.js` uses one so that each `createModel()` call gets its own private `row`, `col` and `cmd`.
- **class** ([MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_classes), [W3Schools](https://www.w3schools.com/js/js_classes.asp)): a blueprint for objects. `new Model()` builds an *instance* with its own fields; methods such as `update` are stored once, on the class's *prototype*, and shared by all instances. Inside a method, `this` is the object before the dot, as in `model.update(c)`. Like a C struct type plus functions taking a pointer to it, except that `this` comes from the call, so a method handed over on its own loses it.
- **# (private member)**: a field or method whose name starts with `#`, such as `#row`, can be used only by code inside its class. The `#` is part of the name, so `#row` and `row` are different members. Using `model.#row` outside the class is a `SyntaxError`. Like an opaque C struct (its fields visible only in its own `.c` file), but no cast can get around it.

</details>

<details open>
<summary>Preact: signal, computed, effect, computed vs effect</summary>
<br>

Reference: the [signals-core 1.14.5 README](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#guide--api).

- **signal**: a box holding one value. Code that reads `.value` inside a `computed` or `effect` is subscribed to it; writing a *different* value to `.value` notifies the subscribers. Writing the same value notifies nobody.
- **computed**: a read-only signal whose value is a function of other signals. `model.js` hands out `computed` wrappers around `row` and `col`, so code outside the model can read them but not write them.
- **effect**: a function that runs immediately, then again whenever a signal it read on its last run changes.
- **computed vs effect**: a `computed` works out a value; an `effect` does something with it outside the signals, such as writing the page or logging.
  - *When its function runs:* a computed's runs only when someone reads its `.value` and a signal it read has changed since its last run, so a computed that nothing reads never runs. An effect's runs once when it is created, then after every change to a signal it read, whether or not anything uses the result.
  - *What it gives back:* a computed is itself a signal, whose value is what its function returns. `effect(fn)` returns a `dispose` function that stops the effect, and `fn` may return a *cleanup* function, which runs before each re-run and on dispose. This repo never disposes: its effects last as long as the page.
  - *Filtering:* a computed that recomputes to the same value (`===`) notifies nobody. `computed(() => savings.value > 1000)` stays `true` as savings goes from 5000 to 6000, so an effect that reads only it doesn't re-run.
  - *Rule of thumb:* if a value follows from signals, make it a computed, as `bondsText` in [STUDY_PLAN_1.md](STUDY_PLAN_1.md) is. Keep effects for the edge, where values leave the signals for the page, like the redraw effect in each `main.js`. Setting one signal from another inside an effect makes the second one lag: an effect that reads both can run once with the new first value and the old second one, then run again.

</details>

<details open>
<summary>lit-html: html, container, render</summary>
<br>

References: the [Templates API page](https://lit.dev/docs/api/templates/) and the [lit-html 3.3.3 declaration file](https://cdn.jsdelivr.net/npm/lit-html@3.3.3/lit-html.d.ts).

- **html**: a tag written in front of a backtick string, a *tagged template literal* (see the `view.js` walkthrough). It returns a description of the DOM and does not touch the page.
- **container**: the element that `render` draws into, here `<div id="app-singleton">`, `<div id="app-factory">` or `<div id="app-class">`. The rest of the page is untouched.
- **render**: writes that description into a container. On later calls it reuses the DOM it built and goes slot by slot (each `${…}`, walking into nested templates and arrays), updating only the slots whose value changed.

</details>

</details>

### One tick, step by step

<details>
<summary>Key press, tick, write, redraw, hex packing</summary>
<br>

All three apps run this same sequence, each with its own controller, model, view and tick.

1. **Key press.** The browser calls `controller.keydown` (the controller's method, registered in `main.js`; in `class/`, through a small wrapper), which stores the command in the controller's `pending` latch. The browser pushes events rather than waiting to be polled, so the key waits in `pending` until the next tick reads it. If two keys arrive within one tick, the last one wins.
2. **Tick.** Every 150 ms (about 6.7 steps per second) `setInterval` calls `model.update(controller.read())`; `read` returns `pending` and clears it. `update` remembers the last real command in a plain variable `cmd`, so the dot keeps moving with no key held. `cmd` is not a signal because nothing on screen shows it. Edges wrap: from column 15, RIGHT goes to column 0.
3. **Write.** `update` writes a new value to `col` or `row`. After Space, it writes nothing, so nothing re-renders.
4. **Redraw.** On its last run the effect in `main.js` read `row`, `col` and `hex` (through the view), so it re-runs the redraw: `viewUpdate(model, container)` in the singleton, `view.update(model)` in the factory and class versions. The view's `template(m)` rebuilds the whole description: 128 cells. `render` then changes only what differs, which for one step is the `class` of two `<td>` cells and the `<output>` text. The saving is in DOM work, not in JavaScript work.

The readout packs the position into one byte: `hex = (row << 4) | col`. Column 0–15 fills the low 4 bits and row 0–7 the next 3, so the range is `00`–`7F`. Example: the start position, row 4 and column 7, gives `(4 << 4) | 7 = 0x40 | 0x07 = 0x47`, shown as `47`.

</details>

## Code walkthrough

Each file in full, cut into short parts, each part followed by its notes. `index.html` comes first, then the singleton version, then the factory version and the class version, whose notes explain only what differs. The notes cover the HTML, CSS and JavaScript as well as the two libraries, so knowing C is enough to follow them. Each file's notes open with the library names it uses, tagged (Preact) or (lit-html), and those names are bold where the notes explain them; everything else is plain HTML, CSS or JavaScript. [How it works](#how-it-works) defines the terms.

### `index.html`

<details>
<summary>Page tree, import map, Eruda console, CSS rules, three containers, three module scripts</summary>
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
  <!-- add console display --> <script src="./vendor/eruda.js"></script> <script> localStorage.removeItem('eruda-dev-tools'); localStorage.setItem('eruda-entry-button', '{"rememberPos":false}'); eruda.init({ tool: ['console'], defaults: { displaySize: 30, theme: 'Dark' } }); eruda.get('console').config.set('displayExtraInfo', true); eruda.show(); </script>
```

- `<!doctype html>` asks for standard rendering instead of a legacy compatibility mode.
- `<html lang="en">` opens the root element. `lang="en"` is an attribute, a `name="value"` setting written inside a tag. It marks the page's text as English, so screen readers use English pronunciation and browsers know the language when they offer to translate.
- Tags nest into a tree that the browser parses into the DOM: `<html>` holds `<head>` (setup, never drawn) and `<body>` (what you see, in the last part). `<meta charset="utf-8">` says how to decode the file's bytes into text, and `<title>` names the browser tab.
- `<script type="importmap">` is the import map from [How it works](#how-it-works). Its paths are relative to the page, so `./vendor/lit-html.js` means `http://localhost:8000/vendor/lit-html.js`. It must come before the module scripts: browsers apply the map only to imports resolved after they have read it.
- The `<!-- add console display -->` line adds [Eruda](https://github.com/liriliri/eruda), a console panel at the bottom of the page that shows what `console.log` prints.

```html
  <style>
    body { background: #333; color: #eee; }
    .matrix { border-collapse: collapse; background: #111; }
    .matrix td { width: 10px; height: 10px; border: 1px solid #333; }
    .matrix td.on { background: #f33; }
    output { font: 1.0em monospace; }
  </style>
```

- `<style>` holds CSS rules of the form `selector { property: value; }`. The selector picks the elements a rule applies to.
- `body` is the `<body>` element: dark gray background, light gray text. Colors are hex RGB, and three digits are shorthand for six: `#f33` means `#ff3333` (red 255, green 51, blue 51).
- `.matrix` is any element with `class="matrix"`, here the table. `border-collapse: collapse` makes neighboring cells share one border line instead of each drawing its own with a gap between.
- `.matrix td` is every `<td>` inside it: 10 × 10 px, with a 1 px border in the page's color, so the grid lines look like gaps.
- `.matrix td.on` is a cell that also has class `on`. This rule alone makes the dot red: the view never sets a color, it only puts `on` in one cell's class. Looks live in CSS, structure in the template.
- `output` is the hex readout: a fixed-width font at `1.0em`. With the family given only as `monospace`, browsers start from their monospace default, 13 px in Chrome, so this comes out at 13 px rather than the 16 px of the body text.

```html
</head>
<body>
  <p>Arrow keys move, Space stops.</p>
  <h3>singleton</h3>
  <div id="app-singleton"></div>
  <h3>factory</h3>
  <div id="app-factory"></div>
  <h3>class</h3>
  <div id="app-class"></div>
  <script type="module" src="./singleton/main.js"></script>
  <script type="module" src="./factory/main.js"></script>
  <script type="module" src="./class/main.js"></script>
</body>
</html>
```

- `<p>` is a paragraph of text: the instruction line. `<h3>` is a third-level heading, smaller than `<h2>`, here the label above each app.
- `<div id="app-singleton">`, `<div id="app-factory">` and `<div id="app-class">` are empty `<div>`s, the three containers. `id` gives an element a name unique in the page, and `#app-singleton` is the CSS selector for it. JavaScript draws one app into each box.
- `<script type="module" src="./singleton/main.js">` loads `singleton/main.js` as a module: a file with its own scope, which shares only the names it `export`s and gets other files' names with `import`. That is close to a C file where everything is `static` except what it exports, but there is no linker: the browser fetches each imported file by URL while loading. A module script also waits until the whole page is parsed, so the containers exist by the time it runs. Each of the three scripts starts one app; its imports pull in the other four files of that version's folder, and the libraries.

</details>

### `singleton/`

<details>
<summary>model-controller-common.js, model.js, view.js, controller.js, main.js: each part exists once</summary>
<dl><dd>

#### `model-controller-common.js`

<details>
<summary>The command table, shared by model and controller</summary>
<br>

Library names: none.

```js
// The message from controller to model, shared by those two only, like the C `command` enum.
export const Cmd = Object.freeze({ NONE: 0, STOP: 1, LEFT: 2, RIGHT: 3, UP: 4, DOWN: 5 });
```

- `//` starts a comment that runs to the end of the line, as in C. This file holds only what the model and the controller both need: the commands, the message one sends to the other. Your C code marks its `command` enum the same way, as the MODEL-CONTROLLER message. The view never imports it. `factory/` has its own identical copy, so neither folder imports from the other.
- `export const Cmd` makes `Cmd` visible to other modules. `const` declares a name that cannot be reassigned, like `T * const p` in C: when the value is an object, the name always refers to that object, but the object itself could still be changed, unless it is frozen as `Cmd` is.
- `Object.freeze({ NONE: 0, … })` stands in for a C `enum`, which JavaScript lacks. `{ NONE: 0, … }` is an object literal: a table of named fields, each with a value. It is frozen (see [Terms](#terms)), so `Cmd.UP = 9` throws a `TypeError`. The numbers only need to be distinct.

</details>

#### `model.js`

<details>
<summary>Imports, file-level state, the one model, update, wrap-around math</summary>
<br>

Library names: **`signal`**, **`computed`** and **`.value`** (Preact).

```js
import { signal, computed } from '@preact/signals-core';
import { Cmd } from './model-controller-common.js';
```

- `import { signal, computed } from '@preact/signals-core'` takes two exported names from a module: Preact's two building blocks. A bare name like `@preact/signals-core` goes through the import map to a file in `vendor/`. The model is built from these alone. Nothing in this file touches the page.
- `'./model-controller-common.js'` is a relative path, which starts with `./` (this file's folder) or `../` (the folder above). Here it is this folder's own file, which provides `Cmd`.
- @preact/signals-core 1.14.5 exports more: **`effect`** (used in each `main.js`); **`batch`**, which groups several writes so that effects run once, at the end; **`untracked`**, which reads signals without subscribing; **`action`**, which wraps a function so that each call runs batched and untracked; and **`createModel`**, a helper for building models out of signals. That last one is unrelated to `factory/model.js`'s own `createModel`, a plain function of the same name. It also exports the classes `Signal`, `Computed` and `Effect`, which `signal()`, `computed()` and `effect()` create. The [signals-core 1.14.5 README](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#guide--api) documents all of the functions except `action`, which it mentions only under `createModel`.

```js
const WIDTH = 16, HEIGHT = 8;               // grid size, owned by the model
const row = signal(4), col = signal(7);     // file-level, like static variables in C
let cmd = Cmd.STOP;                         // not shown on screen, so plain variable
```

- `const WIDTH = 16, HEIGHT = 8` is the grid size. Only the models define it, and the other versions repeat these two numbers on purpose. The view learns them from the model it is given, through `width` and `height` below.
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
- `row: computed(() => row.value)` hands out a read-only **`computed`** view of `row`. `() => row.value` is an arrow function (see [Terms](#terms)) that takes nothing and returns `row.value`. A computed has a getter for **`.value`** but no setter, so `model.row.value = 3` throws a `TypeError`. It is like handing out a `const model_t *`, except that C rejects the write at compile time and JavaScript only at run time. A computed is also lazy and cached: it recalculates only when read after one of its inputs changed.
- `hex: computed(() => (row.value << 4) | col.value)` packs the position into one byte ([How it works](#how-it-works) has the worked example). Ordinary JavaScript numbers are 64-bit floats, but `<<` and `|` convert to 32-bit integers first, so the result matches C for these small values.

```js
  update(c) {    // model_update(); shorthand for update: function (c) {
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

#### `view.js`

<details>
<summary>Imports, range helper, tagged templates, rows and cells, class slot, hex text, viewUpdate</summary>
<br>

Library names: **`html`** and **`render`** (lit-html), **`.value`** (Preact). Inside an **`html`** template, each `${…}` is a slot that lit-html fills.

```js
import { html, render } from 'lit-html';
```

- `import { html, render } from 'lit-html'` takes lit-html's two names, by bare name as in `model.js`. **`html`** is lit-html's template tag and **`render`** writes a template into the page; both are explained below. This is the only file in its folder that imports lit-html, and it imports nothing else: even the grid size comes from the model it is given.
- lit-html 3.3.3 exports more than `html` and `render`: **`svg`** and **`mathml`**, template tags like `html` for SVG graphics and MathML math markup; **`nothing`**, a value that renders as empty; and **`noChange`**, a value that leaves a slot as it was, used mostly when writing directives (add-ons that control how a slot updates). It also exports `_$LH`, which is internal to Lit's own packages. The [Templates API page](https://lit.dev/docs/api/templates/) documents `html`, `svg`, `render` and `nothing`; the [lit-html 3.3.3 declaration file](https://cdn.jsdelivr.net/npm/lit-html@3.3.3/lit-html.d.ts) lists every export, types included. lit.dev writes imports as `from 'lit'`; the `lit` package re-exports `lit-html`, so the names are the same. Ready-made directives such as `repeat` live in separate `lit-html/directives/…` files, which this project has not vendored.

```js
const range = n => [...Array(n).keys()];
```

- `const range = n => [...Array(n).keys()]` returns `[0, 1, …, n−1]`. `n => …` is an arrow function (see [Terms](#terms)), here taking `n` and returning the array. `Array(n)` makes an array of `n` empty places, `.keys()` walks its indexes, and `[...]` collects them into a new array. Example: `range(3)` is `[0, 1, 2]`.

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
- `class=${r === m.row.value && c === m.col.value ? 'on' : ''}` is an attribute slot: it sets the cell's `class` to `on` or to an empty string, and the `.matrix td.on` rule in `index.html` paints it red. `===` is strict equality, and `? :` is the same as in C. These **`.value`** reads are what subscribe the effect in `main.js`, because `viewUpdate` runs inside it.
- `<output>${m.hex.value.toString(16).toUpperCase().padStart(2, '0')}</output>`: `<output>` is the semantic element for a computed result. The chain does what `printf("%02X", hex)` does in C: base-16 text, upper case, padded to two characters with `0`. Example: row 0, column 10 gives 10 → `a` → `A` → `0A`.

```js
export function viewUpdate(m, container) {   // view_update()
  render(template(m), container);
}
```

- `export function viewUpdate(m, container)` draws the model into `container` once and returns: **`render`** writes `template(m)` there, and on later calls changes only what differs from the last frame. It is the only name other files see, so lit-html stays a detail of this file. Redrawing on every change is not its job: `main.js` calls it inside an `effect`.
- It never imports a model; it only reads `m.width`, `m.height`, `m.row`, `m.col` and `m.hex` from whatever it is given.

</details>

#### `controller.js`

<details>
<summary>Command import, key table, file-level latch, keydown, read</summary>
<br>

Library names: none.

```js
import { Cmd } from './model-controller-common.js';
```

- The commands are the message from the controller to the model, so they are defined once per folder, in `model-controller-common.js`, which the two share, and imported here.

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
    if (Object.hasOwn(KEYMAP, e.key)) { pending = KEYMAP[e.key]; e.preventDefault(); }
  },
```

- `export const controller = {` is the one controller, built when the file loads.
- `keydown(e)` is the method `main.js` hands to the browser for key presses. `e` is the key event object, and `e.key` names the key. It uses `pending` from the file level, so it still works when handed over on its own, detached from the object, as `controller.keydown`.
- `Object.hasOwn(KEYMAP, e.key)`, a JavaScript built-in, is true when the table itself has that key. The shorter `e.key in KEYMAP` would also count names built into every object, such as `'toString'`; no real key has such a name, but `hasOwn` is the habit worth copying. `e.preventDefault()` cancels the browser's own action for the key; arrows and Space would otherwise scroll the page. It runs only for mapped keys, so shortcuts such as F5 still work.

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

#### `main.js`

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
import { viewUpdate } from './view.js';
import { controller } from './controller.js';
```

- All three come from this folder: `model` and `controller` are ready-made objects, and `viewUpdate` is a plain function. Importing them is all it takes: the parts already exist.

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

</dd></dl>

</details>

### `factory/`

<details>
<summary>model-controller-common.js, model.js, view.js, controller.js, main.js: main.js creates the parts</summary>
<dl><dd>

#### `model-controller-common.js`

<details>
<summary>Identical to singleton/model-controller-common.js</summary>
<br>

`factory/model-controller-common.js` is a byte-for-byte copy of `singleton/model-controller-common.js` (the first section in the singleton fold above): the same frozen `Cmd` table. Each folder has its own copy so that neither imports from the other. The boundary check fails if the two ever differ, so read that section.

</details>

#### `model.js`

<details>
<summary>What changes from the singleton: createModel, closure, one model per call</summary>
<br>

Library names: **`signal`**, **`computed`** and **`.value`** (Preact). Only what differs from `singleton/model.js` is explained here.

```js
import { signal, computed } from '@preact/signals-core';
import { Cmd } from './model-controller-common.js';
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
- `row`, `col` and `cmd` are now local to `createModel`, yet the functions created inside it keep using them after it returns. That is a closure (see [Terms](#terms)), and each `createModel()` call gets its own set.
- `return {` hands back an object literal with the same fields as the singleton's `model`, `width` and `height` included, which is why the same view template works with either.

```js
    update(c) {    // model_update(); shorthand for update: function (c) {
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

#### `view.js`

<details>
<summary>What changes from the singleton: createView, the container kept per view</summary>
<br>

Library names: **`html`** and **`render`** (lit-html), **`.value`** (Preact). Only what differs from `singleton/view.js` is explained here.

```js
import { html, render } from 'lit-html';
```

- The same import as `singleton/view.js`.

```js
const range = n => [...Array(n).keys()];
```

- The same `range` helper.

```js
const template = m => html`
  <table class="matrix">
    ${range(m.height).map(r => html`<tr>
      ${range(m.width).map(c => html`<td class=${r === m.row.value && c === m.col.value ? 'on' : ''}></td>`)}
    </tr>`)}
  </table>
  <output>${m.hex.value.toString(16).toUpperCase().padStart(2, '0')}</output>`;
```

- The same template, so both versions draw the same grid and readout. It stays at file level: it is a function that holds no state, so every view can share it.

```js
export function createView(container) {     // each view keeps only where it draws
  return {
    update(m) {                             // view_update()
      render(template(m), container);
    },
  };
}
```

- `export function createView(container)` is a factory, the simplest one in this folder: the only thing each view keeps is `container`, the element it draws into, which `main.js` passes in once. `update` reaches it later through a closure (see [Terms](#terms)), so `main.js` no longer hands over the container on every redraw.
- `update(m)` does what the singleton's `viewUpdate(m, container)` does. The model is still passed on every call, as in the C `view_update(mp)`. The last three lines close `update`, the returned object and `createView`.
- `container` never changes, so a factory view gives each app no state the singleton view lacked: it changes how `main.js` wires things, not what each app remembers. The view's one piece of memory lives in lit-html: **`render`** stores the DOM it built on the container element itself, so each container already has its own, with the singleton's `viewUpdate` too. A factory view would start to matter once the view kept memory of its own, such as a blink timer or the dot's last position for an animation.

</details>

#### `controller.js`

<details>
<summary>What changes from the singleton: createController, one latch per controller</summary>
<br>

Library names: none. Only what differs from `singleton/controller.js` is explained here.

```js
import { Cmd } from './model-controller-common.js';
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
      if (Object.hasOwn(KEYMAP, e.key)) { pending = KEYMAP[e.key]; e.preventDefault(); }
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

#### `main.js`

<details>
<summary>What changes from the singleton: creating the model, the view and the controller</summary>
<br>

Library names: **`effect`** (Preact). Only what differs from `singleton/main.js` is explained here.

```js
import { effect } from '@preact/signals-core';
```

- The same import as `singleton/main.js`.

```js
import { createModel } from './model.js';
import { createView } from './view.js';
import { createController } from './controller.js';
```

- This version imports the factories, `createModel`, `createView` and `createController`, instead of ready-made objects and a plain function.

```js
const model = createModel();
const view = createView(document.querySelector('#app-factory'));
const controller = createController();
```

- These three calls are the real difference from `singleton/main.js`: here this file decides that there is one of each. The view is told its container once, here, so the redraw below no longer looks it up. A second set of calls, with a second container, would give a second, independent app.

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
effect(() => view.update(model));            // redraw only on change
```

- The same redraw effect as `singleton/main.js`, now calling the view's `update` with the model. The view already knows it draws into `#app-factory`.

</details>

</dd></dl>

</details>

### `class/`

<details>
<summary>model-controller-common.js, model.js, view.js, controller.js, main.js: main.js creates the parts with new</summary>
<dl><dd>

#### `model-controller-common.js`

<details>
<summary>Identical to singleton/model-controller-common.js</summary>
<br>

`class/model-controller-common.js` is a byte-for-byte copy of `singleton/model-controller-common.js` (the first section in the singleton fold above), like the factory's. The boundary check fails if the copies ever differ, so read that section.

</details>

#### `model.js`

<details>
<summary>What changes from the factory: class Model, private fields, this</summary>
<br>

Library names: **`signal`**, **`computed`** and **`.value`** (Preact). Only what differs from `factory/model.js` is explained here.

```js
import { signal, computed } from '@preact/signals-core';
import { Cmd } from './model-controller-common.js';
```

- The same imports as `factory/model.js`.

```js
const WIDTH = 16, HEIGHT = 8;               // grid size, owned by the model
```

- The same grid size, again at file level because it never changes.

```js
export class Model {
  #row = signal(4); #col = signal(7);       // private (#), like fields of model_t
  #cmd = Cmd.STOP;                          // not shown on screen, so plain variable
  width = WIDTH; height = HEIGHT;           // the view draws whatever size the model says
  row = computed(() => this.#row.value);    // read-only to outsiders: const model_t *
  col = computed(() => this.#col.value);
  hex = computed(() => (this.#row.value << 4) | this.#col.value);
```

- `export class Model {` starts a class (see [Terms](#terms)): a blueprint that `main.js` turns into a model with `new Model()`. It plays the part of `createModel`.
- Each `name = value;` in the class body declares a field. `new Model()` runs every initializer again, in order, for each new model, so each model gets its own two signals and its own `#cmd`, just as each `createModel()` call got its own local variables.
- `#row`, `#col` and `#cmd` are private fields, the class's replacement for the factory's closure variables. Code outside the class body cannot even name them: `model.#row` there is a `SyntaxError`, and the browser refuses to load that file.
- `width`, `height`, `row`, `col` and `hex` are public fields, the same five the factory's object has, so the view reads either one the same way.
- `computed(() => this.#row.value)`: an arrow function has no `this` of its own; it uses the `this` of the code around it. Field initializers run inside `new`, where `this` is the new model, so each computed reads its own model's `#row`.

```js
  update(c) {    // model_update(); a method on Model.prototype, shared by all models
    if (c !== Cmd.NONE) this.#cmd = c;
    switch (this.#cmd) {
      case Cmd.LEFT:  this.#col.value = (this.#col.value + WIDTH - 1) % WIDTH; break;
      case Cmd.RIGHT: this.#col.value = (this.#col.value + 1) % WIDTH;         break;
      case Cmd.UP:    this.#row.value = (this.#row.value + HEIGHT - 1) % HEIGHT; break;
      case Cmd.DOWN:  this.#row.value = (this.#row.value + 1) % HEIGHT;        break;
    }
  }
}
```

- `update(c)` is the factory's rule with each state name written as `this.#name`: the private field of the model it was called on. It is a method, so unlike the factory's `update` it exists once, on the prototype, shared by every model. Unlike in the other two versions, `update(c) {` here is not shorthand for `update: function (c) {`: a class body does not allow that colon form, and it is a `SyntaxError`. `this` tells it which model's fields to use, the way `mp` does in C's `model_update(mp, c)`. The last two lines close `update` and the class.

</details>

#### `view.js`

<details>
<summary>What changes from the factory: class View, a private field, the constructor</summary>
<br>

Library names: **`html`** and **`render`** (lit-html), **`.value`** (Preact). Only what differs from `factory/view.js` is explained here.

```js
import { html, render } from 'lit-html';
```

- The same import as `factory/view.js`.

```js
const range = n => [...Array(n).keys()];
```

- The same `range` helper.

```js
const template = m => html`
  <table class="matrix">
    ${range(m.height).map(r => html`<tr>
      ${range(m.width).map(c => html`<td class=${r === m.row.value && c === m.col.value ? 'on' : ''}></td>`)}
    </tr>`)}
  </table>
  <output>${m.hex.value.toString(16).toUpperCase().padStart(2, '0')}</output>`;
```

- The same template as the factory's, at file level for the same reason: it holds no state.

```js
export class View {
  #container;                               // each view keeps only where it draws
```

- `export class View {` plays the part of `createView`, and `new View(container)` the part of `createView(container)`.
- `#container;` declares a private field. Each view gets its own `#container`, which starts as `undefined` and which only code inside these braces can read or write. It replaces the factory's closure variable `container`.

```js
  constructor(container) {
    this.#container = container;
  }
```

- `constructor(container)` is the function that `new View(container)` runs on the fresh view, after its fields are set up. There `this` is the new view, so `this.#container = container` stores the argument in that view's private field. The factory needs no such step: its closure keeps the `container` parameter itself.

```js
  update(m) {                               // view_update()
    render(template(m), this.#container);
  }
}
```

- `update(m)` is a method: written once, stored on the class's prototype, and shared by every view. When `main.js` calls `view.update(model)`, `this` is `view`, so `this.#container` is that view's own container. The last two lines close `update` and the class.

</details>

#### `controller.js`

<details>
<summary>What changes from the factory: class Controller, a private latch, a plain method</summary>
<br>

Library names: none. Only what differs from `factory/controller.js` is explained here.

```js
import { Cmd } from './model-controller-common.js';
```

- The same import as `factory/controller.js`.

```js
const KEYMAP = Object.freeze({ ArrowUp: Cmd.UP, ArrowDown: Cmd.DOWN, ArrowLeft: Cmd.LEFT,
                               ArrowRight: Cmd.RIGHT, ' ': Cmd.STOP });
```

- The same frozen `KEYMAP`, shared by every controller.

```js
export class Controller {
  #pending = Cmd.NONE;                       // latched key, like KEYPAD bit 7
```

- `#pending` is the latch, now a private field, so each `new Controller()` gets its own.

```js
  keydown(e) {                               // the keypad latching a key
    if (Object.hasOwn(KEYMAP, e.key)) { this.#pending = KEYMAP[e.key]; e.preventDefault(); }
  }
```

- `keydown(e)` is the factory's code, writing `this.#pending`. It is a plain method, so it works only when called on its controller, as `controller.keydown(e)`. Handed to the browser on its own, it would lose `this`; `main.js` below shows the trap and the fix.

```js
  read() {                                   // controller_read(): the latched key, or NONE
    const c = this.#pending;
    this.#pending = Cmd.NONE;
    return c;
  }
}
```

- `read()` is the factory's code. The tick always calls it as `controller.read()`, so `this` is right. The last two lines close `read` and the class.

</details>

#### `main.js`

<details>
<summary>What changes from the factory: new, the wrapped key listener, the this trap</summary>
<br>

Library names: **`effect`** (Preact). Only what differs from `factory/main.js` is explained here.

```js
import { effect } from '@preact/signals-core';
```

- The same import as `factory/main.js`.

```js
import { Model } from './model.js';
import { View } from './view.js';
import { Controller } from './controller.js';
```

- This version imports the classes. By convention a class name starts with a capital letter, which tells the reader to use `new`.

```js
const model = new Model();
const view = new View(document.querySelector('#app-class'));
const controller = new Controller();
```

- `new Model()`, `new View(…)` and `new Controller()` do what the factory's three calls do: this file decides that there is one of each, and the view is told its container once. Forgetting `new` fails straight away: `Model()` throws `TypeError: Class constructor Model cannot be invoked without 'new'`.

```js
window.addEventListener('keydown', e => controller.keydown(e));  // wrapped: passed alone, keydown would lose `this`
```

- This is the one line that has to differ from the other versions. `this` is set by how a function is called, not by where it was written: `controller.keydown(e)` runs `keydown` with `this` set to `controller`, the object before the dot. The arrow function `e => controller.keydown(e)` makes exactly that call on every key press. (Another fix is in the footnote below.)
- Without the wrapper, `addEventListener('keydown', controller.keydown)` hands over only the function. The browser calls a listener with `this` set to the object the listener is attached to, so here it runs as if `window.keydown(e)`, and `this.#pending = …` throws `TypeError: Cannot write private member #pending to an object whose class did not declare it`. Only arrows and Space get that far; other keys never reach the write. The throw comes before `e.preventDefault()`, so the key also does its normal job, such as scrolling the page when the page is taller than the window. On screen the dot simply ignores the keys; the error appears only in the browser's developer console.
- That error comes from the `#` field's *brand check*: before touching `#pending`, the browser checks that `this` really is a `Controller`. With a public field, `this.pending = …` would pass silently and create `window.pending` instead, a stray global that nothing reads.
- The wrapper is a new function, made on this line. Removing the listener later with `removeEventListener` would need that same function, so you would have to keep it in a variable first. This app never removes it.

```js
setInterval(() => {                          // the NMI tick
  model.update(controller.read());
}, 150);
```

- The same tick as `factory/main.js`. Both calls are made on their objects, so `this` is right without a wrapper.

```js
effect(() => view.update(model));            // redraw only on change
```

- The same redraw effect as `factory/main.js`, drawing into `#app-class`.

**Footnote: another fix, `handleEvent`.** `addEventListener` also accepts an object instead of a function. The browser then calls that object's `handleEvent(e)` method, with `this` set to the object. Renaming `keydown` to `handleEvent` would let this file write `window.addEventListener('keydown', controller)`, handing over the controller itself. Pros: a plain method that gets the right `this` by the browser's own rule, no wrapper, and `removeEventListener('keydown', controller)` works. Cons: it is a convention of the browser's event system only, the fixed name loses the descriptive `keydown`, and an object that handles several event types needs a `switch (e.type)` inside `handleEvent`. This version uses the wrapper because it keeps the trap visible on the line where it happens.

</details>

</dd></dl>

</details>

## Singleton vs factory vs class

<details>
<summary>Plain difference, the C comparison, obvious and subtle differences, pros and cons, factory vs class, which to use</summary>
<br>

The versions behave identically here: same model and controller objects, same output. The difference is **when the state is created and how many copies can exist**. A singleton gets exactly one copy, created automatically the first time any file imports it. A factory makes a new, independent copy every time `main.js` calls `createModel()`. The class version is a factory written with JavaScript's `class` syntax: `new Model()` also makes a new copy each time. [Factory vs class](#factory-vs-class) compares those two.

The C original already uses both styles. `controller_read()` keeps its state in `static` variables, so exactly one exists: singleton-style. The model is factory-style: `model_t` is a struct, `model_init(mp)` initializes one, and `model_update(mp, c)` works on whichever one it is given. The JavaScript factory does the same, but instead of passing a pointer, each `update` remembers its own state through a closure (see [Terms](#terms)). The class is closest to the C: `this` plays the part of `mp`, except that the call supplies it (`model.update(c)`) instead of a parameter.

### Obvious differences

<details>
<summary>How many, when created, where the state lives, what main.js does</summary>
<br>

| | Singleton | Factory | Class |
|---|---|---|---|
| How many | exactly one | as many as you create | as many as you create |
| When it's created | when the file is first imported | when `main.js` calls `createModel()` | when `main.js` calls `new Model()` |
| Where the state lives | file-level variables, like C `static` | local variables inside the factory, kept alive by the closure | `#` private fields on each object |
| What `main.js` does | `import { model }`, and it already exists | `import { createModel }`, then `const model = createModel()` | `import { Model }`, then `const model = new Model()` |

That last row is the whole visible difference. Between `singleton/main.js` and `factory/main.js` it comes to the three "create" lines, the import names, and the redraw line, which no longer looks up its container. `class/main.js` differs from `factory/main.js` in the same create lines and imports, which use `new`, and in the wrapped key listener.

</details>

### Subtle differences

<details>
<summary>Shared importers, same URL, settings, resetting, accidental doubles, per-copy functions, detached methods</summary>
<br>

1. **Every importer shares the same singleton.** A JavaScript module runs once per page, so every file that imports `singleton/model.js` gets *the same* model. That is fine while only `main.js` imports it, but it is hidden shared state. Two `main.js` files importing the singleton controller would share one `pending` latch: whichever tick runs first takes each key, and the other app randomly misses key presses, with no error. A factory can't do this by accident, because each caller gets its own copy.
2. **"Same file" means "same URL", and that has a nasty edge.** The browser identifies modules by URL. Imported as `./model.js` and as `./model.js?v=2` (or through a symlinked path), the same file runs twice, and the singleton quietly becomes two. A factory doesn't care.
3. **A singleton can't take settings when it's created.** Its start position and grid size are fixed in the file, because it builds itself before any other code runs. A factory could take them as arguments, as in `createModel({ width: 32, start: [0, 0] })`. In C terms: a static initializer versus an `init(&m, args)` function.
4. **Resetting and testing.** Singleton state lives until the page reloads. Resetting it needs an extra `reset()` function, and tests that import it share leftover state between them. With a factory, you just make a fresh one.
5. **A factory's classic trap is creating two by accident.** If `createModel()` is called in two places, you silently get two separate dots. One view might draw one model while the keys drive the other, with no error anywhere. A singleton can't have this bug.
6. **Each factory copy gets its own set of functions.** Every `createModel()` call builds new `update` and `computed` functions; the singleton builds them once, and the class shares one `update` among all its copies (see [Factory vs class](#factory-vs-class)). Irrelevant at two copies, worth knowing at ten thousand.
7. **The singleton and factory methods survive being handed over detached, as `controller.keydown`,** because neither uses `this` (JavaScript's name for the object a method was called on). The class version's methods do use `this`, so `class/main.js` has to wrap its key listener; its walkthrough shows what breaks without the wrapper, a common trap for C programmers moving to JavaScript.

</details>

### Pros and cons

<details>
<summary>Singleton, factory, class</summary>
<br>

**Singleton**
- **Pros:**
  - Fewest concepts: no closure, no "create" step. It reads top to bottom like a C file with `static` variables.
  - It can't be forgotten or doubled: it simply exists.
  - Easy to find, because the state sits in one obvious place.
- **Cons:**
  - Only ever one: no second player, no second app.
  - Hidden sharing between every file that imports it.
  - No settings at creation time.
  - Awkward to reset and to test.

**Factory**
- **Pros:**
  - Any number of independent copies.
  - Settings per copy.
  - Easy to reset and test: just make a new one.
  - Explicit wiring: `main.js` shows exactly what exists and who gets which copy, like a top-level netlist.
- **Cons:**
  - One more concept (the closure) and one more step in `main.js`.
  - You can accidentally create two.
  - Slightly more memory per copy.

**Class**
- **Pros:**
  - Any number of independent copies, like a factory.
  - Methods are stored once and shared by every copy, which matters at tens of thousands of copies, not at one.
  - A `#` field used on the wrong object throws, instead of failing silently.
  - Some browser features are built around classes: a web component, for example, is defined as a class that extends `HTMLElement`.
- **Cons:**
  - Two more concepts than the factory: `this` and `new`.
  - A method handed over on its own loses `this`, so every hand-over needs a wrapper.

</details>

### Factory vs class

<details>
<summary>Making one, where state lives, how methods find it, shared methods, detaching, privacy</summary>
<br>

A class is another way to write a factory: both make as many independent copies as `main.js` asks for. What differs is how each copy's methods find that copy's state.

| | Factory (`factory/`) | Class (`class/`) |
|---|---|---|
| Making one | `createModel()` | `new Model()`; without `new` it throws a `TypeError` |
| Where a copy's state lives | local variables of that `createModel()` call, kept alive by the closure | `#` private fields on the object itself |
| How a method finds it | through the closure, fixed when the copy was made | through `this`, taken from each call (`model.update(c)`) |
| Methods | a new set of functions per copy | one shared set, on the prototype; the `computed` fields are still made per copy |
| A method handed over on its own | works | loses `this`; wrap it, as `class/main.js` does |
| Privacy | complete: nothing outside can name the locals | complete: a `#` name outside the class body is a `SyntaxError`; and a method run on the wrong object throws instead of writing to it |

</details>

### Which to use

<details>
<summary>One physical thing or many; switching later; when a class</summary>
<br>

Use a **singleton** for things the physical world limits to one: one keyboard, one screen. That is why a singleton controller feels natural. Use a **factory** as soon as you need a second copy, settings per copy, or tests. Switching later is mechanical, and the diff between `singleton/` and `factory/` is exactly that change:

1. wrap the file-level state in a function;
2. `return` the object;
3. have `main.js` call that function.

Use a **class** for the same jobs as a factory when there will be very many copies, since its methods are stored once, or when a library or browser feature expects one. No choice locks you in.

</details>

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
| `.claude/rules/markdown.md` | How to write HOW_AND_WALKTHROUGH.md and docs/: which `##` sections fold. Claude Code loads it when working on those files. |
| `.claude/PROGRESS.md` | Latest session handoff, maintained by `/wrapup`; earlier ones: `git log -p --follow -- .claude/PROGRESS.md`. |
| `.checks/boundaries.py` | Checks the MVC boundaries in CLAUDE.md's Architecture rules: who may import what, each folder only from itself; browser globals and `effect` only in `main.js`; signal writes only in `model.js`; `model.update` and the view used only from `main.js`; file-level changing state, and `static` class fields (shared by every instance), only in `singleton/`; the `model-controller-common.js` copies identical. Run `uv run --no-project python .checks/boundaries.py`. The `PostToolUse` hook runs it after every Edit or Write and tells Claude Code what it broke; it can't undo the edit, and shell edits skip it. |
| `.checks/stop-hook.sh` | The `Stop` hook: runs the same check when Claude Code tries to finish a turn and, on a violation, sends it back to fix the code first. If the violation survives one round, it lets the turn end but shows you a warning, so it can't loop forever. |
| `.gitignore` | OS cruft, Python/uv venv, editor files, and everything in `.temp/` (the study plans' working folders) except `.placeholder`. |
| `.vscode/settings.json` | VS Code workspace settings, tracked so they are shared: hides `.temp/.placeholder` from the Explorer. |
| `.gitattributes` | LF line endings; binary file types; no line diffs for the minified `vendor/` files. |

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

**Not used.** `node`/`npm` (Python's `http.server` serves the page; see [Run](README.md#run)) and the .NET SDK.

</details>
