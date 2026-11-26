---
name: commit
description: Writes git commit messages as well as pull request titles and descriptions. Use whenever you create, amend, or reword a commit or open a PR, including requests like "commit this", 提交, 提交一下, or commit 一下.
---

# Commit

A commit message has a subject line, a blank line, and a body. The subject line summarizes what the commit does, and the body lists the changes:

```text
[feat] Add a --json option to the list command

- Add --json to the list command. It prints tasks as a JSON array
  with each task's id, title, and state.
- Document --json in the Usage section of README.md.
- Add tests for --json in tests/list_test.py.
```

A small commit needs only the subject line (see Body).

## Language and style

- Write commit messages in English.
- Use another language only when a project guideline requires it, such as `CLAUDE.md` or `CONTRIBUTING.md`. Earlier commits in another language do not override this.
- Load the `asd-ste100` skill and write the subject line and body in its STE-flavored mode: short sentences, active voice, simple tenses, no semicolons, and consistent terminology.
- After the tag, start the subject line with an imperative verb (such as `Add`, `Fix`, `Move`, or `Remove`), and start each body bullet with one too.
- When writing in another language, keep the English tags and message format, and apply the other rules as far as that language allows.

## Subject line

```text
[feat] Add "Export speaker notes…" to the File menu
[fix] Start a new voice input segment only after a 0.8 s pause
[doc] Add the step-by-step plan in docs/design/plans/steps.md
[chore] Add tasks.alors to list the project tasks from the repo root
[refactor] Move the page parser into its own file
```

- Start with a lowercase type tag in square brackets followed by one space. Do not add a scope or colon: write `[fix] ...`, not `fix: ...` or `[Fix(ui)] ...`.
- Follow the tag with a short summary of what the commit does.
- Keep the subject line to 72 characters or fewer, including the tag.
- Do not end with a period.
- Pick the tag using the Tags and Choosing a tag sections below.

## Body

- Write the body as a bulleted list starting with `- `.
- Cover one change per item. A second sentence can explain the effect or the reason for the change. End each sentence with a period.
- Put the main change first, followed by supporting changes such as docs and tests.
- Wrap lines at 72 characters, indenting continuation lines by two spaces to align under the item text.
- Omit the body and blank line when the commit makes a single small change that the subject line already covers completely (for example, `[doc] Fix a typo in the install command in README.md`).

## Tags

| Tag | Use it when the commit |
|---|---|
| `[feat]` | intentionally adds, changes, or removes behavior: a feature, an option, or a UI change. |
| `[fix]` | makes the code work as intended: a bug, crash, regression, or behavior that diverges from the docs. |
| `[doc]` | changes only documentation: READMEs, design docs, plans, guides, or code comments. |
| `[refactor]` | changes code without changing behavior: a move, rename, split, cleanup, or optimization. |
| `[test]` | changes only tests. |
| `[chore]` | changes the build, dependencies, packaging, CI, scripts, or settings, with no user-visible effect. |

Use only these six tags. When none fits exactly, pick the closest match.

## Choosing a tag

- Give each commit one tag for its main change.
- Docs and tests that accompany a feature or fix are part of that change: a feature commit that also updates design docs and adds tests is `[feat]`.
- To choose between `[feat]` and `[fix]`, look at the previous behavior. If it was intentional and the design is changing, use `[feat]`. If it was a defect, use `[fix]`.
- When changes include two unrelated edits in different files (such as a feature and a separate bug fix), make two commits with their own tags. When one file contains both, tag the larger change.

## Amend and reword

- Keep the commit's existing tag unless its type has changed.
- When amending a commit, update the body so it lists every change in the amended commit, both old and new.
- Do not rewrite history just to bring older commits into this format.

## Pull requests

The PR title is a subject line and follows the same rules, since a squash merge turns it into the commit's subject line.

Use this format for the PR description:

```markdown
<One to three sentences: what the PR does and why.>

## Changes

- <One change per item, the main change first.>

## Tests

- <What you ran or checked, and the result.>
```

- Follow the rules in Language and style, and write `Changes` bullets in the same style as a commit body.
- Omit the `Changes` section when the PR makes one small change that the opening sentences already cover completely.
- If you did not run or check anything, write `- None.` under `Tests`.
- Do not hard-wrap lines in a PR description; keep each paragraph and bullet on a single line.
