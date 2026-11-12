// Preloaded with `Electron -r` before an app's main script. Keeps the app invisible and
// never active, so it can run while the user works, and exposes `globalThis.electronBackground`
// to a CDP client on the main process (--inspect).
const { app, BaseWindow, BrowserWindow, WebContentsView, Menu, dialog, shell, Notification, nativeImage, screen } = require('electron');

for (const name of ['disable-renderer-backgrounding', 'disable-backgrounding-occluded-windows', 'disable-background-timer-throttling']) {
  app.commandLine.appendSwitch(name);
}

const keepPolicy = app.setActivationPolicy.bind(app);
keepPolicy('prohibited');
app.setActivationPolicy = () => {};
app.focus = () => {};
if (app.dock) for (const name of ['show', 'bounce']) app.dock[name] = () => {};

for (const W of [BaseWindow, BrowserWindow]) {
  W.prototype.show = function () { this.showInactive(); };
  W.prototype.focus = function () {};
  W.prototype.moveTop = function () {};
}

function hide(win) {
  win.setOpacity(0);
  win.setIgnoreMouseEvents(true);
}

// browser-window-created is emitted inside the constructor, before the next screen refresh.
app.on('browser-window-created', (_, win) => hide(win));

// Pages that check document.hasFocus() or wait for focus events behave as in a focused window.
app.on('web-contents-created', (_, contents) => {
  contents.setBackgroundThrottling(false);
  contents.on('dom-ready', () => {
    try {
      if (!contents.debugger.isAttached()) contents.debugger.attach('1.3');
      contents.debugger.sendCommand('Emulation.setFocusEmulationEnabled', { enabled: true });
    } catch (error) {
      console.error('[electron-background] focus emulation:', error.message);
    }
  });
});

const state = { dialogs: [], answers: [], menus: [], opened: [] };

function optionsOf(args) {
  return args.find(a => a && typeof a === 'object' && !(a instanceof BaseWindow)) ?? {};
}

// Each stub records the dialog, then answers with the next queued answer or with "cancel".
function stubDialog(name, cancel, sync) {
  dialog[name] = (...args) => {
    const options = optionsOf(args);
    const answer = state.answers.shift() ?? cancel(options);
    state.dialogs.push({ name, options, answer });
    console.error(`[electron-background] ${name}: ${JSON.stringify(options.message ?? options.title ?? '')} -> ${JSON.stringify(answer)}`);
    return sync ? sync(answer) : Promise.resolve(answer);
  };
}

// The answer Electron gives to Escape: cancelId, else the first button labeled "cancel" or "no", else 0.
function messageCancel(options) {
  const labeled = (options.buttons ?? []).findIndex(b => /^(cancel|no)$/i.test(b));
  return { response: options.cancelId ?? (labeled >= 0 ? labeled : 0), checkboxChecked: false };
}
stubDialog('showMessageBox', messageCancel);
stubDialog('showMessageBoxSync', messageCancel, a => a.response);
stubDialog('showOpenDialog', () => ({ canceled: true, filePaths: [] }));
stubDialog('showOpenDialogSync', () => ({ canceled: true, filePaths: [] }), a => (a.canceled ? undefined : a.filePaths));
stubDialog('showSaveDialog', () => ({ canceled: true, filePath: '' }));
stubDialog('showSaveDialogSync', () => ({ canceled: true, filePath: '' }), a => (a.canceled ? undefined : a.filePath));
stubDialog('showErrorBox', () => ({}), () => undefined);

Menu.prototype.popup = function (options = {}) {
  state.menus.push({ menu: this, options });
  console.error(`[electron-background] menu: ${this.items.map(i => i.label).filter(Boolean).join(' | ')}`);
};

for (const name of ['openExternal', 'openPath', 'showItemInFolder']) {
  shell[name] = async target => { state.opened.push({ name, target }); return ''; };
}
Notification.prototype.show = function () { state.opened.push({ name: 'notification', target: this.title }); };

function viewsOf(view, x, y, out) {
  if (!view.getVisible()) return out;
  const b = view.getBounds();
  const ox = x + b.x, oy = y + b.y;
  if (view instanceof WebContentsView) out.push({ contents: view.webContents, x: ox, y: oy, width: b.width, height: b.height });
  for (const child of view.children) viewsOf(child, ox, oy, out);
  return out;
}

// A BrowserWindow's own page lies under its content view and is not one of its children.
function layersOf(win) {
  const layers = viewsOf(win.contentView, 0, 0, []);
  const own = win.webContents;
  if (own && !layers.some(l => l.contents === own)) {
    const { width, height } = win.getContentBounds();
    layers.unshift({ contents: own, x: 0, y: 0, width, height });
  }
  return layers;
}

function windowOf(id) {
  return id === undefined ? BaseWindow.getAllWindows()[0] : BaseWindow.fromId(id);
}

// Draws BGRA `src` over `dst` with alpha, at pixel offset (dx, dy).
function blit(dst, dw, dh, src, sw, sh, dx, dy) {
  for (let row = 0; row < sh; row++) {
    const ty = dy + row;
    if (ty < 0 || ty >= dh) continue;
    for (let col = 0; col < sw; col++) {
      const tx = dx + col;
      if (tx < 0 || tx >= dw) continue;
      const s = (row * sw + col) * 4, d = (ty * dw + tx) * 4;
      const a = src[s + 3] / 255;
      if (a === 0) continue;
      for (let c = 0; c < 3; c++) dst[d + c] = src[s + c] * a + dst[d + c] * (1 - a);
      dst[d + 3] = Math.max(dst[d + 3], src[s + 3]);
    }
  }
}

globalThis.electronBackground = {
  state,

  windows() {
    return BaseWindow.getAllWindows().map(win => ({
      id: win.id,
      title: win.getTitle(),
      bounds: win.getContentBounds(),
      views: layersOf(win).map(v => ({ url: v.contents.getURL(), x: v.x, y: v.y, width: v.width, height: v.height })),
    }));
  },

  // Returns the PNG of a window's content, all its views drawn in order, as base64.
  async shot(id) {
    const win = windowOf(id);
    const { width, height } = win.getContentBounds();
    const scale = screen.getDisplayMatching(win.getBounds()).scaleFactor;
    const pw = Math.round(width * scale), ph = Math.round(height * scale);
    const canvas = Buffer.alloc(pw * ph * 4);
    for (const view of layersOf(win)) {
      const image = await view.contents.capturePage();
      const size = image.getSize(scale);
      blit(canvas, pw, ph, image.toBitmap({ scaleFactor: scale }), size.width, size.height, Math.round(view.x * scale), Math.round(view.y * scale));
    }
    return nativeImage.createFromBitmap(canvas, { width: pw, height: ph, scaleFactor: scale }).toPNG().toString('base64');
  },

  // Queues the answer for the next dialog: {response} for a message box,
  // {canceled: false, filePath} for a save dialog, {canceled: false, filePaths} for an open dialog.
  answer(next) {
    state.answers.push(next);
  },

  // Labels of the last popup menu, with submenus.
  menu() {
    const list = items => items.map(i => (i.submenu ? { label: i.label, items: list(i.submenu.items) } : i.label || `(${i.type})`));
    const last = state.menus.at(-1);
    return last ? list(last.menu.items) : null;
  },

  // Clicks an item of the last popup menu by its label path, e.g. clickMenu('Format', 'Bold'), then closes the menu.
  clickMenu(...labels) {
    const last = state.menus.at(-1);
    let items = last.menu.items, item;
    for (const label of labels) {
      item = items.find(i => i.label === label);
      if (!item) throw new Error(`no menu item ${label}`);
      items = item.submenu?.items ?? [];
    }
    const win = last.options.window ?? BaseWindow.getAllWindows()[0];
    item.click(undefined, win, win?.webContents);
    last.options.callback?.();
    state.menus.pop();
  },
};
