[README.md](README.md) · [HOW_AND_WALKTHROUGH.md](HOW_AND_WALKTHROUGH.md) · [STUDY_PLAN_2.md](STUDY_PLAN_2.md)

# Study plan 1: one form, two tracks

The goal: by the end you know how a web page reads what the user typed and writes results back, first by hand and then with Preact Signals and lit-html. You build one small form app in plain DOM code (Build 0), then add four ideas, one per build:

- Preact Signals' `signal` and `effect`, which redraw the page by themselves;
- `computed`, for values worked out from other values;
- `batch`, for several changes that belong together;
- lit-html, which draws the whole page from one template.

Two tracks add them in different orders. Both start from Build 0 and end at the same code:

- **[Track 1](#track-1-signals-first), signals first:** signals, `computed`, `batch`, then lit-html. The page's markup stays in `index.html` until the last step, so each new idea lands in code you already know.
- **[Track 2](#track-2-lit-html-first), lit-html first:** lit-html, then signals, `computed` and `batch`.

Pick either. If you then do the other, it goes fast: you know every idea already, and only the order differs.

Every build has the same three parts, in one file: a **model**, which holds the data and the rule that changes it; a **view**, which writes the page from the model; and a **controller**, which turns what the user does into model updates. Each build changes only what its new idea needs, so you can compare it with the one before.

Each build has three steps: **read** the listed sections, in order; then copy the code, run it and read the notes under it; then **try** the things listed. You write no code in this plan: every build is printed in full. Afterwards, [STUDY_PLAN_2.md](STUDY_PLAN_2.md) takes the same tools into the dot runner, where the model, view and controller live in separate files.

## The app

- **Your name:** a text box.
- **Currency:** a dropdown list: USD, EUR, SGD.
- **`+1`:** a button that adds 1 to `bonds`, next to the text "we have N thousand(s) in bonds", where "thousand" takes no "s" when N is 1.
- **`rich`** sets bonds to 98 and savings to 765; **`poor`** sets bonds to 0 and savings to 123.
- **Savings:** a number box. A negative number, or one not finished yet (empty, `-` or `.`), counts as 0.
- **Total:** "*name* has a total of *currency* *bonds × 1000 + savings*", for example "Ann has a total of EUR 98765".

The app's state is four values, `userName`, `currency`, `bonds` and `savings`, held in one `model` object. Everything else on screen is worked out from them.

## Setup

From the repo root:

```bash
mkdir -p .temp/money-app && cp -r vendor .temp/money-app/
```

`.temp/` is scratch space inside the repo: git ignores everything in it except its `.placeholder` file, and the boundary check skips it, so your builds are neither committed nor checked. Build 0 uses no library; the later builds load Preact Signals and lit-html from that copy of `vendor/`. To run any build, from the repo root:

```bash
cd .temp/money-app && uv run --no-project python -m http.server 8001
```

Then open <http://localhost:8001>. Port 8001 leaves 8000 free for the repo. After you replace a file, reload the page; if a change doesn't show, hard-reload with Ctrl+Shift+R (Mac: Cmd+Shift+R). The browser's console, where `console.log` prints, is under F12 → Console. It may also show one `404` error for `favicon.ico`: browsers ask every site for a tab icon, and this one has none. It is harmless.

## Build 0: plain DOM

**Read:**

1. The README introduction and [Run](README.md#run): why the page needs a server.
2. [Terms](HOW_AND_WALKTHROUGH.md#terms): *DOM*, *querySelector*, *activeElement*, *addEventListener*, *semantic HTML*, *output*, *=> (arrow function)*.
3. [Code walkthrough → `index.html`](HOW_AND_WALKTHROUGH.md#indexhtml): tags, attributes and the module script. Skip the import map (this build has none) and all the CSS except the `body` rule, which this build reuses.

**Code:** `.temp/money-app/index.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Money</title>
  <style> :root { color-scheme: dark; } body { background: #333; color: #eee; } </style>
</head>
<body>
  <p><label>Your name: <input id="name"></label></p>
  <p><label>Currency:
    <select id="currency">
      <option>USD</option>
      <option>EUR</option>
      <option>SGD</option>
    </select></label></p>
  <p><button id="add-bond">+1</button> <output id="bonds"></output></p>
  <p><button id="rich">rich</button> <button id="poor">poor</button></p>
  <p><label>Savings: <input id="savings" type="number"></label></p>
  <p>Total: <output id="total"></output></p>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

- `<input id="name">`: an `<input>` with no `type` is a one-line text box. Wrapping it in a `<label>` with its text ties the two together: clicking "Your name:" puts the cursor in the box, and screen readers read the text as the box's name.
- `<select>` is the dropdown list and each `<option>` is one choice. An option with no `value` attribute uses its text as its value, so picking EUR gives `"EUR"`. The first option starts out selected.
- `<input type="number">` is a box for a number; the browser adds small up and down arrows to it. `<button>` is a button, and `<output>` is the element for a computed result, here empty until `main.js` fills it.
- `id="…"` gives each element a name that is unique in the page, so `main.js` can find it.
- `<style> :root { color-scheme: dark; } body { background: #333; color: #eee; } </style>` makes the whole page dark. `<style>` holds CSS rules, and this line has two:
  - `:root { color-scheme: dark; }` tells the browser the page is meant to be dark (`:root` is the `<html>` element), so it draws its own parts dark too: the text boxes, the dropdown, the buttons and the scrollbars. Without it they stay light, because form controls don't take on the page's colors.
  - `body { background: #333; color: #eee; }` is the repo's `index.html` rule: a dark gray background and light gray text. Colors are hex RGB, and three digits are short for six: `#333` is `#333333`, so red, green and blue are each 0x33 = 51 out of 255.
- `<script type="module">` runs `main.js` after the whole page has been parsed, so every element exists by then.

`.temp/money-app/main.js`:

```js
// DOM inputs
const nameBox = document.querySelector('#name');
const currencyBox = document.querySelector('#currency');
const addBondButton = document.querySelector('#add-bond');
const richButton = document.querySelector('#rich');
const poorButton = document.querySelector('#poor');
const savingsBox = document.querySelector('#savings');

// DOM outputs
const bondsOut = document.querySelector('#bonds');
const totalOut = document.querySelector('#total');

// Model state
const model = { userName: '', currency: 'USD', bonds: 0, savings: 0 };

// Update model: a field missing from the argument defaults to the model's current value, so it stays the same
function updateModel({ userName = model.userName, currency = model.currency,
                       bonds = model.bonds, savings = model.savings }) {
  model.userName = userName;
  model.currency = currency;
  model.bonds    = bonds;
  if (Number.isNaN(savings) || savings < 0) {
    model.savings = 0;          // "", ".", "-" (all NaN) and negatives count as 0
  } else {
    model.savings = savings;
  }
}

// Update View
function updateView() {
  // Don't rewrite the box while the user is typing in it: a number box reports "-" and "." as "",
  // so a write would erase them. Clicking rich or poor takes the focus away, so those still update it.
  if (document.activeElement !== savingsBox) savingsBox.value = model.savings;
  bondsOut.textContent = `we have ${model.bonds} thousand${model.bonds === 1 ? '' : 's'} in bonds`;
  totalOut.textContent = `${model.userName} has a total of ${model.currency} ${model.bonds * 1000 + model.savings}`;
}

// Controller Wiring for inputs
nameBox.addEventListener('input',       () => { updateModel({ userName: nameBox.value });           updateView(); });
currencyBox.addEventListener('change',  () => { updateModel({ currency: currencyBox.value });       updateView(); });
addBondButton.addEventListener('click', () => { updateModel({ bonds: model.bonds + 1 });            updateView(); });
richButton.addEventListener('click',    () => { updateModel({ bonds: 98, savings: 765 });           updateView(); });
poorButton.addEventListener('click',    () => { updateModel({ bonds: 0, savings: 123 });            updateView(); });
savingsBox.addEventListener('input',    () => { updateModel({ savings: savingsBox.valueAsNumber }); updateView(); });

updateView();
```

- **DOM inputs and outputs:** `document.querySelector('#name')` returns the first element that matches the CSS selector `#name`: the element with `id="name"`. Each `const` holds a reference to the live element, not a copy, much like a pointer to a memory-mapped register: reading its `value` gives what the box shows now, and writing it changes the page. Where the analogy breaks down: the screen shows the change only after your code returns, not at the moment of the write.
- **Model state:** `{ userName: '', currency: 'USD', … }` is an object literal, a table of named fields, like a C struct filled in one line. `model` is `const` because it always names this one object; its fields still change. The fields match how the page starts: an empty name box, and USD, the first option. It is `userName`, not `name`, because browsers already have a global `name` (`window.name`, the tab's name), which VS Code marks as deprecated wherever a plain `name` looks like it.
- **Update model:** `updateModel` is the only code that writes the model, much like `model_update()` in the C original. It takes one object, such as `{ bonds: 98, savings: 765 }`, and its parameter list *destructures* it: `{ userName = model.userName, … }` copies each field into a local variable of the same name ([MDN: destructuring](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring#default_value)). A field the object doesn't have, or has as `undefined`, takes its default instead, here the model's current value, read at the moment of the call. So `updateModel({ bonds: 98, savings: 765 })` sets those two fields and writes the other two back unchanged.
- **The savings rule:** `Number.isNaN(savings) || savings < 0` is true when the new value is not a number, which is what the box reports for an empty box, `-` or `.`, or when it is negative; then the model stores 0. `Number.isNaN` is needed because `savings === NaN` is always false: by the IEEE 754 floating-point rules, which C's `double` follows too, `NaN` equals nothing, itself included. Because the rule sits in the model, every number gets it, whichever handler it comes from.
- **Update View:** `updateView` writes the page from the model; [Writing the DOM](#writing-the-dom) below explains each line. `` `we have ${model.bonds} thousand…` `` is a template literal: a string in backticks, where `${expr}` inserts the value of any expression. `model.bonds === 1 ? '' : 's'` adds the "s" except when bonds is 1. `===` is equality without type conversion, and `? :` works as in C.
- **Controller wiring:** each listener does the same two steps: tell the model what the user did, with `updateModel`, then redraw, with `updateView()`. The last line draws the first frame, which also puts the starting 0 into the savings box.

### Reading the DOM

Reading means two things: getting a value out of an element, and learning when it changed. For the second, you ask the browser to call a function. `element.addEventListener('input', fn)` calls `fn` each time an `input` event happens on that element. Your code never polls; it waits to be called, like an interrupt handler.

- **`userName`:** `nameBox.value` is the text in the box, always a string. The `input` event fires on every change to that text (each key press, paste or delete), so the total follows as you type. The `change` event would fire only when you leave the box.
- **`currency`:** `currencyBox.value` is the value of the chosen option. A `<select>` fires `change` as soon as a new option is picked.
- **The `+1`, `rich` and `poor` buttons:** a button has no value to read. You read it by listening for `click`, which fires for a mouse click, and also for Enter or Space while the button has keyboard focus.
- **`savings`:** `savingsBox.value` is a string here too, even in a number box: `"12"`, not `12`. Adding a string to a number joins them as text, so `98000 + "12"` is `"9800012"`. `savingsBox.valueAsNumber` gives the number `12` instead, or `NaN` ("not a number") when the box holds no valid number: when it is empty, or holds only `-` or `.`, the half-typed starts of `-5` and `.5`. The model counts `NaN` and negative numbers as 0.

### Writing the DOM

- **"we have N thousand(s) in bonds" and the total:** `element.textContent = text` replaces everything inside the element with that text. `updateView` writes both `<output>`s from the model.
- **`textContent`, not `innerHTML`:** `innerHTML = text` would parse the text as HTML. The name is whatever the user typed: as HTML, `<b>Bo</b>` would show in bold, and a name such as `<img src=x onerror=alert(1)>` would run code. `textContent` shows it exactly as typed.
- **The savings box is written too,** so it is on both sides, but never while it has the keyboard focus. `document.activeElement` (see Terms) is the element your keys go to. A number box reports `-` and `.` as `""`, so half-typed text can't be read back, and writing the model's `0` into the box would erase it. So:
  - while you type, the box is yours: `-`, `.` and an empty box stay as typed, and the total counts them as 0;
  - after `rich` or `poor`, the click has moved the focus to the button, so the box shows the new number;
  - after you leave the box, the next update writes the model's number, so a lone `-` becomes `0`.

  Writing `.value` fires no `input` event, which reports only the user's own changes, so writing the box never calls its handler.

The pattern: every user action runs the same loop, controller → `updateModel` → `updateView()`. The state lives only in `model`; the page is a copy that `updateView` refreshes. Two costs remain. Every handler must remember `updateView()`: forget it in one, and that part of the screen goes stale with no error. And `updateView` rewrites both outputs each time, changed or not. Signals remove the `updateView()` calls (Builds 1.1 and 2.2), and lit-html draws the page from one template that writes only what changed (Builds 1.4 and 2.1).

**Try it:**

- Type a name: the total follows each key press.
- Click `+1` once: "we have 1 thousand in bonds". Click it again: "2 thousands".
- Click `rich`: the box shows 765 and the total ends in 98765. Click `poor`: 123.
- In the savings box, type `1.5`: it stays as typed, and the total ends in 1.5.
- Select the number and type `-5`: the `-` stays while you type, and the total counts the box as 0. Type `.5` the same way: the `.` stays, then the total counts 0.5.
- Leave a lone `-` in the savings box, click into the name box and type a letter: the savings box changes to `0`.
- Type `<b>Bo</b>` as your name: the total shows it as typed, not in bold.

## Track 1: signals first

Signals go into Build 0's plain DOM code, and lit-html comes last. The form stays in `index.html` until Build 1.4.

### Build 1.1: signal and effect

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *import map*, *signal*, *effect*.
2. The signals-core README: [`signal(initialValue)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#signalinitialvalue) and [`effect(fn)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#effectfn), the first example of each.

**Code:** replace `.temp/money-app/index.html` with this, which stays the same through Build 1.3:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Money</title>
  <style> :root { color-scheme: dark; } body { background: #333; color: #eee; } </style>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
</head>
<body>
  <p><label>Your name: <input id="name"></label></p>
  <p><label>Currency:
    <select id="currency">
      <option>USD</option>
      <option>EUR</option>
      <option>SGD</option>
    </select></label></p>
  <p><button id="add-bond">+1</button> <output id="bonds"></output></p>
  <p><button id="rich">rich</button> <button id="poor">poor</button></p>
  <p><label>Savings: <input id="savings" type="number"></label></p>
  <p>Total: <output id="total"></output></p>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

Replace `.temp/money-app/main.js` with:

```js
import { signal, effect } from '@preact/signals-core';

// DOM inputs
const nameBox = document.querySelector('#name');
const currencyBox = document.querySelector('#currency');
const addBondButton = document.querySelector('#add-bond');
const richButton = document.querySelector('#rich');
const poorButton = document.querySelector('#poor');
const savingsBox = document.querySelector('#savings');

// DOM outputs
const bondsOut = document.querySelector('#bonds');
const totalOut = document.querySelector('#total');

// Model state: each field is a signal
const model = { userName: signal(''), currency: signal('USD'), bonds: signal(0), savings: signal(0) };

// Update model: a field missing from the argument defaults to the model's current value, so it stays the same
function updateModel({ userName = model.userName.value, currency = model.currency.value,
                       bonds = model.bonds.value, savings = model.savings.value }) {
  model.userName.value = userName;
  model.currency.value = currency;
  model.bonds.value    = bonds;
  if (Number.isNaN(savings) || savings < 0) {
    model.savings.value = 0;    // "", ".", "-" (all NaN) and negatives count as 0
  } else {
    model.savings.value = savings;
  }
}

// Update View
function updateView() {
  // Don't rewrite the box while the user is typing in it: a number box reports "-" and "." as "",
  // so a write would erase them. Clicking rich or poor takes the focus away, so those still update it.
  if (document.activeElement !== savingsBox) savingsBox.value = model.savings.value;
  bondsOut.textContent = `we have ${model.bonds.value} thousand${model.bonds.value === 1 ? '' : 's'} in bonds`;
  totalOut.textContent = `${model.userName.value} has a total of ${model.currency.value} ${model.bonds.value * 1000 + model.savings.value}`;
}

// Controller Wiring for inputs
nameBox.addEventListener('input',       () => updateModel({ userName: nameBox.value }));
currencyBox.addEventListener('change',  () => updateModel({ currency: currencyBox.value }));
addBondButton.addEventListener('click', () => updateModel({ bonds: model.bonds.value + 1 }));
richButton.addEventListener('click',    () => updateModel({ bonds: 98, savings: 765 }));
poorButton.addEventListener('click',    () => updateModel({ bonds: 0, savings: 123 }));
savingsBox.addEventListener('input',    () => updateModel({ savings: savingsBox.valueAsNumber }));

effect(() => {
  console.log('render');
  updateView();
});
```

- `index.html` gained an import map (see Terms): it tells the browser that `@preact/signals-core` means `./vendor/signals-core.mjs`. It already names lit-html too, for Build 1.4; the browser fetches a library only when some code imports it, so lit-html isn't loaded yet. The form stays where it was.
- `signal('')` makes a box holding one value, and `.value` reads or writes it. Each of the model's four fields is now a signal, so `model.bonds` is the box and `model.bonds.value` the number in it.
- `updateModel` keeps its shape; its reads and writes now go through `.value`. It writes every field on every call, changed or not, but writing a signal the value it already holds notifies nobody, so only the fields that really changed cause a redraw.
- `effect(fn)` runs `fn` once, now, and again each time a signal that `fn` read on its last run changes. Here it runs `updateView`, which reads all four signals, so a change to any of them redraws the page. `console.log('render')` prints a line in the console on each run.
- The handlers now only update the model: their `updateView()` calls are gone, and so is the startup call, because the effect's first run draws the first frame. `() => updateModel({ … })` is an arrow function whose body is one expression, so it needs no braces.
- The redraw happens inside the write: `model.bonds.value = 98` returns only after the effect has run and the page is updated. The README says so: "Changing a signal's value synchronously updates every computed and effect that depends on that signal".
- `updateView` is unchanged apart from the `.value` reads, the savings box line included: the effect now decides when it runs, and the focus check still keeps it away from the box you are typing in.

What changed from Build 0:

1. `index.html` gained the import map, and `main.js` imports `signal` and `effect`.
2. The model's fields became `signal`s, and every read and write goes through `.value`.
3. The `updateView()` calls are gone; one `effect` at the end runs `updateView` and logs `render`.

**Try it,** with the console open:

- Type `Ann`: three `render`s, one per key press.
- Click `+1`: one `render`.
- Click `rich`: **two** `render`s, one after `model.bonds.value = 98` and one after `model.savings.value = 765`. The writes to `userName` and `currency` store the values already there, so they cause none. In between, the page held bonds 98 with the old savings, for an instant. Build 1.3 removes that.
- Click `rich` again: no `render`. Every write stores the value that is already there.
- In the savings box, type `1.5`: it stays as typed. Select it and type `-5`: the `-` stays, and the total counts the box as 0.

### Build 1.2: computed

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *computed*.
2. The signals-core README: [`computed(fn)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#computedfn).

**Code:** replace `.temp/money-app/main.js` with:

```js
import { signal, computed, effect } from '@preact/signals-core';

// DOM inputs
const nameBox = document.querySelector('#name');
const currencyBox = document.querySelector('#currency');
const addBondButton = document.querySelector('#add-bond');
const richButton = document.querySelector('#rich');
const poorButton = document.querySelector('#poor');
const savingsBox = document.querySelector('#savings');

// DOM outputs
const bondsOut = document.querySelector('#bonds');
const totalOut = document.querySelector('#total');

// Model state: each field is a signal
const model = { userName: signal(''), currency: signal('USD'), bonds: signal(0), savings: signal(0) };

// Update model: a field missing from the argument defaults to the model's current value, so it stays the same
function updateModel({ userName = model.userName.value, currency = model.currency.value,
                       bonds = model.bonds.value, savings = model.savings.value }) {
  model.userName.value = userName;
  model.currency.value = currency;
  model.bonds.value    = bonds;
  if (Number.isNaN(savings) || savings < 0) {
    model.savings.value = 0;    // "", ".", "-" (all NaN) and negatives count as 0
  } else {
    model.savings.value = savings;
  }
}

// Derived values
const bondsText = computed(() => {
  console.log('bondsText');
  return `we have ${model.bonds.value} thousand${model.bonds.value === 1 ? '' : 's'} in bonds`;
});
const totalText = computed(() => `${model.userName.value} has a total of ${model.currency.value} ${model.bonds.value * 1000 + model.savings.value}`);

// Update View
function updateView() {
  // Don't rewrite the box while the user is typing in it: a number box reports "-" and "." as "",
  // so a write would erase them. Clicking rich or poor takes the focus away, so those still update it.
  if (document.activeElement !== savingsBox) savingsBox.value = model.savings.value;
  bondsOut.textContent = bondsText.value;
  totalOut.textContent = totalText.value;
}

// Controller Wiring for inputs
nameBox.addEventListener('input',       () => updateModel({ userName: nameBox.value }));
currencyBox.addEventListener('change',  () => updateModel({ currency: currencyBox.value }));
addBondButton.addEventListener('click', () => updateModel({ bonds: model.bonds.value + 1 }));
richButton.addEventListener('click',    () => updateModel({ bonds: 98, savings: 765 }));
poorButton.addEventListener('click',    () => updateModel({ bonds: 0, savings: 123 }));
savingsBox.addEventListener('input',    () => updateModel({ savings: savingsBox.valueAsNumber }));

effect(() => {
  console.log('render');
  updateView();
});
```

- `computed(fn)` makes a read-only signal whose value is `fn`'s result. It runs `fn` again only when one of the signals `fn` read has changed, and only when someone reads its `.value`; otherwise `.value` returns the stored result. `bondsText` and `totalText` hold the two sentences that `updateView` used to build. They sit with the model, because they are worked out from its data.
- `updateView`'s two `textContent` lines now read `bondsText.value` and `totalText.value`. The effect is subscribed to the two computeds, and through them to the signals they read.
- `bondsText` logs each time it recalculates. With a second statement, its arrow function needs braces and a `return` (see *=> (arrow function)* in Terms).
- What `computed` gives you:
  - each derived value has a name and one definition, outside the view, and any code can read it;
  - it is cached: typing a name re-runs the effect, but `bondsText` is not recalculated, because `bonds` didn't change;
  - it is read-only: `bondsText.value = 'x'` throws a `TypeError`.

  At this size the caching saves nothing you could measure. It pays off when a derived value is costly to work out, such as a long sorted list, or is read in several places, since it is then worked out once and shared.

What changed from Build 1.1:

1. `computed` joined the import.
2. Two computeds hold the two sentences.
3. `updateView`'s two `textContent` lines read them.

**Try it,** with the console open:

- Type a name: one `render` per key press, and no `bondsText`.
- Click `+1`: `bondsText`, then `render`. Before it re-runs an effect, Preact Signals recalculates the computeds the effect read, to check that something really changed, so the computed logs first.
- Click `rich`: `bondsText`, `render`, `render`. The second run comes from the `savings` write, and `bondsText` doesn't recalculate for it: `bonds` hasn't changed since the first run.

### Build 1.3: batch

**Read:** the signals-core README: [`batch(fn)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#batchfn), its first example.

**Code:** replace `.temp/money-app/main.js` with:

```js
import { signal, computed, effect, batch } from '@preact/signals-core';

// DOM inputs
const nameBox = document.querySelector('#name');
const currencyBox = document.querySelector('#currency');
const addBondButton = document.querySelector('#add-bond');
const richButton = document.querySelector('#rich');
const poorButton = document.querySelector('#poor');
const savingsBox = document.querySelector('#savings');

// DOM outputs
const bondsOut = document.querySelector('#bonds');
const totalOut = document.querySelector('#total');

// Model state: each field is a signal
const model = { userName: signal(''), currency: signal('USD'), bonds: signal(0), savings: signal(0) };

// Update model: a field missing from the argument defaults to the model's current value, so it stays the same
function updateModel({ userName = model.userName.value, currency = model.currency.value,
                       bonds = model.bonds.value, savings = model.savings.value }) {
  batch(() => {
    model.userName.value = userName;
    model.currency.value = currency;
    model.bonds.value    = bonds;
    if (Number.isNaN(savings) || savings < 0) {
      model.savings.value = 0;    // "", ".", "-" (all NaN) and negatives count as 0
    } else {
      model.savings.value = savings;
    }
  });
}

// Derived values
const bondsText = computed(() => {
  console.log('bondsText');
  return `we have ${model.bonds.value} thousand${model.bonds.value === 1 ? '' : 's'} in bonds`;
});
const totalText = computed(() => `${model.userName.value} has a total of ${model.currency.value} ${model.bonds.value * 1000 + model.savings.value}`);

// Update View
function updateView() {
  // Don't rewrite the box while the user is typing in it: a number box reports "-" and "." as "",
  // so a write would erase them. Clicking rich or poor takes the focus away, so those still update it.
  if (document.activeElement !== savingsBox) savingsBox.value = model.savings.value;
  bondsOut.textContent = bondsText.value;
  totalOut.textContent = totalText.value;
}

// Controller Wiring for inputs
nameBox.addEventListener('input',       () => updateModel({ userName: nameBox.value }));
currencyBox.addEventListener('change',  () => updateModel({ currency: currencyBox.value }));
addBondButton.addEventListener('click', () => updateModel({ bonds: model.bonds.value + 1 }));
richButton.addEventListener('click',    () => updateModel({ bonds: 98, savings: 765 }));
poorButton.addEventListener('click',    () => updateModel({ bonds: 0, savings: 123 }));
savingsBox.addEventListener('input',    () => updateModel({ savings: savingsBox.valueAsNumber }));

effect(() => {
  console.log('render');
  updateView();
});
```

- `batch(fn)` runs `fn` and holds back every effect until `fn` returns; then each effect whose signals changed runs once. `updateModel` is the only code that writes the model, so one `batch` there covers every action: `rich`, `poor`, and any later one that changes several fields at once. An update that changes one field runs the effect once, as before.
- On screen nothing changes from Build 1.2. The browser runs JavaScript and paints the page on the same thread, and it paints only after the click handler has returned, so Build 1.2's half-updated page was never shown. What `batch` removes is the wasted run, and the moment in which the effect saw bonds 98 with the old savings.
- That moment matters once an effect does more than draw. An effect that logs the total, saves it, or sends it over the network would do so twice per click, once with a wrong total.

What changed from Build 1.2: `batch` joined the import, and `updateModel` wraps its writes in `batch(() => { … })`.

**Try it:**

- Click `rich`, then `poor`: each logs one `render` and one `bondsText`.
- Open F12 → Elements, expand the page, and type a name. Chrome briefly highlights each part of the page it changes, and both outputs flash: `updateView` rewrites the bonds sentence too, although it didn't change. Build 1.4 fixes that.

### Build 1.4: lit-html

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *html*, *container*, *render*.
2. [Code walkthrough → `singleton/`](HOW_AND_WALKTHROUGH.md#singleton) → `view.js`: the notes on `` html`…` `` and `render`. Skip the grid details.
3. lit.dev [Expressions](https://lit.dev/docs/templates/expressions/): [child](https://lit.dev/docs/templates/expressions/#child-expressions), [property](https://lit.dev/docs/templates/expressions/#property-expressions) and [event listener](https://lit.dev/docs/templates/expressions/#event-listener-expressions) expressions. lit.dev writes its examples inside Lit components, with `this.` in front of each value; here the values are plain variables.

**Code:** replace `.temp/money-app/index.html` with this shell:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Money</title>
  <style> :root { color-scheme: dark; } body { background: #333; color: #eee; } </style>
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

Replace `.temp/money-app/main.js` with:

```js
import { signal, computed, effect, batch } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: each field is a signal
const model = { userName: signal(''), currency: signal('USD'), bonds: signal(0), savings: signal(0) };

// Update model: a field missing from the argument defaults to the model's current value, so it stays the same
function updateModel({ userName = model.userName.value, currency = model.currency.value,
                       bonds = model.bonds.value, savings = model.savings.value }) {
  batch(() => {
    model.userName.value = userName;
    model.currency.value = currency;
    model.bonds.value    = bonds;
    if (Number.isNaN(savings) || savings < 0) {
      model.savings.value = 0;    // "", ".", "-" (all NaN) and negatives count as 0
    } else {
      model.savings.value = savings;
    }
  });
}

// Derived values
const bondsText = computed(() => {
  console.log('bondsText');
  return `we have ${model.bonds.value} thousand${model.bonds.value === 1 ? '' : 's'} in bonds`;
});
const totalText = computed(() => `${model.userName.value} has a total of ${model.currency.value} ${model.bonds.value * 1000 + model.savings.value}`);

// Update View
const template = () => html`
  <p><label>Your name: <input @input=${onName}></label></p>
  <p><label>Currency:
    <select @change=${onCurrency}>
      <option>USD</option>
      <option>EUR</option>
      <option>SGD</option>
    </select></label></p>
  <p><button @click=${onAddBond}>+1</button>
    <output>${bondsText.value}</output></p>
  <p><button @click=${onRich}>rich</button>
    <button @click=${onPoor}>poor</button></p>
  <p><label>Savings: <input id="savings" type="number" @input=${onSavings}></label></p>
  <p>Total: <output>${totalText.value}</output></p>`;

function updateView() {
  render(template(), document.querySelector('#app'));
  // The savings box has no .value slot, which would rewrite it while the user types; written here, as in Build 0.
  const savingsBox = document.querySelector('#savings');
  if (document.activeElement !== savingsBox) savingsBox.value = model.savings.value;
}

// Controller: the template's @ slots attach these
function onName(e)     { updateModel({ userName: e.target.value }); }
function onCurrency(e) { updateModel({ currency: e.target.value }); }
function onAddBond()   { updateModel({ bonds: model.bonds.value + 1 }); }
function onRich()      { updateModel({ bonds: 98, savings: 765 }); }
function onPoor()      { updateModel({ bonds: 0, savings: 123 }); }
function onSavings(e)  { updateModel({ savings: e.target.valueAsNumber }); }

effect(() => {
  console.log('render');
  updateView();
});
```

This is the final build: Track 2 ends with exactly this `main.js`.

- `index.html` lost the form and keeps only the `<style>` line, the import map and an empty `<div id="app">`, the container.
- `template` holds the same markup the form had, inside `` html`…` ``: a template literal with the tag `html` in front. It describes the page and changes nothing. Each `${…}` is a slot that lit-html fills, and three kinds appear here:
  - **Child slot,** between tags, as in `<output>${bondsText.value}</output>`: the value becomes text. lit-html always inserts it as text, never as HTML, so a slot is as safe as `textContent`.
  - **Event slot,** `@input=${onName}`: lit-html calls `addEventListener('input', onName)` on that element for you. Event slots replace the `addEventListener` lines, and with them all but one `querySelector` line and `id`.
  - **Property slot,** `.value=${…}`: sets an element's property, as `savingsBox.value = …` does. This page has none, on purpose. A slot writes whenever its value differs from the one it last wrote, and while you type `-5` the model's savings changes to 0, so a `.value` slot would write `0` over your `-`. A slot has no way to say "not while the box has the focus".
- So the savings box gets `id="savings"`, and `updateView` writes it by hand after `render`, with Build 0's line: `render` builds the box, `querySelector` finds it, and the focus check leaves it alone while you type.
- `updateView` now calls `render(template(), …)`, then writes the savings box. `render` compares each slot with its value from the last call and touches only the slots that changed, so typing a name now changes only the total's text, where Build 1.3 rewrote both outputs.
- **Controller:** the `addEventListener` lines became named functions, which the template's `@` slots attach. `e.target` is the element the event happened on: no variable holds the elements any more, so each handler gets its element from the event `e`. The template names the handlers before they are defined; that works because a `function` declaration exists from the start of the file, and the effect at the end is the first code to run them.
- **What lit-html adds, honestly.** For a fixed form like this one, the template mostly moves the markup from `index.html` into JavaScript, and signals already redraw only after a real change. What you gain is one place that describes the page, and `@` slots instead of `addEventListener` lines; the savings box shows a limit, since it still needs a hand-written write. lit-html pays off once the markup changes shape with the data: a list drawn with `.map` (as the dot runner's grid is), or a part shown or hidden with `? :`. Writing those by hand means creating, moving and deleting elements yourself.

What changed from Build 1.3:

1. The form moved from `index.html` into `template`, and the `querySelector` lines are gone, except the one in `updateView` that finds the savings box.
2. `updateView` calls `render`, then writes the savings box as before.
3. The `addEventListener` lines became named handlers that `@` slots attach, and the handlers get their element from `e.target`.

**Try it:** everything behaves as in Build 1.3, and the console shows the same lines. In F12 → Elements, typing a name now flashes only the total's text.

## Track 2: lit-html first

lit-html comes first, then signals. Start from [Build 0](#build-0-plain-dom); this track ends at the same `main.js` as [Build 1.4](#build-14-lit-html).

### Build 2.1: lit-html

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *import map*, *html*, *container*, *render*.
2. [Code walkthrough → `singleton/`](HOW_AND_WALKTHROUGH.md#singleton) → `view.js`: the notes on `` html`…` `` and `render`. Skip the grid details.
3. lit.dev [Expressions](https://lit.dev/docs/templates/expressions/): [child](https://lit.dev/docs/templates/expressions/#child-expressions), [property](https://lit.dev/docs/templates/expressions/#property-expressions) and [event listener](https://lit.dev/docs/templates/expressions/#event-listener-expressions) expressions. lit.dev writes its examples inside Lit components, with `this.` in front of each value; here the values are plain variables.

**Code:** replace `.temp/money-app/index.html` with this shell, which stays the same through Build 2.4:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Money</title>
  <style> :root { color-scheme: dark; } body { background: #333; color: #eee; } </style>
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

Replace `.temp/money-app/main.js` with:

```js
import { html, render } from 'lit-html';

// Model state
const model = { userName: '', currency: 'USD', bonds: 0, savings: 0 };

// Update model: a field missing from the argument defaults to the model's current value, so it stays the same
function updateModel({ userName = model.userName, currency = model.currency,
                       bonds = model.bonds, savings = model.savings }) {
  model.userName = userName;
  model.currency = currency;
  model.bonds    = bonds;
  if (Number.isNaN(savings) || savings < 0) {
    model.savings = 0;          // "", ".", "-" (all NaN) and negatives count as 0
  } else {
    model.savings = savings;
  }
}

// Update View
const template = () => html`
  <p><label>Your name: <input @input=${onName}></label></p>
  <p><label>Currency:
    <select @change=${onCurrency}>
      <option>USD</option>
      <option>EUR</option>
      <option>SGD</option>
    </select></label></p>
  <p><button @click=${onAddBond}>+1</button>
    <output>we have ${model.bonds} thousand${model.bonds === 1 ? '' : 's'} in bonds</output></p>
  <p><button @click=${onRich}>rich</button>
    <button @click=${onPoor}>poor</button></p>
  <p><label>Savings: <input id="savings" type="number" @input=${onSavings}></label></p>
  <p>Total: <output>${model.userName} has a total of ${model.currency} ${model.bonds * 1000 + model.savings}</output></p>`;

function updateView() {
  render(template(), document.querySelector('#app'));
  // The savings box has no .value slot, which would rewrite it while the user types; written here, as in Build 0.
  const savingsBox = document.querySelector('#savings');
  if (document.activeElement !== savingsBox) savingsBox.value = model.savings;
}

// Controller: the template's @ slots attach these
function onName(e)     { updateModel({ userName: e.target.value });        updateView(); }
function onCurrency(e) { updateModel({ currency: e.target.value });        updateView(); }
function onAddBond()   { updateModel({ bonds: model.bonds + 1 });          updateView(); }
function onRich()      { updateModel({ bonds: 98, savings: 765 });         updateView(); }
function onPoor()      { updateModel({ bonds: 0, savings: 123 });          updateView(); }
function onSavings(e)  { updateModel({ savings: e.target.valueAsNumber }); updateView(); }

updateView();
```

- `index.html` lost the form and gained the import map (see Terms) and an empty `<div id="app">`, the container. It already names both libraries, so it doesn't change again. The browser fetches a library only when some code imports it, so this build never loads Preact.
- The model and `updateModel` are unchanged. Only the view and the controller change.
- `template` holds the same markup as Build 0's `<body>`, inside `` html`…` ``: a template literal with the tag `html` in front. It describes the page and changes nothing. Each `${…}` is a slot that lit-html fills, and three kinds appear here:
  - **Child slot,** between tags, as in `<output>we have ${model.bonds} …</output>`: the value becomes text. lit-html always inserts it as text, never as HTML, so a slot is as safe as `textContent`.
  - **Event slot,** `@input=${onName}`: lit-html calls `addEventListener('input', onName)` on that element for you. Event slots replace Build 0's `addEventListener` lines, and with them all but one `querySelector` line and `id`.
  - **Property slot,** `.value=${…}`: sets an element's property, as Build 0's `savingsBox.value = …` does. This page has none, on purpose. A slot writes whenever its value differs from the one it last wrote, and while you type `-5` the model's savings changes to 0, so a `.value` slot would write `0` over your `-`. A slot has no way to say "not while the box has the focus".
- So the savings box gets `id="savings"`, and `updateView` writes it by hand after `render`, with Build 0's line: `render` builds the box, `querySelector` finds it, and the focus check leaves it alone while you type.
- `updateView` now calls `render`, which writes `template()` into the container, then writes the savings box. `render` compares each slot with its value from the last call and touches only the slots that changed: a key press in the name box changes only the total's text, where Build 0's `updateView` rewrote both outputs.
- **Controller:** the listeners became named functions, which the template's `@` slots attach. `e.target` is the element the event happened on. Build 0 kept each element in a variable; here none does, so each handler gets its element from the event `e`. The template names the handlers before they are defined; that works because a `function` declaration exists from the start of the file, and nothing runs before the last line, `updateView()`.

What changed from Build 0:

1. The form moved from `index.html` into `template`.
2. The `querySelector` lines are gone, except the one in `updateView` that finds the savings box, and the `addEventListener` lines became named handlers that `@` slots attach.
3. `updateView` calls `render` instead of writing each element by hand; only the savings box is still written by hand.

**Try it:** everything from Build 0 behaves the same. Then open F12 → Elements, expand the page, and type a name: Chrome briefly highlights each part of the page it changes, and only the total's text flashes.

### Build 2.2: signal and effect

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *signal*, *effect*.
2. The signals-core README: [`signal(initialValue)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#signalinitialvalue) and [`effect(fn)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#effectfn), the first example of each.

**Code:** replace `.temp/money-app/main.js` with:

```js
import { signal, effect } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: each field is a signal
const model = { userName: signal(''), currency: signal('USD'), bonds: signal(0), savings: signal(0) };

// Update model: a field missing from the argument defaults to the model's current value, so it stays the same
function updateModel({ userName = model.userName.value, currency = model.currency.value,
                       bonds = model.bonds.value, savings = model.savings.value }) {
  model.userName.value = userName;
  model.currency.value = currency;
  model.bonds.value    = bonds;
  if (Number.isNaN(savings) || savings < 0) {
    model.savings.value = 0;    // "", ".", "-" (all NaN) and negatives count as 0
  } else {
    model.savings.value = savings;
  }
}

// Update View
const template = () => html`
  <p><label>Your name: <input @input=${onName}></label></p>
  <p><label>Currency:
    <select @change=${onCurrency}>
      <option>USD</option>
      <option>EUR</option>
      <option>SGD</option>
    </select></label></p>
  <p><button @click=${onAddBond}>+1</button>
    <output>we have ${model.bonds.value} thousand${model.bonds.value === 1 ? '' : 's'} in bonds</output></p>
  <p><button @click=${onRich}>rich</button>
    <button @click=${onPoor}>poor</button></p>
  <p><label>Savings: <input id="savings" type="number" @input=${onSavings}></label></p>
  <p>Total: <output>${model.userName.value} has a total of ${model.currency.value} ${model.bonds.value * 1000 + model.savings.value}</output></p>`;

function updateView() {
  render(template(), document.querySelector('#app'));
  // The savings box has no .value slot, which would rewrite it while the user types; written here, as in Build 0.
  const savingsBox = document.querySelector('#savings');
  if (document.activeElement !== savingsBox) savingsBox.value = model.savings.value;
}

// Controller: the template's @ slots attach these
function onName(e)     { updateModel({ userName: e.target.value }); }
function onCurrency(e) { updateModel({ currency: e.target.value }); }
function onAddBond()   { updateModel({ bonds: model.bonds.value + 1 }); }
function onRich()      { updateModel({ bonds: 98, savings: 765 }); }
function onPoor()      { updateModel({ bonds: 0, savings: 123 }); }
function onSavings(e)  { updateModel({ savings: e.target.valueAsNumber }); }

effect(() => {
  console.log('render');
  updateView();
});
```

`index.html` stays as it is.

- `signal('')` makes a box holding one value, and `.value` reads or writes it. Each of the model's four fields is now a signal, so `model.bonds` is the box and `model.bonds.value` the number in it.
- `updateModel` keeps its shape; its reads and writes now go through `.value`. It writes every field on every call, changed or not, but writing a signal the value it already holds notifies nobody, so only the fields that really changed cause a redraw.
- `effect(fn)` runs `fn` once, now, and again each time a signal that `fn` read on its last run changes. Here it runs `updateView`, whose template reads all four signals, so a change to any of them redraws the page. `console.log('render')` prints a line in the console on each run.
- The handlers now only update the model: their `updateView()` calls are gone, and so is the startup call, because the effect's first run draws the first frame.
- The redraw happens inside the write: `model.bonds.value = 98` returns only after the effect has run and the page is updated. The README says so: "Changing a signal's value synchronously updates every computed and effect that depends on that signal".

What changed from Build 2.1:

1. `main.js` imports `signal` and `effect`, the model's fields became `signal`s, and every read and write goes through `.value`.
2. The `updateView()` calls are gone; one `effect` at the end runs `updateView` and logs `render`.

**Try it,** with the console open:

- Type `Ann`: three `render`s, one per key press.
- Click `+1`: one `render`.
- Click `rich`: **two** `render`s, one after `model.bonds.value = 98` and one after `model.savings.value = 765`. The writes to `userName` and `currency` store the values already there, so they cause none. In between, the page held bonds 98 with the old savings, for an instant. Build 2.4 removes that.
- Click `rich` again: no `render`. Every write stores the value that is already there.
- Select the savings and type `-5`: the `-` stays, and the total counts the box as 0.

### Build 2.3: computed

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *computed*.
2. The signals-core README: [`computed(fn)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#computedfn).

**Code:** replace `.temp/money-app/main.js` with:

```js
import { signal, computed, effect } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: each field is a signal
const model = { userName: signal(''), currency: signal('USD'), bonds: signal(0), savings: signal(0) };

// Update model: a field missing from the argument defaults to the model's current value, so it stays the same
function updateModel({ userName = model.userName.value, currency = model.currency.value,
                       bonds = model.bonds.value, savings = model.savings.value }) {
  model.userName.value = userName;
  model.currency.value = currency;
  model.bonds.value    = bonds;
  if (Number.isNaN(savings) || savings < 0) {
    model.savings.value = 0;    // "", ".", "-" (all NaN) and negatives count as 0
  } else {
    model.savings.value = savings;
  }
}

// Derived values
const bondsText = computed(() => {
  console.log('bondsText');
  return `we have ${model.bonds.value} thousand${model.bonds.value === 1 ? '' : 's'} in bonds`;
});
const totalText = computed(() => `${model.userName.value} has a total of ${model.currency.value} ${model.bonds.value * 1000 + model.savings.value}`);

// Update View
const template = () => html`
  <p><label>Your name: <input @input=${onName}></label></p>
  <p><label>Currency:
    <select @change=${onCurrency}>
      <option>USD</option>
      <option>EUR</option>
      <option>SGD</option>
    </select></label></p>
  <p><button @click=${onAddBond}>+1</button>
    <output>${bondsText.value}</output></p>
  <p><button @click=${onRich}>rich</button>
    <button @click=${onPoor}>poor</button></p>
  <p><label>Savings: <input id="savings" type="number" @input=${onSavings}></label></p>
  <p>Total: <output>${totalText.value}</output></p>`;

function updateView() {
  render(template(), document.querySelector('#app'));
  // The savings box has no .value slot, which would rewrite it while the user types; written here, as in Build 0.
  const savingsBox = document.querySelector('#savings');
  if (document.activeElement !== savingsBox) savingsBox.value = model.savings.value;
}

// Controller: the template's @ slots attach these
function onName(e)     { updateModel({ userName: e.target.value }); }
function onCurrency(e) { updateModel({ currency: e.target.value }); }
function onAddBond()   { updateModel({ bonds: model.bonds.value + 1 }); }
function onRich()      { updateModel({ bonds: 98, savings: 765 }); }
function onPoor()      { updateModel({ bonds: 0, savings: 123 }); }
function onSavings(e)  { updateModel({ savings: e.target.valueAsNumber }); }

effect(() => {
  console.log('render');
  updateView();
});
```

- `computed(fn)` makes a read-only signal whose value is `fn`'s result. It runs `fn` again only when one of the signals `fn` read has changed, and only when someone reads its `.value`; otherwise `.value` returns the stored result. `bondsText` and `totalText` hold the two sentences that the template used to build inline. They sit with the model, because they are worked out from its data.
- The template now reads `bondsText.value` and `totalText.value`. The effect is subscribed to the two computeds, and through them to the signals they read.
- `bondsText` logs each time it recalculates. With a second statement, its arrow function needs braces and a `return` (see *=> (arrow function)* in Terms).
- What `computed` gives you:
  - each derived value has a name and one definition, outside the markup, and any code can read it;
  - it is cached: typing a name re-runs the effect, but `bondsText` is not recalculated, because `bonds` didn't change;
  - it is read-only: `bondsText.value = 'x'` throws a `TypeError`.

  At this size the caching saves nothing you could measure. It pays off when a derived value is costly to work out, such as a long sorted list, or is read in several places, since it is then worked out once and shared.

What changed from Build 2.2:

1. `computed` joined the import.
2. Two computeds hold the two sentences.
3. The two `<output>` slots read them.

**Try it,** with the console open:

- Type a name: one `render` per key press, and no `bondsText`.
- Click `+1`: `bondsText`, then `render`. Before it re-runs an effect, Preact Signals recalculates the computeds the effect read, to check that something really changed, so the computed logs first.
- Click `rich`: `bondsText`, `render`, `render`. The second run comes from the `savings` write, and `bondsText` doesn't recalculate for it: `bonds` hasn't changed since the first run.

### Build 2.4: batch

**Read:** the signals-core README: [`batch(fn)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#batchfn), its first example.

**Code:** in `.temp/money-app/main.js`, add `batch` to the import on the first line, and change `updateModel` to:

```js
function updateModel({ userName = model.userName.value, currency = model.currency.value,
                       bonds = model.bonds.value, savings = model.savings.value }) {
  batch(() => {
    model.userName.value = userName;
    model.currency.value = currency;
    model.bonds.value    = bonds;
    if (Number.isNaN(savings) || savings < 0) {
      model.savings.value = 0;    // "", ".", "-" (all NaN) and negatives count as 0
    } else {
      model.savings.value = savings;
    }
  });
}
```

The whole file is now exactly [Build 1.4's `main.js`](#build-14-lit-html), so you can also copy it from there.

- `batch(fn)` runs `fn` and holds back every effect until `fn` returns; then each effect whose signals changed runs once. `updateModel` is the only code that writes the model, so one `batch` there covers every action: `rich`, `poor`, and any later one that changes several fields at once. An update that changes one field runs the effect once, as before.
- On screen nothing changes from Build 2.3. The browser runs JavaScript and paints the page on the same thread, and it paints only after the click handler has returned, so Build 2.3's half-updated page was never shown. What `batch` removes is the wasted run, and the moment in which the effect saw bonds 98 with the old savings.
- That moment matters once an effect does more than draw. An effect that logs the total, saves it, or sends it over the network would do so twice per click, once with a wrong total.

What changed from Build 2.3: `batch` joined the import, and `updateModel` wraps its writes in `batch(() => { … })`.

**Try it:** click `rich`, then `poor`. Each logs one `bondsText` and one `render`.

## Next

[STUDY_PLAN_2.md](STUDY_PLAN_2.md) uses the same tools on the dot runner and puts the model, the view and the controller in separate files. Its Step 0 builds a lit-html and Preact Signals hello world, which repeats Builds 1 and 2 here, so you can go through it quickly. Delete `.temp/money-app` when you no longer need it.
