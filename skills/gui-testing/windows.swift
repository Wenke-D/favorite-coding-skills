// Usage: swift windows.swift [app] [title]
// Lists the normal windows of all apps whose name and title contain the given text,
// matching the app either by its shown name (文本编辑) or by its bundle name (TextEdit),
// on-screen windows first, then the largest: id, app, title, on screen, width x height.
// Without Screen Recording permission for the calling app, titles are empty.
import AppKit
import CoreGraphics
import Foundation

let args = CommandLine.arguments.dropFirst()
let app = args.first ?? ""
let title = args.dropFirst().first ?? ""

struct Window {
  let id: Int, app: String, title: String, onScreen: Bool, width: Int, height: Int
}

let info = CGWindowListCopyWindowInfo([.optionAll, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
let windows = info.compactMap { w -> Window? in
  guard (w[kCGWindowLayer as String] as? Int) == 0 else { return nil }
  let bounds = w[kCGWindowBounds as String] as? [String: Any] ?? [:]
  let window = Window(
    id: w[kCGWindowNumber as String] as? Int ?? 0,
    app: w[kCGWindowOwnerName as String] as? String ?? "",
    title: w[kCGWindowName as String] as? String ?? "",
    onScreen: w[kCGWindowIsOnscreen as String] as? Bool ?? false,
    width: bounds["Width"] as? Int ?? 0,
    height: bounds["Height"] as? Int ?? 0)
  guard window.width >= 100, window.height >= 100 else { return nil }
  let pid = w[kCGWindowOwnerPID as String] as? pid_t ?? 0
  let bundle = NSRunningApplication(processIdentifier: pid)?.bundleURL?.deletingPathExtension().lastPathComponent ?? ""
  guard app.isEmpty || window.app.localizedCaseInsensitiveContains(app)
    || bundle.localizedCaseInsensitiveContains(app) else { return nil }
  guard title.isEmpty || window.title.localizedCaseInsensitiveContains(title) else { return nil }
  return window
}

for w in windows.sorted(by: { ($0.onScreen ? 1 : 0, $0.width * $0.height) > ($1.onScreen ? 1 : 0, $1.width * $1.height) }) {
  print("\(w.id)\t\(w.app)\t\(w.title)\t\(w.onScreen ? "on screen" : "off screen")\t\(w.width)x\(w.height)")
}
