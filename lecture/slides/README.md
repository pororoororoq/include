# Slides

`index.html` is a self-contained slide deck (no build step, no external libraries).
Open it in a browser, or serve the folder (`python3 -m http.server` from this directory)
so the videos load reliably.

Keys: `←` `→` navigate · `Space` next · `R` replay video · `N` speaker notes · `L` loop video · `F` fullscreen.
Deep-link a slide with `#12`.

The videos in `media/` are rendered from `../manim/scenes.py` with `../manim/render.sh`
(needs Manim Community ≥ 0.19, ffmpeg, and a LaTeX install for the formulas).
