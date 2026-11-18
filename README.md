[HOW_AND_WALKTHROUGH.md](HOW_AND_WALKTHROUGH.md) · [STUDY_PLAN_1.md](STUDY_PLAN_1.md) · [STUDY_PLAN_2.md](STUDY_PLAN_2.md) · [STUDY_PLAN_3.md](STUDY_PLAN_3.md)

# Dot runner

A small project for learning [Preact Signals](https://github.com/preactjs/signals) and [lit-html](https://lit.dev/docs/libraries/standalone-templates/). A red dot moves on a 16×8 grid in the last arrow direction you pressed, and a readout shows its position as one hex byte. The page runs this app three times, built three ways so you can compare them: a **singleton** version, where each part exists once and keeps its state at file level; a **factory** version, where `main.js` creates the parts by calling functions; and a **class** version, where `main.js` creates them with `new` from JavaScript classes. Each version lives in its own folder and shares no code with the others. There is no npm and no build step: the browser loads both libraries as ES modules straight from `vendor/`.

## Run

```bash
uv run --no-project python -m http.server 8000
```

Open <http://localhost:8000>. Arrow keys move all three dots, Space stops them. The panel at the bottom is [Eruda](https://github.com/liriliri/eruda), an in-page console that shows `console.log` output and errors; its floating button hides it. Ctrl+C stops the server.

- **Why a server:** Chrome refuses to load ES modules (`<script type="module">`) from a `file://` page, so opening `index.html` directly shows the headings but no grids.
- **Why `--no-project`:** uv skips looking for a `pyproject.toml` and creates no venv. It just runs Python's built-in file server.
- **Network exposure:** `http.server` listens on every network interface, so other machines on your network can browse this folder, `.git/` included. Add `--bind 127.0.0.1` to keep it to this machine.

## Documents

- [HOW_AND_WALKTHROUGH.md](HOW_AND_WALKTHROUGH.md) — how the app works, every source file explained part by part, the three patterns compared, and the Claude Code and Debian setup.
- [STUDY_PLAN_1.md](STUDY_PLAN_1.md) — start here: one small form app, from plain DOM code to Preact Signals (`signal`, `effect`, `computed`, `batch`), then one section per component, then lit-html.
- [STUDY_PLAN_2.md](STUDY_PLAN_2.md) — a name list (append, delete, up and down, edit, no duplicates, edit in a dialog, animated rows, swipe to delete, hold to reorder), where lit-html draws rows that appear, disappear and move.
- [STUDY_PLAN_3.md](STUDY_PLAN_3.md) — a read-then-build path: a hello world, a step counter in each version, then an app of your own.
- [TEMPLATE_PROPOSAL.md](TEMPLATE_PROPOSAL.md) — a proposal (not started) to turn this setup into a reusable MVC template repo.
