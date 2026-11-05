---
name: commit
description: Writes git commit messages, and the titles and descriptions of pull requests. Use whenever you make, amend or reword a commit or open a PR, including requests like "commit this", 提交, 提交一下 or commit 一下.
---

# Commit

A commit message has a subject line, one blank line and a body. The subject line tells what the commit does. The body lists the changes in the commit:

```text
[feat] Add a --json option to the list command

- Add --json to the list command. It prints the tasks as a JSON array
  with the id, the title and the state of each task.
- Describe --json in the Usage section of README.md.
- Add tests for --json in tests/list_test.py.
```

A small commit has only the subject line (see Body).

## Language and style

- Write the commit message in English.
- Use a different language only when an instruction of the project tells you to, for example its CLAUDE.md or CONTRIBUTING.md. Earlier commits in a different language are not such an instruction.
- Load the asd-ste100 skill. Write the subject line and the body in its STE-flavored mode: short sentences, active voice, simple tenses, no semicolons, one name for one thing.
- After the tag, start the subject line with an imperative verb, such as Add, Fix, Move or Remove. Start each body item with one too.
- In a different language, keep the English tags and the format of the message. Apply the other rules where that language lets you.

## Subject line

```text
[feat] Add "Export speaker notes…" to the File menu
[fix] Start a new voice input segment only after a 0.8 s pause
[doc] Add the step-by-step plan in docs/design/plans/steps.md
[chore] Add tasks.alors to list the project tasks from the repo root
[refactor] Move the page parser into its own file
```

- Start with a type tag in lowercase and in square brackets, then one space. Do not add a scope or a colon: write `[fix] ...`, not `fix: ...` or `[Fix(ui)] ...`.
- After the tag, write a short summary of what the commit does.
- Keep the subject line to 72 characters or fewer, with the tag.
- Do not put a period at the end.
- Choose the tag with the sections Tags and Choose the tag below.

## Body

- Write the body as a bulleted list. Start each item with `- `.
- Give each item one change in the commit. A second sentence can tell the effect or the reason of the change. End each sentence with a period.
- Put the main change first. Then list the other changes, including the docs and tests that come with the main change.
- Wrap the lines at 72 characters. Indent a continued line by two spaces, so that it starts under the text of its item.
- Leave out the body and the blank line when the commit makes one small change and the subject line tells all of it. For example, `[doc] Fix a typo in the install command in README.md` has no body.

## Tags

| Tag | Use it when the commit |
|---|---|
| `[feat]` | adds, changes or removes a behavior on purpose: a feature, an option, a different UI. |
| `[fix]` | makes the code do what it was meant to do: a bug, a crash, a regression, behavior that does not match the docs. |
| `[doc]` | changes only documentation: a README, design docs, plans, guides or code comments. |
| `[refactor]` | changes code and keeps its behavior: a move, a rename, a split, a cleanup or a speed-up. |
| `[test]` | changes only tests. |
| `[chore]` | changes the build, dependencies, packaging, CI, scripts or settings, and nothing that a user of the program sees. |

Use only these six tags. When no tag fits exactly, use the nearest one.

## Choose the tag

- Give each commit one tag, for its main change.
- Docs and tests that come with a feature or a fix are part of that change. A feature commit that also updates the design docs and adds tests is `[feat]`.
- To choose between `[feat]` and `[fix]`, look at the old behavior. If the old behavior was the design and the design changes, use `[feat]`. If the old behavior was a defect, use `[fix]`.
- When the changes hold two unrelated changes in different files, such as a feature and a separate fix, make two commits with a tag each. When one file holds both, tag the larger change.

## Amend and reword

- Keep the tag of the commit. Change the tag only when the commit is now a different type.
- When you amend a commit, make the body list all the changes of the amended commit, the old changes and the new changes.
- Do not rewrite history only to bring old commits to this format.

## Pull requests

The PR title is a subject line and follows the same rules. A squash merge makes the title the subject line of the commit.

The PR description has this format:

```markdown
<One to three sentences: what the PR does and why.>

## Changes

- <One change per item, the main change first.>

## Tests

- <What you ran or checked, and the result.>
```

- Write the description with the rules of Language and style. Write the Changes items as the items of a commit body.
- Leave out the Changes section when the PR makes one small change and the first sentences tell all of it.
- When you did not run or check anything, write `- None.` under Tests.
- Do not wrap the lines of a PR description. Write each paragraph and each item on one line.
