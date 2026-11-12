#!/bin/sh
# Usage: window-shot.sh <out.png> <window id | app name> [title]
# Captures one window of any app, also when other windows cover it, without the shadow
# and without activating the app. With an app name, takes the first window windows.swift lists.
set -eu

here=$(cd "$(dirname "$0")" && pwd)
out=$1
which=$2
title=${3:-}

case $which in
  *[!0-9]*) id=$(swift "$here/windows.swift" "$which" "$title" | head -1 | cut -f1) ;;
  *) id=$which ;;
esac
[ -n "$id" ] || { echo "no window of $which${title:+ titled $title}" >&2; exit 1; }

if ! screencapture -x -o -l "$id" "$out"; then
  echo "screencapture failed. The app that runs this shell (VS Code, Terminal) needs" >&2
  echo "System Settings > Privacy & Security > Screen Recording, then a restart of that app." >&2
  exit 1
fi
echo "$out"
