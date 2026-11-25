"""Reads this project's Antigravity CLI chats from its conversation databases.

Antigravity keeps no documented transcript format. It keeps an SQLite
database per chat with one protobuf message per step, and an index of all
chats in conversation_summaries.db. The step types and field numbers below
were read from those files with the CLI at version 1.5.
"""
import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

from protobuf_fields import every, first
from turn import Turn

USER_INPUT = 14
RESPONSE = 15
# Field numbers inside a step.
STEP_TYPE = (1,)
CREATED = (5, 1)
PROMPT = (19, 2)
RESPONSE_BODY = (20,)
# Field numbers inside the response body, and inside one of its tool calls.
REPLY_TEXT = 1
TOOL_CALL = 7
CALL_NAME = 2
CALL_ARGS = 3
FILE_TOOLS = ("write_file", "edit_file")
# The tool inputs that say most about a call, in order of preference.
TOOL_ARGS = ("CommandLine", "Path", "Query", "Url", "Prompt", "toolSummary")


def own_dir():
    """The data folder of the Antigravity CLI."""
    return Path(os.environ.get("ANTIGRAVITY_APP_DATA_DIR") or Path.home() / ".gemini" / "antigravity-cli")


def database(chat_id):
    return own_dir() / "conversations" / f"{chat_id}.db"


def connect(path):
    return closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True))


def workspaces(uris):
    """The folders of a chat, from its JSON list of file URIs."""
    return {os.path.realpath(unquote(urlparse(uri).path)) for uri in json.loads(uris)}


def chat_ids():
    """The ids of the chats started in this folder, other than the running one and subagents', newest first."""
    index = own_dir() / "conversation_summaries.db"
    if not index.exists():
        return []
    here = os.path.realpath(os.getcwd())
    current = os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
    with connect(index) as db:
        rows = db.execute("select conversation_id, workspace_uris from conversation_summaries "
                          "where parent_conversation_id = '' order by last_modified_time desc").fetchall()
    return [chat_id for chat_id, uris in rows
            if chat_id != current and here in workspaces(uris) and database(chat_id).exists()]


def title_of(chat_id):
    with connect(own_dir() / "conversation_summaries.db") as db:
        row = db.execute("select title from conversation_summaries where conversation_id = ?", (chat_id,)).fetchone()
    return row[0] if row else ""


def created(step):
    stamp = first(step, *CREATED)
    seconds = (first(stamp, 1) or 0) + (first(stamp, 2) or 0) / 1e9
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def text(value):
    return value.decode("utf-8", "replace") if value else ""


def take_response(turn, body):
    reply = text(first(body, REPLY_TEXT)).strip()
    if reply:
        turn.add_text(reply)
    for call in every(body, TOOL_CALL):
        tool = text(first(call, CALL_NAME))
        try:
            tool_input = json.loads(text(first(call, CALL_ARGS)) or "{}")
        except json.JSONDecodeError:
            tool_input = {}
        arg = next((tool_input[key] for key in TOOL_ARGS if isinstance(tool_input.get(key), str)), "")
        path = tool_input.get("Path") if tool in FILE_TOOLS else None
        turn.add_call(tool, arg, path)


def read_chat(chat_id):
    """The title, the time of the last step and the turns of a chat."""
    end, turns = "", []
    with connect(database(chat_id)) as db:
        steps = [row[0] for row in db.execute("select step_payload from steps order by idx") if row[0]]
    for step in steps:
        try:
            kind = first(step, *STEP_TYPE)
            time = created(step)
            end = time
            if kind == USER_INPUT:
                prompt = text(first(step, *PROMPT)).strip()
                if prompt:
                    turns.append(Turn(time, prompt))
            elif kind == RESPONSE and turns:
                take_response(turns[-1], first(step, *RESPONSE_BODY) or b"")
        except ValueError:
            continue
    return title_of(chat_id), end, turns
