# favorite-coding-skills

My favorite coding skills for Claude Code and the Antigravity CLI (`agy`),
shared across machines.

| Skill | What it covers |
| --- | --- |
| `coding-guidelines` | One responsibility per file, how to split files cleanly, and minimal comments. Applies to all languages. |
| `cpp-coding` | Plain C++20, naming, data members via `this->`, library layout, includes, and treating third-party frameworks as plain libraries. |
| `rust-coding` | One unit per file in Rust, separating traits from their impls, flat `mod.rs` re-exports, and visibility conventions. |
| `python-coding` | Python packages: `src` layout and `pyproject.toml`, one unit per module, `__init__.py` re-exports, strict `mypy`, `ruff` formatting and linting, and frozen-dataclass configs populated from `argparse`. |
| `scripting` | Shell for short command sequences, Python once logic gets complex, and style conventions for both. |
| `recap` | Catches up on a topic from a previous chat transcript, cross-checked against git, and continues the work when asked. |
| `listen-tags` | Watches saved files for `@ai` comments and answers or applies each one in place with an `@claude` reply underneath. |
| `memory-cleanup` | Prunes a project's memory down to what the code and docs do not already record, then fixes its links and index. |
| `commit` | Writes English commit messages and PR titles/descriptions in Simplified Technical English, using bracketed type tags (`[feat]`, `[fix]`, `[doc]`, `[refactor]`, `[test]`, `[chore]`) and bulleted change lists. |
| `typst-assistant` | Watches a Typst project for `// @ai` notes in source files, applies each note, inspects the rendered page, and replies under the note. |
| `doc-writing` | Process for technical docs: verify claims against source, choose an audience, draft section by section, and test on a fresh reader. Uses `asd-ste100` for prose. |
| `asd-ste100` | Writes and rewrites technical English in Simplified Technical English for both people and agents: short sentences, active voice, one instruction per sentence, no semicolons. Third-party; see below. |
| `gui-testing` | Inspects and drives GUI apps on macOS without interrupting the user: headless Chrome, Electron apps in background mode (transparent, never activated, dialogs and menus stubbed), and window screenshots. Drives pages via the Chrome DevTools Protocol. |
| `business-writing` | Writes and rewrites Chinese business text for clients and partners (decks, proposals, letters): fixes colloquial phrasing, template-like AI wording, and weak positioning while preserving every fact and number. Includes one third-party reference; see below. |

## Install

```sh
git clone <this repo> ~/projects/favorite-coding-skills
~/projects/favorite-coding-skills/install.sh
```

`install.sh` symlinks each `skills/<name>` into two folders:

- `~/.claude/skills/<name>` (or `$CLAUDE_CONFIG_DIR/skills`) for Claude Code;
- `~/.gemini/config/skills/<name>` for Antigravity: the CLI, the app and the
  IDE all read it.

Re-run it after adding a new skill, then run `/skills reload` in any running
`agy`. Editing a skill through either folder edits this repo directly; commit
and push from here.

`recap` reads only the saved chats of the agent that runs it. For
Antigravity it reads the CLI's own databases, whose format is undocumented,
so a new CLI version can break it. `memory-cleanup` works on the memory
folder of Claude Code, since Antigravity has no memory folder of its own.

## Third-party skills

`skills/asd-ste100` is copied from
[danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill)
v0.4.0 at commit `8da6b63`, under the MIT license in its `LICENSE` file. The
upstream `README.md` and `.claude-plugin/` directory are omitted.

Upstream scopes the skill to text parsed by agents. Here, `SKILL.md` and
`references/writing-rules.md` extend it to all technical English, including
documentation written for humans. To update it, copy `LICENSE`, `examples/`,
and `scripts/` from a newer upstream commit, then merge upstream changes to
`SKILL.md` and `references/writing-rules.md` by hand to preserve the extended
scope, and update the commit hash above.

`skills/business-writing/references/ai-patterns.md` adapts 12 of the 31 checks
in [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) at commit
`f4518a8`, with new examples tailored to business text. The upstream MIT
license is in `skills/business-writing/references/LICENSE-humanizer-zh`.

## Acknowledgements

LLMs and AI agents have assisted in contributing to this project.
