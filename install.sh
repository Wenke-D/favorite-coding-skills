#!/usr/bin/env bash
# Links every skill in skills/ into the skill folders of Claude Code
# (~/.claude/skills) and Antigravity (~/.gemini/config/skills), so both load
# it for all projects and edits land in this repo. A real directory already in
# the way is left alone; remove it by hand after checking it.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
targets=("${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills" "$HOME/.gemini/config/skills")

for target in "${targets[@]}"; do
    mkdir -p "$target"
    for skill in "$repo"/skills/*/; do
        name=$(basename "$skill")
        link=$target/$name
        if [ -L "$link" ] || [ ! -e "$link" ]; then
            ln -sfn "${skill%/}" "$link"
            echo "linked $link"
        else
            echo "skipped $name: $link exists and is not a symlink" >&2
        fi
    done
done
