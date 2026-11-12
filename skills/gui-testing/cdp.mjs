#!/usr/bin/env node
// A command-line client for the Chrome DevTools Protocol: one command per run.
//
//   cdp.mjs <port> targets
//   cdp.mjs <port>[/<target>] shot <out.png> [--selector <css>] [--full]
//   cdp.mjs <port>[/<target>] eval <expression>
//   cdp.mjs <port>[/<target>] click <x> <y> [--count <n>] [--right]
//   cdp.mjs <port>[/<target>] type <text>
//   cdp.mjs <port>[/<target>] key <key> [--meta] [--shift] [--alt] [--ctrl]
//   cdp.mjs <main port> electron-window <out.png> [<window id>]
//
// <target> is a substring of a page's URL or title; without it, the first page is used.
// <port> may be the main-process inspector of an app started by electron-background.sh;
// there, eval runs in the main process and electron-window draws a whole window.
import { writeFileSync } from 'node:fs';

const [where, command, ...rest] = process.argv.slice(2);
const [port, filter] = where.split(/\/(.*)/s);

const valued = new Set(['selector', 'count']);
const flags = {};
const positional = [];
for (let i = 0; i < rest.length; i++) {
  const name = rest[i].startsWith('--') ? rest[i].slice(2) : null;
  if (name === null) positional.push(rest[i]);
  else flags[name] = valued.has(name) ? rest[++i] : true;
}
const flag = name => flags[name];

const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();

if (command === 'targets') {
  for (const t of targets) console.log(`${t.type}\t${t.title}\t${t.url}`);
  process.exit(0);
}

const target = targets.find(t => (t.type === 'page' || t.type === 'node') && (!filter || t.url.includes(filter) || t.title.includes(filter)));
if (!target) throw new Error(`no page matches ${filter ?? '(any)'} on port ${port}`);

const ws = new WebSocket(target.webSocketDebuggerUrl);
const pending = new Map();
let nextId = 0;
ws.onmessage = e => {
  const m = JSON.parse(e.data);
  const done = pending.get(m.id);
  if (!done) return;
  pending.delete(m.id);
  m.error ? done.reject(new Error(m.error.message)) : done.resolve(m.result);
};
await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
const send = (method, params = {}) => new Promise((resolve, reject) => {
  pending.set(++nextId, { resolve, reject });
  ws.send(JSON.stringify({ id: nextId, method, params }));
});

async function evaluate(expression) {
  const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true, includeCommandLineAPI: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description ?? r.exceptionDetails.text);
  return r.result.value;
}

const keys = {
  Enter: 13, Backspace: 8, Tab: 9, Escape: 27, Delete: 46, Space: 32,
  ArrowLeft: 37, ArrowUp: 38, ArrowRight: 39, ArrowDown: 40, Home: 36, End: 35, PageUp: 33, PageDown: 34,
};

// On macOS, Chromium edits text for a key only when the key event names the editing command.
// Keys are written as modifiers in the order Alt, Ctrl, Meta, Shift, then the key.
const macCommands = {
  Backspace: 'deleteBackward', Delete: 'deleteForward', Enter: 'insertNewline', Tab: 'insertTab', Escape: 'cancelOperation',
  ArrowLeft: 'moveLeft', ArrowRight: 'moveRight', ArrowUp: 'moveUp', ArrowDown: 'moveDown',
  'Shift+ArrowLeft': 'moveLeftAndModifySelection', 'Shift+ArrowRight': 'moveRightAndModifySelection',
  'Shift+ArrowUp': 'moveUpAndModifySelection', 'Shift+ArrowDown': 'moveDownAndModifySelection',
  'Alt+ArrowLeft': 'moveWordLeft', 'Alt+ArrowRight': 'moveWordRight', 'Alt+Backspace': 'deleteWordBackward',
  'Meta+ArrowLeft': 'moveToBeginningOfLine', 'Meta+ArrowRight': 'moveToEndOfLine',
  'Meta+ArrowUp': 'moveToBeginningOfDocument', 'Meta+ArrowDown': 'moveToEndOfDocument', 'Meta+Backspace': 'deleteToBeginningOfLine',
  'Meta+a': 'selectAll', 'Meta+c': 'copy', 'Meta+x': 'cut', 'Meta+v': 'paste', 'Meta+z': 'undo', 'Meta+Shift+z': 'redo',
};

const commands = {
  async shot(out) {
    const selector = flag('selector');
    const params = { format: 'png' };
    if (selector) {
      const r = await evaluate(`(() => { const r = document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect(); return { x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height } })()`);
      Object.assign(params, { clip: { ...r, scale: 1 }, captureBeyondViewport: true });
    } else if (flag('full')) {
      params.captureBeyondViewport = true;
      const m = await send('Page.getLayoutMetrics');
      params.clip = { x: 0, y: 0, width: m.cssContentSize.width, height: m.cssContentSize.height, scale: 1 };
    }
    writeFileSync(out, Buffer.from((await send('Page.captureScreenshot', params)).data, 'base64'));
    console.log(out);
  },

  async eval(expression) {
    const value = await evaluate(expression);
    console.log(typeof value === 'string' ? value : JSON.stringify(value, null, 2));
  },

  async click(x, y) {
    const clickCount = Number(flag('count') ?? 1);
    const button = flag('right') ? 'right' : 'left';
    const at = { x: Number(x), y: Number(y) };
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', ...at });
    for (let n = 1; n <= clickCount; n++) {
      await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...at, button, clickCount: n });
      await send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...at, button, clickCount: n });
    }
  },

  async type(text) {
    await send('Input.insertText', { text });
  },

  async key(key) {
    const held = ['alt', 'ctrl', 'meta', 'shift'].filter(flag);
    const modifiers = held.reduce((sum, m) => sum | { alt: 1, ctrl: 2, meta: 4, shift: 8 }[m], 0);
    const command = macCommands[[...held.map(m => m[0].toUpperCase() + m.slice(1)), key].join('+')];
    const name = key === 'Space' ? ' ' : key;
    const code = keys[key] ?? key.toUpperCase().charCodeAt(0);
    const text = name.length === 1 && !(modifiers & 6) ? name : key === 'Enter' ? '\r' : undefined;
    const event = { key: name, windowsVirtualKeyCode: code, modifiers, text };
    await send('Input.dispatchKeyEvent', { type: text ? 'keyDown' : 'rawKeyDown', ...event, commands: command ? [command] : [] });
    await send('Input.dispatchKeyEvent', { type: 'keyUp', ...event, text: undefined });
  },

  async 'electron-window'(out, id) {
    const data = await evaluate(`electronBackground.shot(${id === undefined ? '' : Number(id)})`);
    writeFileSync(out, Buffer.from(data, 'base64'));
    console.log(out);
  },
};

if (!commands[command]) throw new Error(`unknown command ${command}`);
await commands[command](...positional);
ws.close();
