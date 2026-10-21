# claude-skills

Personal Claude Code skills, shared between machines.

| Skill | What it covers |
| --- | --- |
| `coding-guidelines` | One file, one thing; comments kept to a strict minimum. All languages. |
| `cpp-style` | Plain C++17, naming, data members via `this->`, library layout, includes, third-party frameworks as plain libraries. |

## Install

```sh
git clone <this repo> ~/projects/claude-skills
~/projects/claude-skills/install.sh
```

`install.sh` symlinks each `skills/<name>` into `~/.claude/skills/<name>`
(or `$CLAUDE_CONFIG_DIR/skills`). Re-run it after adding a skill. Editing a
skill through `~/.claude/skills` edits this repo; commit and push from here.
