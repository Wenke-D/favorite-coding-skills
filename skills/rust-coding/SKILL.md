---
name: rust-coding
description: Use alongside coding-guidelines for any Rust project (.rs files).
---

# Rust style

These rules cover a project's own Rust code. Load `coding-guidelines` as well:
these Rust rules take precedence where the two differ. A project's `CLAUDE.md`
or memory can extend or override both; follow the project where they differ.

## One unit per file

- Each file defines one unit: a type with its inherent methods, a trait, a
  group of trait impls covering the same category of types, a macro, or a free
  function. Name the file after it: `book_id.rs`, `machine_column.rs`,
  `entity_macro.rs` (`book/book.rs` is fine).
- Keep a trait and its impls in separate files. Give the trait its own file,
  and group impls by what they map, one group per file: `column.rs` (the
  trait), `machine_column.rs` (`i64`, `i32`, `bool`, `String`),
  `nullable_column.rs` (`Option`), `gc_column.rs` (`GcRef`). Adding a new case
  means adding a new file.
- A type with multiple distinct concerns spreads its methods across files by
  concern, one `impl` block per file: `db.rs` (the struct and its
  constructors), `identity_map.rs`, `tables.rs`, `load.rs`, `upsert.rs`. The
  parent's module doc notes where each part lives.

## Modules

- `mod.rs` contains only the module doc, `mod` declarations, and re-exports.
  The module doc lists each submodule with a one-line summary of what it
  defines.
- Keep submodules private and re-export their public items flat from `mod.rs`
  with `pub use`, so splitting a file never changes a caller's import path.

## Visibility

- Mark the internals of a public type `pub(super)`, Rust's equivalent of
  package-private.
- Inside a private submodule, use plain `pub`: the private module already
  restricts visibility, avoiding repetitive `pub(in crate::x)` annotations on
  every field.
