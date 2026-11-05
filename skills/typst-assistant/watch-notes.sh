#!/usr/bin/env bash
# Prints each new "// @ai" note in the .typ files under <folder> as
# path:line:text, when two scans 2 s apart find the same notes. A note prints
# once, also when edits above it move it to another line. A note that goes
# away and comes back prints again. Folders named in <skip> are not searched.
# Usage: watch-notes.sh <folder> [<skip> ...]

cd "${1:?usage: watch-notes.sh <folder> [<skip> ...]}" || exit 1
shift
skip=()
for name in "$@"; do skip+=(--exclude-dir="$name"); done

scan() {
    grep -rniE --include='*.typ' "${skip[@]}" '//[[:space:]]*@ai([[:space:]]|:|：|$)' . 2>/dev/null |
        sed 's|^\./||'
}

new_only='
function key(line) { sub(/:[0-9]+:/, ":", line); return line }
BEGIN { n = split(ENVIRON["SEEN"], s, "\n"); for (i = 1; i <= n; i++) seen[key(s[i])] = 1 }
!(key($0) in seen) { print; fflush() }
'

seen=""
prev=""
while true; do
    cur=$(scan)
    if [ "$cur" = "$prev" ] && [ "$cur" != "$seen" ]; then
        [ -n "$cur" ] && printf '%s\n' "$cur" | SEEN=$seen awk "$new_only"
        seen=$cur
    fi
    prev=$cur
    sleep 2
done
