---
name: recap
description: Recaps one topic from a previous chat with a coding agent (Claude Code or the Antigravity CLI) in this project so the current chat has its context. Use when the user wants to catch up on an earlier topic or check how far it got, instead of reading the agent's raw transcript files.
---

# Recap

Bring the context of one topic from a previous chat into the current chat.
The user asks for a recap in one of two ways:

- **Without a topic**, e.g. "recap": the target is the last topic of the
  last chat. Follow [Recap without a topic](#recap-without-a-topic).
- **With a topic**, e.g. "recap the login bug": the target is that topic in
  one of this project's chats. Follow [Recap with a topic](#recap-with-a-topic).

Read the chats with `recap.py`, in the folder of this `SKILL.md` file. Run it
as `python3 <that folder>/recap.py`. `recap.py --help` describes what each
command prints and what each option does; run it when the output is unclear
or you need another option.

`recap.py` reads only the chats of the agent that runs it, Claude Code or the
Antigravity CLI, never the chats of the other agent.

## Topics

A topic covers these prompts:

- **Start:** a prompt that introduces a new subject: a new task or question,
  "regarding X", "now let's ...", "next".
- **Continuation:** a short follow-up, such as "yes, do it", "ok",
  "also ...", a correction, or a pasted error.
- **End:** the prompt before the next prompt that introduces a new subject.

## Recap without a topic

1. Run `recap.py` with no options. It shows the last prompts of the last
   chat one line each, then its last two turns in detail. That is usually
   enough to start.
2. Find the first prompt `N` of the last topic. Read the prompts from the
   bottom up, and stop at the latest prompt that opens a new subject. If the
   last prompt opens a new subject, the topic is that prompt alone. If the
   topic starts before the listed prompts, list the earlier ones with
   `recap.py --from 1 --to <K> --brief`.
3. If the topic starts before the two turns shown in detail, print it with
   `recap.py --from N`.
4. Continue with [Check and write the recap](#check-and-write-the-recap).

## Recap with a topic

1. Run `recap.py --search '<pattern>'`. If no chat matches, try other
   terms, such as related words, synonyms, or the other language (e.g.,
   Chinese vs. English). Tell the user only when these also find nothing.
2. Pick the closest-matching chat. The topic starts at the prompt `N` that
   first raises it. To find where it ends, list that chat's prompts with
   `recap.py --chat <id> --from N --brief`.
3. Print the topic from prompt `N` to prompt `M` with
   `recap.py --chat <id> --from N --to M`.
4. Continue with [Check and write the recap](#check-and-write-the-recap).

## Check and write the recap

1. If the project is a git repository, cross-check the topic against git:
   - Run `git log --oneline --since="<date and time of prompt N>"` to see what
     was committed. The `recap.py` header gives the date, and the prompt list
     gives the time.
   - Run `git status --short` on the topic's files to see uncommitted changes.
   - Check files outside this repository in their own repository.

2. Summarize the recap in a few concise lines:
   - **Topic:** one line.
   - **Done:** what was built, changed, or decided, and what was committed.
   - **Files:** the files changed for this topic.
   - **Stopped at:** finished, waiting on the user (state the open question),
     or cut off mid-step.
   - **Next:** the next step proposed in the last reply (omit this line if
     none was proposed).

## Rules

- Cover one topic only; do not include earlier topics.
- Base the recap solely on the transcript and git. Do not open source files.
- Always read transcripts through `recap.py`, never the raw files directly:
  the `.jsonl` files of Claude Code or the `.db` files of the Antigravity
  CLI. They are large and consist mostly of tool output and the agent's own
  context.
- Point out any discrepancy between git and the last reply (for example, when
  the last reply describes a change as uncommitted, but it has since been
  committed).
