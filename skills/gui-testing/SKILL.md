---
name: gui-testing
description: Looks at and drives GUI apps on this Mac without disturbing the user, who keeps working on the same screen. Takes screenshots of web pages, Electron apps and windows of any app, and clicks and types in pages over the Chrome DevTools Protocol. Use whenever you need to see how a change looks, check a layout or render, or test a UI by hand, e.g. "截个图看看", "看看效果", "跑起来看一下", "check the rendering", "take a screenshot of the window", "test it in the app".
---

# GUI testing

The user works on the same Mac while you test. So:

- Never move the real mouse, send real key events, or bring an app to the front.
- Do not use AppleScript `activate`, `keystroke` or `click`. Use `open` only with `-g`.
- When you start an app for a test, give it its own data folder in your scratchpad. Never open the user's own profile or documents in it.
- An app that the user already runs is theirs. Only take screenshots of it.
- Stop every process you start when you are done.
- Look at a screenshot with the Read tool.

The commands below use two names:

```sh
G=~/.claude/skills/gui-testing   # the scripts of this skill
S=<your scratchpad directory>    # all test data and screenshots
```

## Pick the method

| What you test | Method |
| --- | --- |
| A web page, an HTML file, a dev server | Headless Chrome and `cdp.mjs` |
| An Electron app that you run from its source folder | `electron-background.sh` and `cdp.mjs` |
| Any other window: a native app, a packaged Electron app, PowerPoint, a PDF viewer | `window-shot.sh`, screenshots only |

The first two render with the macOS fonts, as the user sees them. Do not use a Linux container to check a layout: it has other fonts and another text renderer.

## Web pages: headless Chrome

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --remote-debugging-port=9444 --user-data-dir=$S/chrome \
  --window-size=1280,800 --force-device-scale-factor=2 <url> >$S/chrome.log 2>&1 &
chrome=$!
until curl -sf localhost:9444/json/version >/dev/null; do sleep 0.2; done
$G/cdp.mjs 9444 shot $S/page.png
kill $chrome
```

Headless Chrome has no window and does not take focus. Before a screenshot, wait for the page: `eval` a promise that resolves when the page is ready, e.g. `document.fonts.ready.then(() => 1)`.

## Electron apps: background mode

```sh
$G/electron-background.sh <app folder> [app arguments...]
# pid=28614 pages=50215 main=50216 log=/var/folders/.../electron-background.XXXX.log
```

The script starts the app with the Electron in its `node_modules`, or with the binary in `ELECTRON`, and preloads `electron-background.cjs`. It passes the app arguments unchanged and returns when both ports answer. `pages` is the CDP port of the app's pages. `main` is the inspector port of the main process. Give the app its own data folder, e.g. `--user-data-dir=$S/ud` if the app accepts it. When you are done, run `kill <pid>`.

In background mode:

- The app never becomes active and has no Dock icon. Its windows are fully transparent and let clicks through, so the user does not see them.
- Pages still render and run timers at full speed, and `document.hasFocus()` is true. So UI that needs focus, such as a popup that opens on focus, works.
- Native dialogs do not open. A message box gets the next answer that you queued. Without one, it gets the answer of the Escape key: `cancelId`, else the first button labeled "Cancel" or "No", else 0. Open and save dialogs are canceled. The log shows each dialog.
- Popup menus do not open. You read and click them from the main process.
- `shell.openExternal`, `openPath`, `showItemInFolder` and notifications do nothing. `electronBackground.state.opened` records them.

Limits:

- It works only for an app that you start from its source folder: `-r` is a flag of Electron's default app. A packaged app (`/Applications/X.app`) has no default app. Use `window-shot.sh` for it.
- The application menu in the menu bar and the tray are not stubbed. Call their actions from the main process instead.

Run these in the main process with `$G/cdp.mjs <main> eval '<expression>'`:

| Expression | What it does |
| --- | --- |
| `electronBackground.windows()` | Returns `[{id, title, bounds, views: [{url, x, y, width, height}]}]`. `x` and `y` are the offset of each page view in the window, in CSS pixels |
| `electronBackground.answer({response: 0})` | Queues the answer for the next dialog. For a message box, `response` is the index of the button. A save dialog takes `{canceled: false, filePath}`, an open dialog `{canceled: false, filePaths}` |
| `electronBackground.state.dialogs` | Returns each dialog shown so far, with its options and answer |
| `electronBackground.menu()` | Returns the labels of the last popup menu, with submenus |
| `electronBackground.clickMenu('Copy')`, `clickMenu('Format', 'Bold')` | Clicks an item of the last popup menu by its label path |
| `process.mainModule.require('electron')` | Gives the Electron API, for anything else |

`$G/cdp.mjs <main> electron-window <out.png> [window id]` draws a whole window, all page views in place, as the user would see it without the transparency. It reads the pages, not the screen. Without a window id, it draws the first window.

## Pages: cdp.mjs

`<port>/<target>` selects the page whose URL or title contains `<target>`. Without `/<target>`, the first page is used. `$G/cdp.mjs <port> targets` lists the pages.

```sh
$G/cdp.mjs <port> targets
$G/cdp.mjs <port>/<target> shot <out.png> [--selector <css>] [--full]
$G/cdp.mjs <port>/<target> eval '<expression>'          # a promise is awaited
$G/cdp.mjs <port>/<target> click <x> <y> [--count 2] [--right]
$G/cdp.mjs <port>/<target> type '<text>'
$G/cdp.mjs <port>/<target> key <key> [--meta] [--shift] [--alt] [--ctrl]
```

- `click` takes CSS pixels in the coordinates of that page. In an Electron window with several page views, each view has its own origin. To go from a point in an `electron-window` image to a click: divide by the screen scale (usually 2), then subtract the offset of the view from `electronBackground.windows()`.
- Get the coordinates of an element with `eval`, e.g. `document.querySelector('h1').getBoundingClientRect()`. Do not guess them from a screenshot.
- A `click` focuses the element under it, as a real click does.
- `type` inserts text as an input method does, and replaces the selection. It works for Chinese.
- `key` takes a key name, such as `Enter`, `Escape`, `Tab`, `Backspace`, `ArrowUp`, `End`, `Space` or `a`. It runs the macOS editing command of the key, e.g. `key a --meta` selects all and `key z --meta --shift` redoes. The table `macCommands` in `cdp.mjs` lists the commands. A page that handles a key itself, such as a ProseMirror editor, gets the key event too.
- A context menu that the page draws in HTML is part of the page. Click its items with `click`. Only native popup menus of an Electron app need `clickMenu`.

## Any window: window-shot.sh

```sh
swift $G/windows.swift [app] [title]                     # id, app, title, on screen, size
$G/window-shot.sh <out.png> <window id | app name> [title]
```

`window-shot.sh` captures one window with `screencapture -l` and does not activate the app. An app name matches the shown name (文本编辑) or the bundle name (TextEdit). With an app name, it captures the first window that `windows.swift` lists: on-screen windows come first, then the largest. To open a file in an app without bringing it to the front, use `open -g -a <App> <file>`. If the test needs clicks or keys in a native app, ask the user first: real input interrupts their work.

This needs Screen Recording permission for the app that runs the shell, e.g. Visual Studio Code. When `windows.swift` shows empty titles, the permission is missing, and `screencapture` fails. Only the user can give the permission, in System Settings > Privacy & Security > Screen Recording, and the app must then restart. Ask the user once. Do not open System Settings yourself.

On recent macOS, the first `screencapture` after the permission also shows a dialog that asks to let the app bypass the system window picker. Tell the user to allow it; macOS can ask again later.

Do not control other apps with AppleScript `tell`, e.g. to minimize a window or close a document. It shows the user a dialog that asks to let VS Code control that app.
