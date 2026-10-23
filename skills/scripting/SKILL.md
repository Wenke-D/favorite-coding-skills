---
name: scripting
description: Shell or Python for scripts, and the style of each - when a script is complex enough for Python, rewriting a shell script that keeps growing, what has to stay shell (environment setup, job scripts), and conventions for Python and bash scripts. Use whenever writing, extending or reviewing a shell or Python script, a Makefile recipe, CI step or job script that runs commands, or a Bash command with loops or parsing in it.
---

# Scripting

Shell for a few commands in a row, Python as soon as there is logic. Load
the general `coding-guidelines` skill too: these rules win where the two
differ. A project's CLAUDE.md or memory can add to both or override them;
follow the project where they differ.

## Shell or Python

Shell is right for a short, straight sequence of commands: set a few
variables, run some programs, loop over files doing the same thing to each.
Write Python as soon as any of these shows up:

- the script passes about 50 lines, not counting comments and blank lines;
- it parses or produces structured data: JSON, CSV, YAML, a config file,
  log output beyond a single `grep`;
- it needs arrays, associative arrays or anything nested;
- it does arithmetic beyond counting: floating point, `bc`, `awk` as a
  calculator;
- it takes options or more than a couple of arguments (a `getopts` loop, a
  `case "$1"` dispatch);
- it handles errors beyond `set -e`: retrying, cleaning up partial results,
  carrying on past a failed item and reporting it at the end;
- it has functions that compute values (`echo` captured by `$(...)`), or
  more than two or three functions at all;
- it builds command lines or strings piece by piece, needs `eval`, or
  fights quoting;
- it embeds another language: an `awk` program longer than one line, a
  `sed` script, a `python3 -c`;
- it must run on both Linux and macOS where GNU and BSD tools differ
  (`sed -i`, `date`, `readlink -f`).

When unsure, pick Python: a short Python script costs little, a shell
script that keeps growing costs a lot. The reverse holds too: a script that
is only a few commands in a row stays shell, since wrapping each in
`subprocess.run` adds nothing but noise.

## Growing an existing shell script

When a change would push a shell script past that line, don't grow it in
shell. First rewrite it in Python in a change of its own that keeps its
behaviour: same arguments, output, exit status and files written. Rename
`name.sh` to `name.py` and update everything that calls it (scripts,
Makefiles, CI, docs) in that same change. Then make the asked-for change on
top, so each diff stays easy to review, and say in your reply that you
rewrote it and why. Shell scripts you are not changing stay as they are.

## What has to stay shell

A child process can't change its parent's environment, so some things only
work in shell:

- loading modules (`module load`), sourcing an environment (`spack load`,
  `conda activate`, OpenFOAM's `etc/bashrc`), exporting variables for the
  commands that follow;
- a file meant to be sourced;
- job scripts (Slurm `#SBATCH`, PBS), which need the above anyway.

Keep these a thin wrapper: set up the environment, then
`exec python3 "$(dirname "$0")/name.py" "$@"`. The logic goes in the
Python script.

Makefile recipes, CI `run:` steps and `package.json` scripts follow the
same rule: once one passes a few lines or has logic, move it into a script
file, and that script is Python if it is complex.

## Python scripts

- `#!/usr/bin/env python3` on the first line, then a module docstring whose
  first line says what the script does; it doubles as the `--help` text
  (`argparse.ArgumentParser(description=__doc__.splitlines()[0])`).
- Standard library only: `argparse`, `pathlib`, `subprocess`, `shutil`,
  `json`, `csv`, `re`, `tempfile`. Use a third-party package only when the
  project already depends on it, so the script runs wherever `python3` does.
- Stay within the oldest Python the script must run on. Clusters and
  enterprise distributions often ship an old `python3`; check
  `python3 --version` there before using newer features (`match` needs
  3.10, `tomllib` 3.11).
- Arguments through `argparse`, never by hand from `sys.argv`.
- Run programs with `subprocess.run([...], check=True)`, arguments as a
  list; never `shell=True` or `os.system` on a string built from variables.
  Add `capture_output=True, text=True` when you need the output.
- Files through `pathlib` and `shutil` (`Path.glob`, `read_text`,
  `shutil.copy2`, `shutil.rmtree`), not by calling `cp`, `mv`, `rm`, `find`
  or `grep`.
- Code in functions, with a `main()` called under
  `if __name__ == "__main__":`, so the file can be imported and tested.
- Results to stdout, progress and diagnostics to stderr. An expected
  failure (missing file, bad input) ends with a one-line message and a
  non-zero exit through `sys.exit("...")`; a bug ends in its traceback.

## Shell scripts

- `#!/usr/bin/env bash` and `set -euo pipefail` right below it, then a
  comment saying what the script does. Use plain `sh` only when the script
  must run where bash isn't installed.
- Quote every expansion: `"$var"`, `"$@"`, `"$(cmd)"`.
- `$(...)`, never backticks.
- Lowercase names for the script's own variables, UPPER_CASE only for
  environment variables.
- Check it with `shellcheck` when that is installed.

## Commands you run yourself

The same line holds for commands run through the Bash tool. A pipeline
(`grep | sort | uniq -c`) or a short loop is fine. Once a command needs
logic, such as parsing JSON, nested loops, or collecting results and
computing on them, write it as a Python script and run that (in the
scratchpad when it doesn't belong to the project; `python3 - <<'EOF'` for a
one-off) rather than growing a long one-liner.
