---
name: rust-style
description: Rust coding style for all projects - what one thing per file means in Rust (a type with its inherent methods, a trait, a group of impls, a macro or a free function), a trait in its own file apart from its impls, a type with several concerns spread over impl blocks in separate files, mod.rs holding only the module doc, the mod declarations and flat re-exports of private submodules, and pub(super) for the internals of a public type. Use whenever writing, reviewing, splitting or restructuring Rust code, even for a small edit.
---

# Rust style

These rules cover a project's own Rust code. Load the general
`coding-guidelines` skill too: these Rust rules win where the two differ. A
project's CLAUDE.md or memory can add to both or override them; follow the
project where they differ.

## One thing per file

- In Rust a thing is one type with its inherent methods, one trait, one
  group of impls that map the same kind of thing, one macro or one free
  function. The file is named after it: `book_id.rs`, `machine_column.rs`,
  `entity_macro.rs`. `book/book.rs` is fine.
- A trait and its impls live apart. The trait has its own file, and the
  impls are grouped by what they map, one group per file: `column.rs` (the
  trait), `machine_column.rs` (`i64`, `i32`, `bool`, `String`),
  `nullable_column.rs` (`Option`), `gc_column.rs` (`GcRef`). A new case is
  a new file.
- A type with several concerns spreads its methods over files by concern,
  one `impl` block each: `db.rs` (the struct and its construction),
  `identity_map.rs`, `tables.rs`, `load.rs`, `upsert.rs`. The parent's
  module doc says where each part lives.

## Modules

- `mod.rs` holds the module doc, the `mod` declarations and the re-exports,
  nothing else. The module doc lists each submodule with one line on what
  it holds.
- Submodules are private, and their public items are re-exported flat from
  `mod.rs` with `pub use`, so splitting a file changes no caller's path.

## Visibility

- The internals of a public type are `pub(super)`, Rust's form of
  package-private.
- Items inside a private submodule are plain `pub`: the private module
  already bounds them, and it saves writing `pub(in crate::x)` on every
  field.
