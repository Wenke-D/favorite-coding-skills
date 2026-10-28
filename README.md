# favorite-coding-skills

My favorite coding skills for Claude Code, shared between machines.

| Skill | What it covers |
| --- | --- |
| `coding-guidelines` | One file, one thing, and how to split a file; comments kept to a strict minimum. All languages. |
| `cpp-coding` | Plain C++20, naming, data members via `this->`, library layout, includes, third-party frameworks as plain libraries. |
| `rust-coding` | One thing per file in Rust terms, a trait apart from its impls, `mod.rs` with flat re-exports, visibility. |
| `recap` | Catches up on the last topic of a previous chat from its saved transcript, checked against git, and carries on with it when asked. |
| `memory-cleanup` | Prunes a project's memory to what the code and docs can't tell, then fixes its links and index. |

## Install

```sh
git clone <this repo> ~/projects/favorite-coding-skills
~/projects/favorite-coding-skills/install.sh
```

`install.sh` symlinks each `skills/<name>` into `~/.claude/skills/<name>`
(or `$CLAUDE_CONFIG_DIR/skills`). Re-run it after adding a skill. Editing a
skill through `~/.claude/skills` edits this repo; commit and push from here.

## Acknowledgements

LLMs and AI agents have assisted in contributing to this project.
