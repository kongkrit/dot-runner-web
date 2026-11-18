# Proposal: extract a reusable MVC template (Preact Signals + lit-html)

**Status:** proposal, nothing built yet. Written 2026-11-16. Describes the code as of commit `d3af8f6` of this repo (`dot-runner-web`), and `HOW_AND_WALKTHROUGH.md` (then part of the README) as of its "Singleton vs factory vs class" revision.
**Audience:** a fresh Claude Code session with no memory of the conversation that produced this repo. Everything you need is here or in the files it names. Where this document and `.claude/CLAUDE.md` ever disagree, `CLAUDE.md` is the source of truth for the current code.
**Before doing anything:** read `.claude/CLAUDE.md`, `.claude/rules/markdown.md`, `.checks/boundaries.py`, `.checks/stop-hook.sh` and `.claude/settings.json`. Then settle the [open decisions](#4-open-decisions-ask-the-user-first) with the user.

## TL;DR

This repo's `.claude/CLAUDE.md`, together with `.checks/boundaries.py` and two hooks, has turned into a general recipe: front-end code in model, view and controller parts using `@preact/signals-core` and `lit-html`, with no build step, and with boundaries enforced while Claude Code edits. About two thirds of it is not specific to the dot app. The proposal is to extract that two thirds into a **one-version skeleton in a GitHub template repository**. The general architecture rules move into `.claude/rules/mvc.md`, so that each new project's `CLAUDE.md` holds only what is specific to it. The template's first user would be a **portfolio app** (portfolios → holdings → buy/sell transactions).

## 1. Context a fresh session needs

### 1.1 The person

- **Background:** a hardware and embedded-C engineer (BS EE) learning front-end development. They said plainly that abstract software ideas make them nervous. Explain with C or hardware analogies that hold, say where each analogy breaks, and lay out pros and cons honestly instead of just reassuring. The full style guide is `CLAUDE.md` → "How to explain things".
- **Values:** simple, minimal, DRY, code split into clear parts. Where an exception to DRY makes code easier to learn from, they accept it if it is stated openly (see "Deliberate duplication" in `CLAUDE.md`).
- **Workflow:**
  - commit or push only when they ask, always straight to `main` and never on a branch;
  - non-trivial changes are planned first, and they often steer the plan;
  - they like being shown options with a recommendation;
  - tooling goes in dot-prefixed folders (`.checks/`, `.tools/`), so learners reading the repo are not distracted;
  - verify by actually running things (headless Chromium, real key presses) rather than assuming.
- **They may run more than one Claude Code session in this repo at once.** Before editing shared files such as `CLAUDE.md`, check `git status`. If files change under you, stop and ask.

### 1.2 What this repo is

A red dot moves on a 16×8 grid in the last arrow-key direction pressed (Space stops it), and a readout shows its position as one hex byte: `(row << 4) | col`, starting at `47`. It ports a bare-metal C program, `C/dot_runner.c`, whose pieces are `model_update()`, `view_update()`, `controller_read()` and an NMI (non-maskable interrupt) tick. The page runs the same app **three times**, built three ways, in three self-contained folders that share nothing but `vendor/`:

```
index.html     import map, CSS, #app-singleton / #app-factory / #app-class containers, one module script each
singleton/     each part exists once; state in file-level variables; parts are ready-made objects
  model-controller-common.js   Cmd only: the controller→model message (like the C `command` enum)
  model.js        exports `model` (signals at file level, read-only computeds, update(cmd))
  view.js         exports viewUpdate(m, container); the only file in the folder importing lit-html
  controller.js   exports `controller` (key table, file-level `pending` latch, keydown/read)
  main.js         wires them; effect(() => viewUpdate(model, document.querySelector('#app-singleton')))
factory/       main.js creates every part with closure factories
  model-controller-common.js   byte-identical copy of the singleton one (enforced by the check)
  model.js        createModel()
  view.js         createView(container) → { update(m) }  (same template as singleton/view.js)
  controller.js   createController()
  main.js         creates model, view, controller; effect(() => view.update(model))
class/         main.js creates every part with `new`; state in `#` private fields
  model-controller-common.js   byte-identical copy of the singleton one (enforced by the check)
  model.js        class Model (update() is a prototype method, shared by all instances)
  view.js         class View: new View(container), view.update(m)
  controller.js   class Controller (#pending latch)
  main.js         new Model() / View / Controller; listener wrapped as e => controller.keydown(e)
vendor/        lit-html 3.3.3 (lit-html.js), @preact/signals-core 1.14.5 (signals-core.mjs)
.checks/       boundaries.py (the checker), stop-hook.sh (Stop hook wrapper)
.tools/        serve.py (dev server: Python's http.server plus Cache-Control: no-store), plan_diffs.py (STUDY_PLAN_2's diffs)
C/             the original C program
```

- **Run it:** `uv run --no-project python .tools/serve.py`, then open <http://localhost:8000>. `.tools/serve.py` is Python's `http.server` plus `Cache-Control: no-store`, so browsers never reuse a stale copy.
- **Build:** there is no npm and no build step. The browser loads the vendored libraries as ES modules, through the import map in `index.html`.
- **README.md** is a short front page: what the app is, how to run it, links to the other docs. **HOW_AND_WALKTHROUGH.md** explains everything for the learner. It has a "Code walkthrough" that copies each file in full, folded per folder, and a "Singleton vs factory vs class" section that compares all three: a three-column table of the obvious differences, subtle differences, pros and cons for each, a "Factory vs class" table and "Which to use". Read it to see how explanations are pitched.
- **History worth knowing:**
  - A version called `mixed/` (a singleton controller plus a factory model) existed from commit `236ef82` and was removed in `3e3c56e`, when the user chose fully self-contained versions.
  - Before `3e3c56e`, `view.js` and `model-controller-common.js` were shared at the root.
  - `class/` was added in `d3af8f6`, after a discussion of closures versus classes, so the trade-off can be compared on real code.

### 1.3 Decisions already made (keep them unless the user reopens them)

| Decision | Reason |
|---|---|
| Model / view / controller / `main.js`, as in the C program | The user thinks in that structure; each file maps to a C function. |
| State lives in `signal`s; the outside gets read-only `computed` views | A write from outside throws at run time, like a `const model_t *` that is actually enforced. |
| Only `model.update(cmd)` changes state | One write path, like `model_update()`. |
| Each view draws once per call: `viewUpdate(m, container)` in singleton; `view.update(m)` on a view made by `createView(container)` in factory or `new View(container)` in class. lit-html is imported only by `view.js` | Swapping the view library would touch one file per version. |
| The redraw `effect` lives in `main.js` (the user chose "option A", after comparing it with putting it in the view) | This matches the Elm architecture, where the runtime owns the update→view loop, and keeps the view a plain drawing function. The check enforces that the redraw call is made only inside an `effect` in `main.js`, so the screen cannot go stale. |
| Browser globals (`window`, `document`, timers, `fetch`, `localStorage`, `addEventListener`, ...) only in `main.js` | Parts get what they need passed in (the key event, the container); the model stays pure and testable. |
| The grid size (`WIDTH`, `HEIGHT`) is defined in the model and given to the view as `model.width` and `model.height` | The view imports nothing from the model; it draws whatever it is given. |
| Each folder is self-contained (every relative import stays in its own folder), and `model-controller-common.js` holds only `Cmd` | The versions can be read, diffed and copied independently. The `Cmd` file mirrors the C split, where the `command` enum is the MODEL-CONTROLLER message. The user picked the file name. |
| Three versions: singleton, factory, class | The comparison is the point of this repo. The advice in HOW_AND_WALKTHROUGH.md ("Which to use"): a singleton for things the world limits to one (the keyboard), and a factory for things you may want several of (models). A class does the same jobs as a factory; use it when there will be very many copies, since its methods are stored once, or when a library or browser feature expects one. |
| Closures and classes both exist side by side; the template's choice is still open (decision 2 in §4) | Closures (`factory/`) have no `this` traps and need no special privacy syntax. Classes (`class/`) share methods on the prototype and match C++ `new`. They cost three things: the `this` trap (a method handed over alone loses its object, so `class/main.js` wraps the listener); `#` fields with their *brand check* (before touching `#pending`, the browser verifies that `this` really is a `Controller`, and throws if not); and `handleEvent` as an alternative to wrapping. `HOW_AND_WALKTHROUGH.md` covers all three. |
| Key lookup uses `Object.hasOwn(KEYMAP, e.key)`, not `e.key in KEYMAP` | `in` also finds names every object inherits: `'toString' in KEYMAP` is `true`. `Object.hasOwn` checks only the table's own keys. All three controllers use it. |
| Vendored libraries, an import map, no npm | No toolchain to learn. `node`/`npm` are not project dependencies (`CLAUDE.md`). |

### 1.4 Enforcement machinery

- **`.checks/boundaries.py`** (stdlib Python, about 100 lines; run with `uv run --no-project python .checks/boundaries.py [root]`):
  - `ALLOWED_IMPORTS` maps path globs (`*/model.js`, ...) to the imports each file may have. Relative imports are resolved, and `{dir}` means "the importing file's own folder", so a file can only import from its own folder.
  - `RULES` is a list of `(regex, globs where allowed, message)` entries:
    - browser globals, `effect`, `.value` writes (including `+=` and `++`) and `.update`;
    - `viewUpdate`/`createView`/`View` used outside `view.js` and `main.js`;
    - file-level changing state (`let`/`var`, or a top-level `const` holding `[`, `{` or `new`), allowed only in `singleton/*` and `*/main.js`. `factory/` and `class/` keep their state per instance.
  - `REDRAW` plus a one-line check require `viewUpdate(...)` or `view.update(...)` in a `main.js` to sit inside `effect(...)`. This covers `class/` too.
  - `COPIES` requires `factory/model-controller-common.js` and `class/model-controller-common.js` to stay byte-identical to the singleton one.
  - `//` comments are stripped first, and an unknown `.js` file is itself a violation.
  - It is **a tripwire for honest mistakes, not a sandbox**: deliberately obfuscated code can get past it.
  - **`static` fields:** a `static` class field (for example `static count = 0;` inside a class body) or `static { … }` block belongs to the class itself, so every instance shares it. That makes it a singleton hidden inside the class, and the check flags it outside `singleton/*` and `*/main.js`. Static methods (`static create() { … }`) hold no state and stay allowed. This rule was added after a live probe showed `static presses = 0;` in `class/controller.js` passing unflagged.
- **Hooks in `.claude/settings.json`:**
  - `PostToolUse` (`Edit|Write|MultiEdit`) runs the check after every edit and gives the agent `file:line` feedback. It **cannot undo** the edit, and edits made with shell commands skip it.
  - `Stop` (`.checks/stop-hook.sh`) runs the check when the agent tries to end its turn, and on a violation sends it back to fix the code. After one failed round it lets the turn end but shows the user a warning, so a violation the agent cannot fix does not loop forever.
- **How it was verified:**
  - A 76-case test matrix ran against an **earlier** rule table (commit `5de3e33`, three versions including `mixed/`). It planted every rule in every folder and checked for the exact message, plus allowed cases and legitimate code. All 76 passed.
  - The matrix lived in a session scratch file and was **not committed**.
  - The rule table has changed twice since (`3e3c56e`, `d3af8f6`), and this session has no record of an equivalent matrix run on the current rules. The template should commit a checker test (see §2.4).

### 1.5 Gotchas already hit (save yourself the time)

- **Browser cache:** headless Chromium (and the user's browser) can serve an old `index.html` from cache after files move. Use a fresh `--user-data-dir` for tests, and tell the user to hard-reload with Ctrl+Shift+R (Mac: Cmd+Shift+R).
- **Ports and `pkill`:** the user usually has a server on port 8000, so test on 8001 with `--bind 127.0.0.1`. To stop it, use `pkill -f '[h]ttp.server 8001'`; the brackets stop `pkill` from killing its own shell.
- **Headless focus:** headless pages never count as focused, so the async clipboard API fails unless `Emulation.setFocusEmulationEnabled` is on.
- **Monospace sizing:** CSS `font: 1.5em monospace` with a bare `monospace` family scales from the browser's 13 px monospace default, giving 19.5 px rather than 24 px.
- **Signals ignore same-value writes:** writing the same value to a signal notifies nobody. Arrays and objects must be **replaced, not mutated** (`list.value = [...list.value, x]`, not `push`). Otherwise nothing redraws.
- **Several writes in one `update`:** wrap them in `batch(() => { … })`, or each write triggers its own redraw.
- **Class methods lose `this` when handed over alone.** `addEventListener('keydown', controller.keydown)` breaks with a class, because the browser calls the method without its object. Wrap it (`e => controller.keydown(e)`), as `class/main.js` does. Closure methods have no `this`, so they don't have this problem.
- **`in` finds inherited names.** Use `Object.hasOwn(table, key)` for lookups in plain tables.
- **Markdown lists:** a blank line between bullets makes the whole list "loose" (evenly spaced). To separate groups visibly, an indented `***` inside the last bullet of each group works on GitHub and in VS Code.
- **Indenting nested folds:** neither renderer indents nested `<details>`, and GitHub strips `style`. Wrap the nested folds in `<dl><dd>` (see `.claude/rules/markdown.md`).

## 2. The proposal

### 2.1 What carries over unchanged

| Piece | Why it is general |
|---|---|
| Architecture rules (roles, one-way imports, globals only in `main`, writes only through `update`, `effect` only in `main`) | None of it mentions dots or grids. |
| `.checks/boundaries.py` and both hooks | Only the rule table at the top is project-specific; the hooks do not change. |
| "Code principles" and "How to explain things" in `CLAUDE.md` | They are about this user, not this app. |
| Conventions and development environment | Commit/push only when asked; `main` only; LF endings; uv for Python; Debian 13 setup. |
| `.claude/rules/markdown.md` | Folding rules for any project's long Markdown documents. Only its `paths:` front matter is specific to this repo (`HOW_AND_WALKTHROUGH.md`, `docs/**/*.md`); point it at the template's `README.md`, or Claude Code never loads it there. |

### 2.2 What stays in dot-runner (not in the template)

- The three versions, their deliberate duplication and the `COPIES` rule. The template has one version.
- The walkthrough rule (HOW_AND_WALKTHROUGH.md "copies each source file in full"). It is great for learning but too much upkeep for a real app.
- Dot-app and C details: `KEYPAD`, the NMI tick, 16×8, `Cmd` as a bare enum.

### 2.3 Skeleton style (decision 2 in §4): factory recommended, class a close second

All three styles exist in this repo as working references. Summary:

- **Factory (recommended), like `factory/`.** Every part is created in `main.js` (`createModel()`, `createView(container)`, `createController()`), so a second model or view costs one line. No `this`, no special privacy syntax, and no file keeps state at file level.
- **Class, like `class/`.** It's closest to C++ `new`, and it has these pros (HOW_AND_WALKTHROUGH.md → "Pros and cons"):
  - methods are stored once on the prototype and shared, which matters at tens of thousands of copies, not at one;
  - a `#` field used on the wrong object throws, instead of failing silently;
  - some browser features are built around classes (a web component is a class that extends `HTMLElement`).

  The costs: two more concepts than the factory (`this` and `new`); every method handed over on its own needs a wrapper in `main.js`; and one more thing to keep out (state in `static` fields, which the check already flags, §1.4). For the portfolio app (a few model instances, data held as plain records), the practical difference from a factory is small.
- **Singleton, like `singleton/`.** One instance only. That's fine for a single-screen app, but it's the wrong default for a template.

The skeleton lives at the root, with no version folders. Shown in the factory style; the class variant of each file is in brackets:

```
index.html             import map, CSS, #app container, one module script
model-controller-common.js   message types shared by model and controller (name kept from dot-runner)
model.js               export function createModel()   [class Model]  — signals inside, read-only computeds out, update(msg)
view.js                export function createView(container) → { update(m) }   [class View]  — lit-html only here
controller.js          export function createController()   [class Controller]  — input → messages
main.js                creates the parts, wires inputs, timers, effect(() => view.update(model))
                       [class: new …(); wrap methods handed to the browser, e.g. e => controller.keydown(e)]
vendor/                lit-html 3.3.3, @preact/signals-core 1.14.5 (copy from this repo)
.checks/boundaries.py  rule table rewritten for root-level files; no COPIES, no {dir} needed
.checks/stop-hook.sh   unchanged
.claude/settings.json  hooks (PostToolUse, Stop, SessionStart) + permission allowlist, as here
.claude/rules/mvc.md   the general architecture rules, with front matter  paths: ["**/*.js"]
.claude/rules/markdown.md  copied; only its paths: changed, to README.md
.claude/CLAUDE.md      short: what this project is, its layout, its conventions; points to rules/mvc.md
README.md              how to run, the architecture in brief, how the checks work
```

Claude Code loads `.claude/rules/*.md` files automatically when working on paths matching their `paths:` front matter, just as `markdown.md` is loaded for `HOW_AND_WALKTHROUGH.md` here.

### 2.4 What the template must add (the dot app never needed it)

1. **Messages that carry data:** `model.update({ type: 'trade', trade })` instead of a bare enum value. Show one example in the skeleton.
2. **`batch()`** in `update` whenever it writes more than one signal. Document why: one redraw instead of several.
3. **An input/output rule:** `fetch`, `localStorage`, timers and the URL live in `main.js` or in small adapter files that `main.js` owns, never in the model. This is half-enforced already, since those globals are allowed only in `main.js`. Decide whether adapter files get their own entry in the rule table.
4. **Tests for the pure parts:** model updates and derived calculations. `CLAUDE.md` currently says `node`/`npm` are not used, so either a browser test page (`test.html` plus `*.test.js`, run in headless Chromium) or an explicit exception for Node in tests only. Ask the user (§4).
5. **A committed test for the checker itself** (a replacement for the scratch matrix in §1.4), so changes to `boundaries.py` can't silently weaken it.
6. **The pitfalls from §1.5** written into `rules/mvc.md`: replace arrays rather than mutating them, `batch`, money stored as integer cents, `Object.hasOwn` for table lookups, and, for classes, wrapping methods handed to the browser.
7. **Keep the `static`-field rule** (§1.4) in the template's check. It matters only if the style is class, but it costs nothing otherwise. A `static` field is class-level shared state, so it belongs with the "no file-level state" rule.

### 2.5 Packaging

1. Create a new repository (name to be agreed, for example `signals-lit-mvc-template`) holding the skeleton above. Mark it as a template on GitHub (`gh repo edit --template`, or the repository's Settings), so new projects start with "Use this template".
2. Optionally, have this repo also take `rules/mvc.md` and slim its `CLAUDE.md`, so both repos share one rule text. dot-runner's rules have the three-version specifics on top, so check with the user before changing this repo.

## 3. First user of the template: the portfolio app

The user plans a portfolio object: each portfolio has many holdings, and each holding has many buy and sell transactions at different prices. They asked whether to use a JavaScript `class`. The guidance they already have:

- **Records, not objects, for the data.** Transactions are **plain data records**, not objects with behavior:
  `{ symbol: 'AAPL', date: '2026-03-02', side: 'buy', qty: 10, priceCents: 18932 }`.
  Holdings, average cost and profit or loss are **computed from** the records by *pure functions* (functions whose result depends only on their inputs and which change nothing), for example `holdingsFrom(transactions)`. This is arrays of structs plus functions in C terms. Plain records also round-trip through `JSON.stringify`/`JSON.parse` for saving, which class instances don't (they lose their methods). This holds whichever style the *model* uses (decision 2).
- **Model sketch** (factory style; one per portfolio. A class version would hold the same signals in `#` fields, with `update` as a method):
  ```js
  export function createPortfolio() {
    const transactions = signal([]);   // records like the one above
    const prices = signal({});         // latest price per symbol in cents, e.g. { AAPL: 18932 }
    const holdings = computed(() => holdingsFrom(transactions.value));     // pure function
    const value = computed(() => totalValue(holdings.value, prices.value));
    return {
      transactions: computed(() => transactions.value),   // read-only to outsiders
      holdings, value,
      update(msg) {
        switch (msg.type) {
          case 'trade': transactions.value = [...transactions.value, msg.trade]; break;  // new array → notifies
          case 'price': prices.value = { ...prices.value, [msg.symbol]: msg.priceCents }; break;
        }
      },
    };
  }
  ```
- **Money as integers:** in JavaScript, `0.10 + 0.20` is `0.30000000000000004`, but `10 + 20` cents is exactly `30`. Integers are exact up to 2⁵³ (about 9 × 10¹⁵ cents). This is fixed-point arithmetic, like Q-format in DSP: pick a scale per field (cents, or 1/10,000 of a dollar for finer prices). Division and averages need explicit rounding.
- **The cost-basis rule must be decided early:** FIFO (sell the oldest shares first) or average cost. It changes realized gains and depends on the user's tax rules, so it is a requirement to ask about, not a coding detail.
- **Where the class trade-offs are written up:**
  - HOW_AND_WALKTHROUGH.md → "Singleton vs factory vs class": the three-column table, "Pros and cons" (with a Class block), "Factory vs class" and "Which to use";
  - the `class/` walkthrough (the `this` trap, the brand check, and the `handleEvent` footnote);
  - the Terms entries for `class` and `#`.

  In HOW_AND_WALKTHROUGH.md's words, a class pays off when there will be very many copies (tens of thousands, not one), since its methods are stored once, or when a library or browser feature expects one, such as a web component extending `HTMLElement`.

## 4. Open decisions (ask the user first)

1. **Where the template lives:** a new GitHub repository, and what name? Creating and pushing a repository is outward-facing, so get explicit approval.
2. **Skeleton style:** factory, like `factory/` (recommended, §2.3); class, like `class/`; or singleton, like `singleton/`? (Mixed, a singleton controller plus a factory model, was tried in this repo and removed in `3e3c56e`.)
3. **Tests:** a browser test page run in headless Chromium (keeps the "no Node" rule), or allow Node for tests only?
4. **README walkthrough** in the template: none (recommended), or a short one?
5. **Should dot-runner adopt `.claude/rules/mvc.md` too**, or keep its own full `CLAUDE.md`?
6. **Portfolio app:** start it from the template straight away, and settle the cost-basis rule (§3) before writing `holdingsFrom`?

## 5. Execution plan for a fresh session

1. Read the files listed at the top, run `git status` (other sessions may be active), then ask the open decisions (§4) in one round.
2. Create the template directory (outside this repo, for example `~/signals-lit-mvc-template`) with the §2.3 layout. Copy `vendor/` unchanged and `.claude/rules/markdown.md` with its `paths:` changed to `README.md` (§2.1), and write the skeleton files in the chosen style, using this repo's matching folder (`factory/`, `class/` or `singleton/`) as the reference.
3. Rewrite `.checks/boundaries.py` for root-level files:
   - `ALLOWED_IMPORTS` keyed by plain file names (`model.js`, `view.js`, ...);
   - remove `COPIES` and the `{dir}` folder rules;
   - keep `RULES` (including the `static`-field rule, §2.4 item 7) and `REDRAW` as they are, adjusting the allowed globs to root-level names (for example `main.js` instead of `*/main.js`).

   Then add the committed checker test (§2.4 item 5).
4. Copy `.claude/settings.json` (hooks and allowlist) and `.checks/stop-hook.sh`. Write `.claude/rules/mvc.md` (§2.1 rules plus the §2.4 additions) and a short `CLAUDE.md`.
5. Write `README.md` for the template, following `.claude/rules/markdown.md`.
6. Verify (§6). Commit or push only when the user asks; always on `main`.

## 6. Acceptance checks

- `uv run --no-project python .checks/boundaries.py` prints `boundaries ok (N files)`, and the committed checker test passes, covering at least: each rule flagged in each file role, allowed cases, and legitimate code such as `===` comparisons and frozen tables (plus a `static` field being flagged, if the style is class).
- **The hooks are proven live:**
  - a deliberately violating edit comes back with the check's message from the `PostToolUse` hook;
  - a violation left in place makes the `Stop` hook refuse to end the turn;
  - both probes are removed afterwards.
- **The app runs** in headless Chromium on port 8001: it renders, reacts to key events, and shows no console errors.
- **The README** follows the markdown rules: folds have the right shape and every in-page link resolves.
