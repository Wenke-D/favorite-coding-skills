#!/usr/bin/env python3
"""Shows a previous Claude Code chat of this project, for /recap.

Without options it shows the last chat: the prompts before its last two turns,
one line each, then those two turns in detail. --from N [--to M] prints a range
of prompts in detail, or one line each with --brief. --search finds the earlier
chats and prompts that match a topic.
"""
import argparse
import functools
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

INJECTED = re.compile(r"<(ide_\w+|system-reminder|task-notification)>.*?</\1>", re.S)
FILE_TOOLS = ("Edit", "MultiEdit", "Write", "NotebookEdit")
# The tool inputs that say most about a call, in order of preference.
TOOL_ARGS = ("command", "file_path", "pattern", "url", "query", "description", "prompt")
LIST_WIDTH = 160
TEXT_LIMIT = 1500
# A range longer than LONG_RANGE turns clips the replies before its last to SHORT_LIMIT.
LONG_RANGE = 8
SHORT_LIMIT = 300
DETAIL_TURNS = 2
LIST_WINDOW = 15
SEARCH_HITS = 10
SNIPPET_CONTEXT = 60


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
        # Every text the assistant wrote and every tool call, in order, for --full.
        self.steps = []
        # Every text the assistant wrote, for --search --replies.
        self.texts = []


@functools.lru_cache(maxsize=None)
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


def tool_call(block):
    """One line for a tool call: its name and its most telling input."""
    tool_input = block.get("input", {})
    arg = next((tool_input[key] for key in TOOL_ARGS if isinstance(tool_input.get(key), str)), "")
    return f"[{block['name']}] {clip(' '.join(arg.split()), LIST_WIDTH)}"


def take_reply(turn, content):
    for block in content:
        if block.get("type") == "text" and block["text"].strip():
            turn.reply = block["text"].strip()
            turn.last_block = "text"
            turn.steps.append(turn.reply)
            turn.texts.append(turn.reply)
        elif block.get("type") == "tool_use":
            turn.last_block = block["name"]
            turn.steps.append(tool_call(block))
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


def work_files(paths):
    """`paths` without Claude's own scratch and memory files, which a recap leaves out."""
    scratch = {tempfile.gettempdir(), "/tmp", "/private/tmp", str(transcript_dir())}
    return [p for p in paths if not p.startswith(tuple(d + os.sep for d in scratch))]


def prompt_line(number, turn):
    marks = []
    files = work_files(turn.files)
    if files:
        marks.append(f"{len(files)} file{'s' if len(files) > 1 else ''}")
    if not turn.last_block:
        marks.append("no answer")
    elif turn.last_block != "text":
        marks.append(f"ends on {turn.last_block}")
    tail = f"  ({', '.join(marks)})" if marks else ""
    return f"[{number}] {local(turn.time, '%H:%M')}  {clip(' '.join(turn.prompt.split()), LIST_WIDTH)}{tail}"


def print_prompts(turns, start, end):
    for number in range(start, end + 1):
        print(prompt_line(number, turns[number - 1]))


def print_topic(turns, start, end, full):
    """Prompts `start` to `end` with their replies; the reply of `end` is never clipped."""
    files = []
    reply_limit = TEXT_LIMIT
    if not full and end - start + 1 > LONG_RANGE:
        reply_limit = SHORT_LIMIT
        print(f"(long range: replies before [{end}] are clipped to {SHORT_LIMIT} characters; "
              f"--from K --to K prints the reply of prompt K in full)\n")
    for number in range(start, end + 1):
        turn = turns[number - 1]
        prompt = turn.prompt if full else clip(turn.prompt, TEXT_LIMIT)
        print(f"## [{number}] {local(turn.time, '%H:%M')}\n{prompt}\n")
        if not turn.last_block:
            print("(no answer)\n")
            continue
        if full:
            print("### Steps\n" + "\n\n".join(turn.steps) + "\n")
        else:
            reply = turn.reply if number == end else clip(turn.reply, reply_limit)
            print(f"### Reply\n{reply or '(no text)'}\n")
            if turn.last_block != "text":
                print(f"(the turn ended on a {turn.last_block} call; the reply above was written before it)\n")
        files += [f for f in work_files(turn.files) if f not in files]
    if files:
        print(f"## Files changed in [{start}]-[{end}]\n" + "\n".join(relative(f) for f in files))


def print_overview(turns, full):
    detail = max(1, len(turns) - DETAIL_TURNS + 1)
    first = max(1, detail - LIST_WINDOW)
    if first > 1:
        print(f"({first - 1} earlier prompts not shown; --from 1 --to {first - 1} --brief lists them)\n")
    if first < detail:
        print_prompts(turns, first, detail - 1)
        print()
    print_topic(turns, detail, len(turns), full)


def reply_match(regex, turn):
    """The words around the first match of `regex` in the turn's replies, or ""."""
    for text in turn.texts:
        text = " ".join(text.split())
        match = regex.search(text)
        if match:
            start = max(0, match.start() - SNIPPET_CONTEXT)
            return f"...{text[start:match.end() + SNIPPET_CONTEXT]}..."
    return ""


def search(pattern, replies):
    try:
        regex = re.compile(pattern, re.I)
    except re.error as error:
        sys.exit(f"bad pattern {pattern!r}: {error}")
    found = False
    for path in previous_sessions():
        title, end, turns = read_session(path)
        hits = []
        for number, turn in enumerate(turns, 1):
            files = [relative(f) for f in work_files(turn.files) if regex.search(f)]
            in_prompt = bool(files or regex.search(turn.prompt))
            snippet = "" if in_prompt or not replies else reply_match(regex, turn)
            if in_prompt or snippet:
                hits.append((number, turn, files, snippet))
        if not turns or not (hits or regex.search(title)):
            continue
        found = True
        print(f'{path.stem[:8]}  {local(turns[0].time)} to {local(end)}  {len(turns)} prompts  "{title or "(no title)"}"')
        for number, turn, files, snippet in hits[:SEARCH_HITS]:
            print("    " + prompt_line(number, turn) + (f"  [{', '.join(files)}]" if files else ""))
            if snippet:
                print(f"        reply: {snippet}")
        if len(hits) > SEARCH_HITS:
            print(f"    ... {len(hits) - SEARCH_HITS} more")
    if not found:
        sys.exit(f"no earlier chat matches {pattern!r}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--search", metavar="PATTERN",
                        help="list the earlier chats and prompts whose text, title or changed files "
                             "match this regex, case-insensitive")
    parser.add_argument("--replies", action="store_true",
                        help="with --search, also match the assistant's replies")
    parser.add_argument("--chat", help="the chat whose id starts with this, from --search; default the last chat")
    parser.add_argument("--from", dest="start", type=int, help="print the prompts from this one on")
    parser.add_argument("--to", dest="end", type=int, help="with --from, stop at this prompt; default the last")
    style = parser.add_mutually_exclusive_group()
    style.add_argument("--brief", action="store_true", help="with --from, one line per prompt")
    style.add_argument("--full", action="store_true", help="no clipping, and every text and tool call of each turn")
    args = parser.parse_args()

    if args.search is not None:
        if args.chat or args.start is not None or args.end is not None or args.brief or args.full:
            parser.error("--search takes no other option but --replies")
        search(args.search, args.replies)
        return
    if args.replies:
        parser.error("--replies needs --search")
    if args.start is None and (args.end is not None or args.brief):
        parser.error("--to and --brief need --from")
    path = pick_session(args.chat)
    title, end, turns = read_session(path)
    if not turns:
        sys.exit(f"{path.name} holds no prompts")
    last = len(turns) if args.end is None else args.end
    if args.start is not None and not 1 <= args.start <= last <= len(turns):
        sys.exit(f"need 1 <= --from <= --to <= {len(turns)}")
    print(f'Chat {path.stem[:8]} "{title}", {local(turns[0].time)} to {local(end)}, {len(turns)} prompts\n')
    if args.start is None:
        print_overview(turns, args.full)
    elif args.brief:
        print_prompts(turns, args.start, last)
    else:
        print_topic(turns, args.start, last, args.full)


if __name__ == "__main__":
    main()
