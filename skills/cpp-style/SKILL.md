---
name: cpp-style
description: C++ style for the user's own projects, covering naming, class data members, headers and includes, library layout under CMake, and how to use frameworks such as OpenFOAM or Qt in project code. Use whenever writing, editing, porting, reviewing or restructuring C++ code (.cpp, .hpp, .H, .C files) or its CMakeLists.txt, even for a small edit, and whenever deciding how a C++ class, library or include should look.
---

# C++ style

These rules cover a project's own C++ code. Load the general
`coding-guidelines` skill too: these C++ rules win where the two differ. A
project's CLAUDE.md or memory can add to both or override them; follow the
project where they differ.

## Plain C++17

- Use the standard library: `std::unique_ptr`, `std::string`, `std::vector`,
  `std::optional`, and exceptions for errors.
- `.hpp` / `.cpp` files, `#pragma once` in every header.
- No run-time polymorphism, factory, registry or self-registration unless
  there really are alternatives selected at run time. A free function, or a
  plain name switch (`make_model(name)` with an `if` chain) for a handful of
  fixed choices, is enough. The user removed a self-registering model
  registry as "too heavy"; keep things that plain.

## Naming

- snake_case: executables, libraries, directories, source files, functions,
  variables (in C++ and in CMake): `hello_foam`, `libhello`, `my_rank`,
  `make_combustion_model()`. The user dislikes camelCase there.
- UpperCamelCase: class and type names, acronyms kept as written:
  `FlameletTable`, `EDC`, `FSD`.
- Names owned by someone else keep their spelling: a third-party API
  (`UPstream::nProcs()`), keys an input file uses, log text that results are
  compared against.

## Data members

- A class's data members are snake_case with a trailing underscore:
  `delta_ratio_`, `cell_point_`.
- Inside member functions, always refer to data members through `this->`
  (`this->delta_ratio_`, `this->grid_.shape()`), never by bare name, so a
  member never reads like a local. This covers members inherited from a
  framework base too, which keep their own spelling (`this->wFuel_`).
- A plain struct of public fields (`GridTensor`, a `Coeffs` or `Inputs`
  struct) keeps plain snake_case names without the underscore, as callers
  write `coeffs.delta_l`; its own member functions still use `this->`.

## Layout

- All code under `src/`, each library and each executable in its own
  directory; tests in `tests/`. Use CMake's default output layout (no
  `bin/` or `lib/` overrides).
- A library has `include/<name>/` for its public headers and `src/` for its
  sources and private headers. Only its own `include/` is PUBLIC on its
  include path, so consumers write `#include <name/header.hpp>`.
- Never put the project-wide `src/` on an include path: it lets every
  consumer see every library's headers.

## Includes

- `""` only for a header of the same target; `<>` for everything else: the
  project's other libraries, third-party headers, the standard library.
  This departs from the Google style on purpose.
- Exception: a framework file meant to be `#include`d textually inside a
  function body (OpenFOAM's `postProcess.H`-style snippets) keeps `""`.

## Third-party frameworks are just libraries

- A framework (OpenFOAM, Qt, ...) is a library the project links. Its
  directory layout, build system, naming, macros, container and smart
  pointer types and run-time selection are not the project's style. For
  OpenFOAM that means no `TypeName`, `declareRunTimeSelectionTable`,
  `dictionary`-driven selection or `autoPtr` in the project's own code.
- Follow the framework's conventions only where code must plug into it
  (deriving from its base class, implementing its interface), and then only
  as far as plugging in requires.
- Qualify its names explicitly (`Foam::argList`); no `using namespace` for
  the framework.
- Before writing a class, ask "does this need to be a framework class?" If
  not, write plain C++. Don't justify a choice by "the framework does it
  this way".
