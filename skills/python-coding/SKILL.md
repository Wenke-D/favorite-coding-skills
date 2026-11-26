---
name: python-coding
description: Use alongside coding-guidelines for Python code in a project or package (.py files, pyproject.toml), covering src layout, one unit per module, strict typing with mypy, formatting and linting with ruff, and configuration via frozen dataclasses populated from argparse. Standalone scripts follow scripting instead.
---

# Python style

These rules cover a project's own Python code: packages and the programs that
use them. Load `coding-guidelines` as well: these Python rules take precedence
where the two differ. A project's `CLAUDE.md` or memory can extend or override
both; follow the project where they differ.

Standalone single-file scripts that use only the standard library follow
`scripting` instead.

## Package layout

- Use a `src` layout: code lives under `src/<package>/`. A single
  `pyproject.toml` at the root holds project metadata, `requires-python`,
  dependencies, and tool configuration (`ruff`, `mypy`). Do not add `setup.py`,
  `setup.cfg`, `requirements.txt`, `mypy.ini`, or `ruff.toml` alongside it.
  Declare dependencies in `pyproject.toml` even when a Nix flake or conda
  environment provides them.
- Stay within `requires-python`: do not use language or standard-library
  features newer than the declared floor.
- Make each program a module inside the package with a `main()` entry point,
  registered under `[project.scripts]` or invoked as
  `python -m <package>.<module>`. Make the package importable through the
  environment (`pip install -e .` or `PYTHONPATH=src` in the devshell), never
  via `sys.path.insert`.
- Importing a module must have no side effects: define symbols only, without
  reading files, parsing arguments, printing, or touching the GPU.
- Keep data, outputs, and checkpoints outside `src/`.

## One unit per module

- Each module defines one class with its methods, one dataclass, one group of
  free functions around a single concept, or one program. Name the module after
  it in `snake_case`: `unet.py` defines `UNet`, `train_config.py` defines
  `TrainConfig`.
- Use subpackages to group modules belonging to a larger component (`models/`,
  `data/`, `training/`) so the directory tree reads like a map of the codebase.
- `__init__.py` contains only a module docstring (listing each submodule with a
  one-line summary) and re-exports of public names listed in `__all__`. Callers
  import from the package (`from <package>.models import UNet`), so splitting a
  module never breaks caller imports.
- Prefix module-private names with `_`.
- Use absolute imports only (`from <package>.data import Sample`), never
  relative imports or `import *`. Let `ruff` sort and group them.

## Naming

- `snake_case` for modules, functions, variables, and arguments;
  `UpperCamelCase` for classes with acronyms preserved (`UNet`, `FSDModel`);
  `UPPER_SNAKE_CASE` for module-level constants.
- Preserve external spellings: third-party API keywords, variable names inside
  data files, and keys in input files.

## Strict typing

- Run `mypy` in strict mode over everything in `src/`; it must pass with zero
  errors before a change is complete.
- Annotate every function and method signature, including `-> None` and
  `__init__`. Annotate local variables only where `mypy` cannot infer them
  (such as empty containers or values initialized to `None`).
- Use modern typing syntax: `list[int]`, `dict[str, float]`, `X | None`, and
  `Sequence`, `Mapping`, `Iterable`, `Callable` from `collections.abc`, not
  `typing.List`, `Optional`, or `Union`. Below Python 3.10, add
  `from __future__ import annotations` for `X | None`.
- Accept the widest type a function needs (`Sequence[float]`) and return a
  concrete type (`list[float]`).
- Avoid `Any` in the project's own signatures. Validate and convert values from
  untyped sources (`json.load`, untyped libraries) into typed objects right at
  the boundary.
- Represent structured records with dataclasses rather than `dict[str, Any]` or
  bare tuples. Represent fixed sets of string choices with
  `Literal["adam", "sgd"]` or `enum.Enum`.
- Treat `cast()` and `# type: ignore` as last resorts. Every ignore must name
  the error code and explain why:
  `# type: ignore[no-untyped-call]  # h5py has no stubs`. Strict mode flags
  unused ignores automatically.
- For an untyped third-party package, install its stubs package if one exists
  (`types-PyYAML`); otherwise add a per-module `ignore_missing_imports`
  override scoped strictly to that package, never globally.
- Use `typing.Protocol` when multiple types need to satisfy one call site.
  Avoid ABC hierarchies, factories, or registries unless alternatives are
  genuinely chosen at runtime; a simple `if` chain in `make_model(name)` is
  enough for a handful of fixed choices.

## Formatting and linting

- Use `ruff` for both: `ruff format` for formatting and `ruff check` for
  linting (including import sorting). Do not add `black`, `isort`, `flake8`, or
  `pylint` alongside it.
- Before finishing a change, run `ruff format`, `ruff check --fix`, and `mypy`
  inside the project's dev environment (Nix devshell, venv, or conda) and fix
  everything they report.
- Fix the code rather than silencing the linter. Any `# noqa: <code>` must name
  the rule and explain why. Change the project's rule set only with the user's
  agreement.
- Start new projects with this configuration (existing projects keep their own):

  ```toml
  [tool.ruff.lint]
  select = ["E", "W", "F", "I", "N", "UP", "B", "SIM", "C4", "PTH", "RUF"]

  [tool.mypy]
  strict = true
  warn_unreachable = true
  files = ["src"]
  ```

- Bringing existing code into compliance (formatting, adding type annotations)
  belongs in its own commit, separate from behavior changes, just like file
  splits in `coding-guidelines`.

## Configuration and arguments

- Store configuration in frozen dataclasses (`@dataclass(frozen=True)`), one per
  cohesive group of settings (`DataConfig`, `ModelConfig`, `TrainConfig`). Keep
  defaults on the fields, validate in `__post_init__` by raising `ValueError`,
  and compose larger configs by nesting smaller ones as fields.
- Pass each function only the narrowest config it needs
  (`train(model, config: TrainConfig)`), never an `argparse.Namespace`, raw
  dict, or module-level global config.
- Parse CLI arguments with `argparse` only in the program module, construct the
  dataclasses there, and pass them down. Nothing below `main()` should know
  about `argparse`.
- Name CLI options after field names with hyphens (`--learning-rate` maps to
  `learning_rate`), include `type=` and `help=`, and pull defaults from the
  dataclass so each default is defined once:

  ```python
  def parse_args(argv: Sequence[str] | None = None) -> TrainConfig:
      parser = argparse.ArgumentParser(
          description=__doc__.splitlines()[0],
          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      )
      parser.add_argument(
          "--learning-rate",
          type=float,
          default=TrainConfig.learning_rate,
          help="optimizer step size",
      )
      args = parser.parse_args(argv)
      try:
          return TrainConfig(learning_rate=args.learning_rate)
      except ValueError as err:
          parser.error(str(err))


  def main(argv: Sequence[str] | None = None) -> None:
      config = parse_args(argv)
      ...
  ```

- Have `main()` accept `argv` so it can be called from Python as well as the
  shell, and invoke it under `if __name__ == "__main__":`.

## Errors and output

- Raise specific exceptions (`ValueError`, `FileNotFoundError`, or a project
  subclass); never use a bare `except:` or an `except Exception` that swallows
  errors. Catch exceptions only where you can handle them. Let `main()` turn
  expected failures into a one-line message and non-zero exit, while unexpected
  bugs surface their tracebacks.
- Use `assert` only for internal invariants, never for input validation
  (`python -O` strips assertions).
- Report from package code using `logging`, with one
  `logger = logging.getLogger(__name__)` per module, and configure logging in
  `main()`. Reserve `print` for program results.
- Use `pathlib.Path` for file paths (including in type signatures), not `str`.
