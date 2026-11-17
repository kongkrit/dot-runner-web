# Study plan 1: one form, five builds

The goal: by the end you know how a web page reads what the user typed and writes results back, first by hand and then with lit-html and Preact Signals. You build one small form app five times, and each build adds one idea:

0. plain DOM code, no libraries;
1. lit-html, which draws the whole page from one template;
2. Preact Signals' `signal` and `effect`, which redraw the page by themselves;
3. `computed`, for values worked out from other values;
4. `batch`, for several changes that belong together.

Each build has three parts: **read** the listed sections, in order; then copy the code, run it and read the notes under it; then **try** the things listed. You write no code in this plan: every build is printed in full. Afterwards, [STUDY_PLAN_2.md](STUDY_PLAN_2.md) takes the same tools into the dot runner and splits an app into model, view and controller.

## The app

- **Your name:** a text box.
- **Currency:** a dropdown list: USD, EUR, SGD.
- **`+1`:** a button that adds 1 to `bonds`, next to the text "we have N thousand(s) in bonds", where "thousand" takes no "s" when N is 1.
- **`rich`** sets bonds to 98 and savings to 765; **`poor`** sets bonds to 0 and savings to 123.
- **Savings:** a number box that refuses negative numbers.
- **Total:** "*name* has a total of *currency* *bonds × 1000 + savings*", for example "Ann has a total of EUR 98765".

The app's state is four values: `name`, `currency`, `bonds` and `savings`. Everything else on screen is worked out from them.

## Setup

From the repo root:

```bash
mkdir ~/money-app && cp -r vendor ~/money-app/
```

Build 0 uses no library; Builds 1–4 load lit-html and Preact Signals from that copy of `vendor/`. To run any build:

```bash
cd ~/money-app && uv run --no-project python -m http.server 8001
```

Then open <http://localhost:8001>. Port 8001 leaves 8000 free for the repo. After you replace a file, reload the page; if a change doesn't show, hard-reload with Ctrl+Shift+R (Mac: Cmd+Shift+R). The browser's console, where `console.log` prints, is under F12 → Console. It may also show one `404` error for `favicon.ico`: browsers ask every site for a tab icon, and this one has none. It is harmless.

## Build 0: plain DOM

**Read:**

1. The README introduction and [Run](README.md#run): why the page needs a server.
2. [Terms](HOW_AND_WALKTHROUGH.md#terms): *DOM*, *semantic HTML*, *=> (arrow function)*.
3. [Code walkthrough → `index.html`](HOW_AND_WALKTHROUGH.md#indexhtml): tags, attributes and the module script. Skip the import map and the CSS; this build has neither.

**Code:** `~/money-app/index.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Money</title>
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
- `id="…"` gives each element a name that is unique in the page, so `main.js` can find it. There is no `<style>`, so everything has the browser's default look.
- `<script type="module">` runs `main.js` after the whole page has been parsed, so every element exists by then.

`~/money-app/main.js`:

```js
const nameBox = document.querySelector('#name');
const currencyBox = document.querySelector('#currency');
const addBondButton = document.querySelector('#add-bond');
const richButton = document.querySelector('#rich');
const poorButton = document.querySelector('#poor');
const savingsBox = document.querySelector('#savings');
const bondsOut = document.querySelector('#bonds');
const totalOut = document.querySelector('#total');

let name = '', currency = 'USD', bonds = 0, savings = 0;

function draw() {
  bondsOut.textContent = `we have ${bonds} thousand${bonds === 1 ? '' : 's'} in bonds`;
  totalOut.textContent = `${name} has a total of ${currency} ${bonds * 1000 + savings}`;
}

function setMoney(b, s) {
  bonds = b;
  savings = s;
  savingsBox.value = s;
  draw();
}

nameBox.addEventListener('input', () => { name = nameBox.value; draw(); });
currencyBox.addEventListener('change', () => { currency = currencyBox.value; draw(); });
addBondButton.addEventListener('click', () => { bonds++; draw(); });
richButton.addEventListener('click', () => setMoney(98, 765));
poorButton.addEventListener('click', () => setMoney(0, 123));
savingsBox.addEventListener('input', () => {
  const n = savingsBox.valueAsNumber;   // NaN when the box holds no number
  if (n >= 0) savings = n;              // NaN >= 0 is false, so this rejects NaN too
  else savingsBox.value = savings;      // rejected: put the last valid number back
  draw();
});

savingsBox.value = savings;
draw();
```

- `document.querySelector('#name')` returns the first element that matches the CSS selector `#name`: the element with `id="name"`. Each `const` holds a reference to the live element, not a copy, much like a pointer to a memory-mapped register: reading its `value` gives what the box shows now, and writing it changes the page. Where the analogy breaks down: the screen shows the change only after your code returns, not at the moment of the write.
- `let name = '', currency = 'USD', bonds = 0, savings = 0` declares the four state values on one line, as `int a = 0, b = 0;` does in C. They match how the page starts: an empty name box, and USD, the first option.
- `` `we have ${bonds} thousand…` `` is a template literal: a string in backticks, where `${expr}` inserts the value of any expression. `bonds === 1 ? '' : 's'` adds the "s" except when bonds is 1. `===` is equality without type conversion, and `? :` works as in C.

### Reading the DOM

Reading means two things: getting a value out of an element, and learning when it changed. For the second, you ask the browser to call a function. `element.addEventListener('input', fn)` calls `fn` each time an `input` event happens on that element. Your code never polls; it waits to be called, like an interrupt handler.

- **`name`:** `nameBox.value` is the text in the box, always a string. The `input` event fires on every change to that text (each key press, paste or delete), so the total follows as you type. The `change` event would fire only when you leave the box.
- **`currency`:** `currencyBox.value` is the value of the chosen option. A `<select>` fires `change` as soon as a new option is picked.
- **The `+1`, `rich` and `poor` buttons:** a button has no value to read. You read it by listening for `click`, which fires for a mouse click, and also for Enter or Space while the button has keyboard focus.
- **`savings`:** `savingsBox.value` is a string here too, even in a number box: `"12"`, not `12`. Adding a string to a number joins them as text, so `98000 + "12"` is `"9800012"`. `savingsBox.valueAsNumber` gives the number `12` instead, or `NaN` ("not a number") when the box holds no valid number, as when it is empty or holds only a `-`. The handler keeps `n` only when `n >= 0`. That one test rejects both negative numbers and `NaN`, because every `<`, `>`, `<=` or `>=` comparison with `NaN` is false.

### Writing the DOM

- **"we have N thousand(s) in bonds" and the total:** `element.textContent = text` replaces everything inside the element with that text. `draw()` writes both `<output>`s from the four state values, and every handler calls it after a change.
- **`textContent`, not `innerHTML`:** `innerHTML = text` would parse the text as HTML. The name is whatever the user typed: as HTML, `<b>Bo</b>` would show in bold, and a name such as `<img src=x onerror=alert(1)>` would run code. `textContent` shows it exactly as typed.
- **The savings box is written too,** so it is on both sides. `setMoney` writes `savingsBox.value = s` for `rich` and `poor`, and the input handler writes it to put back the last valid number after a rejected one. Writing `.value` changes what the box shows and fires no `input` event, which reports only the user's own changes, so writing the box never calls the handler again.
- The last two lines put the starting savings into the box and draw the first frame.

The pattern: the state lives in four variables, and the page holds a copy that the code keeps in step by hand. Every handler reads a value, updates a variable and calls `draw()`. Forget `draw()` in one handler and that part of the screen goes stale, with no error. The writes are also spread out: `draw()` writes the outputs, and `setMoney` and the input handler write the savings box. Build 1 puts the page's writes in one template, and Build 2 removes the `draw()` calls.

**Try it:**

- Type a name: the total follows each key press.
- Click `+1` once: "we have 1 thousand in bonds". Click it again: "2 thousands".
- Click `rich`: the box shows 765 and the total ends in 98765. Click `poor`: 123.
- In the savings box, select the number and type `-`: the number comes back at once. Delete the digits one by one: the last one stays, because an empty box holds no number either. To enter a new number, select the old one and type over it.
- Type `<b>Bo</b>` as your name: the total shows it as typed, not in bold.

## Build 1: lit-html

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *import map*, *html*, *container*, *render*.
2. [Code walkthrough → `singleton/`](HOW_AND_WALKTHROUGH.md#singleton) → `view.js`: the notes on `` html`…` `` and `render`. Skip the grid details.
3. lit.dev [Expressions](https://lit.dev/docs/templates/expressions/): [child](https://lit.dev/docs/templates/expressions/#child-expressions), [property](https://lit.dev/docs/templates/expressions/#property-expressions) and [event listener](https://lit.dev/docs/templates/expressions/#event-listener-expressions) expressions. lit.dev writes its examples inside Lit components, with `this.` in front of each value; here the values are plain variables.

**Code:** replace `~/money-app/index.html` with this shell, which stays the same through Build 4:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Money</title>
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

Replace `~/money-app/main.js` with:

```js
import { html, render } from 'lit-html';

let name = '', currency = 'USD', bonds = 0, savings = 0;

function setMoney(b, s) {
  bonds = b;
  savings = s;
  draw();
}

function onSavings(e) {
  const n = e.target.valueAsNumber;     // NaN when the box holds no number
  if (n >= 0) savings = n;              // NaN >= 0 is false, so this rejects NaN too
  else e.target.value = savings;        // rejected: put the last valid number back
  draw();
}

const template = () => html`
  <p><label>Your name: <input @input=${e => { name = e.target.value; draw(); }}></label></p>
  <p><label>Currency:
    <select @change=${e => { currency = e.target.value; draw(); }}>
      <option>USD</option>
      <option>EUR</option>
      <option>SGD</option>
    </select></label></p>
  <p><button @click=${() => { bonds++; draw(); }}>+1</button>
    <output>we have ${bonds} thousand${bonds === 1 ? '' : 's'} in bonds</output></p>
  <p><button @click=${() => setMoney(98, 765)}>rich</button>
    <button @click=${() => setMoney(0, 123)}>poor</button></p>
  <p><label>Savings: <input type="number" .value=${savings} @input=${onSavings}></label></p>
  <p>Total: <output>${name} has a total of ${currency} ${bonds * 1000 + savings}</output></p>`;

const draw = () => render(template(), document.querySelector('#app'));

draw();
```

- `index.html` lost the form and gained the import map (see Terms) and an empty `<div id="app">`, the container. It already names both libraries, so it doesn't change again. The browser fetches a library only when some code imports it, so this build never loads Preact.
- `template` holds the same markup as Build 0's `<body>`, inside `` html`…` ``: a template literal with the tag `html` in front. It describes the page and changes nothing. Each `${…}` is a slot that lit-html fills, and three kinds appear here:
  - **Child slot,** between tags, as in `<output>we have ${bonds} …</output>`: the value becomes text. lit-html always inserts it as text, never as HTML, so a slot is as safe as `textContent`.
  - **Event slot,** `@input=${fn}`: lit-html calls `addEventListener('input', fn)` on that element for you. Event slots replace Build 0's `addEventListener` lines, and with them the `querySelector` lines and the `id`s.
  - **Property slot,** `.value=${savings}`: sets the box's `value` property, as `savingsBox.value = savings` did, the first time included. The dot matters. Without it, `value=${savings}` would set the `value` *attribute*, which only supplies the box's starting value: once the user has typed, changing the attribute no longer changes what the box shows.
- Only the savings box has a `.value` slot, because only its value is ever changed by code (by `rich` and `poor`). The name box and the currency list only report what the user did.
- `e.target` is the element the event happened on. Build 0 kept each element in a variable; here none does, so each handler gets its element from the event `e`.
- `draw()` must still follow every change, as in Build 0, but it now writes the whole page from one template. `render` compares each slot with its value from the last call and touches only the slots that changed: a key press in the name box changes only the total's text.
- That comparison is against what lit-html last wrote, not against what the box shows, which is why `onSavings` still puts the number back itself. After a rejected key `savings` is unchanged, so the `.value` slot gets the same value as last time and `render` leaves the box alone.
- `setMoney`, `onSavings` and the template all call `draw`, which is defined below them. That works because none of them runs before the last line, `draw()`, or a later event.

What changed from Build 0:

1. The form moved from `index.html` into `template`.
2. The eight `querySelector` lines and six `addEventListener` lines became `@` slots.
3. `draw()` calls `render` instead of setting `textContent` twice, and `setMoney` no longer writes the box: the `.value` slot does.
4. The handlers get their element from `e.target`.

**Try it:** everything from Build 0 behaves the same. Then open F12 → Elements, expand the page, and type a name: Chrome briefly highlights each part of the page it changes, and only the total's text flashes.

## Build 2: signal and effect

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *signal*, *effect*.
2. The signals-core README: [`signal(initialValue)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#signalinitialvalue) and [`effect(fn)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#effectfn), the first example of each.

**Code:** replace `~/money-app/main.js` with:

```js
import { signal, effect } from '@preact/signals-core';
import { html, render } from 'lit-html';

const name = signal(''), currency = signal('USD'), bonds = signal(0), savings = signal(0);

function setMoney(b, s) {
  bonds.value = b;
  savings.value = s;
}

function onSavings(e) {
  const n = e.target.valueAsNumber;     // NaN when the box holds no number
  if (n >= 0) savings.value = n;        // NaN >= 0 is false, so this rejects NaN too
  else e.target.value = savings.value;  // rejected: put the last valid number back
}

const template = () => html`
  <p><label>Your name: <input @input=${e => name.value = e.target.value}></label></p>
  <p><label>Currency:
    <select @change=${e => currency.value = e.target.value}>
      <option>USD</option>
      <option>EUR</option>
      <option>SGD</option>
    </select></label></p>
  <p><button @click=${() => bonds.value++}>+1</button>
    <output>we have ${bonds.value} thousand${bonds.value === 1 ? '' : 's'} in bonds</output></p>
  <p><button @click=${() => setMoney(98, 765)}>rich</button>
    <button @click=${() => setMoney(0, 123)}>poor</button></p>
  <p><label>Savings: <input type="number" .value=${savings.value} @input=${onSavings}></label></p>
  <p>Total: <output>${name.value} has a total of ${currency.value} ${bonds.value * 1000 + savings.value}</output></p>`;

effect(() => {
  console.log('render');
  render(template(), document.querySelector('#app'));
});
```

`index.html` stays as it is.

- `signal('')` makes a box holding one value, and `.value` reads or writes it. The four state values are now signals. They are `const` because each name always refers to the same box; only what is inside changes.
- `effect(fn)` runs `fn` once, now, and again each time a signal that `fn` read on its last run changes. The template reads all four signals, so a change to any of them redraws the page. `console.log('render')` prints a line in the console on each run.
- The handlers now only write signals: there is no `draw()` anywhere. `e => name.value = e.target.value` is an arrow function whose body is one expression, the assignment. Its result is returned, and lit-html ignores it.
- The redraw happens inside the write: `bonds.value = 98` returns only after the effect has run and the page is updated. The README says so: "Changing a signal's value synchronously updates every computed and effect that depends on that signal".
- After a rejected key, `onSavings` writes no signal, so no effect runs and nothing redraws. Putting the number back is still its own job.

What changed from Build 1:

1. The four `let`s became `signal`s, and every read and write goes through `.value`.
2. Every `draw()` call is gone, and `draw` itself became the `effect`.
3. The effect logs `render`.

**Try it,** with the console open:

- Type `Ann`: three `render`s, one per key press.
- Click `+1`: one `render`.
- Click `rich`: **two** `render`s, one after `bonds.value = 98` and one after `savings.value = 765`. In between, the page held bonds 98 with the old savings, for an instant. Build 4 removes that.
- Click `rich` again: no `render`. Both writes store the value that is already there, and writing the same value notifies nobody.
- Type `-` into the savings box: no `render`.

## Build 3: computed

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *computed*.
2. The signals-core README: [`computed(fn)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#computedfn).

**Code:** replace `~/money-app/main.js` with:

```js
import { signal, computed, effect } from '@preact/signals-core';
import { html, render } from 'lit-html';

const name = signal(''), currency = signal('USD'), bonds = signal(0), savings = signal(0);

const bondsText = computed(() => {
  console.log('bondsText');
  return `we have ${bonds.value} thousand${bonds.value === 1 ? '' : 's'} in bonds`;
});
const totalText = computed(() => `${name.value} has a total of ${currency.value} ${bonds.value * 1000 + savings.value}`);

function setMoney(b, s) {
  bonds.value = b;
  savings.value = s;
}

function onSavings(e) {
  const n = e.target.valueAsNumber;     // NaN when the box holds no number
  if (n >= 0) savings.value = n;        // NaN >= 0 is false, so this rejects NaN too
  else e.target.value = savings.value;  // rejected: put the last valid number back
}

const template = () => html`
  <p><label>Your name: <input @input=${e => name.value = e.target.value}></label></p>
  <p><label>Currency:
    <select @change=${e => currency.value = e.target.value}>
      <option>USD</option>
      <option>EUR</option>
      <option>SGD</option>
    </select></label></p>
  <p><button @click=${() => bonds.value++}>+1</button>
    <output>${bondsText.value}</output></p>
  <p><button @click=${() => setMoney(98, 765)}>rich</button>
    <button @click=${() => setMoney(0, 123)}>poor</button></p>
  <p><label>Savings: <input type="number" .value=${savings.value} @input=${onSavings}></label></p>
  <p>Total: <output>${totalText.value}</output></p>`;

effect(() => {
  console.log('render');
  render(template(), document.querySelector('#app'));
});
```

- `computed(fn)` makes a read-only signal whose value is `fn`'s result. It runs `fn` again only when one of the signals `fn` read has changed, and only when someone reads its `.value`; otherwise `.value` returns the stored result. `bondsText` and `totalText` hold the two sentences that the template used to build inline.
- The template now reads `bondsText.value` and `totalText.value`. The effect is subscribed to the two computeds, and through them to the signals they read.
- `bondsText` logs each time it recalculates. With a second statement, its arrow function needs braces and a `return` (see *=> (arrow function)* in Terms).
- What `computed` gives you:
  - each derived value has a name and one definition, outside the markup, and any code can read it;
  - it is cached: typing a name re-runs the effect, but `bondsText` is not recalculated, because `bonds` didn't change;
  - it is read-only: `bondsText.value = 'x'` throws a `TypeError`.

  At this size the caching saves nothing you could measure. It pays off when a derived value is costly to work out, such as a long sorted list, or is read in several places, since it is then worked out once and shared.

What changed from Build 2:

1. `computed` joined the import.
2. Two computeds hold the two sentences.
3. The two `<output>` slots read them.

**Try it,** with the console open:

- Type a name: one `render` per key press, and no `bondsText`.
- Click `+1`: `bondsText`, then `render`. Before it re-runs an effect, Preact Signals recalculates the computeds the effect read, to check that something really changed, so the computed logs first.
- Click `rich`: `bondsText`, `render`, `render`. The second run comes from the `savings` write, and `bondsText` doesn't recalculate for it: `bonds` hasn't changed since the first run.

## Build 4: batch

**Read:** the signals-core README: [`batch(fn)`](https://github.com/preactjs/signals/blob/%40preact/signals-core%401.14.5/packages/core/README.md#batchfn), its first example.

**Code:** replace `~/money-app/main.js` with:

```js
import { signal, computed, effect, batch } from '@preact/signals-core';
import { html, render } from 'lit-html';

const name = signal(''), currency = signal('USD'), bonds = signal(0), savings = signal(0);

const bondsText = computed(() => {
  console.log('bondsText');
  return `we have ${bonds.value} thousand${bonds.value === 1 ? '' : 's'} in bonds`;
});
const totalText = computed(() => `${name.value} has a total of ${currency.value} ${bonds.value * 1000 + savings.value}`);

function setMoney(b, s) {
  batch(() => {
    bonds.value = b;
    savings.value = s;
  });
}

function onSavings(e) {
  const n = e.target.valueAsNumber;     // NaN when the box holds no number
  if (n >= 0) savings.value = n;        // NaN >= 0 is false, so this rejects NaN too
  else e.target.value = savings.value;  // rejected: put the last valid number back
}

const template = () => html`
  <p><label>Your name: <input @input=${e => name.value = e.target.value}></label></p>
  <p><label>Currency:
    <select @change=${e => currency.value = e.target.value}>
      <option>USD</option>
      <option>EUR</option>
      <option>SGD</option>
    </select></label></p>
  <p><button @click=${() => bonds.value++}>+1</button>
    <output>${bondsText.value}</output></p>
  <p><button @click=${() => setMoney(98, 765)}>rich</button>
    <button @click=${() => setMoney(0, 123)}>poor</button></p>
  <p><label>Savings: <input type="number" .value=${savings.value} @input=${onSavings}></label></p>
  <p>Total: <output>${totalText.value}</output></p>`;

effect(() => {
  console.log('render');
  render(template(), document.querySelector('#app'));
});
```

- `batch(fn)` runs `fn` and holds back every effect until `fn` returns; then each effect whose signals changed runs once. `setMoney` is the only place where one action writes two signals, so it is the only place with a `batch`.
- On screen nothing changes from Build 3. The browser runs JavaScript and paints the page on the same thread, and it paints only after the click handler has returned, so Build 3's half-updated page was never shown. What `batch` removes is the wasted run, and the moment in which the effect saw bonds 98 with the old savings.
- That moment matters once an effect does more than draw. An effect that logs the total, saves it, or sends it over the network would do so twice per click, once with a wrong total.

What changed from Build 3: `batch` joined the import, and `setMoney` wraps its two writes in `batch(() => { … })`.

**Try it:** click `rich`, then `poor`. Each logs one `bondsText` and one `render`.

## Next

[STUDY_PLAN_2.md](STUDY_PLAN_2.md) uses the same tools on the dot runner and splits an app into model, view and controller. Its Step 0 builds a lit-html and Preact Signals hello world, which repeats Builds 1 and 2 here, so you can go through it quickly. Delete `~/money-app` when you no longer need it.
