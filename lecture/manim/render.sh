#!/usr/bin/env bash
# Render every scene at 720p30 into lecture/slides/media/<Scene>.mp4
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/../slides/media"
MANIM="${MANIM:-manim}"
QUALITY="${QUALITY:--qm}"   # -ql for fast drafts, -qh for 1080p
mkdir -p "$OUT"
SCENES=$(grep -oE '^class (A[0-9]+[A-Za-z]*)\(' "$HERE/scenes.py" | sed -E 's/class (.*)\(/\1/')
for s in $SCENES; do
  echo "== $s"
  "$MANIM" $QUALITY --disable_caching --media_dir "$HERE/_media" "$HERE/scenes.py" "$s" >/dev/null
  f=$(find "$HERE/_media/videos" -name "$s.mp4" | head -1)
  ffmpeg -y -loglevel error -i "$f" -c:v libx264 -crf 26 -preset slow -pix_fmt yuv420p -movflags +faststart "$OUT/$s.mp4"
done
echo "done → $OUT"
