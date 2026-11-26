---
name: gui-testing
description: Inspects and drives GUI apps on this Mac without disturbing the user, who keeps working on the same screen. Takes screenshots of web pages, Electron apps, and any app window, and clicks and types in pages over the Chrome DevTools Protocol. Use whenever you need to see how a change looks, check a layout or render, or manually test a UI, e.g. "截个图看看", "看看效果", "跑起来看一下", "check the rendering", "take a screenshot of the window", "test it in the app".
---

# GUI testing

The user is working on the same Mac while you test, so:

- Never move the real mouse, send real key events, or bring an app to the front.
- Do not use AppleScript `activate`, `keystroke`, or `click`. Use `open` only with `-g`.
- When starting an app for testing, give it its own data folder inside your scratchpad. Never open the user's own profile or documents in it.
- An app the user is already running belongs to them. Only take screenshots of it.
- Stop every process you start when you are done.
- Inspect screenshots with the Read tool.

The commands below use two variables:

```sh
G=~/.claude/skills/gui-testing   # this skill's scripts
S=<your scratchpad directory>    # all test data and screenshots
```

## Choosing a method

| What you are testing | Method |
| --- | --- |
| A web page, HTML file, or dev server | Headless Chrome and `cdp.mjs` |
| An Electron app launched from its source folder | `electron-background.sh` and `cdp.mjs` |
| Any other window: a native app, packaged Electron app, PowerPoint, or PDF viewer | `window-shot.sh`, screenshots only |

The first two render with macOS fonts, matching what the user sees. Do not use a Linux container to check a layout, as its fonts and text renderer differ.

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

Headless Chrome opens no window and never steals focus. Before taking a screenshot, wait for the page to finish loading by evaluating a promise that resolves when ready, e.g. `document.fonts.ready.then(() => 1)`.

## Electron apps: background mode

```sh
$G/electron-background.sh <app folder> [app arguments...]
# pid=28614 pages=50215 main=50216 log=/var/folders/.../electron-background.XXXX.log
```

The script launches the app using Electron from its `node_modules` (or the binary in `ELECTRON`), preloading `electron-background.cjs`. It forwards the app arguments unchanged and returns once both ports respond. `pages` is the CDP port for the app's pages, and `main` is the inspector port for the main process. Give the app its own data folder (e.g. `--user-data-dir=$S/ud` if supported). When done, stop it with `kill <pid>`.

In background mode:

- The app never activates and shows no Dock icon. Its windows are fully transparent and pass clicks through, so the user does not see or hit them.
- Pages still render and run timers at full speed, and `document.hasFocus()` stays `true`, so focus-dependent UI (such as popups that open on focus) works normally.
- Native dialogs do not open. A message box receives the next queued response; if none is queued, it falls back to the Escape-key default (`cancelId`, otherwise the first button labeled "Cancel" or "No", otherwise `0`). Open and save dialogs are canceled automatically. Every dialog is logged.
- Popup menus do not open; inspect and click them from the main process instead.
- `shell.openExternal`, `openPath`, `showItemInFolder`, and notifications are no-ops, recorded in `electronBackground.state.opened`.

Limits:

- This only works when launching an app from its source folder: `-r` is a flag on Electron's default app. A packaged app (`/Applications/X.app`) has no default app, so use `window-shot.sh` instead.
- The menu bar application menu and system tray are not stubbed; invoke their actions from the main process instead.

Run these in the main process with `$G/cdp.mjs <main> eval '<expression>'`:

| Expression | What it does |
| --- | --- |
| `electronBackground.windows()` | Returns `[{id, title, bounds, views: [{url, x, y, width, height}]}]`. `x` and `y` are each page view's offset inside the window in CSS pixels |
| `electronBackground.answer({response: 0})` | Queues the response for the next dialog. For a message box, `response` is the button index. A save dialog takes `{canceled: false, filePath}`, and an open dialog takes `{canceled: false, filePaths}` |
| `electronBackground.state.dialogs` | Returns every dialog shown so far, with its options and response |
| `electronBackground.menu()` | Returns the labels of the last popup menu, including submenus |
| `electronBackground.clickMenu('Copy')`, `clickMenu('Format', 'Bold')` | Clicks an item in the last popup menu by its label path |
| `process.mainModule.require('electron')` | Exposes the Electron API for anything else |

`$G/cdp.mjs <main> electron-window <out.png> [window id]` composites a full window with all page views in place, as the user would see it without transparency. It captures the pages directly rather than the screen. Without a window id, it captures the first window.

## Pages: cdp.mjs

`<port>/<target>` selects the page whose URL or title contains `<target>`. Without `/<target>`, the first page is used. `$G/cdp.mjs <port> targets` lists available pages.

```sh
$G/cdp.mjs <port> targets
$G/cdp.mjs <port>/<target> shot <out.png> [--selector <css>] [--full]
$G/cdp.mjs <port>/<target> eval '<expression>'          # awaits promises
$G/cdp.mjs <port>/<target> click <x> <y> [--count 2] [--right]
$G/cdp.mjs <port>/<target> type '<text>'
$G/cdp.mjs <port>/<target> key <key> [--meta] [--shift] [--alt] [--ctrl]
```

- `click` takes CSS pixel coordinates relative to that page. In an Electron window with multiple page views, each view has its own origin. To convert a point in an `electron-window` screenshot to a click coordinate, divide by the screen scale (usually 2), then subtract the view's offset from `electronBackground.windows()`.
- Get element coordinates via `eval` (e.g. `document.querySelector('h1').getBoundingClientRect()`) instead of guessing from a screenshot.
- `click` focuses the element under it, just like a real click.
- `type` inserts text like an input method and replaces the current selection. It supports Chinese input.
- `key` takes a key name such as `Enter`, `Escape`, `Tab`, `Backspace`, `ArrowUp`, `End`, `Space`, or `a`. It triggers the key's macOS editing command. For example, `key a --meta` selects all and `key z --meta --shift` redoes (see `macCommands` in `cdp.mjs`). Pages that handle keys directly, such as ProseMirror editors, receive the key event as well.
- HTML-rendered context menus are part of the page; click their items with `click`. Only native Electron popup menus need `clickMenu`.

## Any window: window-shot.sh

```sh
swift $G/windows.swift [app] [title]                     # id, app, title, on screen, size
$G/window-shot.sh <out.png> <window id | app name> [title]
```

`window-shot.sh` captures a single window with `screencapture -l` without activating the app. An app name matches either the display name (文本编辑) or the bundle name (TextEdit). Given an app name, it captures the first window listed by `windows.swift` (on-screen windows first, then largest). To open a file in an app without bringing it to the front, run `open -g -a <App> <file>`. If a test requires clicking or typing in a native app, ask the user first, since real input interrupts their work.

This requires Screen Recording permission for the app running the shell (e.g. Visual Studio Code). If `windows.swift` outputs empty titles, permission is missing and `screencapture` will fail. Only the user can grant it (in System Settings > Privacy & Security > Screen Recording), after which the app must restart. Ask the user once; do not open System Settings yourself.

On recent macOS versions, the first `screencapture` after granting permission also displays a dialog asking to let the app bypass the system window picker. Ask the user to allow it; macOS may prompt again later.

Do not control other apps with AppleScript `tell` (for example, to minimize a window or close a document); it triggers a permission prompt asking to let VS Code control that app.
