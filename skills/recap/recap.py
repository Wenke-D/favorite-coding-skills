#!/usr/bin/env python3
"""Shows a previous chat of this project with a coding agent, for the recap skill.

The chats are those of the running agent, Claude Code or the Antigravity CLI;
--agent reads the other agent's chats instead. They are the chats started in
this directory, except the running one. A chat is named by the first 8
characters of its id, and its prompts are numbered from 1.

recap.py
    The last chat: its last prompts one line each, then its last two turns in
    detail. For the last topic of the last chat.

recap.py --search PATTERN [--replies]
    The earlier chats whose prompts, title or changed files match PATTERN, a
    regex, case-insensitive. Newest chat first, each with its id, dates, title
    and matching prompts. --replies also matches the assistant's replies and
    shows the words around the match. For a named topic: pass the chat id to
    --chat and the prompt numbers to --from and --to.

recap.py [--chat ID] --from N [--to M] [--brief | --full]
    Prompts N to M of the chat, default the last chat and its last prompt.
    Each prompt comes with the last reply of its turn, clipped except for the
    reply of M, then the files that the range changed. --brief prints one line
    per prompt instead. --full prints each turn without clipping, with every
    text and one line per tool call: use it when the replies do not show
    where the work stopped.

A prompt line reads "[N] HH:MM <prompt> (<marks>)". The marks give the number
of files the turn changed, "no answer" when the assistant wrote nothing, and
"ends on <tool>" when the turn ended on a tool call, e.g. when it was cut off.
A note in the output tells how to see what it leaves out.
"""
import argparse
import os
import re
import sys
import tempfile
from datetime import datetime

import antigravity_chats
import claude_code_chats

AGENTS = {"claude-code": claude_code_chats, "antigravity": antigravity_chats}
LIST_WIDTH = 160
TEXT_LIMIT = 1500
# A range longer than LONG_RANGE turns clips the replies before its last to SHORT_LIMIT.
LONG_RANGE = 8
SHORT_LIMIT = 300
DETAIL_TURNS = 2
LIST_WINDOW = 15
SEARCH_HITS = 10
SNIPPET_CONTEXT = 60


def pick_chat(chats, prefix):
    """The newest chat whose id starts with `prefix`; the last chat when it is None."""
    ids = [i for i in chats.chat_ids() if i.startswith(prefix or "")]
    if not ids:
        wanted = f"chat {prefix}" if prefix else "earlier chat"
        sys.exit(f"no {wanted} in {chats.own_dir()}")
    return ids[0]


def read_chat(chats, chat_id):
    """The chat's title, end and turns, without the agent's own files among the changed ones."""
    title, end, turns = chats.read_chat(chat_id)
    scratch = {tempfile.gettempdir(), "/tmp", "/private/tmp", str(chats.own_dir())}
    for turn in turns:
        turn.files = [p for p in turn.files if not p.startswith(tuple(d + os.sep for d in scratch))]
    return title, end, turns


def local(timestamp, layout="%Y-%m-%d %H:%M"):
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone().strftime(layout)


def clip(text, limit):
    return text if len(text) <= limit else text[:limit] + " [...]"


def relative(path):
    return os.path.relpath(path) if path.startswith(os.getcwd() + os.sep) else path


def step_text(step):
    """A text as it is, a (tool, argument) pair as one line."""
    if isinstance(step, str):
        return step
    tool, arg = step
    return f"[{tool}] {clip(' '.join(arg.split()), LIST_WIDTH)}"


def prompt_line(number, turn):
    marks = []
    if turn.files:
        marks.append(f"{len(turn.files)} file{'s' if len(turn.files) > 1 else ''}")
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
            print("### Steps\n" + "\n\n".join(step_text(step) for step in turn.steps) + "\n")
        else:
            reply = turn.reply if number == end else clip(turn.reply, reply_limit)
            print(f"### Reply\n{reply or '(no text)'}\n")
            if turn.last_block != "text":
                print(f"(the turn ended on a {turn.last_block} call; the reply above was written before it)\n")
        files += [f for f in turn.files if f not in files]
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


def search(chats, pattern, replies):
    try:
        regex = re.compile(pattern, re.I)
    except re.error as error:
        sys.exit(f"bad pattern {pattern!r}: {error}")
    found = False
    for chat_id in chats.chat_ids():
        title, end, turns = read_chat(chats, chat_id)
        hits = []
        for number, turn in enumerate(turns, 1):
            files = [relative(f) for f in turn.files if regex.search(f)]
            in_prompt = bool(files or regex.search(turn.prompt))
            snippet = "" if in_prompt or not replies else reply_match(regex, turn)
            if in_prompt or snippet:
                hits.append((number, turn, files, snippet))
        if not turns or not (hits or regex.search(title)):
            continue
        found = True
        print(f'{chat_id[:8]}  {local(turns[0].time)} to {local(end)}  {len(turns)} prompts  "{title or "(no title)"}"')
        for number, turn, files, snippet in hits[:SEARCH_HITS]:
            print("    " + prompt_line(number, turn) + (f"  [{', '.join(files)}]" if files else ""))
            if snippet:
                print(f"        reply: {snippet}")
        if len(hits) > SEARCH_HITS:
            print(f"    ... {len(hits) - SEARCH_HITS} more; --chat {chat_id[:8]} --from 1 --brief lists every prompt")
    if not found:
        sys.exit(f"no earlier chat matches {pattern!r}")


def main():
    summary, _, usage = __doc__.partition("\n\n")
    parser = argparse.ArgumentParser(description=summary, epilog=usage,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--search", metavar="PATTERN",
                        help="list the earlier chats and prompts whose text, title or changed files "
                             "match this regex, case-insensitive")
    parser.add_argument("--replies", action="store_true",
                        help="with --search, also match the assistant's replies")
    parser.add_argument("--chat", metavar="ID", help="the chat whose id starts with this, from --search; default the last chat")
    parser.add_argument("--from", dest="start", type=int, metavar="N", help="print the prompts from this one on")
    parser.add_argument("--to", dest="end", type=int, metavar="M", help="with --from, stop at this prompt; default the last")
    style = parser.add_mutually_exclusive_group()
    style.add_argument("--brief", action="store_true", help="with --from, one line per prompt")
    style.add_argument("--full", action="store_true", help="no clipping, and every text and tool call of each turn")
    parser.add_argument("--agent", choices=AGENTS,
                        default="antigravity" if os.environ.get("ANTIGRAVITY_AGENT") else "claude-code",
                        help="the agent whose chats to read; default the running one")
    args = parser.parse_args()
    chats = AGENTS[args.agent]

    if args.search is not None:
        if args.chat or args.start is not None or args.end is not None or args.brief or args.full:
            parser.error("--search takes no other option but --replies")
        search(chats, args.search, args.replies)
        return
    if args.replies:
        parser.error("--replies needs --search")
    if args.start is None and (args.end is not None or args.brief):
        parser.error("--to and --brief need --from")
    chat_id = pick_chat(chats, args.chat)
    title, end, turns = read_chat(chats, chat_id)
    if not turns:
        sys.exit(f"chat {chat_id[:8]} holds no prompts")
    last = len(turns) if args.end is None else args.end
    if args.start is not None and not 1 <= args.start <= last <= len(turns):
        sys.exit(f"need 1 <= --from <= --to <= {len(turns)}")
    print(f'Chat {chat_id[:8]} "{title}", {local(turns[0].time)} to {local(end)}, {len(turns)} prompts\n')
    if args.start is None:
        print_overview(turns, args.full)
    elif args.brief:
        print_prompts(turns, args.start, last)
    else:
        print_topic(turns, args.start, last, args.full)


if __name__ == "__main__":
    main()
