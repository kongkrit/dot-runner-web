[README.md](README.md) · [HOW_AND_WALKTHROUGH.md](HOW_AND_WALKTHROUGH.md) · [STUDY_PLAN_1.md](STUDY_PLAN_1.md) · [STUDY_PLAN_3.md](STUDY_PLAN_3.md)

# Study plan 2: a name list, four builds

The goal: see lit-html do the job it is made for. In [STUDY_PLAN_1.md](STUDY_PLAN_1.md)'s Build 5, the form's elements never change, only their text does, and Build 4's effects already handled that, so lit-html added little. Here the data decides how many rows the page has and in what order: rows appear, disappear and move. That is where hand-written DOM code grows with every feature, and lit-html code doesn't.

You build one small app, a list of names, in four steps, one per build:

1. append a name;
2. delete a row;
3. move a row up or down;
4. edit a name in place.

What never changes, the form and the table's caption and header, stays in `index.html`, written once. lit-html draws only the table's rows. Each build has STUDY_PLAN_1's three parts, in one `main.js`: a **model**, which holds the names and the one function that changes them; a **view**, which draws the rows; and a **controller**, the listeners that turn clicks and key presses into model updates. The code is grouped as in STUDY_PLAN_1's Build 4: the model at the top, then one section per component.

Each build has three steps: **read** the listed sections, in order; then copy the code, run it and read the notes under it; then **try** the things listed. You write no code in this plan: every build is printed in full. It builds on STUDY_PLAN_1, so `signal`, `effect`, `batch`, `` html`…` ``, `render` and slots are not explained again.

## The app

- **Name:** a text box and an **append** button. Clicking append, or pressing Enter in the box, adds the name to the end of the list and clears the box. A blank name is ignored.
- **Name List:** a table with the columns **No.** (1, 2, 3, …) and **Name**. When it is empty, it says "No names yet".
- Each row ends in buttons, one kind more per build: **delete** (Build 2); **up** and **down**, which swap the row with its neighbor (Build 3); and **edit**, which turns the name into a text box, where leaving the box or pressing Enter saves the new name (Build 4).

The app's state is one value, `names`, an array of strings held in a signal. Build 4 adds a second signal, which belongs to the view, not the model: which row is being edited.

## Setup

From the repo root:

```bash
mkdir -p .temp/name-list && cp -r vendor .temp/name-list/
```

Then create `.temp/name-list/index.html`, the same for all four builds:

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

- **The model is one signal holding an array,** and `updateModel(cmd)` is the only code that writes it. `cmd` is an object that says what to do, such as `{ type: 'append', name: 'Ann' }`, and the `switch` on `cmd.type` picks the rule for it. Each build adds one `case`. The dot runner works the same way: its `model.update(cmd)` is the one function that changes its state.
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
2. MDN [`HTMLElement.focus()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus), [`HTMLElement.blur()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/blur) and, again, the [`blur` event](https://developer.mozilla.org/en-US/docs/Web/API/Element/blur_event).
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
  if (e.key === 'Enter') e.target.blur();   // Enter commits too, by leaving the box
}

function row(name, i, names) {
  return html`<tr>
    <td>${i + 1}</td>
    <td>${i === editing.value
      ? html`<input value=${name} @blur=${e => onEditDone(i, e)} @keydown=${onEditKey}>`
      : name}</td>
    <td>
      <button ?disabled=${i === 0} @click=${() => updateModel({ type: 'move', index: i, by: -1 })}>up</button>
      <button ?disabled=${i === names.length - 1} @click=${() => updateModel({ type: 'move', index: i, by: 1 })}>down</button>
      <button @click=${() => onEdit(i)}>edit</button>
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
- **Leaving the box commits.** `@blur` calls `onEditDone`, which renames and closes the box. Enter calls `e.target.blur()`, which takes the focus away and so fires the same `blur`: one path for both. Clicking anywhere else, another row's button included, also blurs the box first: the browser moves the focus when the mouse button goes down, before the click, so the name is saved before the other button acts.
- `onEditDone` wraps its two writes in `batch`, so the effect draws once, with the new name and the box closed, rather than twice.
- **One rule for blank names.** Rename needs the rule that append already had, so the rule moved from the `append` case to the top of `updateModel`, where it covers both. In `cmd.name?.trim()`, the `?.` gives `undefined` instead of throwing an error when `cmd.name` is missing, as it is for delete and move. So `name` is `''` only for a blank append or rename, and a blank edit leaves the old name.
- **Why lit-html helps here.** By hand, edit means: swap the name's text for an `<input>`, swap it back on blur, and remember which row is open. Here the template says what a row looks like with and without `editing`, and the same effect as before draws it.

What changed from Build 3:

1. `batch` joined the import.
2. The blank-name check moved from the `append` case to the top of `updateModel`, and a `rename` case joined the `switch`.
3. The list section has the `editing` signal and three handlers: `onEdit`, `onEditDone` and `onEditKey`.
4. `row`'s name cell switches between the name and a text box, and an edit button sits before delete.

**Try it,** with the console open:

- Append `Ann` and `Bob`, then click edit on `Ann`: her name becomes a text box holding `Ann`, with the cursor in it. One `render`.
- Change it to `Anna` and click an empty part of the page: the box closes on `Anna`. One `render`, thanks to `batch`.
- Edit again and press Enter instead: the same.
- Edit, clear the box and press Enter: `Anna` stays.
- Edit `Bob`, then click up on his row without leaving the box first: the new name is saved, then the row moves.

## Next

[STUDY_PLAN_3.md](STUDY_PLAN_3.md) uses the same tools on the dot runner and puts the model, the view and the controller in separate files. Its Step 0 builds a lit-html and Preact Signals hello world, which you can now go through quickly. Delete `.temp/name-list` when you no longer need it.
