# Study plan 2: the dot runner

New to reading and writing a web page from JavaScript? Do [STUDY_PLAN_1.md](STUDY_PLAN_1.md) first: it builds one small form app from plain DOM code up to lit-html and Preact Signals.

The goal: by the end you can build a small Preact Signals + lit-html app on your own. Each step has two parts: **read** the listed sections, in order (most are in [HOW_AND_WALKTHROUGH.md](HOW_AND_WALKTHROUGH.md)), then **build** something small and see it run. The steps go: a hello world from a blank folder, built twice (lit-html alone, then with Preact Signals added), then one small feature added to the singleton, factory and class versions in turn, then an app of your own. The code comments name the C counterpart of each piece, if that helps.

## Can I skip the factory?

You can, but it costs more than it saves:

- The `class/` walkthrough explains only what differs from `factory/`.
- The factory step is small: `git diff --no-index -w singleton factory` is 21 lines added and 10 removed.
- Skipping it means meeting the closure, `new`, `this` and `#` all in one step instead of two.

## Step 0: hello world from a blank folder

The same click counter, built twice: first with lit-html alone, to learn how a page is drawn, then with Preact Signals added, so that it redraws by itself. Both builds live outside the repo, so nothing here is checked against the repo's rules.

**Setup.** From the repo root:

```bash
mkdir ~/hello-signals && cp -r vendor ~/hello-signals/
```

`~/hello-signals/index.html`, used by both builds:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Hello signals</title>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

The import map names both libraries from the start, so this file never changes. The browser fetches a module only when some code imports it, so Build 1 never loads Preact.

### Build 1: lit-html alone

**Read:**

1. The README introduction and [Run](README.md#run): how the page is served, and why it needs a server.
2. [Terms](HOW_AND_WALKTHROUGH.md#terms): *DOM*, *import map*, *=> (arrow function)*, *html*, *container*, *render*. Skip the rest for now.
3. [Code walkthrough → `index.html`](HOW_AND_WALKTHROUGH.md#indexhtml): the import map and module scripts. The `index.html` above is a trimmed copy.

**Build:** `~/hello-signals/main.js`:

```js
import { html, render } from 'lit-html';

let count = 0;

const template = () => html`
  <button @click=${() => count++}>clicked ${count} times</button>`;

render(template(), document.querySelector('#app'));
```

Run `cd ~/hello-signals && uv run --no-project python -m http.server 8001` and open <http://localhost:8001>. Port 8001 leaves 8000 free for the repo.

- `` html`…` `` is a template: HTML in backticks, with `${…}` slots that lit-html fills. It only describes the page; it changes nothing.
- `template` is a function, so each call reads the current `count`. Written as `` const template = html`…` `` it would read `count` once, at 0, and keep that.
- `render(template(), container)` writes that description into the element. On later calls it changes only the slots whose value changed, here the number.
- `@click=${fn}` is lit-html's way to attach `fn` as the button's click listener. The repo doesn't use it: it listens for keys on the whole window, which no template draws, so its `main.js` attaches the listener with `addEventListener`.

**Now click the button.** The label stays at "clicked 0 times". Make it count. Hint: `count++` changes only the variable; `render` is what changes the page, and it ran once, when the file loaded.

<details>
<summary>Solution</summary>

Call `render` again after every change. A `draw` function keeps that call in one place:

```js
import { html, render } from 'lit-html';

let count = 0;

const template = () => html`
  <button @click=${() => { count++; draw(); }}>clicked ${count} times</button>`;

const draw = () => render(template(), document.querySelector('#app'));

draw();
```

The click handler now runs two statements, so its body goes in braces (see *=> (arrow function)* in Terms). Each click runs `count++`, then `draw()`, which builds a fresh description with the new number; `render` compares it with the last one and changes only the text.

</details>

### Build 2: add Preact Signals

Build 1 works only because every change remembers to call `draw()`. Preact Signals makes the redraw automatic.

**Read:** [Terms](HOW_AND_WALKTHROUGH.md#terms): *signal*, *effect*.

**Build:** replace `~/hello-signals/main.js` with:

```js
import { signal, effect } from '@preact/signals-core';
import { html, render } from 'lit-html';

const count = signal(0);                       // a box holding one value

const template = () => html`
  <button @click=${() => count.value++}>clicked ${count.value} times</button>`;

effect(() => render(template(), document.querySelector('#app')));  // re-runs when count changes
```

Reload the page and click the button.

- `signal(0)` makes a box holding one value. You read and write it through `.value`.
- `effect(fn)` runs `fn` now, and again whenever a signal that `fn` read last time changes. `template()` reads `count.value`, so every click redraws.

Three changes from Build 1's solution:

1. `let count = 0` became `const count = signal(0)`.
2. `count` became `count.value`, in the template and in the click handler.
3. `draw` and its two calls became one `effect`. The click handler only changes `count`; the effect sees the change and redraws. Code added later that changes `count`, such as a timer, needs no `draw()` call either.

The loop from here on is: edit, save, reload. There is no build step. If a change doesn't show, hard-reload with Ctrl+Shift+R (Mac: Cmd+Shift+R).

## Step 1: singleton

The same four blocks, split into the repo's five files. Run the repo (`uv run --no-project python -m http.server 8000` from its root) and keep the page open while you read.

**Read:**

1. [Files](HOW_AND_WALKTHROUGH.md#files): what each of the five files is for.
2. [Terms](HOW_AND_WALKTHROUGH.md#terms): *singleton*, *computed*, *Object.freeze*.
3. [One tick, step by step](HOW_AND_WALKTHROUGH.md#one-tick-step-by-step): what happens between a key press and the redraw.
4. [Code walkthrough → `singleton/`](HOW_AND_WALKTHROUGH.md#singleton), all five files in the walkthrough's order:
   - `model-controller-common.js`: the `Cmd` table;
   - `model.js`: `signal`, `computed` and the one rule that changes state;
   - `view.js`: tagged templates and slots, the heart of lit-html;
   - `controller.js`: the key latch;
   - `main.js`: the wiring and the redraw `effect`.

Compared with the hello world:

- `count` became the model's `row` and `col` signals, in `model.js`.
- `template` moved to `view.js`.
- `effect(() => render(…))` is the redraw line in `main.js`.
- `@click` became `controller.js` (key → command) plus `addEventListener` in `main.js`.
- New: `computed(fn)`, a read-only signal whose value is `fn` of other signals. The model hands out `computed` wrappers so that no other file can write its state.

**Build: a step counter.** Show, under the hex readout, how many ticks the dot has moved. Hint: a new signal in `model.js` that `update` increments, a `computed` to hand it out, and one slot in the template.

<details>
<summary>Solution</summary>

`singleton/model.js`, three new lines:

```js
let cmd = Cmd.STOP;                         // not shown on screen, so plain variable
const steps = signal(0);                    // new: ticks the dot moved

export const model = {
  // ...
  hex: computed(() => (row.value << 4) | col.value),
  steps: computed(() => steps.value),       // new: read-only to outsiders, like row and col
  update(c) {
    if (c !== Cmd.NONE) cmd = c;
    if (cmd !== Cmd.STOP) steps.value++;    // new
    switch (cmd) {
```

`singleton/view.js`, the end of the template:

```js
  <output>${m.hex.value.toString(16).toUpperCase().padStart(2, '0')}</output>
  <p>steps: ${m.steps.value}</p>`;
```

A `<p>` rather than a second `<output>`, because two `<output>`s sit on one line and their numbers run together. The view reads `m.steps.value` inside the effect, so each moving tick redraws; after Space, `update` writes nothing and nothing redraws.

</details>

Then run `uv run --no-project python .checks/boundaries.py`. It checks the repo's MVC rules and names the rule you broke, so use it as a tutor: write `m.row.value = 0;` in `view.js` and it answers `only model.js writes signal values`.

## Step 2: factory

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *factory*, *closure*.
2. `git diff --no-index -w singleton factory` in a terminal. `-w` hides the re-indentation, so only the real changes show.
3. [Code walkthrough → `factory/`](HOW_AND_WALKTHROUGH.md#factory), all five files. Each one explains only what changed from the singleton.
4. [Singleton vs factory vs class](HOW_AND_WALKTHROUGH.md#singleton-vs-factory-vs-class): its introduction, [Obvious differences](HOW_AND_WALKTHROUGH.md#obvious-differences), [Subtle differences](HOW_AND_WALKTHROUGH.md#subtle-differences) items 1–5, and the singleton and factory halves of [Pros and cons](HOW_AND_WALKTHROUGH.md#pros-and-cons).

The whole pattern is three moves: wrap the file-level state in a function, `return` the object, and have `main.js` call the function. The returned functions keep using the locals of the call that made them; that is the closure.

**Build 1:** add the step counter to `factory/`. Hint: `steps` goes inside `createModel`, next to `row` and `col`.

**Build 2: two dots**, the thing a singleton can't do. Add a second grid whose dot starts at row 0, column 0 and moves with the same keys. Hint: give `createModel` arguments, then create a second model and view in `main.js`.

<details>
<summary>Solution</summary>

`index.html`, after `<div id="app-factory"></div>`:

```html
  <div id="app-factory-2"></div>
```

`factory/model.js` (with the step counter from Build 1):

```js
export function createModel(startRow = 4, startCol = 7) {   // = 4: used when no argument is given
  const row = signal(startRow), col = signal(startCol);
  let cmd = Cmd.STOP;
  const steps = signal(0);
  return {
    // ...
    steps: computed(() => steps.value),
    update(c) {
      if (c !== Cmd.NONE) cmd = c;
      if (cmd !== Cmd.STOP) steps.value++;
```

`factory/main.js`:

```js
const model = createModel();
const view = createView(document.querySelector('#app-factory'));
const controller = createController();
const model2 = createModel(0, 0);
const view2 = createView(document.querySelector('#app-factory-2'));

window.addEventListener('keydown', controller.keydown);  // the browser calls it on each key press

setInterval(() => {                          // the NMI tick
  const c = controller.read();               // read once: read() clears the latch
  model.update(c);
  model2.update(c);
}, 150);

effect(() => view.update(model));            // redraw only on change
effect(() => view2.update(model2));
```

Why read once: `read()` empties the latch, so a second `controller.read()` in the same tick returns `Cmd.NONE`, and `model2` would never get a command and never move. Giving each copy its own start is what the walkthrough calls settings per copy (Subtle differences, item 3).

</details>

## Step 3: class

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *class*, *# (private member)*.
2. `git diff --no-index -w factory class`.
3. [Code walkthrough → `class/`](HOW_AND_WALKTHROUGH.md#class), all five files. Take your time on `main.js`: the `this` trap, the brand check, and the `handleEvent` footnote.
4. [Subtle differences](HOW_AND_WALKTHROUGH.md#subtle-differences) items 6–7, [Factory vs class](HOW_AND_WALKTHROUGH.md#factory-vs-class), and the class half of [Pros and cons](HOW_AND_WALKTHROUGH.md#pros-and-cons).

The pattern: `class Model { … }` is the blueprint, `new Model()` makes a copy, `#name` fields hold each copy's private state, and inside a method `this` is the copy it was called on (`model.update(c)` → `this` is `model`).

**Build:** add the step counter to `class/`. Hint: a `#steps` field, a public `steps` field, and `this.#…` everywhere the factory used a bare name.

<details>
<summary>Solution</summary>

`class/model.js`:

```js
  #cmd = Cmd.STOP;                          // not shown on screen, so plain variable
  #steps = signal(0);                       // new
  // ...
  hex = computed(() => (this.#row.value << 4) | this.#col.value);
  steps = computed(() => this.#steps.value); // new

  update(c) {
    if (c !== Cmd.NONE) this.#cmd = c;
    if (this.#cmd !== Cmd.STOP) this.#steps.value++;   // new
```

`class/view.js`: the same `<p>steps: …</p>` line as in step 1.

</details>

Optional: build the two dots here too. You'll need a `constructor(startRow, startCol)` (`class/view.js` has one). Field initializers such as `#row = signal(4)` run before the constructor body, so they can't see its arguments.

**The one trap to see once:** in `class/main.js`, replace `e => controller.keydown(e)` with plain `controller.keydown` and reload. The class dot ignores the arrows, and the browser console (F12) shows `TypeError: Cannot write private member #pending to an object whose class did not declare it`. Handed over on its own, the method loses its object: the browser calls it with `this` set to `window`.

## Step 4: your own small app

**Read:**

1. [Which to use](HOW_AND_WALKTHROUGH.md#which-to-use): which pattern fits which part.
2. The Architecture rules in [.claude/CLAUDE.md](.claude/CLAUDE.md): the repo's MVC rules, which become your checklist.

**Build:** back in `~/hello-signals`, build something of your own and split it into `model.js`, `view.js`, `controller.js` and `main.js` the way the repo does. Use the factory style, the walkthrough's default for parts you may want several of. Ideas: a traffic light that cycles on a timer, or a counter driven by `+` and `-` keys. `.checks/boundaries.py` checks only this repo's folders, not `~/hello-signals`, so you check the rules by hand.

## Cleaning up

- Undo your practice edits with `git restore index.html singleton factory class`. Not `git restore .`, which also throws away uncommitted edits to the docs.
- Restore before asking Claude anything in this repo. Claude's `Stop` hook runs the boundary check before each of its turns can end, so a practice edit that breaks a rule makes Claude try to fix it.
