---
name: cpp-coding
description: Use alongside coding-guidelines for any C++ project (.cpp, .hpp) and OpenFOAM (.H, .C files).
---

# C++ style

These rules cover a project's own C++ code. Load `coding-guidelines` as well:
these C++ rules take precedence where the two differ. A project's `CLAUDE.md`
or memory can extend or override both; follow the project where they differ.

## Plain C++20

- Use the standard library: `std::unique_ptr`, `std::string`, `std::vector`,
  `std::optional`, and exceptions for error handling.
- Use `.hpp` / `.cpp` files, with `#pragma once` in every header.
- Avoid runtime polymorphism, factories, registries, or self-registration
  unless alternatives genuinely need to be selected at runtime. A free
  function, or a simple name dispatch (`make_model(name)` with an `if` chain)
  for a handful of fixed choices, is enough. Avoid heavy self-registering
  hierarchies.

## Naming

- `snake_case` for executables, libraries, directories, source files,
  functions, and variables (in both C++ and CMake): `hello_foam`, `libhello`,
  `my_rank`, `make_combustion_model()`. Avoid `camelCase` for these.
- `UpperCamelCase` for class and type names, keeping acronyms as written:
  `FlameletTable`, `EDC`, `FSD`.
- Preserve external spellings: third-party APIs (`UPstream::nProcs()`), keys in
  input files, and log text compared against expected outputs.

## Data members

- Name class data members in `snake_case` with a trailing underscore:
  `delta_ratio_`, `cell_point_`.
- Inside member functions, always access data members via `this->`
  (`this->delta_ratio_`, `this->grid_.shape()`), never by bare name, so members
  never look like local variables. This includes members inherited from a
  framework base class, which keep their original spelling (`this->wFuel_`).
- Plain structs of public fields (`GridTensor`, or a `Coeffs` / `Inputs`
  struct) use plain `snake_case` without a trailing underscore so callers write
  `coeffs.delta_l`; their own member functions still use `this->`.

## Layout

- Place all code under `src/`, with each library and executable in its own
  directory, and tests under `tests/`. Use CMake's default output layout (do
  not override `bin/` or `lib/`).
- Each library puts public headers in `include/<name>/` and sources and private
  headers in `src/`. Expose only its own `include/` as `PUBLIC` on its include
  path so consumers write `#include <name/header.hpp>`.
- Never add the project-wide `src/` directory to an include path, as that
  exposes every library's internal headers to every consumer.

## Includes

- Use `""` only for headers in the same target, and `<>` for everything else:
  other project libraries, third-party headers, and the standard library. (This
  intentionally departs from Google C++ style.)
- Exception: framework files meant to be `#include`d textually inside a
  function body (such as OpenFOAM's `postProcess.H`-style snippets) keep `""`.

## Third-party frameworks are just libraries

- Treat a framework (OpenFOAM, Qt, etc.) as a library the project links
  against. Its directory layout, build system, naming, macros, containers,
  smart pointers, and runtime selection are not the project's style. For
  OpenFOAM, avoid `TypeName`, `declareRunTimeSelectionTable`,
  `dictionary`-driven selection, and `autoPtr` in project code.
- Follow the framework's conventions only at the boundary where code must plug
  into it (deriving from its base class or implementing its interface), and
  only as far as required.
- Qualify framework names explicitly (`Foam::argList`); never use
  `using namespace` for a framework.
- Before writing a class, ask whether it actually needs to be a framework
  class. If not, write plain C++. Do not justify a design choice simply because
  the framework does it that way.
