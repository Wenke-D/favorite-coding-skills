---
name: typst-assistant
description: Watches a Typst project's .typ files for "// @ai" comments written beside a line. Performs what each note asks, renders the affected page to verify the result, and replies directly in the file under the note. Use when the user wants to give feedback on Typst slides or documents inside the source instead of chat, or when they run /typst-assistant or ask to start the note watcher, e.g. "开批注监听", "看批注", "I'll comment in the source", "set up the listener like yesterday".
---

# Typst assistant

The user writes a note beside a line in a `.typ` file and saves it:

```typst
- Our solver scales to 4k GPUs  // @ai too strong, soften it
```

A background watcher sends each new note to this session. You act on the note and reply directly in the file below it, keeping every discussion next to the text it refers to.

## Steps

1. Locate the project: the folder containing `main.typ` for the file the user has open, or the folder the user specifies. Note any folders for cut or unused material, such as `dropped/`.

2. Start the watcher using the Monitor tool with `timeout_ms` set to `1800000` (the maximum):

   ```sh
   <skill base directory>/watch-notes.sh <project folder> [<folder to skip> ...]
   ```

   It prints each new note as `path:line:text`, 2 seconds after file edits settle. Existing notes are printed first. After `@ai`, it accepts a space, `:`, or `：` (case-insensitive).

3. Tell the user in a few lines how to leave a note, including the example above. Explain that they can follow up with a new `// @ai` line below your reply, and let you know when they are done.

4. For each note, working from the top of the file downward:
   1. Read the surrounding lines in the file. A note may continue across subsequent comment lines.
   2. Act on the note or answer the question. If the note is unclear, ask for clarification in your reply without editing the document.
   3. If you edited the document, render the affected page and inspect it (see Render and check).
   4. Change `// @ai <note>` to `// Q: <note>` so the watcher does not report it again. On the next line, matching the note's indentation, write `// ↳ AI: <answer>`. Wrap long answers across additional `//` lines.
   5. In the chat, post a one- or two-line summary with a link to your reply; keep the full answer in the file.

5. When the watcher times out, restart it with the same command. Stop after three consecutive timeouts with no notes (any note resets the count to zero), and let the user know they can say `"开批注监听"` whenever they want to restart it.

6. When the user says they are done, remove every `// Q:` comment along with any continuation lines for the note or reply. If `// Q:` sits at the end of a code line, remove only the comment.

## Render and check

After every edit, render the changed page and visually inspect it before replying.

1. Find the page number. In a slide deck, this command lists each heading with its page:

   ```sh
   typst eval --in main.typ '{ let t(c) = if c.has("text") { c.text } else if c.has("children") { c.children.map(t).join() } else { " " }; query(heading).map(h => str(h.location().page()) + " " + t(h.body)).join("\n") }' --format yaml
   ```

   If `typst eval` is unavailable, count the pages preceding the slide.

2. Render that page into the scratchpad, then open the PNG. Typst substitutes the zero-padded page number for `{0p}`:

   ```sh
   typst compile main.typ <scratchpad>/p{0p}.png --pages <n> --ppi 160
   ```

3. Verify that text and code are readable with adequate contrast, and check for overflow, misalignment, or awkward empty space. Fix any issues and re-render.

4. Verify that compiling produces no new errors or warnings.

## Rules

- Inside a raw block (between backtick fences), `//` is not a comment, so a note there would render on the page. Place the `// Q:` and `// ↳ AI:` lines above the block and remove the note from inside it.
- If an edit removes the note's file from the document, place the `// Q:` and `// ↳ AI:` lines where the file was included.
- Follow the layout rules in the project's `CLAUDE.md` and memory.
- Do not run `caffeinate` for the watcher. The user only writes notes while the Mac is awake, so sleep loses nothing.
- The watcher only runs while this session remains open.
