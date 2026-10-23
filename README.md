# favorite-coding-skills

My favorite coding skills for Claude Code, shared between machines.

| Skill | What it covers |
| --- | --- |
| `coding-guidelines` | One file, one thing, and how to split a file; comments kept to a strict minimum. All languages. |
| `cpp-coding` | Plain C++20, naming, data members via `this->`, library layout, includes, third-party frameworks as plain libraries. |
| `rust-coding` | One thing per file in Rust terms, a trait apart from its impls, `mod.rs` with flat re-exports, visibility. |
| `scripting` | Shell only for a few commands in a row, Python once a script gets complex; style for both. |
| `recap` | Catches up on the last topic of a previous chat from its saved transcript, checked against git, and carries on with it when asked. |
| `memory-cleanup` | Prunes a project's memory to what the code and docs can't tell, then fixes its links and index. |
| `doc-writing` | The process for technical documents: check each claim against the source, choose the reader, draft section by section, test the draft on a fresh reader. `asd-ste100` sets the prose. |
| `asd-ste100` | Writes and rewrites technical English in Simplified Technical English, for people and agents: one instruction per sentence, short sentences, active voice, no semicolons. Third party, see below. |

## Install

```sh
git clone <this repo> ~/projects/favorite-coding-skills
~/projects/favorite-coding-skills/install.sh
```

`install.sh` symlinks each `skills/<name>` into `~/.claude/skills/<name>`
(or `$CLAUDE_CONFIG_DIR/skills`). Re-run it after adding a skill. Editing a
skill through `~/.claude/skills` edits this repo; commit and push from here.

## Third-party skills

`skills/asd-ste100` is a copy of
[danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill)
v0.4.0 at commit `8da6b63`, under the MIT license in its `LICENSE`. The
upstream `README.md` and `.claude-plugin/` are left out.

Upstream writes the skill for text that agents parse. Here, `SKILL.md` and
`references/writing-rules.md` extend it to all technical English, including
documentation for people. To update the copy, copy `LICENSE`, `examples/` and
`scripts/` from a newer upstream commit. Merge the upstream changes to
`SKILL.md` and `references/writing-rules.md` by hand, so that the extended
scope stays. Then change the commit here.

## Acknowledgements

LLMs and AI agents have assisted in contributing to this project.
