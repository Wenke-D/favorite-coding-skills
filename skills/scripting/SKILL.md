---
name: scripting
description: Choosing between shell and Python for scripts, plus style conventions for each: when a script is complex enough for Python, rewriting a growing shell script, what must stay shell (environment setup, job scripts), and conventions for Python and bash. Use whenever writing, extending, or reviewing a shell or Python script, Makefile recipe, CI step, job script, or Bash command with loops or parsing.
---

# Scripting

Use shell for a few commands in a row; switch to Python as soon as real logic
appears. Load `coding-guidelines` as well: these rules take precedence where
the two differ. A project's `CLAUDE.md` or memory can extend or override both;
follow the project where they differ.

## Shell or Python

Shell fits a short, linear sequence of commands: setting a few variables,
running programs, or looping over files to run the same command on each. Write
Python as soon as any of the following apply:

- the script exceeds roughly 50 lines (excluding comments and blank lines);
- it parses or emits structured data (JSON, CSV, YAML, config files, or log
  output beyond a single `grep`);
- it needs arrays, associative arrays, or nested data structures;
- it performs arithmetic beyond simple counting (floating point, `bc`, or `awk`
  as a calculator);
- it parses options or more than a couple of arguments (a `getopts` loop or
  `case "$1"` dispatch);
- it needs error handling beyond `set -e` (retries, cleanup of partial results,
  or continuing past failures and summarizing them at the end);
- it has functions returning computed values (`echo` captured via `$(...)`), or
  more than two or three functions in total;
- it constructs command lines or strings dynamically, needs `eval`, or fights
  shell quoting;
- it embeds another language (an `awk` program longer than one line, a `sed`
  script, or `python3 -c`);
- it must run on both Linux and macOS where GNU and BSD tools differ
  (`sed -i`, `date`, `readlink -f`).

When in doubt, pick Python: a short Python script costs little, whereas a
growing shell script becomes expensive fast. Conversely, keep a short sequence
of commands in shell, since wrapping every command in `subprocess.run` only adds
noise.

## Growing an existing shell script

When a change would push a shell script past this threshold, do not keep
extending it in shell. First rewrite it in Python in a dedicated change that
preserves its exact behavior: same arguments, output, exit status, and files
written. Rename `name.sh` to `name.py` and update every caller (scripts,
Makefiles, CI, docs) in that same change. Then apply the requested feature on
top so each diff stays easy to review, and explain in your reply why you
rewrote it. Leave untouched shell scripts as they are.

## What must stay shell

Because a child process cannot modify its parent's environment, some scripts
must remain shell:

- loading modules (`module load`), sourcing environments (`spack load`,
  `conda activate`, OpenFOAM's `etc/bashrc`), or exporting variables for
  subsequent commands;
- files intended to be sourced;
- job scripts (Slurm `#SBATCH`, PBS), which require the above anyway.

Keep these as thin wrappers: set up the environment, then run
`exec python3 "$(dirname "$0")/name.py" "$@"`. Put the actual logic in Python.

Apply the same rule to Makefile recipes, CI `run:` steps, and `package.json`
scripts: once one grows past a few lines or adds logic, extract it into a
script file (in Python if it is complex).

## Python scripts

These guidelines cover standalone scripts. Python code inside a package
(including its CLI programs) follows `python-coding`.

- Start with `#!/usr/bin/env python3`, followed by a module docstring whose
  first line summarizes the script and doubles as `--help` text
  (`argparse.ArgumentParser(description=__doc__.splitlines()[0])`).
- Use the standard library only (`argparse`, `pathlib`, `subprocess`, `shutil`,
  `json`, `csv`, `re`, `tempfile`). Rely on a third-party package only if the
  project already depends on it, so the script runs wherever `python3` is
  installed.
- Target the oldest Python version the script must support. Clusters and
  enterprise distributions often ship older `python3` versions; check
  `python3 --version` there before using newer syntax (`match` requires 3.10,
  `tomllib` requires 3.11).
- Parse arguments with `argparse`, never manually from `sys.argv`.
- Invoke external programs with `subprocess.run([...], check=True)` using an
  argument list; never use `shell=True` or `os.system` on strings built from
  variables. Add `capture_output=True, text=True` when capturing output.
- Handle files via `pathlib` and `shutil` (`Path.glob`, `read_text`,
  `shutil.copy2`, `shutil.rmtree`) instead of shelling out to `cp`, `mv`, `rm`,
  `find`, or `grep`.
- Structure code into functions with a `main()` called under
  `if __name__ == "__main__":` so the file can be imported and tested.
- Write results to stdout and progress/diagnostics to stderr. Handle expected
  failures (missing files, bad input) with a one-line message and non-zero exit
  via `sys.exit("...")`; let bugs surface their tracebacks.

## Shell scripts

- Start with `#!/usr/bin/env bash` and `set -euo pipefail`, followed by a brief
  comment describing what the script does. Use plain `sh` only when the script
  must run where bash is unavailable.
- Quote every expansion: `"$var"`, `"$@"`, `"$(cmd)"`.
- Use `$(...)`, never backticks.
- Use `lowercase` names for script-local variables and `UPPER_CASE` only for
  environment variables.
- Lint with `shellcheck` when installed.

## Commands you run yourself

The same threshold applies to commands run via the Bash tool. A simple pipeline
(`grep | sort | uniq -c`) or short loop is fine. Once a command needs real
logic (parsing JSON, nested loops, or collecting and aggregating results), write
and run a Python script (in the scratchpad if it does not belong in the
project, or `python3 - <<'EOF'` for a quick one-off) instead of building a
tangled one-liner.
