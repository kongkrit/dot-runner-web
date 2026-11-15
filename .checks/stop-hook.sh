#!/usr/bin/env bash
# Claude Code Stop hook: refuse to finish a turn while .checks/boundaries.py reports violations.
# Exit 2 sends the list back to Claude and keeps it working. If Claude is already continuing
# because of this hook (stop_hook_active), let it stop but warn the user instead, so a violation
# it cannot fix does not loop forever.
input=$(cat)
problems=$(uv run --no-project python "$CLAUDE_PROJECT_DIR/.checks/boundaries.py" 2>&1 >/dev/null </dev/null) && exit 0
if [ "$(jq -r '.stop_hook_active // false' <<<"$input")" = true ]; then
  jq -n --arg m "MVC boundary violations remain:
$problems" '{systemMessage: $m}'
  exit 0
fi
printf 'Fix these MVC boundary violations before finishing:\n%s\n' "$problems" >&2
exit 2
