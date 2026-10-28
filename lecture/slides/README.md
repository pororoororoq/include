# Slides

`index.html` is a self-contained slide deck (no build step, no external libraries).
Open it in a browser, or serve the folder (`python3 -m http.server` from this directory)
so the videos load reliably.

Keys: `←` `→` navigate · `Space` next · `R` replay video · `N` speaker notes · `L` loop video · `F` fullscreen.
Deep-link a slide with `#12`.

The videos in `media/` are rendered from `../manim/scenes.py` with `../manim/render.sh`
(needs Manim Community ≥ 0.19, ffmpeg, and a LaTeX install for the formulas).

## Exported images

- `export/` — all 56 slides as 1920×1080 PNGs; animation slides show the clip's final frame.
- `export-blank/` — the same 56 slides, but each animation slide has an empty dashed box naming the clip
  to drop in (`media/<Scene>.mp4`). Use this set when rebuilding the deck in Keynote / PowerPoint / Google Slides.
- `figures/` — the nine static figures as PNG and SVG.
- `media/` — the 18 animation clips (720p H.264, silent). Slide 55 lists where each one goes.
