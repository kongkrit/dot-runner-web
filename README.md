# Dot runner

A small project for learning [Preact Signals](https://github.com/preactjs/signals) and [lit-html](https://lit.dev/docs/libraries/standalone-templates/). A red dot moves on a 16×8 grid in the last arrow direction you pressed, and a readout shows its position as one hex byte. There is no npm and no build step: the browser loads both libraries as ES modules straight from `vendor/`.

## Run

<details>
<summary>Start command, why a server, network exposure</summary>
<br>

```bash
uv run --no-project python -m http.server 8000
```

Open <http://localhost:8000>. Arrow keys move the dot, Space stops it. Ctrl+C stops the server.

- **Why a server:** Chrome refuses to load ES modules (`<script type="module">`) from a `file://` page, so opening `index.html` directly gives an empty page.
- **Why `--no-project`:** uv skips looking for a `pyproject.toml` and creates no venv. It just runs Python's built-in file server.
- **Network exposure:** `http.server` listens on every network interface, so other machines on your network can browse this folder, `.git/` included. Add `--bind 127.0.0.1` to keep it to this machine.

</details>

## How it works

<details>
<summary>Files, terms, one tick step by step</summary>

### Files

The code is split the way an embedded C program often is: a model (state plus the rule that changes it), a view (draws the state), and a main loop that feeds input to the model on a timer. Comments in the code name the C counterpart of each piece (`model_t`, `model_update()`, `view_update()`).

| File | Role |
|------|------|
| `index.html` | Page shell: the import map, the grid's CSS, and the empty `#app` container. An import map is a JSON block that tells the browser which file a bare module name like `lit-html` means, the job a bundler does in an npm project. |
| `model.js` | State and update rule: `row` and `col` signals, a `hex` computed, `update(cmd)`. No DOM. |
| `view.js` | `view(m)`: a lit-html template for the 16×8 table and the hex readout. Reads signals, writes none. |
| `main.js` | Wiring: keyboard → `pending`, a 150 ms timer → `m.update()`, `effect` → `render`. |
| `vendor/` | lit-html 3.3.3 (`lit-html.js`) and @preact/signals-core 1.14.5 (`dist/signals-core.mjs`), the published files used as-is. |

### Terms

- **signal** (Preact): a box holding one value. Code that reads `.value` inside a `computed` or `effect` is subscribed to it; writing a *different* value to `.value` notifies the subscribers. Writing the same value notifies nobody.
- **computed** (Preact): a read-only signal whose value is a function of other signals. `model.js` hands out `computed` wrappers around `row` and `col`, so code outside the model can read them but not write them.
- **effect** (Preact): a function that runs immediately, then again whenever a signal it read on its last run changes.
- **html** (lit-html): a tagged template literal. It returns a description of the DOM and does not touch the page.
- **render** (lit-html): writes that description into a container. On later calls it reuses the DOM it built and goes slot by slot (each `${…}`, walking into nested templates and arrays), updating only the slots whose value changed.

### One tick, step by step

1. **Key press.** The browser calls `main.js`'s `keydown` handler, which stores the command in `pending`. A C loop would poll `controller_read()`; here the browser pushes events, so the key waits in `pending` until the next tick. If two keys arrive within one tick, the last one wins.
2. **Tick.** Every 150 ms (about 6.7 steps per second) `setInterval` calls `m.update(pending)` and clears `pending`. `update` remembers the last real command in a plain variable `cmd`, so the dot keeps moving with no key held. `cmd` is not a signal because nothing on screen shows it. Edges wrap: from column 15, RIGHT goes to column 0.
3. **Write.** `update` writes a new value to `col` or `row`. After Space, it writes nothing, so nothing re-renders.
4. **Redraw.** On its last run the effect in `main.js` read `row`, `col` and `hex` (through `view`), so it re-runs `render(view(m), #app)`. `view(m)` rebuilds the whole description: 128 cells. `render` then changes only what differs, which for one step is the `class` of two `<td>` cells and the `<output>` text. The saving is in DOM work, not in JavaScript work.

The readout packs the position into one byte: `hex = (row << 4) | col`. Column 0–15 fills the low 4 bits and row 0–7 the next 3, so the range is `00`–`7F`. Example: the start position, row 4 and column 7, gives `(4 << 4) | 7 = 0x40 | 0x07 = 0x47`, shown as `47`.

</details>

## Claude Code setup

<details>
<summary>Settings, the /wrapup skill, project instructions, handoff file</summary>
<br>

| File | Purpose |
|------|---------|
| `.claude/CLAUDE.md` | Project instructions Claude Code loads every session: code principles, explanation style, conventions, environment. |
| `.claude/settings.json` | Claude Code settings (`model: opus`, `effortLevel: xhigh`), a permission allowlist, and a `SessionStart` hook that prints `.claude/PROGRESS.md` into context. |
| `.claude/skills/wrapup/SKILL.md` | `/wrapup` rewrites `.claude/PROGRESS.md` as a handoff for the work since the previous one, then commits. It runs only when you type it. |
| `.claude/rules/markdown.md` | How to write README.md and docs/: which `##` sections fold. Claude Code loads it when working on those files. |
| `.claude/PROGRESS.md` | Latest session handoff, maintained by `/wrapup`; earlier ones: `git log -p --follow -- .claude/PROGRESS.md`. |
| `.gitignore` | OS cruft, Python/uv venv, editor files. |
| `.gitattributes` | LF line endings; binary file types; no line diffs for the minified `vendor/` files. |

Personal overrides go in `.claude/settings.local.json`, which is gitignored ([settings docs](https://code.claude.com/docs/en/settings)).

</details>

## Development setup (Debian 13)

<details>
<summary>Base packages, uv, more tools, Python, Docker multi-arch</summary>
<br>

`docker` is assumed installed. Base toolchain:

```bash
sudo apt install -y git gh python3 python3-dev build-essential curl jq wget
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

**Not used.** `node`/`npm` (Python's `http.server` serves the page; see [Run](#run)) and the .NET SDK.

</details>
