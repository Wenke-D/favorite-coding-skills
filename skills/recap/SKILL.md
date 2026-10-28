---
name: recap
description: Recaps the last topic of a previous Claude Code chat in this project from its saved transcript, checked against git, and carries on with that work when asked. Use when the user runs /recap, asks where the last chat stopped, or wants to continue or finish it, e.g. "where were we", "catch up", "continue from last time", "上次聊到哪了", "接着上个对话", "把上次的任务做完", or refers to something from an earlier chat that is not in the current context. Use it instead of reading the .jsonl transcripts under ~/.claude/projects.
---

# Recap

Bring the user back to where a previous chat stopped, on one topic: the
chat's last, unless the user names another. Earlier topics stay out of the
recap. When the user asked to continue or finish that work, the recap is a
checkpoint and the work goes on in the same turn.

## Steps

1. List the last chat's prompts, numbered, with `recap.py` from this skill's
   base directory:

   ```sh
   python3 <skill base directory>/recap.py
   ```

   When the user means an older chat, or the listed chat is plainly not the
   one they mean, run it with `--list` for the recent chats and their ids,
   then add `--chat <id>` here and in step 3. Several chats can run
   at once, and the last one is the one written to most recently. If the
   skill was invoked with an argument, a hex prefix is a chat id and
   anything else names the topic to look for.

2. Find where the topic starts. If the user named a topic, it starts at the
   prompt that first raises it. Otherwise read the prompts from the bottom
   up and stop at the latest one that opens a new subject: a new task or
   question, "regarding X", "now let's ...", "next". Short follow-ups ("yes,
   do it", "ok", "also ...", a correction, a pasted error) belong to the
   topic above them. If the last prompt opens a new subject, the topic is
   that prompt alone.

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

6. Then go by what the user asked for:
   - Where things stopped ("where were we", "上次聊到哪了", a bare
     `/recap`): stop and let the user say what to do. Don't start the next
     step.
   - To continue or finish the work ("continue from last time", "接着上次的",
     "把上次的任务做完"): go on with **Next** in the same turn, as with any
     other task.

## Rules

- One topic only. No section on what came before it.
- The recap comes from the transcript and git alone; open source files only
  once you go on with the work.
- Read transcripts only through `recap.py`, never the `.jsonl` files
  themselves: they run to megabytes, almost all of it tool output.
- Say where git disagrees with the last reply, e.g. something it called
  uncommitted has been committed since.
- Save no memory. Ongoing progress is what /recap is for; memory is for
  milestones and lasting decisions.
