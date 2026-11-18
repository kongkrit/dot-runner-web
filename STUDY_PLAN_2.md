[README.md](README.md) · [HOW_AND_WALKTHROUGH.md](HOW_AND_WALKTHROUGH.md) · [STUDY_PLAN_1.md](STUDY_PLAN_1.md) · [STUDY_PLAN_3.md](STUDY_PLAN_3.md)

# Study plan 2: a name list, eight builds

The goal: see lit-html do the job it is made for. In [STUDY_PLAN_1.md](STUDY_PLAN_1.md)'s Build 5, the form's elements never change, only their text does, and Build 4's effects already handled that, so lit-html added little. Here the data decides how many rows the page has and in what order: rows appear, disappear and move. That is where hand-written DOM code grows with every feature, and lit-html code doesn't.

You build one small app, a list of names, in eight steps, one per build:

1. append a name;
2. delete a row;
3. move a row up or down;
4. edit a name in place;
5. refuse a name already in the list, by searching the array;
6. the same, with a Set, which finds a name without searching;
7. edit a name in a pop-up dialog instead of in place;
8. animate the rows as they appear, disappear and move.

Builds 5 and 6 change only the model, so the view stays Build 4's. Build 7 changes only how a name is edited, and Build 8 only animates the changes.

What never changes, the form and the table's caption and header, stays in `index.html`, written once. lit-html draws only the table's rows. Each build has STUDY_PLAN_1's three parts, in one `main.js`: a **model**, which holds the names and the one function that changes them; a **view**, which draws the rows; and a **controller**, the listeners that turn clicks and key presses into model updates. The code is grouped as in STUDY_PLAN_1's Build 4: the model at the top, then one section per component.

Each build has three steps: **read** the listed sections, in order; then copy the code, run it and read the notes under it; then **try** the things listed. You write no code in this plan: every build is printed in full. It builds on STUDY_PLAN_1, so `signal`, `computed`, `effect`, `batch`, `` html`…` ``, `render` and slots are not explained again.

## The app

- **Name:** a text box and an **append** button. Clicking append, or pressing Enter in the box, adds the name to the end of the list and clears the box. A blank name is ignored, and from Build 5 on, so is a name already in the list.
- **Name List:** a table with the columns **No.** (1, 2, 3, …) and **Name**. When it is empty, it says "No names yet".
- Each row ends in buttons, one kind more per build: **delete** (Build 2); **up** and **down**, which swap the row with its neighbor (Build 3); and **edit**, placed first, which turns the name into a text box, where leaving the box or pressing Enter saves the new name and Escape puts the old one back (Build 4). Build 7's edit opens a pop-up dialog instead, with **Ok**, which saves; **Revert**, which puts the old name back in the box; and **Cancel**, which closes the dialog without saving.
- From Build 8 on, a new row fades in, a deleted one fades out, and a moved one slides to its new place.

The app's state is one value, `names`, an array of strings held in a signal. Build 4 adds a second signal, which belongs to the view, not the model: which row is being edited. Build 7 keeps that in a plain variable instead, since nothing on the screen is drawn from it.

## Setup

From the repo root:

```bash
mkdir -p .temp/name-list && cp -r vendor .temp/name-list/
```

Then create `.temp/name-list/index.html`, the same for Builds 1 to 6 (Build 7 adds a dialog to it, and Build 8 one CSS rule):

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

To run any build, from the repo root:

```bash
cd .temp/name-list && uv run --no-project python -m http.server 8001
```

Then open <http://localhost:8001>. After you replace `main.js`, reload the page; if a change doesn't show, hard-reload with Ctrl+Shift+R (Mac: Cmd+Shift+R). What `console.log` prints shows in the Eruda panel at the bottom of the page.

## Build 1: append

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

## Build 2: delete

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

## Build 3: up and down

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

## Build 4: edit

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

## Build 5: no duplicates, with includes

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

## Build 6: no duplicates, with a Set

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

## Build 7: edit in a dialog

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

## Build 8: animate the rows

A new row fades in, a deleted one fades out while the rows below slide up, and up and down slide two rows past each other. The browser does the animation; the code only tells it when a change starts and which element is which row. The model and the edit dialog are Build 7's.

**Read:**

1. MDN [View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API): the introduction.
2. MDN [Using the View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using): [The view transition process](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using#the_view_transition_process), [Basic SPA view transition](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using#basic_spa_view_transition) (an *SPA*, single-page app, is a page that changes itself, as this one does), [Customizing your animations](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using#customizing_your_animations) and [Different animations for different elements](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using#different_animations_for_different_elements).
3. MDN: [`Document.startViewTransition()`](https://developer.mozilla.org/en-US/docs/Web/API/Document/startViewTransition), [`view-transition-name`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/view-transition-name) and [`CSS.escape()`](https://developer.mozilla.org/en-US/docs/Web/API/CSS/escape_static).

**Code:** in `.temp/name-list/index.html`, replace the `<style>` line with:

```html
  <style> :root { color-scheme: dark; } body { background: #333; color: #eee; } ::view-transition-group(*) { animation-duration: 0.5s; } </style>
```

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

## Next

[STUDY_PLAN_3.md](STUDY_PLAN_3.md) uses the same tools on the dot runner and puts the model, the view and the controller in separate files. Its Step 0 builds a lit-html and Preact Signals hello world, which you can now go through quickly. Delete `.temp/name-list` when you no longer need it.
