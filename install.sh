#!/usr/bin/env bash
# Links every skill in skills/ into ~/.claude/skills, so Claude Code loads it
# for all projects and edits land in this repo. A real directory already in
# the way is left alone; remove it by hand after checking it.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
target=${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills
mkdir -p "$target"

for skill in "$repo"/skills/*/; do
    name=$(basename "$skill")
    link=$target/$name
    if [ -L "$link" ] || [ ! -e "$link" ]; then
        ln -sfn "${skill%/}" "$link"
        echo "linked $name"
    else
        echo "skipped $name: $link exists and is not a symlink" >&2
    fi
done
