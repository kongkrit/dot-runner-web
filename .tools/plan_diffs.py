# Rewrites the diff blocks in a study plan from its whole files, so no diff is ever written by hand.
# A file's first version is the plan's first js block (main.js) or html block (index.html). Each
# "Complete main.js" or "Complete index.html" fold is that file's next version, and the diff block
# just before the fold becomes the change from the version before it.
# A change in whitespace alone, such as a block indented deeper or a comment realigned, is left out.
# Usage, from the repo root: uv run --no-project python .tools/plan_diffs.py STUDY_PLAN_2.md
import difflib
import pathlib
import re
import sys


def tidy(line):   # what a line is compared by: whitespace at either end dropped, each run inside cut to one space
    return ' '.join(line.split())


def span(start, stop):   # a hunk header's "first line,count", as diff -u writes it
    count = stop - start
    first = start + 1 if count else start   # an empty range names the line before it
    return str(first) if count == 1 else f'{first},{count}'


def diff(old, new):   # old, new: lists of lines; unchanged lines are shown as they are in old
    out = []
    matcher = difflib.SequenceMatcher(None, [tidy(line) for line in old], [tidy(line) for line in new])
    for hunk in matcher.get_grouped_opcodes(2):   # 2: unchanged lines kept around each change
        out.append(f'@@ -{span(hunk[0][1], hunk[-1][2])} +{span(hunk[0][3], hunk[-1][4])} @@\n')
        for tag, i1, i2, j1, j2 in hunk:
            if tag == 'equal':
                out += [' ' + line for line in old[i1:i2]]
            else:
                out += ['-' + line for line in old[i1:i2]] + ['+' + line for line in new[j1:j2]]
    return ''.join(out)


path = pathlib.Path(sys.argv[1])
text = path.read_text()
latest = {name: re.search(rf'^```{lang}\n((?:.*\n)*?)```$', text, re.M)[1]
          for name, lang in [('main.js', 'js'), ('index.html', 'html')]}
FOLD = re.compile(r'(```diff\n)((?:[ +\-@].*\n|\n)*)(```\n\n<details>\n<summary>Complete (\S+)</summary>\n\n```\w+\n((?:.*\n)*?)```\n)')
changed = 0


def rewrite(m):
    global changed
    name, new = m[4], m[5]
    body = diff(latest[name].splitlines(True), new.splitlines(True))
    latest[name] = new
    changed += body != m[2]
    return m[1] + body + m[3]


text = FOLD.sub(rewrite, text)
if changed:
    path.write_text(text)
print(f'{changed} diffs changed')
