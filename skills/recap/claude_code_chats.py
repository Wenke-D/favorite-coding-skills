"""Reads this project's Claude Code chats from their .jsonl transcripts."""
import functools
import json
import os
import re
from pathlib import Path

from turn import Turn

INJECTED = re.compile(r"<(ide_\w+|system-reminder|task-notification)>.*?</\1>", re.S)
FILE_TOOLS = ("Edit", "MultiEdit", "Write", "NotebookEdit")
# The tool inputs that say most about a call, in order of preference.
TOOL_ARGS = ("command", "file_path", "pattern", "url", "query", "description", "prompt")


@functools.lru_cache(maxsize=None)
def own_dir():
    """The transcript folder of this project."""
    projects = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"
    current = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if current:
        for hit in projects.glob(f"*/{current}.jsonl"):
            return hit.parent
    return projects / re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())


def chat_ids():
    """The ids of this project's chats other than the running one, newest first."""
    current = os.environ.get("CLAUDE_CODE_SESSION_ID")
    transcripts = sorted(
        (f for f in own_dir().glob("*.jsonl") if f.stem != current),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    return [f.stem for f in transcripts]


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
            turn.add_text(block["text"].strip())
        elif block.get("type") == "tool_use":
            tool_input = block.get("input", {})
            arg = next((tool_input[key] for key in TOOL_ARGS if isinstance(tool_input.get(key), str)), "")
            path = tool_input.get("file_path") if block["name"] in FILE_TOOLS else None
            turn.add_call(block["name"], arg, path)


def read_chat(chat_id):
    """The title, the time of the last record and the turns of a chat."""
    title, end, turns = "", "", []
    for record in records(own_dir() / f"{chat_id}.jsonl"):
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
