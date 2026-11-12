#!/bin/sh
# Usage: electron-background.sh <app dir> [app args...]
# Starts an Electron app from its source folder in background mode (see electron-background.cjs)
# and prints its pid, the CDP port of its pages, the CDP port of its main process and its log.
# Set ELECTRON to an Electron binary to override the one found in node_modules.
set -eu

here=$(cd "$(dirname "$0")" && pwd)
app_dir=$(cd "$1" && pwd)
shift

electron=${ELECTRON:-}
dir=$app_dir
while [ -z "$electron" ] && [ "$dir" != / ]; do
  candidate=$dir/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron
  [ -x "$candidate" ] && electron=$candidate
  dir=$(dirname "$dir")
done
[ -n "$electron" ] || { echo "no Electron in node_modules above $app_dir; set ELECTRON" >&2; exit 1; }

free_port() {
  node -e "const s = require('net').createServer().listen(0, '127.0.0.1', () => { console.log(s.address().port); s.close() })"
}
pages=$(free_port)
main=$(free_port)
log=$(mktemp -t electron-background).log

cd "$app_dir"
env -u ELECTRON_RUN_AS_NODE "$electron" -r "$here/electron-background.cjs" \
  --remote-debugging-port="$pages" --inspect="$main" "$app_dir" "$@" >"$log" 2>&1 &
pid=$!

for _ in $(seq 100); do
  if curl -sf "http://127.0.0.1:$pages/json/version" >/dev/null && curl -sf "http://127.0.0.1:$main/json/list" >/dev/null; then
    echo "pid=$pid pages=$pages main=$main log=$log"
    exit 0
  fi
  kill -0 "$pid" 2>/dev/null || break
  sleep 0.2
done
echo "the app did not open its CDP ports; log: $log" >&2
tail -20 "$log" >&2
exit 1
