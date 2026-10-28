#!/usr/bin/env python3
"""Shows a previous Claude Code chat of this project, for /recap.

With --list it lists the recent chats. Otherwise, for the last chat or the one
--chat names: without --from it lists the chat's prompts, numbered; with
--from N it prints the topic that starts at prompt N: each prompt, the reply
that closed it and the files the topic changed.
"""
import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

INJECTED = re.compile(r"<(ide_\w+|system-reminder)>.*?</\1>", re.S)
FILE_TOOLS = ("Edit", "MultiEdit", "Write", "NotebookEdit")
LIST_WIDTH = 160
TEXT_LIMIT = 1500


class Turn:
    """One prompt of the user and what the assistant did after it."""

    def __init__(self, time, prompt):
        self.time = time
        self.prompt = prompt
        # The last text the assistant wrote in this turn.
        self.reply = ""
        # What the turn ended on: "text", a tool name, or "" when nothing came.
        self.last_block = ""
        # Files edited or written, in the order first touched.
        self.files = []


def transcript_dir():
    projects = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"
    current = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if current:
        for hit in projects.glob(f"*/{current}.jsonl"):
            return hit.parent
    return projects / re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())


def previous_sessions():
    """This project's transcripts other than the running chat's, newest first."""
    folder = transcript_dir()
    current = os.environ.get("CLAUDE_CODE_SESSION_ID")
    return sorted(
        (f for f in folder.glob("*.jsonl") if f.stem != current),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )


def pick_session(prefix):
    """The newest transcript whose id starts with `prefix`; the last chat's when it is None."""
    sessions = [f for f in previous_sessions() if f.stem.startswith(prefix or "")]
    if not sessions:
        wanted = f"chat {prefix}" if prefix else "earlier chat"
        sys.exit(f"no {wanted} in {transcript_dir()}")
    return sessions[0]


def records(path):
    for line in path.open(encoding="utf-8"):
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def prompt_text(content):
    if isinstance(content, str):
        parts = [content]
    elif any(block.get("type") == "tool_result" for block in content):
        return None
    else:
        parts = [block.get("text", "") for block in content if block.get("type") == "text"]
    text = INJECTED.sub("", "\n".join(parts)).strip()
    if not text or text.startswith("[Request interrupted"):
        return None
    return text


def take_reply(turn, content):
    for block in content:
        if block.get("type") == "text" and block["text"].strip():
            turn.reply = block["text"].strip()
            turn.last_block = "text"
        elif block.get("type") == "tool_use":
            turn.last_block = block["name"]
            path = block.get("input", {}).get("file_path")
            if block["name"] in FILE_TOOLS and path and path not in turn.files:
                turn.files.append(path)


def read_session(path):
    title, end, turns = "", "", []
    for record in records(path):
        kind = record.get("type")
        end = record.get("timestamp", end)
        if kind == "ai-title":
            title = record.get("aiTitle", title)
        if record.get("isSidechain") or record.get("isMeta") or record.get("isCompactSummary"):
            continue
        if kind == "user":
            text = prompt_text(record["message"]["content"])
            if text:
                turns.append(Turn(record["timestamp"], text))
        elif kind == "assistant" and turns:
            take_reply(turns[-1], record["message"]["content"])
    return title, end, turns


def local(timestamp, layout="%Y-%m-%d %H:%M"):
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone().strftime(layout)


def clip(text, limit):
    return text if len(text) <= limit else text[:limit] + " [...]"


def relative(path):
    return os.path.relpath(path) if path.startswith(os.getcwd() + os.sep) else path


def is_work_file(path):
    """False for Claude's own scratch and memory files, which a recap leaves out."""
    return not path.startswith((tempfile.gettempdir() + os.sep, str(transcript_dir()) + os.sep))


def print_chats(count):
    sessions = previous_sessions()[:count]
    if not sessions:
        sys.exit(f"no earlier chat in {transcript_dir()}")
    for path in sessions:
        title, _, turns = read_session(path)
        when = datetime.fromtimestamp(path.stat().st_mtime).strftime("%m-%d %H:%M")
        last = clip(" ".join(turns[-1].prompt.split()), LIST_WIDTH) if turns else ""
        print(f"{path.stem[:8]}  {when}  {len(turns):3} prompts  {title or '(no title)'}\n    last: {last}")


def print_prompts(turns):
    for number, turn in enumerate(turns, 1):
        print(f"[{number}] {local(turn.time, '%H:%M')}  {clip(' '.join(turn.prompt.split()), LIST_WIDTH)}")


def print_topic(turns, start):
    if not 1 <= start <= len(turns):
        sys.exit(f"--from must be between 1 and {len(turns)}")
    files = []
    for number, turn in enumerate(turns[start - 1:], start):
        last = number == len(turns)
        print(f"## [{number}] {local(turn.time, '%H:%M')}\n{clip(turn.prompt, TEXT_LIMIT)}\n")
        if not turn.last_block:
            print("(no answer)\n")
            continue
        reply = turn.reply if last else clip(turn.reply, TEXT_LIMIT)
        print(f"### Reply\n{reply or '(no text)'}\n")
        if turn.last_block != "text":
            print(f"(the turn ended on a {turn.last_block} call; the reply above was written before it)\n")
        files += [f for f in turn.files if f not in files and is_work_file(f)]
    if files:
        print("## Files changed in this topic\n" + "\n".join(relative(f) for f in files))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", dest="count", type=int, nargs="?", const=8,
                        help="list the last COUNT chats (default 8) with their ids")
    parser.add_argument("--chat", help="the chat whose id starts with this, from --list; default the last chat")
    parser.add_argument("--from", dest="start", type=int, help="print the topic that starts at this prompt")
    args = parser.parse_args()

    if args.count is not None:
        print_chats(args.count)
        return
    path = pick_session(args.chat)
    title, end, turns = read_session(path)
    if not turns:
        sys.exit(f"{path.name} holds no prompts")
    print(f'Chat {path.stem[:8]} "{title}", {local(turns[0].time)} to {local(end)}, {len(turns)} prompts\n')
    if args.start is None:
        print_prompts(turns)
    else:
        print_topic(turns, args.start)


if __name__ == "__main__":
    main()
