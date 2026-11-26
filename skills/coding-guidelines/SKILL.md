---
name: coding-guidelines
description: Coding rules for every project, covering programming languages, scripts, and build system files. Use whenever writing, editing, moving, commenting, refactoring, or reviewing code, even for a one-line fix.
---

# Coding guidelines

These rules apply to every language. Language skills (`cpp-coding` for C++,
`rust-coding` for Rust, `python-coding` for Python) add their own rules and
take precedence where the two differ; a project's `CLAUDE.md` or memory takes
precedence over both. When writing C++, Rust, or Python in a project or
package, load `cpp-coding`, `rust-coding`, or `python-coding` as well; when
writing a shell script or standalone Python script, load `scripting`.

## One file, one thing

Modularity starts at the file level: each file has a single focus.

- **One responsibility per file.** A file holds one class, one model, one
  algorithm, or one group of free functions around a single concept, along with
  any private helpers used only by it. You should be able to describe what the
  file does in a few words without using "and"; if you need "and", split it
  into two files.
- **Name the file after its responsibility.** Someone looking for `X` should be
  able to find it by filename alone (`flamelet_table.cpp` defines
  `FlameletTable`). Names like `utils`, `helpers`, or `misc` indicate a file
  with no single focus. Give each piece its own file instead.
- **New concept, new file.** Put new code in its own file rather than appending
  it to an existing file just because that file is nearby or open. Extend an
  existing file only when the new code belongs to the same responsibility.
- **Split on responsibility, not length.** A long file focused on one thing
  stays one file; a short file doing two things gets split.
- **Don't scatter one concept.** Keep a small helper in the file that uses it,
  and move it out only when a second file needs it. Paired language files (such
  as a C++ `.hpp`/`.cpp` pair) count as one file here, and tests live in a
  matching test file.
- **Group related files in directories.** Organize the parts of a larger unit
  in its own directory (for example, a model and its private components under
  `models/fsd/`) so the directory tree reads like a map of what the code does.

## Splitting existing code

When a file you touch already mixes responsibilities, point it out or split it
in a separate commit, apart from behavior changes, so each diff stays easy to
review. Keep the split itself clean:

- **Make it a pure move.** Do not change behavior or public paths.
- **Move comments with their code.** Turn a section header from the old file
  into the new file's top-level one-line comment.
- **Verify the split:** the build produces no new warnings, tests pass, any
  end-to-end script produces identical output before and after (diff it), and
  any tracked counts stay unchanged.
- **Record it** in the project's journal if it maintains one (usually
  `CLAUDE.md`).

## Comments

Keep comments to a strict minimum. Avoid adding them except:

- on non-trivial code, to explain *why* it works that way (a constraint,
  workaround, or non-obvious choice), never to restate what each line does;
- on function definitions whose arguments are not self-explanatory;
- on class definitions and their members.

Do not remove existing comments unless they directly relate to what you are
changing. When a change makes a comment inaccurate, update it in the same
change.

Describe the code as it is, not how it evolved: no "added X", "now uses Y", or
"changed from Z". That history belongs in commit messages.

Follow the language skill or the project's conventions for comment format
(`//` vs. `/** */`, doc tags).
