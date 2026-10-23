#!/usr/bin/env python3
"""Checks a Claude Code memory folder, for /memory-cleanup.

Lists each memory with its size, type and description, then what needs a
look: links to memories that don't exist, index lines and files that don't
match, paths that no longer exist, and wording that reads like progress or
history.
"""
import argparse
import os
import re
import sys
from pathlib import Path

LINK = re.compile(r"\[\[([^\]]+)\]\]")
INDEX_ENTRY = re.compile(r"\]\(([^)]+\.md)\)")
PATH = re.compile(r"`((?:~|\.{1,2})?/?[\w.-]+(?:/[\w.-]+)+/?)`")
PLACEHOLDER = re.compile(r"^(?:[A-Z_]+|\.\.\.)$")
PROGRESS = re.compile(
    r"\b(?:next step|next:|in progress|still (?:open|to do|deciding|missing)|open:|todo|"
    r"currently|for now|so far|not yet|until .{0,40}(?:pushed|done|merged))",
    re.I,
)
HISTORY = re.compile(
    r"\b(?:since 20\d\d-\d\d|update 20\d\d|renamed|moved (?:to|from|out|into)|used to|"
    r"formerly|was replaced|replaced (?:both|the old)|commit [0-9a-f]{7,})",
    re.I,
)
HINTS_PER_FILE = 3


def memory_dir():
    projects = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"
    current = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if current:
        for hit in projects.glob(f"*/{current}.jsonl"):
            return hit.parent / "memory"
    return projects / re.sub(r"[^A-Za-z0-9]", "-", os.getcwd()) / "memory"


def front_matter(text):
    """The `name`, `description` and `type` fields of a memory's front matter."""
    head = text.split("\n---\n", 1)[0] if text.startswith("---\n") else ""
    fields = {}
    for key in ("name", "description", "type"):
        match = re.search(rf"^\s*{key}: *(.*)$", head, re.M)
        fields[key] = match.group(1).strip().strip('"') if match else ""
    return fields


def missing_path(path):
    """True when `path` is gone although its top directory exists, i.e. it looks stale."""
    if any(PLACEHOLDER.match(part) for part in path.split("/")):
        return False
    full = Path(os.path.expanduser(path))
    top = Path(full.parts[0]) / full.parts[1] if full.is_absolute() else Path(full.parts[0])
    return top.exists() and not full.exists()


def wording_hints(text):
    body = text.split("\n---\n", 1)[-1]
    hints = []
    for line in body.splitlines():
        for kind, pattern in (("progress", PROGRESS), ("history", HISTORY)):
            match = pattern.search(line)
            if match:
                start = max(0, match.start() - 30)
                hints.append(f'{kind}? "...{line[start:match.end() + 30].strip()}..."')
    return hints[:HINTS_PER_FILE]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dir", nargs="?", type=Path, help="the memory folder (default: this project's)")
    folder = parser.parse_args().dir or memory_dir()
    if not folder.is_dir():
        sys.exit(f"no memory folder at {folder}")

    files = sorted(f for f in folder.glob("*.md") if f.name != "MEMORY.md")
    index_path = folder / "MEMORY.md"
    index = index_path.read_text() if index_path.exists() else ""
    names = {f.stem for f in files}
    total = sum(f.stat().st_size for f in files)
    print(f"Memory {folder}: {len(files)} memories, {total / 1024:.1f} KB, index {len(index.splitlines())} lines\n")

    problems = []
    for f in files:
        text = f.read_text()
        fields = front_matter(text)
        print(f"{f.stat().st_size / 1024:5.1f} KB  {fields['type'] or '?':9}  {f.stem}  {fields['description'][:90]}")
        if fields["name"] != f.stem:
            problems.append(f"{f.name}: front matter name is '{fields['name']}'")
        for link in LINK.findall(text):
            if link not in names:
                problems.append(f"{f.name}: link [[{link}]] has no memory")
        for path in dict.fromkeys(PATH.findall(text)):
            if missing_path(path):
                problems.append(f"{f.name}: path {path} does not exist")
        problems += [f"{f.name}: {hint}" for hint in wording_hints(text)]

    listed = INDEX_ENTRY.findall(index)
    problems += [f"MEMORY.md: lists {entry}, which does not exist" for entry in listed if not (folder / entry).exists()]
    problems += [f"MEMORY.md: does not list {f.name}" for f in files if f.name not in listed]

    print("\nNeeds a look" if problems else "\nNothing flagged")
    for problem in problems:
        print(f"  {problem}")


if __name__ == "__main__":
    main()
