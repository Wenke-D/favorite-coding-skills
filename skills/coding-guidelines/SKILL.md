---
name: coding-guidelines
description: Coding rules for every language and project. Use whenever writing, editing, commenting, refactoring or reviewing code, even a one-line fix.
---

# Coding guidelines

These hold for every language. A language skill (`cpp-coding` for C++,
`rust-coding` for Rust) adds its own rules and wins where the two differ; a
project's CLAUDE.md or memory wins over both. When writing C++ or Rust, load
`cpp-coding` or `rust-coding` too.

## One file, one thing

Modularity starts at the file: each file holds one thing.

- **One responsibility per file.** A file holds one class, one model, one
  algorithm or one group of free functions about a single concept, together
  with the private helpers only it uses. You should be able to say what the
  file is in a few words without "and"; if you need "and", it is two files.
- **The file name names that thing.** Someone looking for the code of X
  should find it by file name alone (`flamelet_table.cpp` holds
  `FlameletTable`). A name like `utils`, `helpers` or `misc` means the file
  has no single thing; give each piece its own file instead.
- **New thing, new file.** Put new code in a file of its own rather than
  appending it to an existing file because that file is nearby or already
  open. Extend a file only when the code belongs to the thing it holds.
- **Split when a file gains a second responsibility,** not because of its
  length. A long file about one thing stays one file; a short file doing two
  things gets split.
- **Don't scatter one thing.** A small helper used by one file stays in that
  file; it moves out only when a second file needs it. Files the language
  pairs (a C++ `.hpp`/`.cpp`) count as one file here, and a file's tests
  live in a matching test file.
- **Directories group the files of one larger thing,** for example a model
  and the parts only it uses in `models/fsd/`, so the tree reads like the
  list of what the code does.

## Splitting existing code

When a file you touch already mixes things, point it out or split it in a
separate commit, apart from changes in behaviour, so each diff stays easy to
review. The split itself:

- **A pure move.** No behaviour changes and no public path changes.
- **Comments travel with their code.** A section header in the old file
  becomes the new file's one-line comment.
- **Verify it:** the build gives no new warnings, the tests pass, any
  end-to-end script gives the same output before and after (diff it), and
  any count the project tracks stays the same.
- **Record it** in the project's journal if it keeps one (usually its
  CLAUDE.md).

## Comments

Keep comments to a strict minimum. Almost never add one, except:

- on non-trivial code, to say why it does what it does (a constraint, a
  workaround, a choice that would otherwise look wrong), not to restate
  what each line does;
- on function definitions whose arguments are not self-explanatory;
- on class definitions and their members.

Don't remove existing comments unless they are directly related to what you
are changing. When a change makes a comment wrong, fix the comment in the
same change.

Comments describe the code as it is, not how it got there: no "added X",
"now uses Y" or "changed from Z". That history belongs in the commit message.

The format of a comment (`//` or `/** */`, doc tags) follows the language
skill or the project's own rule.
