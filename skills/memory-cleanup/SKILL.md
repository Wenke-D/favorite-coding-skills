---
name: memory-cleanup
description: Clean up this project's Claude Code memory - backs it up, then drops ongoing progress (that is /recap's job), what the code or docs already establish, history and stale facts, merges duplicates, hands open to-dos to the project's docs, and keeps only what the repos can't tell (preferences, rules, reasons, facts outside the repos, milestones); then fixes links and the MEMORY.md index. Use when the user runs /memory-cleanup or asks to clean up, tidy, prune or review memory.
---

# Memory cleanup

Memory holds only what the code and the docs can't tell:

- the user's preferences and rules for working;
- the reasons behind decisions that would otherwise be undone;
- facts outside the repos: the machine, clusters, accounts, tools, other
  people's systems;
- important milestones.

Everything else goes:

- **Progress**: dated updates, "next", "in progress", "open", "still
  deciding", logs of runs and results. `/recap` brings back where the last
  chat stopped; a project's own log or checklist keeps the rest.
- **What the code or docs already establish**: how a system is built, where
  a dependency comes from, which flags a script passes, what a README
  explains. Once the code establishes it, it is the fact, and a memory of it
  only repeats it or drifts from it.
- **History**: moves, renames, earlier designs, commit hashes, "since <date>".
- **Stale facts**: paths, names and setups that are no longer true.

## Steps

1. **Back up** the memory folder (named in your system prompt) into your
   scratchpad, e.g. `cp -r <memory dir> <scratchpad>/memory-backup-<date>`.

2. **Check** it with `memory_check.py` from this skill's base directory:

   ```sh
   python3 <skill base directory>/memory_check.py
   ```

   It lists every memory and flags broken `[[links]]`, index lines and files
   that don't match, paths that no longer exist, and wording that reads like
   progress or history. The flags are hints: a path on a remote machine or
   relative to another repo shows as missing, and "the next step" in an
   explanation is not progress.

3. **Read every memory in full**, not only the index.

4. **Judge each one against the repos.** Before dropping a detail because
   the code or docs establish it, find it there (grep the repo, read the
   README or the comment). Before keeping a fact, check it is still true:
   the path exists, the repo is where it says, the tool is still used. A
   detail nothing else records but that is plainly history or progress
   goes anyway.

5. **Rewrite**, one fact per memory, as short as it stays clear:
   - shrink a memory to the rule or reason the repo can't show; delete it
     when nothing is left;
   - merge memories that say the same thing;
   - fix stale facts from what you just checked.

   Keep the front matter's `metadata` as it is; update `description`, and
   `name` only when renaming (then rename the file too). Point a link to a
   deleted or renamed memory at its new home, keep one index line per
   memory in `MEMORY.md`, and rerun the check until it flags nothing real.

6. **Report**: what was deleted, shrunk, merged or fixed (one line each),
   what stayed and why in a sentence, the size before and after, and the
   backup's full path.

## Rules

- Open to-dos don't belong in memory either, but a to-do nothing else
  records would be lost. Propose moving it into the project's own docs (a
  checklist, plan or log), and do so only once the user agrees: that edits
  a repo file. Until then it stays in memory.
- Touch only this project's memory folder. CLAUDE.md files and other
  projects' memory are the user's to change.
- Don't add new memories during a cleanup, except to record a rule the user
  states while it runs.
