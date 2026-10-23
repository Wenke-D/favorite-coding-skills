---
name: recap
description: Catch up on the last topic of the previous Claude Code chat in this project - reads that chat's saved transcript, finds where its last topic began, and recaps only that topic (what was asked, what was done or decided, where it stopped, what comes next), checked against git. Use when the user runs /recap or opens a chat with "where were we", "catch up", "recap the last chat" or "continue from last time". Read-only; it saves no memory.
---

# Recap

Bring the user back to where the last chat stopped, on its last topic only.
Earlier topics of that chat stay out of the recap.

## Steps

1. List the last chat's prompts, numbered, with `recap.py` from this skill's
   base directory:

   ```sh
   python3 <skill base directory>/recap.py
   ```

   Add `--back 2` (3, ...) when the user means an older chat, or when the
   listed chat is plainly not the one they mean: several chats can run at
   once, and the last one is the one written to most recently.

2. Find where the last topic starts. Read the prompts from the bottom up and
   stop at the latest one that opens a new subject: a new task or question,
   "regarding X", "now let's ...", "next". Short follow-ups ("yes, do it",
   "ok", "also ...", a correction, a pasted error) belong to the topic above
   them. If the last prompt opens a new subject, the topic is that prompt
   alone.

3. Print that topic in detail, `N` being the prompt it starts at:

   ```sh
   python3 <skill base directory>/recap.py --from N
   ```

4. Check it against git: `git log --oneline --since="<topic start>"` for what
   was committed, and `git status --short` on the topic's files for what is
   still uncommitted. Files outside this repository get the same check in
   their own repository.

5. Write the recap in a few short lines:
   - **Topic:** one line.
   - **Done:** what was built, changed or decided, and what got committed.
   - **Stopped at:** finished, waiting on the user (give the open question),
     or cut off mid-step.
   - **Next:** the step the last reply proposed, or the one that plainly
     follows.

   Then stop and let the user say what to do. Don't start the next step.

## Rules

- Only the last topic. No section on what came before it.
- The transcript and git are the sources; don't open source files.
- Say where git disagrees with the last reply, e.g. something it called
  uncommitted has been committed since.
- Save no memory. Ongoing progress is what /recap is for; memory is for
  milestones and lasting decisions.
