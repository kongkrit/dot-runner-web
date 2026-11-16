"""Check the MVC boundaries described in .claude/CLAUDE.md ("Architecture rules").

Run: uv run --no-project python .checks/boundaries.py
Prints "boundaries ok (N files)" and exits 0, or prints each violation as
path:line: rule: code on stderr and exits 1. A Claude Code hook in
.claude/settings.json runs it after every edit.
"""
import posixpath
import re
import sys
from fnmatch import fnmatchcase
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent

# What each file may import, keyed by path glob from the root. Relative imports are resolved
# to such paths; {dir} is the importing file's own folder. A .js file matching no key is itself
# a violation.
ALLOWED_IMPORTS = {
    "*/model-controller-common.js": set(),
    "*/view.js": {"lit-html"},
    "*/model.js": {"@preact/signals-core", "{dir}/model-controller-common.js"},
    "*/controller.js": {"{dir}/model-controller-common.js"},
    "*/main.js": {"@preact/signals-core", "{dir}/view.js", "{dir}/model.js", "{dir}/controller.js"},
}

# (pattern, path globs where it may appear, the rule it protects). A tripwire for honest mistakes,
# not a sandbox: deliberately obfuscated code (e.g. globalThis['doc' + 'ument']) can still slip by.
RULES = [
    (r"\b(window|document|navigator|location|history|localStorage|sessionStorage|fetch|alert"
     r"|setTimeout|setInterval|requestAnimationFrame|queueMicrotask|addEventListener|globalThis|self)\b",
     {"*/main.js"}, "browser globals only in main.js"),
    (r"\beffect\b", {"*/main.js"}, "effects are created only in main.js"),
    # =, compound assignments (+=, <<=, ...), and ++/-- before or after
    (r"\.value\s*(?:[-+*/%&|^]|\*\*|<<|>>>?)?=(?!=)|\.value\s*(?:\+\+|--)|(?:\+\+|--)\s*[\w$.]+\.value\b",
     {"*/model.js"}, "only model.js writes signal values"),
    (r"\.update\b|\[\s*['\"]update['\"]\s*\]", {"*/main.js"}, "only main.js uses model.update"),
    # let/var, or a const holding an array, object or new instance (Object.freeze(...) is fine)
    (r"^(?:export\s+)?(?:let|var)\b|^(?:export\s+)?const\s+[\w$]+\s*=\s*(?:\[|\{|new\b)",
     {"*/main.js", "singleton/*"},
     "file-level changing state only in singleton/ (factory parts keep it inside the factory)"),
    (r"\b(?:viewUpdate|createView)\b", {"*/view.js", "*/main.js"}, "only main.js uses the view"),
]

# Deliberate copies that must stay byte-identical (the README walkthrough only points to the original).
COPIES = {"factory/model-controller-common.js": "singleton/model-controller-common.js"}

# A redraw call: viewUpdate(...) in singleton/, view.update(...) in factory/.
REDRAW = r"\b(?:viewUpdate|view\.update)\s*\("

# import ... from 'x', export ... from 'x', import 'x', import('x')
IMPORTS = re.compile(r"""\b(?:import|export)\b[^'";]*?\bfrom\s*['"]([^'"]+)['"]"""
                     r"""|\bimport\s*\(?\s*['"]([^'"]+)['"]""")


def matches(path, globs):
    return any(fnmatchcase(path, g) for g in globs)


def check(file):
    path = file.relative_to(ROOT).as_posix()
    folder = posixpath.dirname(path)
    allowed = next((a for g, a in ALLOWED_IMPORTS.items() if fnmatchcase(path, g)), None)
    if allowed is None:
        yield f"{path}:1: not in the rules; add it to ALLOWED_IMPORTS in .checks/boundaries.py"
        return
    allowed = {a.format(dir=folder) for a in allowed}
    # Drop // comments (but not the // in ://) so a comment can't trip a rule.
    lines = [re.sub(r"(?<!:)//.*", "", line) for line in file.read_text().splitlines()]
    code = "\n".join(lines)
    for m in IMPORTS.finditer(code):
        source = m.group(1) or m.group(2)
        if source.startswith("."):
            source = posixpath.normpath(posixpath.join(folder, source))
        if source not in allowed:
            n = code.count("\n", 0, m.start()) + 1
            yield f"{path}:{n}: may not import {source}: {lines[n - 1].strip()}"
    for n, line in enumerate(lines, 1):
        for pattern, globs, rule in RULES:
            if not matches(path, globs) and re.search(pattern, line):
                yield f"{path}:{n}: {rule}: {line.strip()}"
        if (fnmatchcase(path, "*/main.js") and re.search(REDRAW, line)
                and not re.search(r"\beffect\s*\(.*" + REDRAW, line)):
            yield f"{path}:{n}: call the view inside effect(...) on one line, or the screen goes stale: {line.strip()}"


files = sorted(p for p in ROOT.rglob("*.js")
               if not any(part.startswith(".") or part == "vendor" for part in p.relative_to(ROOT).parts))
problems = [p for f in files for p in check(f)]
for copy, original in COPIES.items():
    if (ROOT / copy).exists() and (ROOT / copy).read_bytes() != (ROOT / original).read_bytes():
        problems.append(f"{copy}:1: must stay identical to {original} (keep the copies in step)")
if problems:
    print("\n".join(problems), file=sys.stderr)
    sys.exit(1)
print(f"boundaries ok ({len(files)} files)")
