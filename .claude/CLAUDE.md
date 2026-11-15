# CLAUDE.md

Guidance for Claude Code in this repository.

## What this is

A small browser app for **learning Preact Signals and lit-html**: a dot moving on a 16×8 grid, built three times on one page (singleton, factory, and mixed: a singleton controller with a factory model) so the patterns can be compared. Plain ES modules with no npm and no build step; the two libraries are vendored in `vendor/` and loaded through an import map in `index.html`.

## Code principles

Code is simple, minimal, easy to understand, and DRY. These come before cleverness, speculative flexibility, and personal style.

- **Simple:** use the most straightforward approach that works. No clever tricks, premature abstraction, or premature optimization.
- **Minimal:** write only what the task needs. No speculative features, unused options, or "just in case" code. Fewer lines, files, and dependencies win. Delete dead code.
- **Easy to understand:** a newcomer should follow it on first read. Clear names, small functions, shallow nesting, obvious control flow.
- **DRY:** one source of truth for each piece of logic, data, and config. Search for existing code to reuse before writing new code; never copy-paste logic. Extract it once instead.
- **When in doubt, choose the simpler option.** Before finishing, re-read your diff and cut anything that isn't needed.

## Architecture rules

The app is split like the bare-metal C original in `C/`: model, view, controller, and a main that wires them. It exists in three versions, each in its own folder with the same file names: `singleton/` (each part exists once, its state in file-level variables), `factory/` (`main.js` creates the parts with `createModel()` and `createController()`), and `mixed/` (a singleton controller with a factory model; its `controller.js` is a copy of the singleton one and its `model.js` a copy of the factory one). All share `model-controller-common.js` (`Cmd`, the model–controller message, like the C `command` enum) and `view.js`. The grid size (`WIDTH`, `HEIGHT`) belongs to the model: each `model.js` defines it, repeated on purpose, and hands it to the view as `model.width` and `model.height`. The rules below apply per file name in all three folders. They are checked by `.checks/boundaries.py`, which a `PostToolUse` hook runs after every edit and a `Stop` hook runs before a turn may end (shell edits skip the first, not the second); run it by hand with `uv run --no-project python .checks/boundaries.py`.

- **Roles:** `model.js` holds the state and the only rule that changes it, `update(cmd)`. `view.js` draws the state once per call (`viewUpdate`). `controller.js` turns key presses into commands. `main.js` connects the parts to the browser and decides when things run: the key listener, the tick, and the redraw `effect`.
- **Imports go one way:** `model-controller-common.js` imports nothing and holds only `Cmd`; `view.js` → `lit-html` only; `model.js` → `@preact/signals-core`, `model-controller-common.js`; `controller.js` → `model-controller-common.js`; `main.js` → `@preact/signals-core`, `view.js`, and the `model.js` and `controller.js` of its own folder. Nothing imports a `main.js`, and the two versions never import each other.
- **Browser globals** (`window`, `document`, `navigator`, `location`, `history`, `localStorage`, `sessionStorage`, `fetch`, `alert`, `setTimeout`, `setInterval`, `requestAnimationFrame`, `queueMicrotask`, `addEventListener`, `globalThis`, `self`) appear only in `main.js`. Other parts get what they need passed in: the key event, the container element.
- **State changes only through `model.update(cmd)`:** only `model.js` writes `.value` (with `=`, `+=` and the like, or `++`/`--`); only `main.js` uses `.update` and creates `effect`s; `viewUpdate` is called only inside an `effect(...)` in `main.js`, on one line, so the screen never goes stale.
- **File-level state:** allowed only in `singleton/` and `mixed/controller.js` (that is the pattern). Factory parts (`factory/` and `mixed/model.js`) keep no changing state at file level (no top-level `let` or `var`, and no top-level `const` holding an array, object or `new` instance; constant tables are wrapped in `Object.freeze`) and `main.js` creates the instances.
- **Deliberate duplication:** the update rule and the key table appear once per version on purpose, so the patterns can be read side by side: `mixed/controller.js` equals `singleton/controller.js`, and `mixed/model.js` equals `factory/model.js`. This is a stated exception to DRY; keep all copies in step. The two `mixed/` copies must stay byte-identical to their originals, and `.checks/boundaries.py` fails if they differ.
- **New `.js` file:** add it to `ALLOWED_IMPORTS` in `.checks/boundaries.py` (and to these rules) before using it; the check rejects files it doesn't know.

## How to explain things

These rules apply to explanations to the user and to code comments, not to commit messages.

For code comments:
- Explain why and the mechanism; don't restate what the code plainly does.
- Define a term once, at its first use in the file.
- Add a worked numeric example only for non-obvious math (scaling, units, bit layouts).
- Keep comments as short as the point allows; "Simple", "Minimal", "Easy to understand", and "DRY" still apply.

Audience: someone with a BS in EE who remembers the fundamentals (circuits, signals, calculus, basic probability and statistics) but not every formula or every field's jargon. Write for a sharp engineer outside the specialty.

Goal: as simple as possible, without saying anything false.

1. Start with the plain-language answer in 1-2 sentences, then the reasoning.
2. Explain the mechanism (what causes what) in words before any math.
3. Define each technical term the first time it appears, in a short phrase. Introduce as few new terms as possible.
4. Use an equation only when it makes the point clearer than words. If you use one, define every symbol and show one worked example with real numbers.
5. Prefer a concrete numeric example over abstract notation.
6. Use an analogy (EE analogies are welcome) only if it maps accurately, and say where it breaks down.
7. When you simplify, say what you left out and when it would matter.
8. No handwaving: back each claim with a reason, a number, or a source. If the answer depends on something, say what. If unsure, say so.
9. Before sending, check: could I follow this on the first read without looking anything up? If not, rewrite it.

## Layout

- `index.html` — page shell: import map, grid CSS, the `#app-singleton`, `#app-factory` and `#app-mixed` containers, one module script per version.
- `model-controller-common.js` — `Cmd`, shared by model and controller; `view.js` — lit-html template and `viewUpdate(m, container)`, shared by all versions, grid size read from the model.
- `singleton/` — `model.js` (state as file-level signals, exports `model`), `controller.js` (key table and file-level latch, exports `controller`), `main.js` (wiring into `#app-singleton`).
- `factory/` — `model.js` (`createModel()`), `controller.js` (`createController()`), `main.js` (creates one of each, wiring into `#app-factory`).
- `mixed/` — `model.js` (copy of the factory one), `controller.js` (copy of the singleton one), `main.js` (creates a model, imports the controller, wiring into `#app-mixed`).
- `.checks/boundaries.py` — checks the Architecture rules above (stdlib Python); run by the `PostToolUse` hook. `.checks/stop-hook.sh` — the `Stop` hook: runs the same check and refuses to let a turn end while it fails.
- `vendor/` — minified lit-html 3.3.3 and @preact/signals-core 1.14.5, used as-is.
- `.claude/settings.json` — committed settings (`model: opus`, `effortLevel: xhigh`), permission allowlist, a `SessionStart` hook that prints `.claude/PROGRESS.md` into context, a `PostToolUse` hook that runs `.checks/boundaries.py` after every edit (feedback; it cannot undo the edit), and a `Stop` hook (`.checks/stop-hook.sh`) that keeps Claude working until that check passes. Personal overrides go in the gitignored `.claude/settings.local.json`, never here.
- `.claude/skills/wrapup/SKILL.md` — `/wrapup`: rewrites `.claude/PROGRESS.md` as a handoff for the work since the previous one (base: the last commit that touched it), then commits.
- `.claude/rules/markdown.md` — how to write README.md and docs/: which `##` sections fold, and how. Claude Code loads it by itself when working on those files.
- `.claude/PROGRESS.md` — latest session handoff only, maintained by `/wrapup`; earlier ones: `git log -p --follow -- .claude/PROGRESS.md`.
- `.gitignore`, `.gitattributes` — ignore rules; LF line endings and binary file types.
- `README.md` — human-facing overview. Its Code walkthrough copies each source file in full, so update it in the same change as the file. The exceptions are `mixed/model.js` and `mixed/controller.js`: identical copies whose sections only point to `factory/model.js` and `singleton/controller.js`.

## Conventions

- **NEVER `git commit` or `git push` on your own.** Do either only when the user's current message asks for it. Exception: `/wrapup` always commits, never pushes.
- **Never branch: always commit to `main`.** No feature branches or PRs; commit and push straight to `main`.
- Line endings follow `.gitattributes`: LF for every text file.
- New languages or toolchains extend `.gitignore` and `.gitattributes` — no parallel ignore files. Keep new entries consistent with existing ones.
- **Read first, edit once, check once.** Before changing anything, list every file the change touches and read them in one pass. Then make all the edits, then run whatever verifies them once. Don't loop read, edit, rerun per file. If a check fails, fix it and rerun that check.
- **Run:** `uv run --no-project python -m http.server 8000`, then open http://localhost:8000. No build step and no tests yet.

## Development environment

- **Debian 13 (trixie)** with `docker` installed. Base tooling via `apt`: `git`, `gh`, `python3`, `python3-dev`, `build-essential`, `curl`, `jq`, `wget`, `time`; plus `uv` from its standalone installer into `~/.local/bin` (commands in the [README](../README.md#development-setup-debian-13)).
- **Install missing tools yourself:** `sudo apt install -y <package>` (`sudo apt update` first if not found). Use `apt` for system tools only. If the project will keep relying on a new tool, add it to the README's install command.
- **Python: use `uv` only.** Never run `pip`, `pip3`, `python3 -m pip`, `python3 -m venv`, or `pipx`; `uv pip …` is uv's own subcommand and is fine. uv handles both venvs and installs, and Debian 13 blocks system-wide `pip install` anyway (PEP 668). One venv per project:

  ```bash
  uv sync                                          # pyproject.toml project; add packages with: uv add <pkg>
  uv venv && uv pip install -r requirements.txt    # requirements.txt-only project
  uv run <cmd>                                     # run a command in the project venv
  ```
- `node`/`npm` and .NET are not used; serve the page with the Run command above. Multi-arch Docker builds need a one-time QEMU + buildx setup (see README).
