---
name: typst-assistant
description: Watches the .typ files of a Typst project for "// @ai" notes that the user writes beside a line. Does what each note asks, renders the page to check the result, and answers in the file under the note. Use when the user wants to give feedback on Typst slides or documents in the source instead of the chat. Also use when the user runs /typst-assistant or asks to start the note watcher, e.g. "开批注监听", "看批注", "I'll comment in the source", "set up the listener like yesterday".
---

# Typst assistant

The user writes a note beside a line of a `.typ` file and saves the file:

```typst
- Our solver scales to 4k GPUs  // @ai too strong, soften it
```

A watcher sends each new note to this session. You do what the note asks
and answer in the file, under the note. Each discussion stays beside the
text it is about.

## Steps

1. Find the project: the folder with the `main.typ` of the file the user has
   open, or the folder the user names. Note the folders that hold cut or
   unused material, such as `dropped/`.

2. Start the watcher with the Monitor tool and `timeout_ms` 1800000, the
   maximum:

   ```sh
   <skill base directory>/watch-notes.sh <project folder> [<folder to skip> ...]
   ```

   It prints each new note as `path:line:text`, 2 seconds after the files
   stop changing. Notes already in the files come first. After `@ai`, it
   accepts a space, `:` or `：`, in any letter case.

3. Tell the user in a few lines how to write a note, with the example above.
   A follow-up is a new `// @ai` line under your answer. The user tells you
   when the notes are done.

4. For each note, from the top of the file:
   1. Read the file around the line. A note can continue on the comment
      lines under it.
   2. Do what the note asks. Answer a question. If the note is not clear,
      ask in your answer and change nothing.
   3. If you changed the document, render the page and look at it (see
      Render and check).
   4. Change `// @ai <note>` to `// Q: <note>`, so that the watcher does not
      send it again. On the next line, at the indent of the note's line,
      write `// ↳ AI: <answer>`. Continue a long answer on more `//` lines.
   5. In the chat, write one or two lines with a link to your answer. The
      answer itself goes in the file.

5. When the watcher expires, start it again with the same command. After
   three expiries in a row with no notes, stop. A note sets the count back
   to zero. Tell the user to say
   "开批注监听" when they want it again.

6. When the user says the notes are done, remove each `// Q:` comment and
   the comment lines under it that continue the note or the answer. If a
   `// Q:` comment follows code on the same line, remove only the comment.

## Render and check

After each change, render the changed page and look at it before you
answer.

1. Find the page. In a slide deck, this command lists each heading with its
   page:

   ```sh
   typst eval --in main.typ '{ let t(c) = if c.has("text") { c.text } else if c.has("children") { c.children.map(t).join() } else { " " }; query(heading).map(h => str(h.location().page()) + " " + t(h.body)).join("\n") }' --format yaml
   ```

   If `typst eval` is not available, count the pages before the slide.

2. Render that page into the scratchpad, then read the PNG. Typst writes
   the page number, padded with zeros, in place of `{0p}`:

   ```sh
   typst compile main.typ <scratchpad>/p{0p}.png --pages <n> --ppi 160
   ```

3. Check that text and code are readable, with enough contrast. Check for
   content outside the page, bad alignment and large empty areas. Fix what
   you see and render again.

4. Make sure that the compile gives no new errors or warnings.

## Rules

- In a raw block (between backtick fences), `//` is not a comment, so a
  note there shows on the page. Put the `// Q:` and `// ↳ AI:` lines above
  the block, and remove the note from the block.
- If the change removes the note's file from the document, write the
  `// Q:` and `// ↳ AI:` lines where the file was included.
- Follow the layout rules in the project's CLAUDE.md and memory.
- Do not start `caffeinate` for the watcher. The user writes notes only
  while the Mac is awake, so sleep loses no notes.
- The watcher runs only while this session is open.
