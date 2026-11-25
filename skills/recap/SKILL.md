---
name: recap
description: Recaps one topic of a previous chat with a coding agent (Claude Code or the Antigravity CLI) in this project, so that the current chat has its context. Use when the user wants to catch up on a topic from an earlier chat, or on how far it got. Use it instead of reading the agent's transcript files.

---

# Recap

Give the current chat the context of one topic from a previous chat. The
user asks for a recap in one of two ways:

- **Without a topic**, e.g. "recap": the target is the last topic of the
  last chat. Follow [Recap without a topic](#recap-without-a-topic).
- **With a topic**, e.g. "recap the login bug": the target is that topic in
  one of this project's chats. Follow [Recap with a topic](#recap-with-a-topic).

Read the chats with `recap.py`, in the folder of this `SKILL.md` file. Run it
as `python3 <that folder>/recap.py`. `recap.py --help` shows what each
command prints and what each option does. Run it when the output is not
clear or you need another option.

`recap.py` reads the chats of the agent that runs it, Claude Code or the
Antigravity CLI. To read the chats of the other agent, add
`--agent claude-code` or `--agent antigravity`. Do this when the user says
that the earlier work was with the other agent.

## Topics

A topic covers these prompts:

- **Start:** a prompt that opens a new subject: a new task or question,
  "regarding X", "now let's ...", "next".
- **Continuation:** a short follow-up, such as "yes, do it", "ok",
  "also ...", a correction or a pasted error.
- **End:** the prompt before the next prompt that opens a new subject.

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
   words, such as related terms, synonyms or the other language. Then try
   the other agent with `--agent`. Tell the user only when these also find
   no chat.
2. Pick the chat that matches best. The topic starts at the prompt `N` that
   first raises it. To find where it ends, list the prompts of that chat
   with `recap.py --chat <id> --from N --brief`.
3. Print the topic from prompt `N` to prompt `M` with
   `recap.py --chat <id> --from N --to M`.
4. Continue with [Check and write the recap](#check-and-write-the-recap).

## Check and write the recap

1. If the project is a git repository, check the topic against git:
   - `git log --oneline --since="<date and time of prompt N>"` shows what
     was committed. The header line of `recap.py` gives the date. The prompt
     list gives the time.
   - `git status --short` on the files of the topic shows what is not
     committed.
   - Check files outside this repository in their own repository.

2. Write the recap in a few short lines:
   - **Topic:** one line.
   - **Done:** what the topic built, changed or decided, and what was
     committed.
   - **Files:** the files that the topic changed.
   - **Stopped at:** finished, waiting on the user (give the open question),
     or cut off in the middle of a step.
   - **Next:** the step that the last reply proposed. Leave this line out if
     the last reply proposed no step.

## Rules

- One topic only. No section on what came before it.
- Write the recap from the transcript and git only. Do not open source files
  for it.
- Read transcripts only through `recap.py`, never the files themselves:
  the `.jsonl` files of Claude Code or the `.db` files of the Antigravity
  CLI. They are large, and almost all of their content is tool output and
  the agent's own context.
- Say where git disagrees with the last reply, e.g. the last reply calls a change not committed, but it is committed now.
