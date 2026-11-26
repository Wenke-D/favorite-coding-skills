---
name: python-coding
description: Use alongside coding-guidelines for Python code in a project or package (.py files, pyproject.toml) - package layout, one thing per module, strict typing with mypy, formatting and linting with ruff, and configuration as dataclasses filled from argparse. Standalone scripts follow scripting instead.
---

# Python style

These rules cover a project's own Python code: a package and the programs
that use it. Load the general `coding-guidelines` skill too: these Python
rules win where the two differ. A project's CLAUDE.md or memory can add to
both or override them; follow the project where they differ.

A standalone script, one file that runs wherever `python3` does with the
standard library only, follows `scripting` instead.

## Package layout

- `src` layout: the code lives in `src/<package>/`. One `pyproject.toml` at
  the root holds the metadata, `requires-python`, the dependencies and the
  config of every tool (ruff, mypy). No `setup.py`, `setup.cfg`,
  `requirements.txt`, `mypy.ini` or `ruff.toml` beside it. List the
  dependencies there even when a Nix flake or conda environment installs
  them.
- Stay within `requires-python`: no language or library feature newer than
  it.
- Each program is a module in the package with a `main()`, registered under
  `[project.scripts]` or run as `python -m <package>.<module>`. The package
  reaches the path through the environment (`pip install -e .`, or
  `PYTHONPATH=src` in the devshell), never through `sys.path.insert`.
- Importing a module does no work: it defines things, and does not read
  files, parse arguments, print or touch the GPU.
- Data, outputs and checkpoints stay out of `src/`.

## One thing per module

- In Python a thing is one class with its methods, one dataclass, one group
  of free functions about a single concept, or one program. The module is
  named after it in snake_case: `unet.py` holds `UNet`, `train_config.py`
  holds `TrainConfig`.
- Subpackages group the modules of one larger thing (`models/`, `data/`,
  `training/`), so the tree reads like the list of what the code does.
- `__init__.py` holds a docstring listing each submodule with one line on
  what it holds, and the imports that re-export the public names, listed in
  `__all__`; nothing else. Callers import from the package
  (`from <package>.models import UNet`), so splitting a module changes no
  caller's import.
- Names used only inside their module start with `_`.
- Absolute imports only (`from <package>.data import Sample`), never
  relative or `import *`. ruff sorts and groups them.

## Naming

- snake_case for modules, functions, variables and arguments; UpperCamelCase
  for classes, acronyms kept as written (`UNet`, `FSDModel`); UPPER_SNAKE_CASE
  for module-level constants.
- Names owned by someone else keep their spelling: a third-party API's
  keywords, variable names inside a data file, keys of an input file.

## Strict typing

- mypy in strict mode checks everything under `src/`, and passes with no
  errors before a change is done.
- Annotate every function and method signature, including `-> None` and
  `__init__`. Annotate a variable only where mypy can't infer it (an empty
  container, a value that starts as `None`).
- Modern syntax: `list[int]`, `dict[str, float]`, `X | None`, and
  `Sequence`, `Mapping`, `Iterable`, `Callable` from `collections.abc`; not
  `typing.List`, `Optional` or `Union`. Below Python 3.10, add
  `from __future__ import annotations` for `X | None`.
- Take the widest type a function needs (`Sequence[float]`), return the
  concrete one (`list[float]`).
- No `Any` in the project's own signatures. A value from an untyped source
  (`json.load`, an untyped library) is checked and converted into a typed
  object at that boundary, right away.
- A record is a dataclass, not a `dict[str, Any]` or a bare tuple passed
  around. A fixed set of string choices is a `Literal["adam", "sgd"]` or an
  `enum.Enum`.
- `cast()` and `# type: ignore` are last resorts. An ignore always names the
  error code and gives the reason: `# type: ignore[no-untyped-call]  # h5py
  has no stubs`. Strict mode reports ignores that are no longer needed.
- A third-party package without types gets its stubs package if one exists
  (`types-PyYAML`), otherwise `ignore_missing_imports` in a per-module
  override for that package only; never globally.
- `typing.Protocol` when several types must fit one call. No ABC hierarchy,
  factory or registry unless there really are alternatives chosen at run
  time: a plain `if` chain in `make_model(name)` is enough for a handful of
  fixed choices.

## Formatting and linting

- ruff does both: `ruff format` formats and `ruff check` lints, including the
  import order. No black, isort, flake8 or pylint beside it.
- Before a change is done, run `ruff format`, `ruff check --fix` and `mypy`
  through the project's dev environment (its Nix devshell, venv or conda
  environment) and fix what they report.
- Fix the code, not the rule. A `# noqa: <code>` names the rule and gives the
  reason. Change the rule set only when the user agrees.
- A new project starts from this config; a project with its own keeps it:

  ```toml
  [tool.ruff.lint]
  select = ["E", "W", "F", "I", "N", "UP", "B", "SIM", "C4", "PTH", "RUF"]

  [tool.mypy]
  strict = true
  warn_unreachable = true
  files = ["src"]
  ```

- Bringing existing code up to these rules (formatting, adding types) is a
  commit of its own, apart from changes in behaviour, as for a split in
  `coding-guidelines`.

## Configuration and arguments

- Configuration is frozen dataclasses (`@dataclass(frozen=True)`), one per
  group of settings that belong together (`DataConfig`, `ModelConfig`,
  `TrainConfig`). Defaults live in the fields; checks live in
  `__post_init__` and raise `ValueError`. A config made of others holds them
  as fields.
- Code takes the narrowest config it needs (`train(model, config:
  TrainConfig)`), never an `argparse.Namespace`, a dict or a module-level
  global config.
- argparse reads the command line in the program's module only, builds the
  dataclasses there and passes them on. Nothing below `main()` sees
  `argparse`.
- An option is the field name with dashes (`--learning-rate` sets
  `learning_rate`), has `type=` and `help=`, and takes its default from the
  dataclass, so each default is written once:

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

- `main()` takes `argv` so it can be called from Python as well as from the
  shell, and runs under `if __name__ == "__main__":`.

## Errors and output

- Raise a specific exception (`ValueError`, `FileNotFoundError`, or the
  project's own subclass); never a bare `except:` or an `except Exception`
  that swallows the error. Catch only where you can handle it. The program's
  `main()` turns an expected failure into a one-line message and a non-zero
  exit; a bug ends in its traceback.
- `assert` only for internal invariants, never to check input: `python -O`
  removes it.
- Package code reports through `logging`, one
  `logger = logging.getLogger(__name__)` per module; the program configures
  logging in `main()`. `print` only for a program's results.
- Paths are `pathlib.Path`, in signatures too, not `str`.
