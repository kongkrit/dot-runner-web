[README.md](README.md) · [HOW_AND_WALKTHROUGH.md](HOW_AND_WALKTHROUGH.md) · [STUDY_PLAN_1.md](STUDY_PLAN_1.md) · [STUDY_PLAN_3.md](STUDY_PLAN_3.md)

# Study plan 2: a name list, fifteen builds

<details>
<summary>The goal</summary>
<br>

The goal: see lit-html do the job it is made for. In [STUDY_PLAN_1.md](STUDY_PLAN_1.md)'s Build 5, the form's elements never change, only their text does, and Build 4's effects already handled that, so lit-html added little. Here the data decides how many rows the page has and in what order: rows appear, disappear and move. That is where hand-written DOM code grows with every feature, and lit-html code doesn't.

</details>

<details open>
<summary>The fifteen builds</summary>
<br>

You build one small app, a list of names, in fifteen steps, one per build:

1. append a name;
2. delete a row;
3. move a row up or down;
4. edit a name in place;
5. refuse a name already in the list, by searching the array;
6. the same, with a Set, which finds a name without searching;
7. edit a name in a pop-up dialog instead of in place.

From Build 8 on, the features are heavy on mobile and CSS:

8. animate the rows as they appear, disappear and move;
9. fit the page to a phone's screen, however long a name is;
10. delete a row by swiping it left;
11. make a name VIP, or not, by swiping it right;
12. make the left swipe show a Delete button instead;
13. make the right swipe show a VIP button instead;
14. move a row by holding it and dragging it;
15. make the other rows step aside while you drag.

</details>

<details>
<summary>How the builds are laid out</summary>
<br>

Builds 5 and 6 change only the model, so the view stays Build 4's. Build 7 changes only how a name is edited, and Build 8 only animates the changes. Build 9 fits the page to a phone, and Builds 10 to 15 add touch gestures; the buttons stay.

What never changes, the form and the table's caption and header, stays in `index.html`, written once. lit-html draws only the table's rows. Each build has STUDY_PLAN_1's three parts, in one `main.js`: a **model**, which holds the names and the one function that changes them; a **view**, which draws the rows; and a **controller**, the listeners that turn clicks and key presses into model updates. The code is grouped as in STUDY_PLAN_1's Build 4: the model at the top, then one section per component.

Each build has three steps: **read** the listed sections, in order; then copy the code, run it and read the notes under it; then **try** the things listed. You write no code in this plan: every build is printed in full. It builds on STUDY_PLAN_1, so `signal`, `computed`, `effect`, `batch`, `` html`…` ``, `render` and slots are not explained again.

</details>

## The app

<details>
<summary>What the app does, build by build</summary>
<br>

- **Name:** a text box and an **append** button. Clicking append, or pressing Enter in the box, adds the name to the end of the list and clears the box. A blank name is ignored, and from Build 5 on, so is a name already in the list.
- **Name List:** a table with the columns **No.** (1, 2, 3, …) and **Name**. When it is empty, it says "No names yet".
- Each row ends in buttons, one kind more per build: **delete** (Build 2); **up** and **down**, which swap the row with its neighbor (Build 3); and **edit**, placed first, which turns the name into a text box, where leaving the box or pressing Enter saves the new name and Escape puts the old one back (Build 4). Build 7's edit opens a pop-up dialog instead, with **Ok**, which saves; **Revert**, which puts the old name back in the box; and **Cancel**, which closes the dialog without saving.
- From Build 8 on, a new row fades in, a deleted one fades out, and a moved one slides to its new place.
- From Build 9 on, a long name wraps onto more lines, so the buttons stay on the screen.
- From Build 10 on, a finger can do the same without the buttons. Swipe a name left to delete its row, and, from Build 11, right to add " VIP" to the end of the name, or take it off. From Builds 12 and 13, each swipe shows a button to tap instead: Delete on the right, VIP on the left, and a swipe the other way puts it away. From Build 14, hold a name still for half a second, then drag its row up or down. A mouse still uses the buttons.

The app's state is one value, `names`, an array of strings held in a signal. Build 4 adds a second signal, which belongs to the view, not the model: which row is being edited. Build 7 keeps that in a plain variable instead, since nothing on the screen is drawn from it. Builds 10, 12 and 14 add three more signals of the view's own: the row being swiped, the row whose button is out, and the row being dragged.

</details>

## Setup

<details>
<summary>The folder and index.html</summary>
<br>

From the repo root:

```bash
mkdir -p .temp/name-list && cp -r vendor .temp/name-list/
```

Then create `.temp/name-list/index.html`, the same for Builds 1 to 6 (Build 7 adds a dialog to it, Build 8 one CSS rule, Build 9 a viewport line, Builds 9 to 15 a few more rules, and Build 11 a `<div>` around the table):

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Names</title>
  <style> :root { color-scheme: dark; } body { background: #333; color: #eee; } </style>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
  <!-- add console display --> <script src="./vendor/eruda.js"></script> <script> localStorage.removeItem('eruda-dev-tools'); localStorage.setItem('eruda-entry-button', '{"rememberPos":false}'); eruda.init({ tool: ['console'], defaults: { displaySize: 30, theme: 'Dark' } }); eruda.get('console').config.set('displayExtraInfo', true); eruda.show(); </script>
</head>
<body>
  <form id="name-form"><label>Name: <input id="name-box"></label> <button>append</button></form>
  <table>
    <caption>Name List</caption>
    <thead><tr><th>No.</th><th>Name</th></tr></thead>
    <tbody id="name-rows"></tbody>
  </table>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

- The `<head>` is STUDY_PLAN_1 Build 5's, with a new title.
- The box and the button sit in a `<form>`, so that Enter in the box submits the form, just as clicking the button does. A `<button>` inside a form submits it unless told otherwise.
- `<caption>` is the table's title. `<thead>` (*table head*) holds the header row, and `<th>` (*table header*) is a header cell, drawn bold and centered. The rows go in `<tbody>` (*table body*), which starts empty; lit-html fills it.
- From Build 2 on, each row has a third cell, for its buttons, with no header cell above it. The browser draws the extra column anyway.

</details>

## Run any build

<details open>
<summary>Start the server, open the page</summary>
<br>

To run any build, from the repo root:

```bash
uv run --no-project python serve.py 8001 .temp/name-list
```

Then open <http://localhost:8001>. After you replace `main.js`, reload the page: `serve.py` tells the browser to keep no copies ([README → Run](README.md#run)), so a reload always gets the new files, on a phone too. What `console.log` prints shows in the Eruda panel at the bottom of the page.

</details>

## Build 1: append

<details>
<summary>Read, code, notes, try it</summary>
<br>

**Read:**

1. lit.dev [Lists](https://lit.dev/docs/templates/lists/): [Rendering arrays](https://lit.dev/docs/templates/lists/#rendering-arrays) and [Repeating templates with map](https://lit.dev/docs/templates/lists/#repeating-templates-with-map).
2. lit.dev [Conditionals](https://lit.dev/docs/templates/conditionals/): the first section, on the conditional (ternary) operator.
3. MDN: [`Array.prototype.map`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map), the array part of [spread syntax `...`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax), [`switch`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/switch), the form's [`submit` event](https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/submit_event) and [`preventDefault`](https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault).
4. [Terms](HOW_AND_WALKTHROUGH.md#terms): *table, tr, td*.

**Code:** `.temp/name-list/main.js`:

```js
import { signal, effect } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  switch (cmd.type) {
    case 'append': {
      const name = cmd.name.trim();
      if (name !== '') model.names.value = [...names, name];   // a new array, not push: see the notes
      break;
    }
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  updateModel({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- name list
const nameRows = document.querySelector('#name-rows');

function row(name, i) {
  return html`<tr><td>${i + 1}</td><td>${name}</td></tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **The model is one signal holding an array,** and `updateModel(cmd)` is the only code that writes it. `cmd` is an object that says what to do, such as `{ type: 'append', name: 'Ann' }`, and the `switch` on `cmd.type` picks the rule for it. Builds 2 to 4 each add one `case`. The dot runner works the same way: its `model.update(cmd)` is the one function that changes its state.
- `cmd.name.trim()` removes spaces from both ends, so a name of only spaces becomes `''` and is ignored. The braces after `case 'append':` give `name` a scope of its own; without them, a `const` in one `case` is visible in the whole `switch`.
- **`[...names, name]` makes a new array:** `...names` copies the old names into the new array, and `name` goes on the end. Why not `names.push(name)`: `push` changes the array in place, so the signal would still hold the same array, and a signal notifies only when it is given a *different* value (compared with `!==`). Assigning the same array back does nothing, and the page never redraws. The last **Try it** shows this.
- **The form section is plain DOM,** as in STUDY_PLAN_1: the form never changes, so lit-html has nothing to do there. Its `submit` listener runs when you click append and when you press Enter in the box. `e.preventDefault()` cancels what the browser would do next: send the form to the server and load the reply, which reloads the page and wipes the list.
- **The list section is where lit-html works.** `row(name, i)` returns one `<tr>` template. `names.map(row)` calls `row` once per name, with the name and its index (0, 1, 2, …), and returns an array of templates. `render` accepts an array, as a slot does, and draws its items one after another. The **No.** cell shows `i + 1`, so the count starts at 1.
- `names.length === 0 ? … : …` picks what to draw: the "No names yet" row when the list is empty, the rows otherwise. `colspan="2"` stretches that one cell across both columns.
- One effect draws the whole list and logs `render` each time. `render` compares each slot with the value it wrote last time and writes only the ones that changed; for a new name it adds a new row.
- **Why lit-html helps here:** not much yet. By hand, append is still easy: create a `<tr>` and two `<td>`s, fill them, add the row, and remove "No names yet" the first time. The gap opens from Build 2 on.

**Try it,** with the console open:

- Reload: one `render`, and "No names yet".
- Type `Ann` and press Enter: one `render`, the row "1 Ann", and the box is empty again.
- Append a few spaces: nothing changes, and no `render`. `updateModel` ignores the blank name before it writes the signal.
- Open F12 → Elements, expand `<tbody>`, and append a name: only the new `<tr>` flashes. lit-html leaves the rows that didn't change alone.
- **The `push` trap:** replace the line `if (name !== '') model.names.value = [...names, name];` with `if (name !== '') { names.push(name); model.names.value = names; }` and reload. Append `Ann`: the list still says "No names yet", and no `render` is logged, although the array now holds `Ann`. Put the line back.

</details>

## Build 2: delete

<details>
<summary>Read, code, notes, try it</summary>
<br>

**Read:**

1. MDN [`Array.prototype.filter`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/filter).
2. [Terms](HOW_AND_WALKTHROUGH.md#terms): *closure*.

**Code:** replace `.temp/name-list/main.js` with:

```js
import { signal, effect } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  switch (cmd.type) {
    case 'append': {
      const name = cmd.name.trim();
      if (name !== '') model.names.value = [...names, name];   // a new array, not push: see the notes
      break;
    }
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  updateModel({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- name list
const nameRows = document.querySelector('#name-rows');

function row(name, i) {
  return html`<tr>
    <td>${i + 1}</td>
    <td>${name}</td>
    <td><button @click=${() => updateModel({ type: 'delete', index: i })}>delete</button></td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- `names.filter(fn)` returns a new array of the items for which `fn` returns true. `fn` gets each name and its index; `(_, i) => i !== cmd.index` keeps every index but one. `_` is the usual name for a parameter you don't use, here the name itself.
- Each row's delete button gets its own handler, `() => updateModel({ type: 'delete', index: i })`. The arrow function is a closure: it remembers the `i` of the row it was made for. Every render makes new handlers with the current indexes, so after a delete, the row now at index 1 deletes index 1.
- `row` now spreads over several lines. The spaces and line breaks between the cells don't show.
- **Why lit-html helps here.** By hand, delete means: remove the `<tr>`, renumber the **No.** cell of every row after it, and put "No names yet" back when the last row goes. Each button's listener must also know its row's current index, which changes whenever a row above it is deleted: a listener added once with a fixed index goes stale and deletes the wrong row. Here none of that is code. The effect redraws from `names`, `i + 1` renumbers, and each render hands out fresh handlers.

What changed from Build 1:

1. `updateModel` has a `delete` case.
2. `row` has a third cell, with a delete button.

**Try it:**

- Append `Ann`, `Bob` and `Cy`, then delete `Bob`: `Cy` becomes number 2. Each click logs one `render`.
- Delete the rest: "No names yet" comes back.

</details>

## Build 3: up and down

<details>
<summary>Read, code, notes, try it</summary>
<br>

**Read:**

1. lit.dev Expressions → [Boolean attributes](https://lit.dev/docs/templates/expressions/#boolean-attribute-expressions).
2. MDN [`Array.prototype.with`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/with).
3. lit.dev Lists → [When to use map or repeat](https://lit.dev/docs/templates/lists/#when-to-use-map-or-repeat).

**Code:** replace `.temp/name-list/main.js` with:

```js
import { signal, effect } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  switch (cmd.type) {
    case 'append': {
      const name = cmd.name.trim();
      if (name !== '') model.names.value = [...names, name];   // a new array, not push: see the notes
      break;
    }
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;   // by is -1 (up) or +1 (down)
      if (j < 0 || j >= names.length) break;          // the first name can't go up, nor the last down
      model.names.value = names.with(i, names[j]).with(j, names[i]);   // swap the two
      break;
    }
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  updateModel({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- name list
const nameRows = document.querySelector('#name-rows');

function row(name, i, names) {
  return html`<tr>
    <td>${i + 1}</td>
    <td>${name}</td>
    <td>
      <button ?disabled=${i === 0} @click=${() => updateModel({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => updateModel({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => updateModel({ type: 'delete', index: i })}>delete</button>
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **The swap.** `cmd.by` is `-1` for up and `+1` for down, so `j` is the neighbor's index. `names.with(i, x)` returns a copy of the array with the item at `i` replaced by `x` and leaves the original alone, which is what a signal needs (Build 1). Two of them swap the names. Example: `['Ann', 'Bob', 'Cy']`, down on Ann, so `i = 0` and `j = 1`. `.with(0, 'Bob')` gives `['Bob', 'Bob', 'Cy']`, then `.with(1, 'Ann')` gives `['Bob', 'Ann', 'Cy']`.
- **The model guards the ends,** although the buttons there are disabled, so that the rule doesn't depend on the view getting it right. Without the guard, up on the first name would make it `undefined`, since `names[-1]` doesn't exist, and copy it over the last name, since `with(-1, …)` counts from the end. Down on the last name would throw a `RangeError`.
- `row` takes a third parameter, `names`. `map` calls its function with three arguments, the item, its index and the whole array, so `names.map(row)` hands `row` the array for free. `row` needs it to tell which row is last.
- **`?disabled=${i === 0}` is a boolean attribute slot:** the `?` tells lit-html to add the attribute `disabled` when the value is true and remove it when false. A disabled button is grayed out and ignores clicks. Without the `?`, `disabled=${false}` would write `disabled="false"`, and the button would still be disabled: for a boolean attribute, being there is what counts, whatever its value.
- **Why lit-html helps here.** By hand, a move means swapping two `<tr>`s with `insertBefore`, renumbering both, and fixing `disabled` on every button that moved onto or off the first or last row. Here the swap is one line in the model, and the template already says which buttons are off.
- **What `.map` does underneath.** lit-html keeps each `<tr>` where it is and rewrites what's inside it: after a swap, the first row's elements show the other name. No element moves. The keyboard focus, which stays on one element, shows it below. lit-html's `repeat` directive instead ties each row to its item and moves the elements with it. It matters when a row holds state of its own, such as the focus or half-typed text. It isn't in `vendor/`, and this app doesn't need it.

What changed from Build 2:

1. `updateModel` has a `move` case.
2. `row` takes `names`, and its last cell has up and down buttons, with `?disabled` slots, before delete.

**Try it:**

- Append `Ann`, `Bob` and `Cy`: up is grayed out on row 1, and down on row 3.
- Click down on `Ann` twice: she ends up last, and her down button grays out.
- **Rows stay, names move:** click into the name box and press Tab twice, which puts the focus on row 1's down button (Tab skips the disabled up). Press Space, which presses the focused button: the first two names swap. Press Space again: they swap back. The focus stayed on row 1's button while the name moved away from it.

</details>

## Build 4: edit

<details>
<summary>Read, code, notes, try it</summary>
<br>

**Read:**

1. [Terms](HOW_AND_WALKTHROUGH.md#terms): *activeElement*.
2. MDN [`HTMLElement.focus()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus), [`HTMLElement.blur()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/blur), again the [`blur` event](https://developer.mozilla.org/en-US/docs/Web/API/Element/blur_event), and [`HTMLInputElement.defaultValue`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/defaultValue).
3. MDN [optional chaining `?.`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining).
4. STUDY_PLAN_1's [Build 3: batch](STUDY_PLAN_1.md#build-3-batch), if you need a refresher.

**Code:** replace `.temp/name-list/main.js` with:

```js
import { signal, effect, batch } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  const name = cmd.name?.trim();   // append and rename carry a name; for delete and move, ?. gives undefined
  if (name === '') return;         // a blank name changes nothing
  switch (cmd.type) {
    case 'append':
      model.names.value = [...names, name];   // a new array, not push: see Build 1's notes
      break;
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;   // by is -1 (up) or +1 (down)
      if (j < 0 || j >= names.length) break;          // the first name can't go up, nor the last down
      model.names.value = names.with(i, names[j]).with(j, names[i]);   // swap the two
      break;
    }
    case 'rename':
      model.names.value = names.with(cmd.index, name);
      break;
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  updateModel({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- name list
const nameRows = document.querySelector('#name-rows');
const editing = signal(null);   // the view's own state: the index of the row being edited, or null

function onEdit(i) {
  editing.value = i;                         // the effect re-renders before this line returns,
  nameRows.querySelector('input').focus();   // so the text box exists; focusing it means leaving it commits
}

function onEditDone(i, e) {
  batch(() => {
    updateModel({ type: 'rename', index: i, name: e.target.value });
    editing.value = null;
  });
}

function onEditKey(e) {
  if (e.key === 'Escape') e.target.value = e.target.defaultValue;   // Escape puts the old name back first,
  if (e.key === 'Enter' || e.key === 'Escape') e.target.blur();      // then both keys commit, by leaving the box
}

function row(name, i, names) {
  return html`<tr>
    <td>${i + 1}</td>
    <td>${i === editing.value
      ? html`<input value=${name} @blur=${e => onEditDone(i, e)} @keydown=${onEditKey}>`
      : name}</td>
    <td>
      <button @click=${() => onEdit(i)}>edit</button>
      <button ?disabled=${i === 0} @click=${() => updateModel({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => updateModel({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => updateModel({ type: 'delete', index: i })}>delete</button>
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **`editing` is the view's own state, not the model's.** It says which row shows a text box, or `null` for none. If you saved the list, you would save `names`, not `editing`. So it lives in the list section, next to the code that uses it, and the view writes it directly. It is still a signal, because the rows must redraw when it changes; the effect reads it through `row`.
- The name cell is a `? :` again: the row being edited gets a nested template with an `<input>`, the others get the name. `value=${name}` starts the new box with the current name.
- **`onEdit` focuses the box straight after the write.** Outside a `batch`, writing a signal runs the effects that read it before the write returns, so on the next line the `<input>` already exists, and `querySelector` finds it; it is the only `<input>` in the table. The focus matters because `blur` fires only on an element that had the focus.
- **Leaving the box commits.** `@blur` calls `onEditDone`, which renames and closes the box. Enter and Escape call `e.target.blur()`, which takes the focus away and so fires the same `blur`: one path for all three. Clicking anywhere else, another row's button included, also blurs the box first: the browser moves the focus when the mouse button goes down, before the click, so the name is saved before the other button acts.
- **Escape cancels by putting the old name back first.** `e.target.defaultValue` is the box's `value` attribute, which `value=${name}` set when lit-html drew the box; typing changes only the box's `value` property. So after Escape, the blur saves the name the row already had, and nothing visible changes. Closing the box with `editing.value = null` instead would remove it while it has the focus, and Chrome then fires `blur`, which would save the text you meant to discard.
- `onEditDone` wraps its two writes in `batch`, so the effect draws once, with the new name and the box closed, rather than twice.
- **One rule for blank names.** Rename needs the rule that append already had, so the rule moved from the `append` case to the top of `updateModel`, where it covers both. In `cmd.name?.trim()`, the `?.` gives `undefined` instead of throwing an error when `cmd.name` is missing, as it is for delete and move. So `name` is `''` only for a blank append or rename, and a blank edit leaves the old name.
- **Why lit-html helps here.** By hand, edit means: swap the name's text for an `<input>`, swap it back on blur, and remember which row is open. Here the template says what a row looks like with and without `editing`, and the same effect as before draws it.

What changed from Build 3:

1. `batch` joined the import.
2. The blank-name check moved from the `append` case to the top of `updateModel`, and a `rename` case joined the `switch`.
3. The list section has the `editing` signal and three handlers: `onEdit`, `onEditDone` and `onEditKey`, for Enter and Escape.
4. `row`'s name cell switches between the name and a text box, and an edit button comes first in the last cell, before up.

**Try it,** with the console open:

- Append `Ann` and `Bob`, then click edit on `Ann`: her name becomes a text box holding `Ann`, with the cursor in it. One `render`.
- Change it to `Anna` and click an empty part of the page: the box closes on `Anna`. One `render`, thanks to `batch`.
- Edit again and press Enter instead: the same.
- Edit, clear the box and press Enter: `Anna` stays.
- Edit, type `Zed` and press Escape: the box closes on `Anna`.
- Edit `Bob`, then click up on his row without leaving the box first: the new name is saved, then the row moves.

</details>

## Build 5: no duplicates, with includes

<details>
<summary>Read, code, notes, try it</summary>
<br>

**Read:** MDN [`Array.prototype.includes`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/includes).

**Code:** replace `.temp/name-list/main.js` with:

```js
import { signal, effect, batch } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  const name = cmd.name?.trim();   // append and rename carry a name; for delete and move, ?. gives undefined
  if (name === '') return;                                  // a blank name changes nothing,
  if (name !== undefined && names.includes(name)) return;   // nor does one already in the list
  switch (cmd.type) {
    case 'append':
      model.names.value = [...names, name];   // a new array, not push: see Build 1's notes
      break;
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;   // by is -1 (up) or +1 (down)
      if (j < 0 || j >= names.length) break;          // the first name can't go up, nor the last down
      model.names.value = names.with(i, names[j]).with(j, names[i]);   // swap the two
      break;
    }
    case 'rename':
      model.names.value = names.with(cmd.index, name);
      break;
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  updateModel({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- name list
const nameRows = document.querySelector('#name-rows');
const editing = signal(null);   // the view's own state: the index of the row being edited, or null

function onEdit(i) {
  editing.value = i;                         // the effect re-renders before this line returns,
  nameRows.querySelector('input').focus();   // so the text box exists; focusing it means leaving it commits
}

function onEditDone(i, e) {
  batch(() => {
    updateModel({ type: 'rename', index: i, name: e.target.value });
    editing.value = null;
  });
}

function onEditKey(e) {
  if (e.key === 'Escape') e.target.value = e.target.defaultValue;   // Escape puts the old name back first,
  if (e.key === 'Enter' || e.key === 'Escape') e.target.blur();      // then both keys commit, by leaving the box
}

function row(name, i, names) {
  return html`<tr>
    <td>${i + 1}</td>
    <td>${i === editing.value
      ? html`<input value=${name} @blur=${e => onEditDone(i, e)} @keydown=${onEditKey}>`
      : name}</td>
    <td>
      <button @click=${() => onEdit(i)}>edit</button>
      <button ?disabled=${i === 0} @click=${() => updateModel({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => updateModel({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => updateModel({ type: 'delete', index: i })}>delete</button>
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **`names.includes(name)` returns `true` if some item of the array equals `name`,** and `false` if none does. It checks the items in order, from the first, and stops at the first match. So a name that isn't in the list costs one comparison per name, since only after the last one can it say no: with 1,000 names, 1,000 comparisons. In C, it is the `for` loop with `strcmp` that you would write yourself.
- **It compares as `===` does.** (Strictly, it uses *SameValueZero*, which differs from `===` only in counting `NaN` as equal to itself; no name is a number, so that doesn't matter here.) Two strings are equal when they hold the same characters in the same order, case included, so `Ann` and `ann` are different names. `trim()` runs first, so `  Ann  ` counts as `Ann`.
- **One rule for append and rename.** The new check sits under the blank check, at the top of `updateModel`, so it covers both, as the blank check has since Build 4. A rename to a taken name leaves the old name, as a blank rename does. Leaving the box unchanged is a rename to the row's own name, which is taken, so nothing is written; the box still closes, because `onEditDone` writes `editing`.
- `name !== undefined` skips the search for delete and move, which carry no name. They would work without it, since no item in the list is `undefined`, but they would search the whole list for nothing.
- **The rule lives in the model.** The view and the controller are Build 4's, unchanged. Which names may be in the list is a rule about the state, so it goes in `updateModel`, the one function that writes the state. Like the end guard in `move` (Build 3), it then holds whatever the view does.
- **The box empties even when a name is refused,** as it does for a blank name: the submit handler clears it after every append, whatever the model did.

What changed from Build 4:

1. `updateModel` has a second check at the top, `names.includes(name)`.

**Try it,** with the console open:

- Append `Ann`, then `Ann` again: still one row, and the second append logs no `render`.
- Append `ann`: a second row.
- Append `  Ann  `: refused, since `trim` runs before the check.
- Click edit on `ann`, change it to `Ann` and press Enter: the box closes on `ann`.

</details>

## Build 6: no duplicates, with a Set

<details>
<summary>Read, code, notes, try it</summary>
<br>

**Read:**

1. MDN [`Set`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set): the introduction and the [Description](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set#description), whose [Performance](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set#performance) part compares `has` with `includes`.
2. MDN [`Set.prototype.has`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set/has).
3. STUDY_PLAN_1's [Build 2: computed](STUDY_PLAN_1.md#build-2-computed), if you need a refresher.

**Code:** replace `.temp/name-list/main.js` with:

```js
import { signal, computed, effect, batch } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Derived value: the names as a Set, which finds a name without searching
const taken = computed(() => {
  console.log('taken');
  return new Set(model.names.value);
});

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  const name = cmd.name?.trim();   // append and rename carry a name; for delete and move, ?. gives undefined
  if (name === '') return;                                   // a blank name changes nothing,
  if (name !== undefined && taken.value.has(name)) return;   // nor does one already in the list
  switch (cmd.type) {
    case 'append':
      model.names.value = [...names, name];   // a new array, not push: see Build 1's notes
      break;
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;   // by is -1 (up) or +1 (down)
      if (j < 0 || j >= names.length) break;          // the first name can't go up, nor the last down
      model.names.value = names.with(i, names[j]).with(j, names[i]);   // swap the two
      break;
    }
    case 'rename':
      model.names.value = names.with(cmd.index, name);
      break;
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  updateModel({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- name list
const nameRows = document.querySelector('#name-rows');
const editing = signal(null);   // the view's own state: the index of the row being edited, or null

function onEdit(i) {
  editing.value = i;                         // the effect re-renders before this line returns,
  nameRows.querySelector('input').focus();   // so the text box exists; focusing it means leaving it commits
}

function onEditDone(i, e) {
  batch(() => {
    updateModel({ type: 'rename', index: i, name: e.target.value });
    editing.value = null;
  });
}

function onEditKey(e) {
  if (e.key === 'Escape') e.target.value = e.target.defaultValue;   // Escape puts the old name back first,
  if (e.key === 'Enter' || e.key === 'Escape') e.target.blur();      // then both keys commit, by leaving the box
}

function row(name, i, names) {
  return html`<tr>
    <td>${i + 1}</td>
    <td>${i === editing.value
      ? html`<input value=${name} @blur=${e => onEditDone(i, e)} @keydown=${onEditKey}>`
      : name}</td>
    <td>
      <button @click=${() => onEdit(i)}>edit</button>
      <button ?disabled=${i === 0} @click=${() => updateModel({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => updateModel({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => updateModel({ type: 'delete', index: i })}>delete</button>
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **A Set** is a collection in which each value appears at most once. `new Set(array)` builds one from the array's items, and `set.has(x)` returns `true` if `x` is in it. It compares as `includes` does.
- **`has` finds a name without searching.** The engine turns each name into a number, its *hash*, with a fixed recipe that mixes the name's characters, and keeps the name in the slot of a table that the hash picks. To check a name, it hashes the name and looks only in that slot. So a lookup costs about the same with 10 names as with 10,000: hashing reads the name's characters, so a long name takes a little longer, but how many names there are doesn't matter. "About", because two names can land in the same slot (a *collision*), and the engine then compares the few names there. The JavaScript standard requires that lookups take, on average, time that grows slower than the number of names, and names hash tables as one way to get it ([ECMAScript, Set Objects](https://tc39.es/ecma262/#sec-set-objects)).
- An analogy: a RAM whose address is the name's hash. Reading one address takes one access, however many words are stored. Where it breaks down: two names can share an address, so each address holds a short list of names, not one word.
- **`new Set(model.names.value)`, not `new Set(model.names)`.** The signal is the box, and `.value` is the array in it. `new Set` needs something it can walk through item by item, such as an array, and a signal isn't one: `new Set(model.names)` throws `TypeError: object is not iterable`. Reading `.value` inside the computed is also what ties `taken` to `names`.
- **`taken` is a computed, so one Set serves every check until `names` changes.** `updateModel` reads it from an event handler, outside any effect, and a computed caches there too: on each read it checks whether `names` changed since its last run, and runs its function again only if so. Its `console.log` shows each run. It sits right after the model, next to its only reader, `updateModel`.
- `name !== undefined` now also keeps delete and move from reading `taken`, which would rebuild the Set for them after every change, for nothing.
- **When the Set pays off.** Building a Set visits every name, as `includes` does. Here every accepted append or rename changes `names`, so the next check builds a new Set: one check per change costs what `includes` costs, plus the work of building. The Set wins when many checks share one build. Example: finding which of 100 pasted names are new, before adding any, against a list of 10,000. With `includes`, that is up to 100 × 10,000 = 1,000,000 comparisons; with the Set, 10,000 steps to build it and 100 lookups, about 10,100. At this app's size neither is measurable: the build is here to show the pattern.

What changed from Build 5:

1. `computed` joined the import.
2. `taken`, a computed, holds the names as a Set.
3. The second check reads `taken.value.has(name)` instead of `names.includes(name)`.

**Try it,** with the console open:

- Reload: one `render`, and no `taken`. Nothing has read `taken` yet, so its function hasn't run.
- Append `Ann`: `taken`, then `render`. The check built the Set, still empty, and then the append redrew.
- Append `Ann` again: `taken`, and no `render`. `names` changed since the last check, so the Set was built again, now holding `Ann`, and the check refused her.
- Append `Ann` a third time: nothing is logged. `names` hasn't changed, so the last Set answers.
- Delete `Ann`: `render`, and no `taken`. Append `Ann`: `taken`, then `render`. She is accepted, because the Set was built again from the new list.

</details>

## Build 7: edit in a dialog

<details>
<summary>Read, code, notes, try it</summary>
<br>

The same edit as Build 4's, done another way: edit opens a pop-up dialog, and you leave it only with Ok, which saves, or with Cancel or Escape, which don't. Revert puts the old name back in the box and leaves the dialog open. The model is Build 6's.

**Read:**

1. MDN [`<dialog>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog): the introduction, then, under Description, [Controlling dialogs using JavaScript](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog#controlling_dialogs_using_javascript) and [Closing dialogs](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog#closing_dialogs).
2. MDN [`HTMLDialogElement.showModal()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLDialogElement/showModal) and [`HTMLDialogElement.close()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLDialogElement/close).
3. MDN `<button>` → its [`type`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button#type) attribute.

**Code:** in `.temp/name-list/index.html`, add the dialog between the `<form id="name-form" …>` line and `<table>`:

```html
  <dialog id="edit-dialog">
    <form id="edit-form" method="dialog">
      <p id="edit-title"></p>
      <p><input id="edit-box" autofocus></p>
      <button>Ok</button> <button type="reset">Revert</button> <button id="edit-cancel" type="button">Cancel</button>
    </form>
  </dialog>
```

<details>
<summary>Complete index.html</summary>

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Names</title>
  <style> :root { color-scheme: dark; } body { background: #333; color: #eee; } </style>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
  <!-- add console display --> <script src="./vendor/eruda.js"></script> <script> localStorage.removeItem('eruda-dev-tools'); localStorage.setItem('eruda-entry-button', '{"rememberPos":false}'); eruda.init({ tool: ['console'], defaults: { displaySize: 30, theme: 'Dark' } }); eruda.get('console').config.set('displayExtraInfo', true); eruda.show(); </script>
</head>
<body>
  <form id="name-form"><label>Name: <input id="name-box"></label> <button>append</button></form>
  <dialog id="edit-dialog">
    <form id="edit-form" method="dialog">
      <p id="edit-title"></p>
      <p><input id="edit-box" autofocus></p>
      <button>Ok</button> <button type="reset">Revert</button> <button id="edit-cancel" type="button">Cancel</button>
    </form>
  </dialog>
  <table>
    <caption>Name List</caption>
    <thead><tr><th>No.</th><th>Name</th></tr></thead>
    <tbody id="name-rows"></tbody>
  </table>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

</details>

Then replace `.temp/name-list/main.js` with:

```js
import { signal, computed, effect } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Derived value: the names as a Set, which finds a name without searching
const taken = computed(() => {
  console.log('taken');
  return new Set(model.names.value);
});

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  const name = cmd.name?.trim();   // append and rename carry a name; for delete and move, ?. gives undefined
  if (name === '') return;                                   // a blank name changes nothing,
  if (name !== undefined && taken.value.has(name)) return;   // nor does one already in the list
  switch (cmd.type) {
    case 'append':
      model.names.value = [...names, name];   // a new array, not push: see Build 1's notes
      break;
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;   // by is -1 (up) or +1 (down)
      if (j < 0 || j >= names.length) break;          // the first name can't go up, nor the last down
      model.names.value = names.with(i, names[j]).with(j, names[i]);   // swap the two
      break;
    }
    case 'rename':
      model.names.value = names.with(cmd.index, name);
      break;
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  updateModel({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- edit dialog
const editDialog = document.querySelector('#edit-dialog');
const editForm = document.querySelector('#edit-form');
const editTitle = document.querySelector('#edit-title');
const editBox = document.querySelector('#edit-box');
const editCancel = document.querySelector('#edit-cancel');
let editIndex;   // the row the dialog edits: a plain variable, since nothing is drawn from it

function onEdit(i, name) {
  editIndex = i;
  editTitle.textContent = `Editing No. ${i + 1} Name: ${name}`;
  editBox.value = name;
  editBox.defaultValue = name;   // what Revert, a reset button, puts back
  editDialog.showModal();   // until the dialog closes, the rest of the page ignores the mouse and keyboard
}

editForm.addEventListener('submit', () => {   // Ok, or Enter in the box; method="dialog" then closes the dialog
  updateModel({ type: 'rename', index: editIndex, name: editBox.value });
});
editCancel.addEventListener('click', () => editDialog.close());   // Escape closes it too, with no code of ours

// --------------- name list
const nameRows = document.querySelector('#name-rows');

function row(name, i, names) {
  return html`<tr>
    <td>${i + 1}</td>
    <td>${name}</td>
    <td>
      <button @click=${() => onEdit(i, name)}>edit</button>
      <button ?disabled=${i === 0} @click=${() => updateModel({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => updateModel({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => updateModel({ type: 'delete', index: i })}>delete</button>
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **A *modal* dialog** is a box drawn above the page that takes the mouse and the keyboard until it closes, so you must answer it before doing anything else. `<dialog>` is the HTML element for a dialog box, hidden until opened. `showModal()` opens it as modal, puts the focus on the element marked `autofocus`, here the text box, and lets Escape close it; `close()` closes it. (`show()` would open it without blocking the page.)
- **`method="dialog"`** makes submitting the form close its dialog instead of sending the form to a server, so the submit handler needs no `preventDefault`, unlike the name form's. Ok submits it, and so does Enter in the box, as in the name form. The handler runs first, then the dialog closes.
- **Only Ok and Enter save,** because the rename sits in the submit handler, and only they submit the form. Cancel has `type="button"`, so it doesn't submit (a `<button>` in a form does unless told otherwise; see Setup's notes), and its handler only closes the dialog. Escape closes it without submitting.
- **Revert is a reset button,** so it needs no handler. `type="reset"` makes a button reset its form: each box goes back to its `defaultValue`, the box's `value` attribute (Build 4). Typing changes only the `value` property, so `defaultValue` still holds the name the dialog opened with, because `onEdit` set it; without that line, Revert would empty the box. A reset doesn't submit, so the dialog stays open. Enter in the box still means Ok: Enter presses the form's first submit button, and a reset button isn't one. After the click the focus is on Revert, so click the box to type again.
- **No signal for the row being edited.** In Build 4, `editing` had to be a signal, because the rows are drawn from it: writing it had to redraw them. Here the rows look the same whether the dialog is open or not, so nothing on the screen is drawn from the index. It only has to last from the click on edit to the submit, and a plain variable does that. The rule: a value the screen is drawn from goes in a signal; a value that only a later event reads can be a plain variable.
- **`editIndex` can't go stale.** While the dialog is open, the page ignores clicks, so no row can move or be deleted, and the index still points at the same name when Ok is pressed. In Build 4, the blur that saves the name comes before any other button acts, which gives the same guarantee.
- **The dialog is plain DOM code.** Its shape never changes, only its text, so like the name form it lives in `index.html`, and `onEdit` writes `textContent`, `value` and `defaultValue` directly. lit-html still draws only the rows, and `row`'s name cell is just the name again, as in Build 3. The edit button hands `name` to `onEdit`, for the title and the box.
- **A refused name is still silent:** a blank or taken name leaves the old one, and the dialog closes, as Build 6's box does. Keeping the dialog open with a message would need `updateModel` to report whether it accepted the name, which it doesn't.

What changed from Build 6:

1. `index.html` has a `<dialog>` holding a form: a title, a text box, Ok, Revert and Cancel.
2. `batch` left the import.
3. A new section, the edit dialog, holds `editIndex`, a plain variable; `onEdit`, which fills the dialog, sets the name Revert puts back, and opens the dialog; a submit listener, which renames; and a click listener on Cancel.
4. The list section lost `editing`, `onEditDone`, `onEditKey` and its own `onEdit`. `row`'s name cell is the name again, and edit calls `onEdit(i, name)`.

**Try it,** with the console open:

- Append `Ann` and `Bob`, then click edit on `Bob`: a dialog opens, titled `Editing No. 2 Name: Bob`, with `Bob` in the box and the cursor in it. Nothing is logged, since no signal changed; Build 4 logged a `render` here.
- Click up on row 1, behind the dialog: nothing happens.
- Change `Bob` to `Cy` and press Enter: the dialog closes, and row 2 reads `Cy`. `taken`, then `render`.
- Edit `Cy`, type `Zed` and press Escape: the dialog closes, and the row still reads `Cy`. Nothing is logged. Cancel does the same.
- Edit `Cy`, type `Zed` and click Revert: the box reads `Cy` again, and the dialog stays open. Nothing is logged. Press Escape.
- Edit `Cy`, change it to `Ann` and click Ok: the dialog closes, and the row still reads `Cy`, since `Ann` is taken. `taken`, and no `render`.

</details>

## Build 8: animate the rows

<details>
<summary>Read, code, notes, try it</summary>
<br>

A new row fades in, a deleted one fades out while the rows below slide up, and up and down slide two rows past each other. The browser does the animation; the code only tells it when a change starts and which element is which row. The model and the edit dialog are Build 7's.

**Read:**

1. MDN [View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API): the introduction.
2. MDN [Using the View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using): [The view transition process](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using#the_view_transition_process), [Basic SPA view transition](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using#basic_spa_view_transition) (an *SPA*, single-page app, is a page that changes itself, as this one does), [Customizing your animations](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using#customizing_your_animations) and [Different animations for different elements](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using#different_animations_for_different_elements).
3. MDN: [`Document.startViewTransition()`](https://developer.mozilla.org/en-US/docs/Web/API/Document/startViewTransition), [`view-transition-name`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/view-transition-name) and [`CSS.escape()`](https://developer.mozilla.org/en-US/docs/Web/API/CSS/escape_static).

**Code:** in `.temp/name-list/index.html`, replace the `<style>` line with:

```html
  <style> :root { color-scheme: dark; } body { background: #333; color: #eee; } ::view-transition-group(*) { animation-duration: 0.5s; } </style>
```

<details>
<summary>Complete index.html</summary>

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Names</title>
  <style> :root { color-scheme: dark; } body { background: #333; color: #eee; } ::view-transition-group(*) { animation-duration: 0.5s; } </style>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
  <!-- add console display --> <script src="./vendor/eruda.js"></script> <script> localStorage.removeItem('eruda-dev-tools'); localStorage.setItem('eruda-entry-button', '{"rememberPos":false}'); eruda.init({ tool: ['console'], defaults: { displaySize: 30, theme: 'Dark' } }); eruda.get('console').config.set('displayExtraInfo', true); eruda.show(); </script>
</head>
<body>
  <form id="name-form"><label>Name: <input id="name-box"></label> <button>append</button></form>
  <dialog id="edit-dialog">
    <form id="edit-form" method="dialog">
      <p id="edit-title"></p>
      <p><input id="edit-box" autofocus></p>
      <button>Ok</button> <button type="reset">Revert</button> <button id="edit-cancel" type="button">Cancel</button>
    </form>
  </dialog>
  <table>
    <caption>Name List</caption>
    <thead><tr><th>No.</th><th>Name</th></tr></thead>
    <tbody id="name-rows"></tbody>
  </table>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

</details>

Then replace `.temp/name-list/main.js` with:

```js
import { signal, computed, effect } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Derived value: the names as a Set, which finds a name without searching
const taken = computed(() => {
  console.log('taken');
  return new Set(model.names.value);
});

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  const name = cmd.name?.trim();   // append and rename carry a name; for delete and move, ?. gives undefined
  if (name === '') return;                                   // a blank name changes nothing,
  if (name !== undefined && taken.value.has(name)) return;   // nor does one already in the list
  switch (cmd.type) {
    case 'append':
      model.names.value = [...names, name];   // a new array, not push: see Build 1's notes
      break;
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;   // by is -1 (up) or +1 (down)
      if (j < 0 || j >= names.length) break;          // the first name can't go up, nor the last down
      model.names.value = names.with(i, names[j]).with(j, names[i]);   // swap the two
      break;
    }
    case 'rename':
      model.names.value = names.with(cmd.index, name);
      break;
  }
}

// --------------- view transitions
// Update the model, and let the browser animate the page from its old look to its new one
function updateAnimated(cmd) {
  document.startViewTransition(() => updateModel(cmd));
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  updateAnimated({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- edit dialog
const editDialog = document.querySelector('#edit-dialog');
const editForm = document.querySelector('#edit-form');
const editTitle = document.querySelector('#edit-title');
const editBox = document.querySelector('#edit-box');
const editCancel = document.querySelector('#edit-cancel');
let editIndex;   // the row the dialog edits: a plain variable, since nothing is drawn from it

function onEdit(i, name) {
  editIndex = i;
  editTitle.textContent = `Editing No. ${i + 1} Name: ${name}`;
  editBox.value = name;
  editBox.defaultValue = name;   // what Revert, a reset button, puts back
  editDialog.showModal();   // until the dialog closes, the rest of the page ignores the mouse and keyboard
}

editForm.addEventListener('submit', () => {   // Ok, or Enter in the box; method="dialog" then closes the dialog
  updateModel({ type: 'rename', index: editIndex, name: editBox.value });
});
editCancel.addEventListener('click', () => editDialog.close());   // Escape closes it too, with no code of ours

// --------------- name list
const nameRows = document.querySelector('#name-rows');

function row(name, i, names) {
  return html`<tr style="view-transition-name: row-${CSS.escape(name)}">
    <td>${i + 1}</td>
    <td>${name}</td>
    <td>
      <button @click=${() => onEdit(i, name)}>edit</button>
      <button ?disabled=${i === 0} @click=${() => updateAnimated({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => updateAnimated({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => updateAnimated({ type: 'delete', index: i })}>delete</button>
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **A *view transition*** animates the page from how it looked before a change to how it looks after. `document.startViewTransition(callback)` first captures how the page looks, then calls `callback`, which changes the DOM, then animates from the old look to the new. Here the callback is `updateModel(cmd)`: writing the signal runs the effect, which redraws the rows before the callback returns.
- **`view-transition-name` says which elements move as one piece.** The browser pairs the elements before and after the change by this name:
  - A name on the page before and after is one piece, which slides from its old place to its new one, as both rows do on up or down.
  - A name only before is a piece that left. It fades out where it was, and the rows below slide up into the gap: that is the delete.
  - A name only after fades in, as an appended row does.
  - Everything without a name, the rest of the page, is one more piece, which cross-fades from old to new. Where nothing changed, that shows nothing.
- **The animation is CSS.** During the transition, the browser draws extra elements above the page, one `::view-transition-group(name)` per piece, each holding a picture of its piece's old and new look, and runs CSS animations on them. These are *pseudo-elements*: CSS can style them, but they aren't in the DOM. `::view-transition-group(*)` selects every group, so the rule in `index.html` slows them all from the default 0.25 s to 0.5 s, and the pictures inside follow their group's duration.
- **It pairs by name, not by element, so `.map` works.** Build 3 showed that no `<tr>` moves: after a swap, the first row's elements show the other name. lit-html rewrites the style slot along with the text, so the name `row-Ann` goes with Ann to the other `<tr>`, and the browser sees Ann's row move. `repeat` would move the elements too, but the animation doesn't need that.
- **`row-${CSS.escape(name)}`.** A transition name must be one CSS *identifier*: letters, digits, `-` and `_`, with anything else, a space included, escaped by a backslash. `CSS.escape` writes any string that way: `CSS.escape('Ann Lee')` gives `Ann\ Lee`. Without it, `row-Ann Lee` isn't one identifier, the browser ignores the whole style, and the row gets no name and doesn't slide; the last **Try it** shows this. The prefix `row-` keeps a person's name from being a word CSS already uses for something else: `none` means "no name", and `root` is the name of the page itself.
- **Each name must be on one row only.** If two rows share a name, the browser skips the animation, and the change happens without it. Build 6's rule, no duplicates, is what makes each name safe to use.
- **The callback runs a moment later.** `startViewTransition` returns at once, and the browser calls the callback once it has captured the old look, at its next frame, about 16 ms later on a 60 Hz screen. So `updateModel` no longer runs inside the click handler. Nothing here depends on that: in the form's handler, the `cmd` copies the box's text when it is made, before the next line clears the box.
- **An animation isn't state,** so the model doesn't change: nothing about it would be saved with the list. `updateAnimated` only decides how an update shows. It uses `document`, a browser global, so in the dot runner's split it would sit in `main.js`, which decides when things run. Rename still calls `updateModel`, so it changes without animation.
- **A click during the animation is lost.** In Chrome, clicking a button while the rows are still moving does nothing; click again once they stop. At 0.5 s this is easy to miss.
- **Browser support:** Chrome and Edge 111+, Safari 18+ and Firefox 144+. In an older browser `document.startViewTransition` doesn't exist, so a click throws a `TypeError` and changes nothing. A check that falls back to plain `updateModel` would fix that; it's left out to keep the build short. Also left out: the setting some people turn on to reduce motion, which a `@media (prefers-reduced-motion: reduce)` rule could honor by turning the animation off.

What changed from Build 7:

1. `index.html`'s `<style>` has a rule for the animation's length.
2. A new section, view transitions, holds `updateAnimated`.
3. Append, up, down and delete call `updateAnimated` instead of `updateModel`.
4. `row`'s `<tr>` has a style slot, which names the row after its name.

**Try it,** with the console open:

- Append `Ann`, `Bob` and `Cy`: each new row fades in.
- Click down on `Ann`: she and `Bob` slide past each other. One `render`, as before.
- Delete `Bob`: his row fades out, and `Cy`'s slides up into the gap.
- In `index.html`, change `0.5s` to `3s` and reload, then append and move a few names to watch it slowly. Click a button while the rows are moving: nothing happens. Put it back.
- Edit a name in the dialog and click Ok: it changes without animation.
- **The escape:** append `Ann Lee` and move her: she slides like the others. Now change `row-${CSS.escape(name)}` to `row-${name}`, reload and do it again: `Ann Lee` fades out of one row and into the other, while the name she swaps with slides. Put it back.

</details>

## Build 9: fit the screen

<details>
<summary>Read, code, notes, try it</summary>
<br>

On a phone, a long name pushes the buttons off the screen. Two CSS rules let the name wrap onto more lines instead, so the buttons always stay in view, on one line; `main.js` doesn't change. This is also the first build for a phone: it adds the viewport line, and shows how to open the page on one.

**Read:**

1. MDN [`<meta name="viewport">`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name/viewport): the introduction.
2. MDN CSS [`overflow-wrap`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overflow-wrap) and [`white-space`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/white-space): the introductions.
3. MDN [`:nth-child()`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:nth-child) and [`:last-child`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:last-child): the introductions.

**Code:** in `.temp/name-list/index.html`, add this line under `<meta charset="utf-8">`:

```html
  <meta name="viewport" content="width=device-width">
```

and replace the `<style>` line with:

```html
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows td:nth-child(2) { overflow-wrap: anywhere; }
    #name-rows td:last-child { white-space: nowrap; }
  </style>
```

<details>
<summary>Complete index.html</summary>

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>Names</title>
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows td:nth-child(2) { overflow-wrap: anywhere; }
    #name-rows td:last-child { white-space: nowrap; }
  </style>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
  <!-- add console display --> <script src="./vendor/eruda.js"></script> <script> localStorage.removeItem('eruda-dev-tools'); localStorage.setItem('eruda-entry-button', '{"rememberPos":false}'); eruda.init({ tool: ['console'], defaults: { displaySize: 30, theme: 'Dark' } }); eruda.get('console').config.set('displayExtraInfo', true); eruda.show(); </script>
</head>
<body>
  <form id="name-form"><label>Name: <input id="name-box"></label> <button>append</button></form>
  <dialog id="edit-dialog">
    <form id="edit-form" method="dialog">
      <p id="edit-title"></p>
      <p><input id="edit-box" autofocus></p>
      <button>Ok</button> <button type="reset">Revert</button> <button id="edit-cancel" type="button">Cancel</button>
    </form>
  </dialog>
  <table>
    <caption>Name List</caption>
    <thead><tr><th>No.</th><th>Name</th></tr></thead>
    <tbody id="name-rows"></tbody>
  </table>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

</details>

`.temp/name-list/main.js` stays as it is.

- **The problem, measured.** In Chrome on a phone screen 390 px wide, a one-word name of 20 to 35 letters pushed the buttons onto 2 or 3 lines. One of 50 or 60 letters made the table 578 to 738 px wide, with its last buttons off the screen, so the page grew, and the phone zoomed out to show it all, to 0.67 and 0.53 of its size.
- **Why the table grows.** A table column is never narrower than the longest piece of its content that can't be broken, its *min-content* width: for the names, the longest word; for the buttons, the widest button, since the browser may wrap between buttons. While those minimums fit the screen, the browser narrows the columns it can, here by wrapping the buttons. Once they add up to more than the screen, the table is wider than the screen.
- **The two rules turn both minimums around.** `overflow-wrap: anywhere` lets the browser break a name between any two letters when a line is full, so the name column's min-content is one letter. `white-space: nowrap` forbids line breaks between the buttons, so their cell's min-content is the whole row of buttons. The table then fits the screen: the buttons keep one line, and the name gets the width that is left, wrapping onto as many lines as it needs. With the same names, measured: the table ended at 382 px and the last button at 379 px, the page stayed 390 px wide at full size, and a 60-letter name took 5 lines.
- **No measuring.** The browser lays the table out again whenever the screen's width changes, such as when the phone turns, so the code never needs the screen's size.
- `td:nth-child(2)` picks each row's second cell, the name, and `td:last-child` its last, the buttons. Build 10 gives the name cell a class of its own.
- **Support:** `overflow-wrap: anywhere` works in Chrome 80+, Safari on iPhone 15.4+ and Firefox 65+.
- **The viewport line.** Without it, a phone lays the page out 980 px wide, like a desktop screen, and shrinks it to fit. On an iPhone 390 points wide, everything is drawn at 390 / 980 ≈ 0.4 times its size, too small to touch, and the two rules above would have 980 px to work with. `width=device-width` makes one CSS pixel one *point*, Apple's unit for sizes on screen.
- **To try it on a phone,** run the server as usual, find the computer's address with `hostname -I`, and open `http://<that address>:8001` on a phone on the same Wi-Fi. `serve.py` listens on all of the computer's addresses, not only `localhost`, and tells the phone to keep no copies, so a reload there shows your latest change; if the phone can't connect, a firewall may be blocking port 8001. **On the computer,** open Chrome's DevTools (F12) and click the device toolbar button (Ctrl+Shift+M): the page then gets a phone's screen, and the mouse acts as a finger.

What changed from Build 8:

1. `index.html` has a viewport line, and its `<style>` became a block with two more rules.
2. `main.js` is Build 8's.

**Try it,** on a phone or with the device toolbar:

- Append `Ann`, then the one-word name `Wolfeschlegelsteinhausenbergerdorffvoralternwaren`: it wraps, and its buttons stay on one line at the right.
- With the device toolbar, turn the screen with its rotate button: the long name gets the extra width and takes fewer lines.
- Delete the two new rules and reload: the long name pushes its buttons off the screen, and the page zooms out. Put them back.

</details>

## Build 10: swipe left to delete

<details>
<summary>Read, code, notes, try it</summary>
<br>

On a phone, swipe a name to the left: its row follows the finger and turns red past a line. Let go past the line and the row is deleted; let go before it and the row slides back. Only a finger swipes; a mouse still uses the buttons. The model is Build 8's.

**Read:**

1. MDN [Pointer events](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events): the introduction, then [Pointer capture](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events#pointer_capture) and [touch-action CSS property](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events#touch-action_css_property).
2. MDN: the [`pointercancel` event](https://developer.mozilla.org/en-US/docs/Web/API/Element/pointercancel_event), the [`touchend` event](https://developer.mozilla.org/en-US/docs/Web/API/Element/touchend_event), and CSS [`touch-action`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/touch-action) and [`translate`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/translate).

**Code:** in `.temp/name-list/index.html`, replace the `<style>` block with:

```html
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; }
    #name-rows td:last-child { white-space: nowrap; }
    #name-rows tr.deleting { background: #a33; }
  </style>
```

<details>
<summary>Complete index.html</summary>

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>Names</title>
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; }
    #name-rows td:last-child { white-space: nowrap; }
    #name-rows tr.deleting { background: #a33; }
  </style>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
  <!-- add console display --> <script src="./vendor/eruda.js"></script> <script> localStorage.removeItem('eruda-dev-tools'); localStorage.setItem('eruda-entry-button', '{"rememberPos":false}'); eruda.init({ tool: ['console'], defaults: { displaySize: 30, theme: 'Dark' } }); eruda.get('console').config.set('displayExtraInfo', true); eruda.show(); </script>
</head>
<body>
  <form id="name-form"><label>Name: <input id="name-box"></label> <button>append</button></form>
  <dialog id="edit-dialog">
    <form id="edit-form" method="dialog">
      <p id="edit-title"></p>
      <p><input id="edit-box" autofocus></p>
      <button>Ok</button> <button type="reset">Revert</button> <button id="edit-cancel" type="button">Cancel</button>
    </form>
  </dialog>
  <table>
    <caption>Name List</caption>
    <thead><tr><th>No.</th><th>Name</th></tr></thead>
    <tbody id="name-rows"></tbody>
  </table>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

</details>

Then replace `.temp/name-list/main.js` with:

```js
import { signal, computed, effect, batch } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Derived value: the names as a Set, which finds a name without searching
const taken = computed(() => {
  console.log('taken');
  return new Set(model.names.value);
});

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  const name = cmd.name?.trim();   // append and rename carry a name; for delete and move, ?. gives undefined
  if (name === '') return;                                   // a blank name changes nothing,
  if (name !== undefined && taken.value.has(name)) return;   // nor does one already in the list
  switch (cmd.type) {
    case 'append':
      model.names.value = [...names, name];   // a new array, not push: see Build 1's notes
      break;
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;   // by is -1 (up) or +1 (down)
      if (j < 0 || j >= names.length) break;          // the first name can't go up, nor the last down
      model.names.value = names.with(i, names[j]).with(j, names[i]);   // swap the two
      break;
    }
    case 'rename':
      model.names.value = names.with(cmd.index, name);
      break;
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  settle({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- edit dialog
const editDialog = document.querySelector('#edit-dialog');
const editForm = document.querySelector('#edit-form');
const editTitle = document.querySelector('#edit-title');
const editBox = document.querySelector('#edit-box');
const editCancel = document.querySelector('#edit-cancel');
let editIndex;   // the row the dialog edits: a plain variable, since nothing is drawn from it

function onEdit(i, name) {
  editIndex = i;
  editTitle.textContent = `Editing No. ${i + 1} Name: ${name}`;
  editBox.value = name;
  editBox.defaultValue = name;   // what Revert, a reset button, puts back
  editDialog.showModal();   // until the dialog closes, the rest of the page ignores the mouse and keyboard
}

editForm.addEventListener('submit', () => {   // Ok, or Enter in the box; method="dialog" then closes the dialog
  updateModel({ type: 'rename', index: editIndex, name: editBox.value });
});
editCancel.addEventListener('click', () => editDialog.close());   // Escape closes it too, with no code of ours

// --------------- name list
const nameRows = document.querySelector('#name-rows');

// Gesture settings: change these until a swipe feels right
const MOVE_PX = 10;      // a finger must move this far left before the row follows it, so a tap stays a tap
const DELETE_PX = 100;   // a row swiped at least this far left is deleted when the finger lifts

const swipe = signal(null);   // the view's own state: { index, dx }, the row being swiped and how far (dx < 0: left), or null
let press = null;             // the finger on a name: { pointerId, index, x }; nothing is drawn from it

// Build 8's updateAnimated, plus letting go of a swiped row: in one view transition, apply cmd, if any,
// and clear swipe, so every row slides to its new place
function settle(cmd) {
  document.startViewTransition(() => batch(() => {
    if (cmd) updateModel(cmd);
    swipe.value = null;
  }));
}

function onPointerDown(e, i) {
  if (e.pointerType !== 'touch' || press) return;   // fingers only, one at a time; a mouse uses the buttons
  press = { pointerId: e.pointerId, index: i, x: e.clientX };
}

function onPointerMove(e) {
  if (e.pointerId !== press?.pointerId) return;   // not the finger we follow
  const dx = e.clientX - press.x;
  if (swipe.value || dx <= -MOVE_PX) swipe.value = { index: press.index, dx: Math.min(0, dx) };   // left only
}

function onPointerEnd(e) {   // pointerup: the finger lifted; pointercancel: the browser took it over, to scroll
  if (e.pointerId !== press?.pointerId) return;
  const s = swipe.value;
  if (s) settle(e.type === 'pointerup' && s.dx <= -DELETE_PX ? { type: 'delete', index: s.index } : null);
  press = null;
}

nameRows.addEventListener('pointermove', onPointerMove);
nameRows.addEventListener('pointerup', onPointerEnd);
nameRows.addEventListener('pointercancel', onPointerEnd);
nameRows.addEventListener('touchend', e => { if (e.target.closest('.name')) e.preventDefault(); });   // a touch on a name never becomes a click

function row(name, i, names) {
  const dx = swipe.value?.index === i ? swipe.value.dx : 0;
  return html`<tr style="view-transition-name: row-${CSS.escape(name)}; translate: ${dx}px 0"
      class=${dx <= -DELETE_PX ? 'deleting' : ''}>
    <td>${i + 1}</td>
    <td class="name" @pointerdown=${e => onPointerDown(e, i)}>${name}</td>
    <td>
      <button @click=${() => onEdit(i, name)}>edit</button>
      <button ?disabled=${i === 0} @click=${() => settle({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => settle({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => settle({ type: 'delete', index: i })}>delete</button>
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- ***Pointer events*** are one set of events for a mouse, a finger and a pen: `pointerdown` when it touches (for a mouse, when a button goes down), `pointermove` as it moves, `pointerup` when it lifts. `e.pointerType` says which kind it is, `e.clientX` how far from the window's left edge it is, in CSS pixels, and `e.pointerId` which one, since several fingers can be down at once. `onPointerDown` takes only a finger, and only one at a time; the other handlers ignore every pointer but that one.
- **Only the name takes gestures.** Its cell has the class `name` and the `@pointerdown`. A gesture that started on a button could end in a click on it: in Chrome, a touch that moves 15 px still counts as a tap. The name cell has no click to set off.
- **A touch on a name never becomes a click.** Chrome also moves a tap that lands near a button onto the button: in a test, a finger that slid 15 px right from `Ann` and lifted clicked the edit button beside her, and the edit dialog opened. The `touchend` listener stops that. `touchend` is the older *touch event* for a lifting finger, sent after `pointerup`, and cancelling it with `preventDefault()` tells the browser not to turn the touch into a click.
- **Where the listeners go.** `pointerdown` belongs to one name, so it sits in the template with its `i`, like the buttons' `@click`. Moving and lifting belong to whichever press is under way, so each has one listener on `nameRows`, added once. The browser *captures* a finger's pointer: its events keep going to the element it first touched, even after it slides off. They bubble up to `<tbody>`, so `nameRows` hears them.
- **`touch-action: pan-y`** tells the browser which finger moves it keeps for itself: `pan-y` is a vertical pan, so a vertical swipe on a name still scrolls the page, and a sideways one is left to the code. Without it, the browser claims the sideways move too and sends `pointercancel` before the row has moved; the last **Try it** shows this. The rule is on the cell, because `touch-action` doesn't apply to table rows ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/touch-action)). It shares the `.name` rule with Build 9's `overflow-wrap`, which now finds the name cell by its class.
- **`pointercancel`** is the browser saying "this finger is mine now", for example when it starts to scroll. `onPointerEnd` handles it like a lift, but never deletes on it.
- **`swipe` is a signal, `press` a plain variable:** Build 7's rule again. The screen is drawn from how far the row is swiped, but nothing is drawn from where the finger landed. Every finger move writes `swipe`, so the effect redraws and logs `render`, about once per screen frame. lit-html compares the slots and rewrites one: the swiped row's `style`.
- **The row follows the finger with `translate`:** `translate: -40px 0` draws the row 40 px to the left without moving anything else; the table's layout stays as it was. `dx` is negative to the left, and `Math.min(0, dx)` keeps it from going right. The swipe waits for `MOVE_PX`, 10 px, so a tap that wobbles a little isn't a swipe.
- **Why left:** a row drawn past the right edge of the screen makes the page wider, and a phone then zooms out to fit it. In Chrome on a phone screen 390 px wide, a 150 px swipe to the right made the page 417 px wide, drawn at 0.94 of its size, and the whole page could be dragged around. Past the left edge, the row is just cut off, and the page stays 390 px. Left is also the iPhone's direction for delete. A row can also go right without widening the page: the fold below shows two fixes and compares them, and Build 11, which swipes right, uses the second.

<details>
<summary>Swiping right without widening the page: two fixes</summary>

Both fixes use `overflow-x: clip`, which cuts off whatever is drawn past an element's right edge and doesn't count it toward the page's width. With either one, a row swiped right is cut off 8 px from the screen's edge (`body`'s margin), and the page stays as wide as the screen.

**Fix 1, a CSS rule:** add this to the `<style>` block in `index.html`:

```css
html, body { overflow-x: clip; }
```

**Fix 2, a `<div>` around the table:** in `index.html`, put the table inside a `<div>` that clips:

```html
  <div style="overflow-x: clip">
    <table>
      …
    </table>
  </div>
```

How they compare:

| | Fix 1: `html, body { overflow-x: clip; }` | Fix 2: a `<div>` around the table |
|---|---|---|
| What changes | one CSS rule; the HTML stays as it is | one more element in the HTML |
| What it clips | the whole page: anything drawn past the screen's right edge, anywhere, is cut off | only the table |
| Where a swiped row is cut off | 8 px from the screen's edge | the same, because a `<div>` is as wide as `body`'s content |
| A trap | it must name `html` as well: on `body` alone it does nothing (see below) | none |
| Support | `overflow: clip`: Chrome 90+, Safari on iPhone 16+, Firefox 81+ | the same |

**Which to pick:** Fix 2, for this page. It clips only the part that needs it, so anything else that someday reaches past the screen's edge isn't silently cut off, and it has no trap. Fix 1 is the quicker edit, and is fine on a page where nothing should ever be wider than the screen. Neither hides a row's buttons, since Build 9's rules keep the table within the screen however long a name is.

What each place for the clip did during a 150 px right swipe, on a 390 px-wide phone screen emulated in Chromium:

| Where the clip goes | Page width | Zoom | What you see |
|---|---|---|---|
| nothing | 417 px | 0.94 | the page grows and zooms out |
| `body` only | 417 px | 0.94 | no effect |
| **`html, body`** | 390 px | 1 | the row cut off 8 px from the screen's edge |
| a `<div>` around the table | 390 px | 1 | the same, but it needs an extra element in the HTML |
| `table { contain: paint }` | 390 px | 1 | the row cut off at the table's edge, mid-screen, which looks wrong |

**Why `body` alone does nothing:** when `<html>` has no `overflow` of its own, the browser applies `body`'s setting to the whole window instead of to `body`. For the window, `clip` acts like `hidden`, which, as measured, still lets the page grow and zoom out. Setting it on `html` as well stops that hand-off, so `body` clips its own content.

Neither fix was tested on a real iPhone, where Safari's zoom handling may differ.

</details>

- **`settle` replaces Build 8's `updateAnimated`.** It does the same, and also clears `swipe`, so one function serves the buttons, the form and the end of a swipe. At the end of a swipe, the browser captures the row where the finger left it; then the callback deletes the name, if the row is past the line, and clears `swipe`, both in one `batch`, so the effect draws once. A deleted row's name is gone afterward, so it fades out where it was and the rows below slide up; a kept one slides home. The form calls `settle`, which is written further down; that works, because the call happens only when the form is submitted, after the whole file has run.
- **The `deleting` class** turns the row red from `DELETE_PX` on, so you see before you let go that it will be deleted.

What changed from Build 9:

1. `index.html`'s `<style>` finds the name cell by its class, `name`, which also gets `touch-action`, and has a `deleting` rule.
2. `batch` is back in the import.
3. `updateAnimated` became `settle`, in the list section, which also lets go of a swiped row; the form and the buttons call it.
4. The list section has the gesture settings, the `swipe` signal, the `press` variable, three pointer handlers and four listeners.
5. `row` draws the swiped row with its `translate` and the `deleting` class, and the name cell, now class `name`, takes `pointerdown`.

**Try it,** on a phone or with the device toolbar:

- Append `Ann`, `Bob` and `Cy`. Swipe `Bob` left by about half a name's width and let go: the row slides back.
- Swipe further: the row turns red. Let go: it fades out, and `Cy` slides up.
- Swipe a name right: nothing moves.
- Tap the buttons: they still work. Turn the device toolbar off and drag a name with the mouse: nothing moves.
- Change `DELETE_PX` to `40`, then to `200`, and find the distance that feels right.
- **Without `touch-action`:** delete `touch-action: pan-y;` from the `.name` rule and reload. A swipe now leaves the row where it is: the browser took the finger with `pointercancel`. Put it back.

</details>

## Build 11: swipe right to make a name VIP

<details>
<summary>Read, code, notes, try it</summary>
<br>

Swipe a name right, past a line, and let go: " VIP" goes on the end of the name, or comes off if it was there. The row follows the finger and turns gold past the line. A swipe left still deletes. The model gets one new rule.

**Read:** MDN [`String.prototype.endsWith`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/endsWith) and [`String.prototype.slice`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/slice).

**Code:** in `.temp/name-list/index.html`, replace the `<style>` block with:

```html
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; }
    #name-rows td:last-child { white-space: nowrap; }
    #name-rows tr.deleting { background: #a33; }
    #name-rows tr.toggling { background: #a80; }
  </style>
```

and put the table inside a `<div>` that clips, Fix 2 from Build 10's fold:

```html
  <div style="overflow-x: clip">
    <table>
      …
    </table>
  </div>
```

<details>
<summary>Complete index.html</summary>

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>Names</title>
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; }
    #name-rows td:last-child { white-space: nowrap; }
    #name-rows tr.deleting { background: #a33; }
    #name-rows tr.toggling { background: #a80; }
  </style>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
  <!-- add console display --> <script src="./vendor/eruda.js"></script> <script> localStorage.removeItem('eruda-dev-tools'); localStorage.setItem('eruda-entry-button', '{"rememberPos":false}'); eruda.init({ tool: ['console'], defaults: { displaySize: 30, theme: 'Dark' } }); eruda.get('console').config.set('displayExtraInfo', true); eruda.show(); </script>
</head>
<body>
  <form id="name-form"><label>Name: <input id="name-box"></label> <button>append</button></form>
  <dialog id="edit-dialog">
    <form id="edit-form" method="dialog">
      <p id="edit-title"></p>
      <p><input id="edit-box" autofocus></p>
      <button>Ok</button> <button type="reset">Revert</button> <button id="edit-cancel" type="button">Cancel</button>
    </form>
  </dialog>
  <div style="overflow-x: clip">
    <table>
      <caption>Name List</caption>
      <thead><tr><th>No.</th><th>Name</th></tr></thead>
      <tbody id="name-rows"></tbody>
    </table>
  </div>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

</details>

Then replace `.temp/name-list/main.js` with:

```js
import { signal, computed, effect, batch } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Derived value: the names as a Set, which finds a name without searching
const taken = computed(() => {
  console.log('taken');
  return new Set(model.names.value);
});

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  const name = cmd.name?.trim();   // append and rename carry a name; for the others, ?. gives undefined
  if (name === '') return;                                   // a blank name changes nothing,
  if (name !== undefined && taken.value.has(name)) return;   // nor does one already in the list
  switch (cmd.type) {
    case 'append':
      model.names.value = [...names, name];   // a new array, not push: see Build 1's notes
      break;
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;   // by is -1 (up) or +1 (down)
      if (j < 0 || j >= names.length) break;          // the first name can't go up, nor the last down
      model.names.value = names.with(i, names[j]).with(j, names[i]);   // swap the two
      break;
    }
    case 'rename':
      model.names.value = names.with(cmd.index, name);
      break;
    case 'vip': {   // add " VIP" to the end of the name, or take it off: a rename, so the rename rules apply
      const old = names[cmd.index];
      updateModel({ type: 'rename', index: cmd.index, name: old.endsWith(' VIP') ? old.slice(0, -4) : old + ' VIP' });
      break;
    }
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  settle({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- edit dialog
const editDialog = document.querySelector('#edit-dialog');
const editForm = document.querySelector('#edit-form');
const editTitle = document.querySelector('#edit-title');
const editBox = document.querySelector('#edit-box');
const editCancel = document.querySelector('#edit-cancel');
let editIndex;   // the row the dialog edits: a plain variable, since nothing is drawn from it

function onEdit(i, name) {
  editIndex = i;
  editTitle.textContent = `Editing No. ${i + 1} Name: ${name}`;
  editBox.value = name;
  editBox.defaultValue = name;   // what Revert, a reset button, puts back
  editDialog.showModal();   // until the dialog closes, the rest of the page ignores the mouse and keyboard
}

editForm.addEventListener('submit', () => {   // Ok, or Enter in the box; method="dialog" then closes the dialog
  updateModel({ type: 'rename', index: editIndex, name: editBox.value });
});
editCancel.addEventListener('click', () => editDialog.close());   // Escape closes it too, with no code of ours

// --------------- name list
const nameRows = document.querySelector('#name-rows');

// Gesture settings: change these until a swipe feels right
const MOVE_PX = 10;      // a finger must move this far sideways before the row follows it, so a tap stays a tap
const DELETE_PX = 100;   // a row swiped at least this far left is deleted when the finger lifts
const VIP_PX = 100;      // a row swiped at least this far right gains or loses " VIP" when the finger lifts

const swipe = signal(null);   // the view's own state: { index, dx }, the row being swiped and how far (dx < 0: left), or null
let press = null;             // the finger on a name: { pointerId, index, x }; nothing is drawn from it

// Build 8's updateAnimated, plus letting go of a swiped row: in one view transition, apply cmd, if any,
// and clear swipe, so every row slides to its new place
function settle(cmd) {
  document.startViewTransition(() => batch(() => {
    if (cmd) updateModel(cmd);
    swipe.value = null;
  }));
}

function onPointerDown(e, i) {
  if (e.pointerType !== 'touch' || press) return;   // fingers only, one at a time; a mouse uses the buttons
  press = { pointerId: e.pointerId, index: i, x: e.clientX };
}

function onPointerMove(e) {
  if (e.pointerId !== press?.pointerId) return;   // not the finger we follow
  const dx = e.clientX - press.x;
  if (swipe.value || Math.abs(dx) >= MOVE_PX) swipe.value = { index: press.index, dx };   // left or right
}

// What a swipe let go at s.dx does: past the line on the left deletes, past the one on the right toggles VIP
function swipeCmd(s) {
  if (s.dx <= -DELETE_PX) return { type: 'delete', index: s.index };
  if (s.dx >= VIP_PX) return { type: 'vip', index: s.index };
  return null;
}

function onPointerEnd(e) {   // pointerup: the finger lifted; pointercancel: the browser took it over, to scroll
  if (e.pointerId !== press?.pointerId) return;
  if (swipe.value) settle(e.type === 'pointerup' ? swipeCmd(swipe.value) : null);
  press = null;
}

nameRows.addEventListener('pointermove', onPointerMove);
nameRows.addEventListener('pointerup', onPointerEnd);
nameRows.addEventListener('pointercancel', onPointerEnd);
nameRows.addEventListener('touchend', e => { if (e.target.closest('.name')) e.preventDefault(); });   // a touch on a name never becomes a click

function row(name, i, names) {
  const dx = swipe.value?.index === i ? swipe.value.dx : 0;
  return html`<tr style="view-transition-name: row-${CSS.escape(name)}; translate: ${dx}px 0"
      class=${dx <= -DELETE_PX ? 'deleting' : dx >= VIP_PX ? 'toggling' : ''}>
    <td>${i + 1}</td>
    <td class="name" @pointerdown=${e => onPointerDown(e, i)}>${name}</td>
    <td>
      <button @click=${() => onEdit(i, name)}>edit</button>
      <button ?disabled=${i === 0} @click=${() => settle({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => settle({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => settle({ type: 'delete', index: i })}>delete</button>
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **The rule lives in the model.** `{ type: 'vip', index }` is a new command. Whether a name ends in " VIP" is a fact about the data, so toggling it is a rule of the model, next to the others. The `vip` case works out the new name and hands it to `rename` by calling `updateModel` again, so a VIP name obeys the rename rules: not blank, not taken. Example: `Bob` becomes `Bob VIP`, and `Bob VIP` becomes `Bob`: `slice(0, -4)` drops the last 4 characters, " VIP". With `Ann VIP` already in the list, swiping `Ann` right changes nothing, just as renaming `Ann` to `Ann VIP` would.
- **One swipe, two directions.** `onPointerMove` now keeps `dx` either way, once the finger has moved `MOVE_PX` either way. `swipeCmd` says what letting go does: past `DELETE_PX` to the left, delete; past `VIP_PX` to the right, toggle VIP; in between, nothing. The row turns red (`deleting`) or gold (`toggling`) as it passes either line.
- **The row moves right, so the table needs the clip.** A row drawn past the screen's right edge would widen the page (Build 10's "Why left"). The `<div>` around the table cuts it off 8 px from the edge. Measured: the page stayed 390 px wide at full size, both during a 150 px right swipe and during the animation after it.
- **Start a right swipe on the name, not at the screen's very left edge:** there, a right swipe is Safari's "go back".

What changed from Build 10:

1. `index.html` has a `toggling` rule, and the table sits in a clipping `<div>`.
2. The model has a `vip` case.
3. The gesture settings have `VIP_PX`, `onPointerMove` swipes both ways, and `swipeCmd` turns a swipe that was let go into a command.
4. `row` colors the row `toggling` past the right-hand line.

**Try it,** on a phone or with the device toolbar:

- Append `Ann`, `Bob` and `Cy`. Swipe `Bob` right past the line: the row turns gold. Let go: it reads `Bob VIP`. Swipe it again: `Bob`.
- Swipe a name right a little and let go: the row slides back, unchanged.
- Append `Ann VIP`, then swipe `Ann` right: nothing changes, since `Ann VIP` is taken.
- Swipe `Cy` left: it is still deleted.
- Delete the `<div>` lines and reload, then swipe a name far right: the page grows and zooms out, as Build 10's fold measured. Put them back.

</details>

## Build 12: swipe to show a Delete button

<details>
<summary>Read, code, notes, try it</summary>
<br>

As on the iPhone, a left swipe no longer deletes by itself. Swipe a name left, and a red Delete button slides out from the row's right end; let go past halfway and it stays out. Tap it to delete the row, or swipe the name right to put it away. The right swipe still toggles VIP, as in Build 11, and the row's own delete button still works as before. The model is Build 11's.

**Read:**

1. MDN CSS [`position`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position): the introduction, and [`relative`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position#relative) and [`absolute`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position#absolute) under Values.
2. MDN [Default parameters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Default_parameters): the introduction.

**Code:** in `.temp/name-list/index.html`, replace the `<style>` block with:

```html
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; }
    #name-rows td:last-child { white-space: nowrap; position: relative; }
    #name-rows .bin { position: absolute; right: 0; top: 0; height: 100%; padding: 0; border: 0; overflow: hidden; background: #a33; color: #eee; }
    #name-rows tr.toggling { background: #a80; }
  </style>
```

<details>
<summary>Complete index.html</summary>

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>Names</title>
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; }
    #name-rows td:last-child { white-space: nowrap; position: relative; }
    #name-rows .bin { position: absolute; right: 0; top: 0; height: 100%; padding: 0; border: 0; overflow: hidden; background: #a33; color: #eee; }
    #name-rows tr.toggling { background: #a80; }
  </style>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
  <!-- add console display --> <script src="./vendor/eruda.js"></script> <script> localStorage.removeItem('eruda-dev-tools'); localStorage.setItem('eruda-entry-button', '{"rememberPos":false}'); eruda.init({ tool: ['console'], defaults: { displaySize: 30, theme: 'Dark' } }); eruda.get('console').config.set('displayExtraInfo', true); eruda.show(); </script>
</head>
<body>
  <form id="name-form"><label>Name: <input id="name-box"></label> <button>append</button></form>
  <dialog id="edit-dialog">
    <form id="edit-form" method="dialog">
      <p id="edit-title"></p>
      <p><input id="edit-box" autofocus></p>
      <button>Ok</button> <button type="reset">Revert</button> <button id="edit-cancel" type="button">Cancel</button>
    </form>
  </dialog>
  <div style="overflow-x: clip">
    <table>
      <caption>Name List</caption>
      <thead><tr><th>No.</th><th>Name</th></tr></thead>
      <tbody id="name-rows"></tbody>
    </table>
  </div>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

</details>

Then replace `.temp/name-list/main.js` with:

```js
import { signal, computed, effect, batch } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Derived value: the names as a Set, which finds a name without searching
const taken = computed(() => {
  console.log('taken');
  return new Set(model.names.value);
});

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  const name = cmd.name?.trim();   // append and rename carry a name; for the others, ?. gives undefined
  if (name === '') return;                                   // a blank name changes nothing,
  if (name !== undefined && taken.value.has(name)) return;   // nor does one already in the list
  switch (cmd.type) {
    case 'append':
      model.names.value = [...names, name];   // a new array, not push: see Build 1's notes
      break;
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;   // by is -1 (up) or +1 (down)
      if (j < 0 || j >= names.length) break;          // the first name can't go up, nor the last down
      model.names.value = names.with(i, names[j]).with(j, names[i]);   // swap the two
      break;
    }
    case 'rename':
      model.names.value = names.with(cmd.index, name);
      break;
    case 'vip': {   // add " VIP" to the end of the name, or take it off: a rename, so the rename rules apply
      const old = names[cmd.index];
      updateModel({ type: 'rename', index: cmd.index, name: old.endsWith(' VIP') ? old.slice(0, -4) : old + ' VIP' });
      break;
    }
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  settle({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- edit dialog
const editDialog = document.querySelector('#edit-dialog');
const editForm = document.querySelector('#edit-form');
const editTitle = document.querySelector('#edit-title');
const editBox = document.querySelector('#edit-box');
const editCancel = document.querySelector('#edit-cancel');
let editIndex;   // the row the dialog edits: a plain variable, since nothing is drawn from it

function onEdit(i, name) {
  editIndex = i;
  editTitle.textContent = `Editing No. ${i + 1} Name: ${name}`;
  editBox.value = name;
  editBox.defaultValue = name;   // what Revert, a reset button, puts back
  editDialog.showModal();   // until the dialog closes, the rest of the page ignores the mouse and keyboard
}

editForm.addEventListener('submit', () => {   // Ok, or Enter in the box; method="dialog" then closes the dialog
  updateModel({ type: 'rename', index: editIndex, name: editBox.value });
});
editCancel.addEventListener('click', () => editDialog.close());   // Escape closes it too, with no code of ours

// --------------- name list
const nameRows = document.querySelector('#name-rows');

// Gesture settings: change these until a swipe feels right
const MOVE_PX = 10;   // a finger must move this far sideways before the row follows it, so a tap stays a tap
const OPEN_PX = 80;   // the width of an open row's Delete button
const VIP_PX = 100;   // a row swiped at least this far right gains or loses " VIP" when the finger lifts

const swipe = signal(null);   // the view's own state: { index, dx }, the row being swiped and how far (dx < 0: its Delete button out), or null
const open = signal(null);    // the view's own state: the index of the row showing its Delete button, or null
let press = null;             // the finger on a name: { pointerId, index, x, from }; nothing is drawn from it

// Build 8's updateAnimated, grown: in one view transition, apply cmd, if any, open row openIndex, if any (any
// change to the list closes an open row, whose index may now be another name's), and let go of a swiped row
function settle(cmd, openIndex = null) {
  document.startViewTransition(() => batch(() => {
    if (cmd) updateModel(cmd);
    open.value = openIndex;
    swipe.value = null;
  }));
}

function onPointerDown(e, i) {
  if (e.pointerType !== 'touch' || press) return;   // fingers only, one at a time; a mouse uses the buttons
  press = { pointerId: e.pointerId, index: i, x: e.clientX, from: i === open.value ? -OPEN_PX : 0 };   // from: how far out its button was
}

function onPointerMove(e) {
  if (e.pointerId !== press?.pointerId) return;   // not the finger we follow
  const dx = e.clientX - press.x;
  if (!swipe.value && Math.abs(dx) < MOVE_PX) return;   // not a swipe yet: a tap stays a tap
  let x = press.from + dx;
  if (press.from < 0) x = Math.min(0, x);   // an open row can only close
  swipe.value = { index: press.index, dx: x };
}

function onPointerEnd(e) {   // pointerup: the finger lifted; pointercancel: the browser took it over, to scroll
  if (e.pointerId !== press?.pointerId) return;
  const s = swipe.value, up = e.type === 'pointerup';
  if (s && up && s.dx >= VIP_PX) settle({ type: 'vip', index: s.index });   // right past the line: toggle VIP
  else if (s) settle(null, up && s.dx <= -OPEN_PX / 2 ? s.index : null);   // left past halfway: the Delete button stays out
  press = null;
}

// The Delete button: grows from the row's right end, over the row's other buttons
function deleteButton(i, width) {
  return html`<button class="bin" style="width: ${width}px" @click=${() => settle({ type: 'delete', index: i })}>Delete</button>`;
}

nameRows.addEventListener('pointermove', onPointerMove);
nameRows.addEventListener('pointerup', onPointerEnd);
nameRows.addEventListener('pointercancel', onPointerEnd);
nameRows.addEventListener('touchend', e => { if (e.target.closest('.name')) e.preventDefault(); });   // a touch on a name never becomes a click

function row(name, i, names) {
  const dx = swipe.value?.index === i ? swipe.value.dx : i === open.value ? -OPEN_PX : 0;
  return html`<tr style="view-transition-name: row-${CSS.escape(name)}; translate: ${Math.max(0, dx)}px 0"
      class=${dx >= VIP_PX ? 'toggling' : ''}>
    <td>${i + 1}</td>
    <td class="name" @pointerdown=${e => onPointerDown(e, i)}>${name}</td>
    <td>
      <button @click=${() => onEdit(i, name)}>edit</button>
      <button ?disabled=${i === 0} @click=${() => settle({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => settle({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => settle({ type: 'delete', index: i })}>delete</button>
      ${dx < 0 ? deleteButton(i, -dx) : ''}
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **`open` is a second view-only signal, beside `swipe`:** the index of the row whose Delete button is out, or `null`. A row is drawn from it, so it is a signal (Build 7's rule). It holds one index, so opening one row closes any other.
- **The button grows; the row stays.** `deleteButton` draws the button `-dx` pixels wide, and `row` draws it only while `dx` is below 0. `position: absolute` takes it out of the layout and places it by its *containing block*, the nearest ancestor with a `position` of its own: here the last cell, which `position: relative` makes one without moving it. `right: 0` and `height: 100%` pin the button to that cell's right edge, full height, and `width` sets how far it reaches left, over the row's own buttons. Why not move the row, as Build 10 does: the table starts 8 px from the screen's left edge, so a row moved 80 px left would put its name off the screen, and there would be nothing left to swipe back. And since the button stays inside the row, it never widens the page.
- **`press.from` lets one swipe code open and close.** It is where the button was when the finger landed: `-OPEN_PX` for an open row, 0 for a closed one. The swipe is then at `press.from + dx`, and for an open row, `Math.min(0, …)` keeps it to closing. Example: an open row, and the finger moves 20 px right: −80 + 20 = −60, so the button is 60 px wide. On a closed row, a right move is Build 11's VIP swipe: the row is drawn `Math.max(0, dx)` to the right, so only a right swipe moves it.
- **Let go past halfway, and the button stays out.** `onPointerEnd` compares it with half of `OPEN_PX`: 40 px or more opens the row, with the button 80 px wide; less closes it. Past `VIP_PX` to the right, it toggles VIP instead, as in Build 11. A `pointercancel` closes the row.
- **The Delete button is the only way a swipe deletes now:** letting go never deletes, however far you swiped. Tapping the button calls `settle({ type: 'delete', index: i })`, and the row fades out with it.
- **`settle` has a second parameter, `openIndex`,** the row to leave open. `openIndex = null` is a *default parameter*: a call that leaves the argument out gets `null`. The buttons and the form call `settle(cmd)`, so any change to the list closes an open row. That matters because `open` is an index: after a move or a delete, the same index can belong to another name.
- **The end of a swipe is a view transition, as in Build 10.** The button is part of the row's picture, so its change shows as a cross-fade between the button before and after.

What changed from Build 11:

1. `index.html`'s `<style>` lost the red `deleting` row. The last cell is also `position: relative`, and the `bin` rule draws the Delete button.
2. `DELETE_PX` became `OPEN_PX`, and the `open` signal joined the list section.
3. `settle` takes `openIndex` and sets `open`.
4. `press` keeps `from`, and `onPointerMove` keeps an open row to closing. `onPointerEnd` toggles VIP past the right-hand line, and otherwise opens or closes the row; `swipeCmd` is gone.
5. `deleteButton` draws the Delete button. `row` moves a row only to the right, and draws the button in its last cell while it is out.

**Try it,** on a phone or with the device toolbar:

- Append `Ann`, `Bob`, `Cy` and `Dee`. Swipe `Bob` left a little and let go: the button slides back in.
- Swipe further, past 40 px: the button stays out. Tap it: Bob's row fades out.
- Swipe `Cy` open, then swipe Cy's name right: the button goes back in, and the row doesn't go on to VIP. A short right swipe, under 40 px, leaves the button out.
- Swipe a closed row right past the line: VIP toggles, as in Build 11.
- Swipe a row open, then tap up on another row: the button closes, and the rows move.
- Change `OPEN_PX` to `120` and reload: a wider button, which covers more of the row.

</details>

## Build 13: swipe right to show a VIP button

<details>
<summary>Read, code, notes, try it</summary>
<br>

The right swipe gets a button too. Swipe a name right, and the row slides right, with a VIP button in the gap it leaves; let go past halfway and the button stays. Tap it: a regular name gets " VIP", and a VIP name loses it. The button shows which it will do: gold `VIP` to add, gray `Not VIP` to take off. A left swipe puts it away. The model is Build 11's, with one rule pulled out.

**Read:** MDN [Class selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Class_selectors): the introduction and the examples.

**Code:** in `.temp/name-list/index.html`, replace the `<style>` block with:

```html
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; }
    #name-rows td:first-child { position: relative; }
    #name-rows td:last-child { white-space: nowrap; position: relative; }
    #name-rows .bin, #name-rows .vip { position: absolute; top: 0; height: 100%; padding: 0; border: 0; overflow: hidden; white-space: nowrap; }
    #name-rows .bin { right: 0; background: #a33; color: #eee; }
    #name-rows .vip { right: 100%; background: #fc0; color: #333; }
    #name-rows .vip.off { background: #777; color: #eee; }
  </style>
```

<details>
<summary>Complete index.html</summary>

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>Names</title>
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; }
    #name-rows td:first-child { position: relative; }
    #name-rows td:last-child { white-space: nowrap; position: relative; }
    #name-rows .bin, #name-rows .vip { position: absolute; top: 0; height: 100%; padding: 0; border: 0; overflow: hidden; white-space: nowrap; }
    #name-rows .bin { right: 0; background: #a33; color: #eee; }
    #name-rows .vip { right: 100%; background: #fc0; color: #333; }
    #name-rows .vip.off { background: #777; color: #eee; }
  </style>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
  <!-- add console display --> <script src="./vendor/eruda.js"></script> <script> localStorage.removeItem('eruda-dev-tools'); localStorage.setItem('eruda-entry-button', '{"rememberPos":false}'); eruda.init({ tool: ['console'], defaults: { displaySize: 30, theme: 'Dark' } }); eruda.get('console').config.set('displayExtraInfo', true); eruda.show(); </script>
</head>
<body>
  <form id="name-form"><label>Name: <input id="name-box"></label> <button>append</button></form>
  <dialog id="edit-dialog">
    <form id="edit-form" method="dialog">
      <p id="edit-title"></p>
      <p><input id="edit-box" autofocus></p>
      <button>Ok</button> <button type="reset">Revert</button> <button id="edit-cancel" type="button">Cancel</button>
    </form>
  </dialog>
  <div style="overflow-x: clip">
    <table>
      <caption>Name List</caption>
      <thead><tr><th>No.</th><th>Name</th></tr></thead>
      <tbody id="name-rows"></tbody>
    </table>
  </div>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

</details>

Then replace `.temp/name-list/main.js` with:

```js
import { signal, computed, effect, batch } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Derived value: the names as a Set, which finds a name without searching
const taken = computed(() => {
  console.log('taken');
  return new Set(model.names.value);
});

// A VIP's name ends in " VIP"; the model and the VIP button both ask
const isVip = name => name.endsWith(' VIP');

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  const name = cmd.name?.trim();   // append and rename carry a name; for the others, ?. gives undefined
  if (name === '') return;                                   // a blank name changes nothing,
  if (name !== undefined && taken.value.has(name)) return;   // nor does one already in the list
  switch (cmd.type) {
    case 'append':
      model.names.value = [...names, name];   // a new array, not push: see Build 1's notes
      break;
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;   // by is -1 (up) or +1 (down)
      if (j < 0 || j >= names.length) break;          // the first name can't go up, nor the last down
      model.names.value = names.with(i, names[j]).with(j, names[i]);   // swap the two
      break;
    }
    case 'rename':
      model.names.value = names.with(cmd.index, name);
      break;
    case 'vip': {   // add " VIP" to the end of the name, or take it off: a rename, so the rename rules apply
      const old = names[cmd.index];
      updateModel({ type: 'rename', index: cmd.index, name: isVip(old) ? old.slice(0, -4) : old + ' VIP' });
      break;
    }
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  settle({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- edit dialog
const editDialog = document.querySelector('#edit-dialog');
const editForm = document.querySelector('#edit-form');
const editTitle = document.querySelector('#edit-title');
const editBox = document.querySelector('#edit-box');
const editCancel = document.querySelector('#edit-cancel');
let editIndex;   // the row the dialog edits: a plain variable, since nothing is drawn from it

function onEdit(i, name) {
  editIndex = i;
  editTitle.textContent = `Editing No. ${i + 1} Name: ${name}`;
  editBox.value = name;
  editBox.defaultValue = name;   // what Revert, a reset button, puts back
  editDialog.showModal();   // until the dialog closes, the rest of the page ignores the mouse and keyboard
}

editForm.addEventListener('submit', () => {   // Ok, or Enter in the box; method="dialog" then closes the dialog
  updateModel({ type: 'rename', index: editIndex, name: editBox.value });
});
editCancel.addEventListener('click', () => editDialog.close());   // Escape closes it too, with no code of ours

// --------------- name list
const nameRows = document.querySelector('#name-rows');

// Gesture settings: change these until a swipe feels right
const MOVE_PX = 10;   // a finger must move this far sideways before the row follows it, so a tap stays a tap
const OPEN_PX = 80;   // the width of an open row's Delete or VIP button

const swipe = signal(null);   // the view's own state: { index, dx }, the row being swiped and how far (dx < 0: Delete button out; dx > 0: VIP button out), or null
const open = signal(null);    // the view's own state: { index, dx }, the open row and its button (dx = -OPEN_PX: Delete; OPEN_PX: VIP), or null
let press = null;             // the finger on a name: { pointerId, index, x, from }; nothing is drawn from it

// Build 8's updateAnimated, grown: in one view transition, apply cmd, if any, open openRow, if any (any change
// to the list closes an open row, whose index may now be another name's), and let go of a swiped row
function settle(cmd, openRow = null) {
  document.startViewTransition(() => batch(() => {
    if (cmd) updateModel(cmd);
    open.value = openRow;
    swipe.value = null;
  }));
}

function onPointerDown(e, i) {
  if (e.pointerType !== 'touch' || press) return;   // fingers only, one at a time; a mouse uses the buttons
  press = { pointerId: e.pointerId, index: i, x: e.clientX, from: open.value?.index === i ? open.value.dx : 0 };   // from: how far out a button was
}

function onPointerMove(e) {
  if (e.pointerId !== press?.pointerId) return;   // not the finger we follow
  const dx = e.clientX - press.x;
  if (!swipe.value && Math.abs(dx) < MOVE_PX) return;   // not a swipe yet: a tap stays a tap
  let x = press.from + dx;                  // how far a button is out: x < 0, Delete; x > 0, VIP
  if (press.from < 0) x = Math.min(0, x);   // an open row can only close,
  if (press.from > 0) x = Math.max(0, x);   // not swing over to the other side
  swipe.value = { index: press.index, dx: x };
}

// What a swipe let go at s.dx leaves open: past halfway on either side, that side's button
function openAt(s) {
  if (s.dx <= -OPEN_PX / 2) return { index: s.index, dx: -OPEN_PX };
  if (s.dx >= OPEN_PX / 2) return { index: s.index, dx: OPEN_PX };
  return null;
}

function onPointerEnd(e) {   // pointerup: the finger lifted; pointercancel: the browser took it over, to scroll
  if (e.pointerId !== press?.pointerId) return;
  if (swipe.value) settle(null, e.type === 'pointerup' ? openAt(swipe.value) : null);
  press = null;
}

// The Delete button: grows from the row's right end, over the row's other buttons
function deleteButton(i, width) {
  return html`<button class="bin" style="width: ${width}px" @click=${() => settle({ type: 'delete', index: i })}>Delete</button>`;
}

// The VIP button: fills the gap at the row's left end; gold to make the name VIP, gray to take it back
function vipButton(i, name, width) {
  const vip = isVip(name);
  return html`<button class=${vip ? 'vip off' : 'vip'} style="width: ${width}px"
      @click=${() => settle({ type: 'vip', index: i })}>${vip ? 'Not VIP' : 'VIP'}</button>`;
}

nameRows.addEventListener('pointermove', onPointerMove);
nameRows.addEventListener('pointerup', onPointerEnd);
nameRows.addEventListener('pointercancel', onPointerEnd);
nameRows.addEventListener('touchend', e => { if (e.target.closest('.name')) e.preventDefault(); });   // a touch on a name never becomes a click

function row(name, i, names) {
  const dx = swipe.value?.index === i ? swipe.value.dx : open.value?.index === i ? open.value.dx : 0;
  return html`<tr style="view-transition-name: row-${CSS.escape(name)}; translate: ${Math.max(0, dx)}px 0">
    <td>${dx > 0 ? vipButton(i, name, dx) : ''}${i + 1}</td>
    <td class="name" @pointerdown=${e => onPointerDown(e, i)}>${name}</td>
    <td>
      <button @click=${() => onEdit(i, name)}>edit</button>
      <button ?disabled=${i === 0} @click=${() => settle({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => settle({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => settle({ type: 'delete', index: i })}>delete</button>
      ${dx < 0 ? deleteButton(i, -dx) : ''}
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **The row moves right, and the VIP button fills the gap.** Unlike Delete, this button needs the row to move. It sits at the row's left end, where the No. and the name are, and growing over them would cover the name, the one place a swipe can start, so the button could never be put away. Moving the row right keeps the name on screen, and the clipping `<div>` cuts off the row's other end. The button is in the first cell, with `right: 100%`: its right edge sits on that cell's left edge, the row's left end, and it moves with the row. Its width is how far the row moved, `dx`, so it fills exactly the gap, from where the row's left end was to where it is.
- **`open` now says which side:** `{ index, dx }`, with `dx` at `-OPEN_PX` for Delete and `OPEN_PX` for VIP, the same numbers a swipe uses. `press.from` reads it, and the move code keeps an open row to closing: `Math.min(0, …)` for Delete, `Math.max(0, …)` for VIP, so a swipe can't swing past closed to the other button. On let-go, `openAt` decides: past halfway either way, that side's button stays out.
- **`isVip`: one rule, two readers.** The model and the VIP button both ask whether a name ends in " VIP", so the test moved into one small function next to the model. A copy of `name.endsWith(' VIP')` in the button would be a second place to keep in step.
- **Two styles from one `class` slot.** `class=${vip ? 'vip off' : 'vip'}` gives the button the class `vip`, plus `off` for a VIP name. `.vip` draws it gold, and `.vip.off`, which matches only an element that has both classes, overrides the colors with gray. The label follows the same test: `VIP` or `Not VIP`.
- **`deleteButton` and `vipButton`** each return one button's template, so `row` stays short: `vipButton` in the first cell while `dx` is above 0, `deleteButton` in the last while it is below. Their shared CSS, such as `position: absolute` and the full height, sits in one rule for both, and each keeps its own side and colors.
- **The VIP button is the only way a swipe toggles VIP now,** as the Delete button is for deleting, so `VIP_PX` and the gold row are gone.

What changed from Build 12:

1. `index.html`'s `<style>`: the first cell is `position: relative`, the `bin` and `vip` buttons share one rule, and `vip` and `vip.off` give the VIP button its two styles. The `toggling` rule is gone.
2. `isVip` sits by the model, which uses it in the `vip` case.
3. `VIP_PX` is gone. `open` holds `{ index, dx }`, `settle`'s second parameter is that open row, and `press.from` reads its `dx`. `onPointerMove` keeps an open VIP button to closing too, and `openAt` decides what stays open on let-go.
4. `vipButton` draws the VIP button, and `row` puts it in the first cell.

**Try it,** on a phone or with the device toolbar:

- Append `Ann`, `Bob`, `Cy` and `Dee`. Swipe `Bob` right past 40 px: the row slides right, and a gold VIP button fills the gap. Tap it: `Bob VIP`, and the button closes.
- Swipe `Bob VIP` right: the button is gray and says Not VIP. Tap it: `Bob`.
- Swipe a row's VIP button out, then swipe its name left: it goes back in. Swipe left again: the Delete button comes out.
- Swipe a row open either way, then tap a button on another row: it closes.

</details>

## Build 14: hold to reorder

<details>
<summary>Read, code, notes, try it</summary>
<br>

Press a name and hold your finger still: after half a second its row grows a little and follows your finger up and down. Let go, and it drops into the nearest place while the view transition slides the rows into their new order. The swipes still work: a finger that moves sideways before the half second is up swipes instead.

**Read:**

1. MDN [`setTimeout()`](https://developer.mozilla.org/en-US/docs/Web/API/Window/setTimeout) and [`clearTimeout()`](https://developer.mozilla.org/en-US/docs/Web/API/Window/clearTimeout).
2. MDN [`Array.prototype.toSpliced`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/toSpliced), and the object part of spread syntax, [Spread in object literals](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax#spread_in_object_literals).
3. MDN `addEventListener` → [Using passive listeners](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener#using_passive_listeners).
4. MDN [`HTMLElement.offsetHeight`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/offsetHeight).
5. MDN CSS: [`scale`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/scale), [`z-index`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/z-index), [`user-select`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/user-select), and the introduction of [Using CSS transitions](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Transitions/Using).

**Code:** in `.temp/name-list/index.html`, replace the `<style>` block with:

```html
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; -webkit-user-select: none; }
    #name-rows td:first-child { position: relative; }
    #name-rows td:last-child { white-space: nowrap; position: relative; }
    #name-rows .bin, #name-rows .vip { position: absolute; top: 0; height: 100%; padding: 0; border: 0; overflow: hidden; white-space: nowrap; }
    #name-rows .bin { right: 0; background: #a33; color: #eee; }
    #name-rows .vip { right: 100%; background: #fc0; color: #333; }
    #name-rows .vip.off { background: #777; color: #eee; }
    #name-rows tr { transition: scale 0.15s; }
    #name-rows tr.lifted { scale: 1.05; background: #555; position: relative; z-index: 1; }
  </style>
```

<details>
<summary>Complete index.html</summary>

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>Names</title>
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; -webkit-user-select: none; }
    #name-rows td:first-child { position: relative; }
    #name-rows td:last-child { white-space: nowrap; position: relative; }
    #name-rows .bin, #name-rows .vip { position: absolute; top: 0; height: 100%; padding: 0; border: 0; overflow: hidden; white-space: nowrap; }
    #name-rows .bin { right: 0; background: #a33; color: #eee; }
    #name-rows .vip { right: 100%; background: #fc0; color: #333; }
    #name-rows .vip.off { background: #777; color: #eee; }
    #name-rows tr { transition: scale 0.15s; }
    #name-rows tr.lifted { scale: 1.05; background: #555; position: relative; z-index: 1; }
  </style>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
  <!-- add console display --> <script src="./vendor/eruda.js"></script> <script> localStorage.removeItem('eruda-dev-tools'); localStorage.setItem('eruda-entry-button', '{"rememberPos":false}'); eruda.init({ tool: ['console'], defaults: { displaySize: 30, theme: 'Dark' } }); eruda.get('console').config.set('displayExtraInfo', true); eruda.show(); </script>
</head>
<body>
  <form id="name-form"><label>Name: <input id="name-box"></label> <button>append</button></form>
  <dialog id="edit-dialog">
    <form id="edit-form" method="dialog">
      <p id="edit-title"></p>
      <p><input id="edit-box" autofocus></p>
      <button>Ok</button> <button type="reset">Revert</button> <button id="edit-cancel" type="button">Cancel</button>
    </form>
  </dialog>
  <div style="overflow-x: clip">
    <table>
      <caption>Name List</caption>
      <thead><tr><th>No.</th><th>Name</th></tr></thead>
      <tbody id="name-rows"></tbody>
    </table>
  </div>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

</details>

Then replace `.temp/name-list/main.js` with:

```js
import { signal, computed, effect, batch } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Derived value: the names as a Set, which finds a name without searching
const taken = computed(() => {
  console.log('taken');
  return new Set(model.names.value);
});

// A VIP's name ends in " VIP"; the model and the VIP button both ask
const isVip = name => name.endsWith(' VIP');

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  const name = cmd.name?.trim();   // append and rename carry a name; for the others, ?. gives undefined
  if (name === '') return;                                   // a blank name changes nothing,
  if (name !== undefined && taken.value.has(name)) return;   // nor does one already in the list
  switch (cmd.type) {
    case 'append':
      model.names.value = [...names, name];   // a new array, not push: see Build 1's notes
      break;
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;        // by: how many places; -1 is up one, +1 down one
      if (j === i || j < 0 || j >= names.length) break;   // the name must go somewhere inside the list
      model.names.value = names.toSpliced(i, 1).toSpliced(j, 0, names[i]);   // take it out, put it back in at j
      break;
    }
    case 'rename':
      model.names.value = names.with(cmd.index, name);
      break;
    case 'vip': {   // add " VIP" to the end of the name, or take it off: a rename, so the rename rules apply
      const old = names[cmd.index];
      updateModel({ type: 'rename', index: cmd.index, name: isVip(old) ? old.slice(0, -4) : old + ' VIP' });
      break;
    }
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  settle({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- edit dialog
const editDialog = document.querySelector('#edit-dialog');
const editForm = document.querySelector('#edit-form');
const editTitle = document.querySelector('#edit-title');
const editBox = document.querySelector('#edit-box');
const editCancel = document.querySelector('#edit-cancel');
let editIndex;   // the row the dialog edits: a plain variable, since nothing is drawn from it

function onEdit(i, name) {
  editIndex = i;
  editTitle.textContent = `Editing No. ${i + 1} Name: ${name}`;
  editBox.value = name;
  editBox.defaultValue = name;   // what Revert, a reset button, puts back
  editDialog.showModal();   // until the dialog closes, the rest of the page ignores the mouse and keyboard
}

editForm.addEventListener('submit', () => {   // Ok, or Enter in the box; method="dialog" then closes the dialog
  updateModel({ type: 'rename', index: editIndex, name: editBox.value });
});
editCancel.addEventListener('click', () => editDialog.close());   // Escape closes it too, with no code of ours

// --------------- name list
const nameRows = document.querySelector('#name-rows');

// Gesture settings: change these until a swipe and a hold feel right
const MOVE_PX = 10;    // a finger that moves less than this is still pressing: a tap stays a tap, and a hold survives a tremble
const HOLD_MS = 500;   // how long a finger must press without moving before its row lifts
const OPEN_PX = 80;    // the width of an open row's Delete or VIP button

const swipe = signal(null);   // the view's own state: { index, dx }, the row being swiped and how far (dx < 0: Delete button out; dx > 0: VIP button out), or null
const open = signal(null);    // the view's own state: { index, dx }, the open row and its button (dx = -OPEN_PX: Delete; OPEN_PX: VIP), or null
const drag = signal(null);    // the view's own state: { index, dy, height }, the lifted row, how far down it is (up is negative) and a row's height, or null
let press = null;             // the finger on a name: { pointerId, index, x, y, from, height, timer }; nothing is drawn from it

// Build 8's updateAnimated, grown: in one view transition, apply cmd, if any, open openRow, if any (any change
// to the list closes an open row, whose index may now be another name's), and let go of a swiped or lifted row
function settle(cmd, openRow = null) {
  document.startViewTransition(() => batch(() => {
    if (cmd) updateModel(cmd);
    open.value = openRow;
    swipe.value = null;
    drag.value = null;
  }));
}

function onPointerDown(e, i) {
  if (e.pointerType !== 'touch' || press) return;   // fingers only, one at a time; a mouse uses the buttons
  press = { pointerId: e.pointerId, index: i, x: e.clientX, y: e.clientY, from: open.value?.index === i ? open.value.dx : 0,
            height: e.currentTarget.offsetHeight, timer: setTimeout(lift, HOLD_MS) };
}

function lift() {   // the finger pressed for HOLD_MS without moving
  drag.value = { index: press.index, dy: 0, height: press.height };
}

function onPointerMove(e) {
  if (e.pointerId !== press?.pointerId) return;   // not the finger we follow
  const dx = e.clientX - press.x, dy = e.clientY - press.y;
  if (drag.value) {
    drag.value = { ...drag.value, dy };   // lifted: the row follows the finger up and down
    return;
  }
  if (Math.abs(dx) >= MOVE_PX || Math.abs(dy) >= MOVE_PX) clearTimeout(press.timer);   // it moved, so it isn't a hold
  if (!swipe.value && Math.abs(dx) < MOVE_PX) return;   // not a swipe yet: a tap stays a tap
  let x = press.from + dx;                  // how far a button is out: x < 0, Delete; x > 0, VIP
  if (press.from < 0) x = Math.min(0, x);   // an open row can only close,
  if (press.from > 0) x = Math.max(0, x);   // not swing over to the other side
  swipe.value = { index: press.index, dx: x };
}

// What a swipe let go at s.dx leaves open: past halfway on either side, that side's button
function openAt(s) {
  if (s.dx <= -OPEN_PX / 2) return { index: s.index, dx: -OPEN_PX };
  if (s.dx >= OPEN_PX / 2) return { index: s.index, dx: OPEN_PX };
  return null;
}

// Where the lifted row would land: its own index plus the rows it has passed, rounded, kept inside the list
function dropIndex() {
  const { index, dy, height } = drag.value;
  return Math.min(Math.max(index + Math.round(dy / height), 0), model.names.value.length - 1);
}

function onPointerEnd(e) {   // pointerup: the finger lifted; pointercancel: the browser took it over, to scroll
  if (e.pointerId !== press?.pointerId) return;
  clearTimeout(press.timer);
  const up = e.type === 'pointerup', d = drag.value, s = swipe.value;
  if (d) settle(up ? { type: 'move', index: d.index, by: dropIndex() - d.index } : null);
  if (s) settle(null, up ? openAt(s) : null);
  press = null;
}

// The Delete button: grows from the row's right end, over the row's other buttons
function deleteButton(i, width) {
  return html`<button class="bin" style="width: ${width}px" @click=${() => settle({ type: 'delete', index: i })}>Delete</button>`;
}

// The VIP button: fills the gap at the row's left end; gold to make the name VIP, gray to take it back
function vipButton(i, name, width) {
  const vip = isVip(name);
  return html`<button class=${vip ? 'vip off' : 'vip'} style="width: ${width}px"
      @click=${() => settle({ type: 'vip', index: i })}>${vip ? 'Not VIP' : 'VIP'}</button>`;
}

nameRows.addEventListener('pointermove', onPointerMove);
nameRows.addEventListener('pointerup', onPointerEnd);
nameRows.addEventListener('pointercancel', onPointerEnd);
nameRows.addEventListener('touchend', e => { if (e.target.closest('.name')) e.preventDefault(); });   // a touch on a name never becomes a click
nameRows.addEventListener('touchmove', e => { if (drag.value) e.preventDefault(); });   // a lifted row moves, not the page

function row(name, i, names) {
  const dx = swipe.value?.index === i ? swipe.value.dx : open.value?.index === i ? open.value.dx : 0;
  const lifted = drag.value?.index === i;
  const dy = lifted ? drag.value.dy : 0;
  return html`<tr style="view-transition-name: row-${CSS.escape(name)}; translate: ${Math.max(0, dx)}px ${dy}px"
      class=${lifted ? 'lifted' : ''}>
    <td>${dx > 0 ? vipButton(i, name, dx) : ''}${i + 1}</td>
    <td class="name" @pointerdown=${e => onPointerDown(e, i)}>${name}</td>
    <td>
      <button @click=${() => onEdit(i, name)}>edit</button>
      <button ?disabled=${i === 0} @click=${() => settle({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => settle({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => settle({ type: 'delete', index: i })}>delete</button>
      ${dx < 0 ? deleteButton(i, -dx) : ''}
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **The model's `move` takes any number of places now.** `toSpliced(i, 1)` returns a copy of the array without the item at `i`, and `toSpliced(j, 0, x)` a copy with `x` put in at `j`; neither changes the original, which is what a signal needs (Build 1). Example: `['Ann', 'Bob', 'Cy', 'Dee']`, move index 0 by 2, so `j = 2`. Without Ann: `['Bob', 'Cy', 'Dee']`; Ann put in at 2: `['Bob', 'Cy', 'Ann', 'Dee']`. For a neighbor, `by` of -1 or +1, that is Build 3's swap, so up and down work as before. `j === i` joined the guard: a drop on the row's own place writes nothing.
- **A hold is a timer that a move cancels.** `onPointerDown` starts `setTimeout(lift, HOLD_MS)`, which calls `lift` 500 ms later unless `clearTimeout` stops it first. `onPointerMove` stops it once the finger has moved `MOVE_PX` any way, and `onPointerEnd` stops it when the finger lifts. So `lift` runs only for a finger that stayed within 10 px for half a second.
- **`lift` writes `drag`,** another view-only signal, like `swipe` and `open`: which row is lifted, how far the finger has moved since it went down (`dy`, negative going up), and the row's height, which `onPointerDown` measured with `offsetHeight`. Each move then writes `{ ...drag.value, dy }`: `...drag.value` copies every field into a new object, and `dy` replaces the old one, so the signal gets a new value (Build 1's rule).
- **A swipe and a hold can't both happen.** A swipe starts only after a move of `MOVE_PX`, which has already stopped the timer, and once the row is lifted, `onPointerMove` returns before it reaches the swipe code.
- **The lifted row** has the class `lifted`. `scale: 1.05` draws it at 105 % size and, like `translate`, moves nothing else; `transition: scale 0.15s` makes it grow over 0.15 s instead of jumping. Every row has a `translate`, even `0px 0px`, and that makes the browser draw each row as a layer of its own, stacked in page order, so a later row covers an earlier one. `z-index: 1` puts the lifted row on top. It works only on a *positioned* element, hence `position: relative`, which, with no offsets, leaves the row where it was.
- **`-webkit-user-select: none`** on the name: on a phone, a long press on text selects it, and this turns that off, so a hold lifts the row instead. iPhone Safari knows only the `-webkit-` spelling, and Chrome and Firefox accept it as well.
- **The page must not scroll under a lifted row.** `touch-action: pan-y` lets the browser scroll on a vertical move, and the browser reads it once, when the finger lands, so it can't be turned off when the row lifts. The touch events, which Build 10 used for `touchend`, still can: the browser waits for `touchmove` listeners before it scrolls, and `e.preventDefault()` in one cancels the scroll. That works from a listener on an element such as `nameRows`. Browsers make touch listeners on the window, the document and the body *passive* by default, unable to cancel, so that pages scroll without waiting for them.
- **`dropIndex()` turns the drag into a place in the list:** the rows passed, `dy / height`, rounded to the nearest whole row and added to where the row started, then kept between 0 and the last index by `Math.max` and `Math.min`. Example: rows 23 px tall, as Chrome draws them here, and `Ann` at index 0 dragged 39 px down: 39 / 23 ≈ 1.7, rounded to 2, so she lands at index 2. Dragged 300 px in a list of 4: 0 + 13 = 13, kept to 3. It assumes every row is as tall as the lifted one, which holds while each name fits on one line.
- **`onPointerEnd` drops the row with `settle`,** which now also clears `drag`: in one view transition, the move is applied, so the lifted row slides from under the finger into its new place, and the rows it passed slide into theirs. A drop on its own place, or a `pointercancel`, moves nothing, and the row settles back. The drop leaves out `settle`'s second argument, so it also closes an open Delete or VIP button.
- **Tuning the feel.** The gesture settings at the top of the list section, and two values in `index.html`:
  - `HOLD_MS`, 500: how long to hold before the row lifts. Shorter, and a row lifts when you only rested your finger before scrolling; longer, and reordering feels slow. Apple's long press waits the same 0.5 s by default ([`minimumPressDuration`](https://developer.apple.com/documentation/uikit/uilongpressgesturerecognizer/minimumpressduration)).
  - `MOVE_PX`, 10: how far a finger may drift and still count as holding still, and how far it must go before a swipe starts. Smaller, and the natural tremble of a fingertip cancels holds; larger, and swipes start late. Apple allows 10 points ([`allowableMovement`](https://developer.apple.com/documentation/uikit/uilongpressgesturerecognizer/allowablemovement)), which, with Build 9's viewport line, is 10 CSS pixels.
  - `OPEN_PX`, 80: the width of the Delete and VIP buttons, from Builds 12 and 13.
  - In `index.html`, `scale: 1.05`, how much the lifted row grows, and `0.15s`, how fast.

What changed from Build 13:

1. The model's `move` takes any number of places, with `toSpliced`.
2. `index.html`'s `<style>` stops the name's text from being selected and styles the lifted row.
3. The list section has `HOLD_MS`, the `drag` signal, `lift`, `dropIndex` and a `touchmove` listener. `press` also keeps `y`, the row's height and the timer; `settle` also clears `drag`; and `onPointerMove` and `onPointerEnd` handle a lifted row.
4. `row` draws the lifted row with a vertical `translate` and the `lifted` class.

**Try it,** on a phone or with the device toolbar:

- Append `Ann`, `Bob`, `Cy` and `Dee`. Hold `Ann`'s name still: after half a second her row grows. Drag it down two rows and let go: she drops in at No. 3, and the rows slide into place.
- Hold a name and let go without moving it: the row settles back.
- Press a name and move down at once: no row lifts. Press and move left at once: its Delete button slides out, as in Build 12.
- **Tune the feel:** set `HOLD_MS` to `200` and reload: rows lift when you meant to tap or scroll. Set it to `1000`: holding feels slow. Set `MOVE_PX` to `3`: holds fail because your finger trembles. Keep the values that feel right to you.

</details>

## Build 15: rows part while you drag

<details>
<summary>Read, code, notes, try it</summary>
<br>

As on the iPhone, the rows step aside while you drag, so you see where the row will land before you let go. Only the view changes.

**Read:** nothing new. The CSS transition is the kind Build 14 read about.

**Code:** in `.temp/name-list/index.html`, replace the `<style>` block with:

```html
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; -webkit-user-select: none; }
    #name-rows td:first-child { position: relative; }
    #name-rows td:last-child { white-space: nowrap; position: relative; }
    #name-rows .bin, #name-rows .vip { position: absolute; top: 0; height: 100%; padding: 0; border: 0; overflow: hidden; white-space: nowrap; }
    #name-rows .bin { right: 0; background: #a33; color: #eee; }
    #name-rows .vip { right: 100%; background: #fc0; color: #333; }
    #name-rows .vip.off { background: #777; color: #eee; }
    #name-rows tr { transition: scale 0.15s; }
    #name-rows tr.lifted { scale: 1.05; background: #555; position: relative; z-index: 1; }
    #name-rows tr.parting { transition: translate 0.2s; }
  </style>
```

<details>
<summary>Complete index.html</summary>

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>Names</title>
  <style>
    :root { color-scheme: dark; } body { background: #333; color: #eee; }
    ::view-transition-group(*) { animation-duration: 0.5s; }
    #name-rows .name { overflow-wrap: anywhere; touch-action: pan-y; -webkit-user-select: none; }
    #name-rows td:first-child { position: relative; }
    #name-rows td:last-child { white-space: nowrap; position: relative; }
    #name-rows .bin, #name-rows .vip { position: absolute; top: 0; height: 100%; padding: 0; border: 0; overflow: hidden; white-space: nowrap; }
    #name-rows .bin { right: 0; background: #a33; color: #eee; }
    #name-rows .vip { right: 100%; background: #fc0; color: #333; }
    #name-rows .vip.off { background: #777; color: #eee; }
    #name-rows tr { transition: scale 0.15s; }
    #name-rows tr.lifted { scale: 1.05; background: #555; position: relative; z-index: 1; }
    #name-rows tr.parting { transition: translate 0.2s; }
  </style>
  <script type="importmap">
  { "imports": {
      "lit-html": "./vendor/lit-html.js",
      "@preact/signals-core": "./vendor/signals-core.mjs"
  } }
  </script>
  <!-- add console display --> <script src="./vendor/eruda.js"></script> <script> localStorage.removeItem('eruda-dev-tools'); localStorage.setItem('eruda-entry-button', '{"rememberPos":false}'); eruda.init({ tool: ['console'], defaults: { displaySize: 30, theme: 'Dark' } }); eruda.get('console').config.set('displayExtraInfo', true); eruda.show(); </script>
</head>
<body>
  <form id="name-form"><label>Name: <input id="name-box"></label> <button>append</button></form>
  <dialog id="edit-dialog">
    <form id="edit-form" method="dialog">
      <p id="edit-title"></p>
      <p><input id="edit-box" autofocus></p>
      <button>Ok</button> <button type="reset">Revert</button> <button id="edit-cancel" type="button">Cancel</button>
    </form>
  </dialog>
  <div style="overflow-x: clip">
    <table>
      <caption>Name List</caption>
      <thead><tr><th>No.</th><th>Name</th></tr></thead>
      <tbody id="name-rows"></tbody>
    </table>
  </div>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

</details>

Then replace `.temp/name-list/main.js` with:

```js
import { signal, computed, effect, batch } from '@preact/signals-core';
import { html, render } from 'lit-html';

// Model state: the names, in order
const model = { names: signal([]) };

// Derived value: the names as a Set, which finds a name without searching
const taken = computed(() => {
  console.log('taken');
  return new Set(model.names.value);
});

// A VIP's name ends in " VIP"; the model and the VIP button both ask
const isVip = name => name.endsWith(' VIP');

// Update model: the only code that writes model.names; cmd says what to do
function updateModel(cmd) {
  const names = model.names.value;
  const name = cmd.name?.trim();   // append and rename carry a name; for the others, ?. gives undefined
  if (name === '') return;                                   // a blank name changes nothing,
  if (name !== undefined && taken.value.has(name)) return;   // nor does one already in the list
  switch (cmd.type) {
    case 'append':
      model.names.value = [...names, name];   // a new array, not push: see Build 1's notes
      break;
    case 'delete':
      model.names.value = names.filter((_, i) => i !== cmd.index);   // keep every name but the one at cmd.index
      break;
    case 'move': {
      const i = cmd.index, j = cmd.index + cmd.by;        // by: how many places; -1 is up one, +1 down one
      if (j === i || j < 0 || j >= names.length) break;   // the name must go somewhere inside the list
      model.names.value = names.toSpliced(i, 1).toSpliced(j, 0, names[i]);   // take it out, put it back in at j
      break;
    }
    case 'rename':
      model.names.value = names.with(cmd.index, name);
      break;
    case 'vip': {   // add " VIP" to the end of the name, or take it off: a rename, so the rename rules apply
      const old = names[cmd.index];
      updateModel({ type: 'rename', index: cmd.index, name: isVip(old) ? old.slice(0, -4) : old + ' VIP' });
      break;
    }
  }
}

// --------------- name form
const nameForm = document.querySelector('#name-form');
const nameBox = document.querySelector('#name-box');
nameForm.addEventListener('submit', e => {
  e.preventDefault();   // a form's default is to send itself to the server, which reloads the page
  settle({ type: 'append', name: nameBox.value });
  nameBox.value = '';
});

// --------------- edit dialog
const editDialog = document.querySelector('#edit-dialog');
const editForm = document.querySelector('#edit-form');
const editTitle = document.querySelector('#edit-title');
const editBox = document.querySelector('#edit-box');
const editCancel = document.querySelector('#edit-cancel');
let editIndex;   // the row the dialog edits: a plain variable, since nothing is drawn from it

function onEdit(i, name) {
  editIndex = i;
  editTitle.textContent = `Editing No. ${i + 1} Name: ${name}`;
  editBox.value = name;
  editBox.defaultValue = name;   // what Revert, a reset button, puts back
  editDialog.showModal();   // until the dialog closes, the rest of the page ignores the mouse and keyboard
}

editForm.addEventListener('submit', () => {   // Ok, or Enter in the box; method="dialog" then closes the dialog
  updateModel({ type: 'rename', index: editIndex, name: editBox.value });
});
editCancel.addEventListener('click', () => editDialog.close());   // Escape closes it too, with no code of ours

// --------------- name list
const nameRows = document.querySelector('#name-rows');

// Gesture settings: change these until a swipe and a hold feel right
const MOVE_PX = 10;    // a finger that moves less than this is still pressing: a tap stays a tap, and a hold survives a tremble
const HOLD_MS = 500;   // how long a finger must press without moving before its row lifts
const OPEN_PX = 80;    // the width of an open row's Delete or VIP button

const swipe = signal(null);   // the view's own state: { index, dx }, the row being swiped and how far (dx < 0: Delete button out; dx > 0: VIP button out), or null
const open = signal(null);    // the view's own state: { index, dx }, the open row and its button (dx = -OPEN_PX: Delete; OPEN_PX: VIP), or null
const drag = signal(null);    // the view's own state: { index, dy, height }, the lifted row, how far down it is (up is negative) and a row's height, or null
let press = null;             // the finger on a name: { pointerId, index, x, y, from, height, timer }; nothing is drawn from it

// Build 8's updateAnimated, grown: in one view transition, apply cmd, if any, open openRow, if any (any change
// to the list closes an open row, whose index may now be another name's), and let go of a swiped or lifted row
function settle(cmd, openRow = null) {
  document.startViewTransition(() => batch(() => {
    if (cmd) updateModel(cmd);
    open.value = openRow;
    swipe.value = null;
    drag.value = null;
  }));
}

function onPointerDown(e, i) {
  if (e.pointerType !== 'touch' || press) return;   // fingers only, one at a time; a mouse uses the buttons
  press = { pointerId: e.pointerId, index: i, x: e.clientX, y: e.clientY, from: open.value?.index === i ? open.value.dx : 0,
            height: e.currentTarget.offsetHeight, timer: setTimeout(lift, HOLD_MS) };
}

function lift() {   // the finger pressed for HOLD_MS without moving
  drag.value = { index: press.index, dy: 0, height: press.height };
}

function onPointerMove(e) {
  if (e.pointerId !== press?.pointerId) return;   // not the finger we follow
  const dx = e.clientX - press.x, dy = e.clientY - press.y;
  if (drag.value) {
    drag.value = { ...drag.value, dy };   // lifted: the row follows the finger up and down
    return;
  }
  if (Math.abs(dx) >= MOVE_PX || Math.abs(dy) >= MOVE_PX) clearTimeout(press.timer);   // it moved, so it isn't a hold
  if (!swipe.value && Math.abs(dx) < MOVE_PX) return;   // not a swipe yet: a tap stays a tap
  let x = press.from + dx;                  // how far a button is out: x < 0, Delete; x > 0, VIP
  if (press.from < 0) x = Math.min(0, x);   // an open row can only close,
  if (press.from > 0) x = Math.max(0, x);   // not swing over to the other side
  swipe.value = { index: press.index, dx: x };
}

// What a swipe let go at s.dx leaves open: past halfway on either side, that side's button
function openAt(s) {
  if (s.dx <= -OPEN_PX / 2) return { index: s.index, dx: -OPEN_PX };
  if (s.dx >= OPEN_PX / 2) return { index: s.index, dx: OPEN_PX };
  return null;
}

// Where the lifted row would land: its own index plus the rows it has passed, rounded, kept inside the list
function dropIndex() {
  const { index, dy, height } = drag.value;
  return Math.min(Math.max(index + Math.round(dy / height), 0), model.names.value.length - 1);
}

// How far row i is drawn from its place during a drag: the lifted row follows the finger, and the rows it passed step aside
function offsetY(i) {
  const { index, dy, height } = drag.value, to = dropIndex();
  if (i === index) return dy;
  if (index < i && i <= to) return -height;   // passed on the way down: up one row, into the gap
  if (to <= i && i < index) return height;    // passed on the way up: down one row
  return 0;
}

function onPointerEnd(e) {   // pointerup: the finger lifted; pointercancel: the browser took it over, to scroll
  if (e.pointerId !== press?.pointerId) return;
  clearTimeout(press.timer);
  const up = e.type === 'pointerup', d = drag.value, s = swipe.value;
  if (d) settle(up ? { type: 'move', index: d.index, by: dropIndex() - d.index } : null);
  if (s) settle(null, up ? openAt(s) : null);
  press = null;
}

// The Delete button: grows from the row's right end, over the row's other buttons
function deleteButton(i, width) {
  return html`<button class="bin" style="width: ${width}px" @click=${() => settle({ type: 'delete', index: i })}>Delete</button>`;
}

// The VIP button: fills the gap at the row's left end; gold to make the name VIP, gray to take it back
function vipButton(i, name, width) {
  const vip = isVip(name);
  return html`<button class=${vip ? 'vip off' : 'vip'} style="width: ${width}px"
      @click=${() => settle({ type: 'vip', index: i })}>${vip ? 'Not VIP' : 'VIP'}</button>`;
}

nameRows.addEventListener('pointermove', onPointerMove);
nameRows.addEventListener('pointerup', onPointerEnd);
nameRows.addEventListener('pointercancel', onPointerEnd);
nameRows.addEventListener('touchend', e => { if (e.target.closest('.name')) e.preventDefault(); });   // a touch on a name never becomes a click
nameRows.addEventListener('touchmove', e => { if (drag.value) e.preventDefault(); });   // a lifted row moves, not the page

function row(name, i, names) {
  const dx = swipe.value?.index === i ? swipe.value.dx : open.value?.index === i ? open.value.dx : 0;
  const lifted = drag.value?.index === i;
  const dy = drag.value ? offsetY(i) : 0;
  return html`<tr style="view-transition-name: row-${CSS.escape(name)}; translate: ${Math.max(0, dx)}px ${dy}px"
      class=${lifted ? 'lifted' : drag.value ? 'parting' : ''}>
    <td>${dx > 0 ? vipButton(i, name, dx) : ''}${i + 1}</td>
    <td class="name" @pointerdown=${e => onPointerDown(e, i)}>${name}</td>
    <td>
      <button @click=${() => onEdit(i, name)}>edit</button>
      <button ?disabled=${i === 0} @click=${() => settle({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => settle({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => settle({ type: 'delete', index: i })}>delete</button>
      ${dx < 0 ? deleteButton(i, -dx) : ''}
    </td>
  </tr>`;
}

effect(() => {
  const names = model.names.value;
  console.log('render');
  render(names.length === 0 ? html`<tr><td colspan="2">No names yet</td></tr>` : names.map(row), nameRows);
});
```

- **`offsetY(i)` says how far each row is drawn from its place during a drag.** The lifted row follows the finger, as in Build 14. A row it has passed steps one row toward the place the lifted row left: up if it passed going down, down if going up. The others stay. Example: `['Ann', 'Bob', 'Cy', 'Dee']`, rows 23 px tall, and `Ann` (index 0) dragged 39 px down, so `dropIndex()` is 2. `Bob` (1) and `Cy` (2) lie between 0 and 2, so each is drawn 23 px up: `Bob` into Ann's old place, `Cy` into Bob's. That leaves place 2 open, where Ann will land. `Dee` (3) stays.
- **`dropIndex()` now has two readers,** the drop and `offsetY`, so the gap you see is where the row lands.
- **Only the rows stepping aside glide.** During a drag, every row but the lifted one has the class `parting`, whose `transition: translate 0.2s` makes each change of its `translate` take 0.2 s. The lifted row has no such transition, so it follows the finger without lag.
- **The class also keeps the drop from moving rows twice.** In the redraw at the drop, each `translate` goes back to 0 and `parting` goes away together, so the rows change without a transition. Nothing visibly jumps: `.map` keeps the `<tr>`s in place (Build 3), and each now shows the name that was drawn there during the drag. Each name is where it was on screen, so the view transition moves only the lifted row, into the gap.

What changed from Build 14:

1. `index.html`'s `<style>` has a `parting` rule.
2. `offsetY` joined the list section.
3. During a drag, `row` draws every row with `offsetY` and gives all but the lifted one the `parting` class.

**Try it,** on a phone or with the device toolbar:

- Append `Ann`, `Bob`, `Cy` and `Dee`. Lift `Ann` and drag her down slowly: `Bob` slides up as she passes him, then `Cy`.
- Drag her back up: they slide back.
- Let go in the gap above `Dee`: only Ann moves, into the gap.
- Change `0.2s` to `1s` and reload, to watch the rows step aside slowly.

</details>

## Next

[STUDY_PLAN_3.md](STUDY_PLAN_3.md) uses the same tools on the dot runner and puts the model, the view and the controller in separate files. Its Step 0 builds a lit-html and Preact Signals hello world, which you can now go through quickly. Delete `.temp/name-list` when you no longer need it.
