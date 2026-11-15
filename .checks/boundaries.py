"""Check the MVC boundaries described in .claude/CLAUDE.md ("Architecture rules").

Run: uv run --no-project python .checks/boundaries.py
Prints "boundaries ok (N files)" and exits 0, or prints each violation as
file:line: rule: code on stderr and exits 1. A Claude Code hook in
.claude/settings.json runs it after every edit.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent

# What each root-level .js file may import. A .js file missing here is itself a violation.
ALLOWED_IMPORTS = {
    "model.js": {"@preact/signals-core"},
    "view.js": {"lit-html", "./model.js"},
    "controller.js": {"./model.js"},
    "main.js": {"@preact/signals-core", "./model.js", "./view.js", "./controller.js"},
}

# (pattern, files where it may appear, the rule it protects)
RULES = [
    (r"\b(window|document|navigator|localStorage|fetch|setTimeout|setInterval)\b",
     {"main.js"}, "browser globals only in main.js"),
    (r"\beffect\s*\(", {"main.js"}, "effects are created only in main.js"),
    (r"\.value\s*=(?!=)", {"model.js"}, "only model.js writes signal values"),
    (r"\.update\s*\(", {"main.js"}, "only main.js calls m.update()"),
    (r"^(let|var)\b", {"main.js"}, "no file-level changing state outside main.js"),
    (r"\bviewUpdate\s*\(", {"view.js", "main.js"}, "only main.js calls viewUpdate"),
]

# import ... from 'x', export ... from 'x', import 'x', import('x')
IMPORTS = re.compile(r"""\b(?:import|export)\b[^'";]*?\bfrom\s*['"]([^'"]+)['"]"""
                     r"""|\bimport\s*\(?\s*['"]([^'"]+)['"]""")


def check(path):
    name = path.name
    allowed = ALLOWED_IMPORTS.get(name)
    if allowed is None:
        yield f"{name}:1: not in the rules; add it to ALLOWED_IMPORTS in .checks/boundaries.py"
        return
    # Drop // comments (but not the // in ://) so a comment can't trip a rule.
    lines = [re.sub(r"(?<!:)//.*", "", line) for line in path.read_text().splitlines()]
    code = "\n".join(lines)
    for m in IMPORTS.finditer(code):
        source = m.group(1) or m.group(2)
        if source not in allowed:
            n = code.count("\n", 0, m.start()) + 1
            yield f"{name}:{n}: may not import {source}: {lines[n - 1].strip()}"
    for n, line in enumerate(lines, 1):
        for pattern, files, rule in RULES:
            if name not in files and re.search(pattern, line):
                yield f"{name}:{n}: {rule}: {line.strip()}"
        if (name == "main.js" and re.search(r"\bviewUpdate\s*\(", line)
                and not re.search(r"\beffect\s*\(.*\bviewUpdate\s*\(", line)):
            yield f"{name}:{n}: call viewUpdate inside effect(...) on one line, or the screen goes stale: {line.strip()}"


files = sorted(ROOT.glob("*.js"))
problems = [p for f in files for p in check(f)]
if problems:
    print("\n".join(problems), file=sys.stderr)
    sys.exit(1)
print(f"boundaries ok ({len(files)} files)")
