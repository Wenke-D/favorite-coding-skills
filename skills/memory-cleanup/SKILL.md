---
name: memory-cleanup
description: Prunes this project's memory folder (the file memory of Claude Code, also used from the Antigravity CLI) down to what the code and docs do not already record, then fixes its links and MEMORY.md index. Use when the user runs /memory-cleanup or asks to clean up, tidy, prune, shrink, or review memory, e.g. "清理一下 memory", "整理记忆", "memory 太乱了", or says memories are stale, duplicated, or wrong.
---

# Memory cleanup

Memory should store only what the code and docs cannot already tell you:

- the user's preferences and working rules;
- the rationale behind decisions that might otherwise be reversed;
- facts outside the repos: machines, clusters, accounts, tools, and external
  systems;
- key milestones.

Everything else should be removed:

- **Progress:** dated status updates, "next", "in progress", "open", "still
  deciding", and run logs. The recap skill recovers where the last chat
  stopped; a project's own log or checklist tracks the rest.
- **Facts already established by code or docs:** how a system is built, where a
  dependency comes from, which flags a script passes, or what a README already
  explains. Once it lives in code or docs, that is the source of truth; a
  memory entry only duplicates it or drifts out of date.
- **History:** file moves, renames, superseded designs, commit hashes, and
  "since `<date>`" notes.
- **Stale facts:** paths, names, and setups that are no longer accurate.

## Which memory

The memory is a folder of Markdown files, one memory in each file, with an
index in `MEMORY.md`. Claude Code keeps one such folder for each project.
The Antigravity CLI keeps no memory folder of its own. When this skill runs
in the Antigravity CLI, it works on the Claude Code memory of the same
project. `memory_check.py` finds that folder from the current directory. If
the user names a different folder, give it to `memory_check.py` as its
argument. If there is no folder, tell the user and stop.

## Steps

1. **Check** the memory with `memory_check.py`, in the folder of this
   `SKILL.md` file:

   ```sh
   python3 <that folder>/memory_check.py
   ```

   Its first line gives the path of the memory folder. It then lists every
   memory and flags broken `[[links]]`, mismatches between index lines and
   files, paths that no longer exist, and wording that looks like progress or
   history. Treat these flags as hints: a path on a remote machine or relative
   to another repo will appear missing, and "the next step" inside an
   explanation is not a progress update.

2. **Back up** that folder into a temporary folder: your scratchpad if you
   have one, otherwise a new folder from `mktemp -d`. For example,
   `cp -r <memory dir> <scratchpad>/memory-backup-<date>`.

3. **Read every memory in full**, not just the index.

4. **Verify each entry against the repos.** Before dropping a detail because
   code or docs already establish it, confirm it is actually there (grep the
   repo, read the README or comments). Before keeping a fact, verify it is
   still true: the path exists, the repo is where it says, and the tool is still
   used. Drop anything that is clearly history or progress even if it is not
   recorded elsewhere.

5. **Rewrite**, keeping one fact per memory, as concise as possible while
   remaining clear:
   - trim each memory to the rule or rationale the repo cannot show, and delete
     it if nothing remains;
   - merge memories that cover the same fact;
   - update stale facts based on what you just verified.

   Leave frontmatter `metadata` untouched; update `description`, and update
   `name` only when renaming (renaming the file to match). Repoint links that
   targeted deleted or renamed memories, keep one index line per memory in
   `MEMORY.md`, and rerun `memory_check.py` until no real issues remain.

6. **Report:** what was deleted, trimmed, merged, or fixed (one line each),
   what stayed and why (in one sentence), total size before and after, and the
   full path to the backup.

## Rules

- Open to-dos do not belong in memory either, but a to-do not recorded anywhere
  else would be lost if deleted outright. Propose moving it into the project's
  own docs (a checklist, plan, or log), and only move it once the user agrees
  since that edits a repo file. Until then, keep it in memory.
- Touch only this project's memory folder. Rule files (`CLAUDE.md`,
  `AGENTS.md`, `GEMINI.md`) and other projects' memories belong to the user
  to change.
- Do not add new memories during cleanup, except to record a rule the user
  explicitly states while it runs.
