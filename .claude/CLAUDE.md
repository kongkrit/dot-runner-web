# CLAUDE.md

Guidance for Claude Code in this repository.

## What this is

A repo for **learning MVC (model, view, controller) front-end programming with Preact Signals and lit-html**. Its app is a dot moving on a 16×8 grid, built three times on one page (singleton, factory and class), each in its own self-contained folder, so the patterns can be compared. Plain ES modules with no npm and no build step; the two libraries are vendored in `vendor/` and loaded through an import map in `index.html`.

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

## Learning style

The user finds the hard part of learning any new tech to be getting a "hello world" working and learning the syntax and patterns to build one small "house". Scaling from there to a "city" is easy for them. So when teaching or planning study (as in `STUDY_PLAN.md`):

- Give each step two parts: first the sections to read and absorb, in order; then a small runnable build, hint first and solution folded.
- Spend the detail on getting the first small thing working. Don't spend effort on scaling up; the user does that on their own.
- Mention a C parallel only in passing, where it helps. Don't map everything to `C/`.

## Code principles

Code is simple, minimal, easy to understand, and DRY. These come before cleverness, speculative flexibility, and personal style.

- **Simple:** use the most straightforward approach that works. No clever tricks, premature abstraction, or premature optimization.
- **Minimal:** write only what the task needs. No speculative features, unused options, or "just in case" code. Fewer lines, files, and dependencies win. Delete dead code.
- **Easy to understand:** a newcomer should follow it on first read. Clear names, small functions, shallow nesting, obvious control flow.
- **DRY:** one source of truth for each piece of logic, data, and config. Search for existing code to reuse before writing new code; never copy-paste logic. Extract it once instead.
- **When in doubt, choose the simpler option.** Before finishing, re-read your diff and cut anything that isn't needed.

## Architecture rules

The app is split like the C original in `C/`: model, view, controller, and a main that wires them. It exists three times: `singleton/` (each part exists once, its state at file level), `factory/` (`main.js` calls `createModel()`, `createView(container)` and `createController()`) and `class/` (`main.js` uses `new Model()`, `new View(container)` and `new Controller()`; state in `#` private fields). Each folder holds the same five files and shares nothing but `vendor/`: `model-controller-common.js` (only `Cmd`, the model–controller message, like the C `command` enum), `model.js`, `view.js`, `controller.js`, `main.js`. The rules apply per file name in every folder. `.checks/boundaries.py` checks them after every edit (`PostToolUse` hook; shell edits skip it) and before a turn ends (`Stop` hook); run it by hand with `uv run --no-project python .checks/boundaries.py`.

- **Roles:** `model.js` holds the state, the only rule that changes it (`update(cmd)`), and the grid size (`WIDTH`, `HEIGHT`), which the view reads as `model.width` and `model.height`. `view.js` draws the state once per call. `controller.js` turns key presses into commands. `main.js` connects the parts to the browser and decides when things run: the key listener, the tick, the redraw `effect`.
- **Imports go one way:** `model-controller-common.js` → nothing; `view.js` → `lit-html`; `model.js` → `@preact/signals-core`, `model-controller-common.js`; `controller.js` → `model-controller-common.js`; `main.js` → `@preact/signals-core`, `view.js`, `model.js`, `controller.js`. Relative imports stay in their own folder, and nothing imports a `main.js`.
- **Browser globals** (`window`, `document`, `fetch`, `localStorage`, timers such as `setInterval`, `addEventListener`, …; the full list is in `.checks/boundaries.py`) appear only in `main.js`. Other parts get what they need passed in: the key event, the container element.
- **State changes only through `model.update(cmd)`:** only `model.js` writes `.value` (`=`, `+=`, `++` and the like); only `main.js` calls `.update` and creates `effect`s; the redraw (`viewUpdate(...)` or `view.update(...)`) runs only inside an `effect(...)` on the same line, so the screen never goes stale.
- **File-level state only in `singleton/`:** in `factory/` and `class/`, no top-level `let` or `var`, no top-level `const` holding an array, object or `new` instance (constant tables use `Object.freeze`), and no `static` class fields or blocks (static methods are fine). `main.js` creates the instances.
- **Deliberate duplication** (a stated exception to DRY): the grid size, update rule, key table and view template appear once per version so the patterns read side by side; keep them in step. `factory/` and `class/` hold byte-identical copies of `singleton/model-controller-common.js`, and the check fails if they differ.
- **New `.js` file:** add it to `ALLOWED_IMPORTS` in `.checks/boundaries.py`, and to these rules, before using it; the check rejects unknown files.

## Layout

- `index.html` — page shell: import map, grid CSS, one container and one module script per version.
- `singleton/`, `factory/`, `class/` — the three versions, five files each (see Architecture rules).
- `vendor/` — minified lit-html 3.3.3 and @preact/signals-core 1.14.5, used as-is.
- `.checks/` — `boundaries.py` checks the Architecture rules; `stop-hook.sh` runs it as the `Stop` hook.
- `.claude/settings.json` — committed settings, permission allowlist and hooks (`SessionStart` prints `.claude/PROGRESS.md`; `PostToolUse` and `Stop` run the check). Personal overrides go in the gitignored `.claude/settings.local.json`, never here.
- `.claude/skills/wrapup/SKILL.md` — `/wrapup`: rewrites `.claude/PROGRESS.md`, the latest session handoff (older ones are in its git history), then commits.
- `.claude/rules/markdown.md` — folding rules for HOW_AND_WALKTHROUGH.md and docs/, loaded automatically for those files.
- `.gitignore`, `.gitattributes` — ignore rules; LF line endings.
- `README.md` — front page: what this is, how to run it, links to the other docs; short and unfolded.
- `HOW_AND_WALKTHROUGH.md` — how it works, the code walkthrough, the three patterns compared, the Claude Code and Debian setup. The walkthrough copies each source file in full, so update it in the same change as the file; the two `model-controller-common.js` copies only point to the singleton one.
- `STUDY_PLAN.md` — the learner's read-then-build path. It quotes the source and links HOW_AND_WALKTHROUGH.md headings, so update it in the same change when either moves.
- `TEMPLATE_PROPOSAL.md` — proposal (not started) to extract this setup into a reusable MVC template repo; read it before working on that.

## Conventions

- **NEVER `git commit` or `git push` on your own.** Do either only when the user's current message asks for it. Exception: `/wrapup` always commits, never pushes.
- **Never branch: always commit to `main`.** No feature branches or PRs; commit and push straight to `main`.
- Line endings follow `.gitattributes`: LF for every text file.
- New languages or toolchains extend `.gitignore` and `.gitattributes` — no parallel ignore files. Keep new entries consistent with existing ones.
- **Read first, edit once, check once.** Before changing anything, list every file the change touches and read them in one pass. Then make all the edits, then run whatever verifies them once. Don't loop read, edit, rerun per file. If a check fails, fix it and rerun that check.
- **Run:** `uv run --no-project python -m http.server 8000`, then open http://localhost:8000. No build step and no tests yet.

## Development environment

- **Debian 13 (trixie)** with `docker` installed. Base tooling via `apt`: `git`, `gh`, `python3`, `python3-dev`, `build-essential`, `curl`, `jq`, `wget`, `time`; plus `uv` from its standalone installer into `~/.local/bin` (commands in [HOW_AND_WALKTHROUGH.md](../HOW_AND_WALKTHROUGH.md#development-setup-debian-13)).
- **Install missing tools yourself:** `sudo apt install -y <package>` (`sudo apt update` first if not found). Use `apt` for system tools only. If the project will keep relying on a new tool, add it to the install command in HOW_AND_WALKTHROUGH.md.
- **Python: use `uv` only.** Never run `pip`, `pip3`, `python3 -m pip`, `python3 -m venv`, or `pipx`; `uv pip …` is uv's own subcommand and is fine. uv handles both venvs and installs, and Debian 13 blocks system-wide `pip install` anyway (PEP 668). One venv per project:

  ```bash
  uv sync                                          # pyproject.toml project; add packages with: uv add <pkg>
  uv venv && uv pip install -r requirements.txt    # requirements.txt-only project
  uv run <cmd>                                     # run a command in the project venv
  ```
- `node`/`npm` and .NET are not used; serve the page with the Run command above. Multi-arch Docker builds need a one-time QEMU + buildx setup (see HOW_AND_WALKTHROUGH.md).
