#!/usr/bin/env python3
"""Prints each unanswered @ai tag once its file has stopped changing, for /listen-tags.

With no paths it watches every file git would track in the current directory.
A tag counts as answered when the next tag or reply below it is an @claude
reply, so a restart reports only the tags still waiting for an answer.
"""
import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

# The boundaries keep out @aiohttp, me@ai.com and the scope in @ai-sdk/core.
TAG = re.compile(r"(?<![\w@./-])@ai(?![\w/-])")
REPLY = re.compile(r"(?<![\w@./-])@claude(?![\w/-])")
POLL_SECONDS = 2


def open_tags(path):
    """Return [(line number, stripped line)] for each unanswered tag in path."""
    try:
        lines = path.read_text().splitlines()
    except (OSError, UnicodeDecodeError):
        # Binary files hold no tags, and an editor's save can remove a file briefly.
        return []

    # A reply is checked first, so that it can quote a tag without becoming one.
    markers = []
    for number, line in enumerate(lines, start=1):
        if REPLY.search(line):
            markers.append((number, line, True))
        elif TAG.search(line):
            markers.append((number, line, False))

    tags = []
    for index, (number, line, is_reply) in enumerate(markers):
        answered = index + 1 < len(markers) and markers[index + 1][2]
        if not is_reply and not answered:
            tags.append((number, line.strip()))
    return tags


def watched_files(paths):
    if paths:
        return paths
    try:
        listing = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        sys.exit("not in a git repository: name the files to watch")
    return [Path(name) for name in listing.stdout.split("\0") if name]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path, help="files to watch")
    parser.add_argument(
        "--quiet-seconds",
        type=float,
        default=30,
        help="how long a file must stay unchanged before its tags are reported",
    )
    args = parser.parse_args()

    for path in args.paths:
        if path.is_dir():
            sys.exit(f"{path} is a directory: name files, or no path to watch the repository")

    seen_mtimes = {}
    reported = {}
    while True:
        now = time.time()
        for path in watched_files(args.paths):
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if now - mtime < args.quiet_seconds or seen_mtimes.get(path) == mtime:
                continue
            seen_mtimes[path] = mtime

            tags = open_tags(path)
            already_reported = reported.get(path, set())
            for number, text in tags:
                if text not in already_reported:
                    print(f"{path}:{number}: {text}", flush=True)
            reported[path] = {text for _, text in tags}
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
