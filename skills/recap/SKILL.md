---
name: recap
description: Recaps one topic of a previous Claude Code chat in this project, so that the current chat has its context. Use when the user wants to catch up on a topic from an earlier chat, or on how far it got. Use it instead of reading the project's .jsonl transcripts.

---

# Recap

Give the current chat the context of one topic from a previous chat.

## Steps

`recap.py` is in this skill's base directory. Run it as
`python3 <skill base directory>/recap.py`.

1. Run `recap.py`. The command depends on what the user names:

   - **No topic:** run `recap.py` with no options. It shows the last chat:
     up to 15 prompts, one line each, then the last two turns in detail.
     The target is the last topic of that chat.
   - **A topic:** run `recap.py --search '<pattern>'`. The pattern is a
     regex, case-insensitive. The output gives the earlier chats whose
     prompts, title or changed files match, newest first, with the
     matching prompts. If no chat matches, try other words, such as
     synonyms or the other language, before you tell the user. The target
     is the topic in the chat that matches best.

   If the skill was invoked with an argument, the argument names a topic.

2. Find the prompts of the topic. A prompt that opens a new subject starts a
   topic: a new task or question, "regarding X", "now let's ...", "next".
   Short follow-ups belong to the topic above them: "yes, do it", "ok",
   "also ...", a correction, a pasted error.
   - For a named topic, the topic starts at the prompt that first raises it.
     It ends before the next prompt that opens a new subject.
   - For the last topic, read the prompts from the bottom up. Stop at the
     latest prompt that opens a new subject. If the last prompt opens a new
     subject, the topic is that prompt alone. If the topic starts before
     the listed prompts, list the earlier ones with
     `recap.py --from 1 --to <K> --brief`.

3. Print the topic in detail, from prompt `N` to prompt `M`. Skip this step
   when the two turns that step 1 shows in detail hold the whole topic.

   ```sh
   python3 <skill base directory>/recap.py [--chat <id>] --from N [--to M]
   ```

   Without `--to`, the output runs to the end of the chat. Add `--full` when
   the replies do not show where the work stopped: it prints each turn
   without clipping, with every text and one line for each tool call.

4. If the project is a git repository, check the topic against git:
   - `git log --oneline --since="<date and time of prompt N>"` shows what
     was committed. The header line of `recap.py` gives the date. The prompt
     list gives the time.
   - `git status --short` on the files of the topic shows what is not
     committed.
   - Check files outside this repository in their own repository.

5. Write the recap in a few short lines:
   - **Topic:** one line.
   - **Done:** what the topic built, changed or decided, and what was
     committed.
   - **Files:** the files that the topic changed.
   - **Stopped at:** finished, waiting on the user (give the open question),
     or cut off in the middle of a step.
   - **Next:** the step that the last reply proposed. Leave this line out if
     the last reply proposed no step.

The skill ends with the recap. If the user's message also asks for work, for
example "接着上次的做完", do that work as with any other request, with the
recap as context.

## Rules

- One topic only. No section on what came before it.
- Write the recap from the transcript and git only. Do not open source files
  for it.
- Read transcripts only through `recap.py`, never the `.jsonl` files
  themselves. They are megabytes in size, and almost all of it is tool
  output.
- Say where git disagrees with the last reply, e.g. the last reply calls a
  change not committed, but it is committed now.
- Save no memory. Ongoing progress is what recap is for. Memory is for
  milestones and lasting decisions.
