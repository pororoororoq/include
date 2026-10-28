// Static figures for the deck, as inline SVG (viewBox 1280×720). Loaded before the deck script.
// Colours follow the deck: queries blue, keys orange, values green, positions purple.
const C = { bg:"#0e1116", panel:"#161b24", line:"#2a3344", fg:"#e6eaf2", dim:"#8b94a7", q:"#58c4dd", k:"#ff862f", v:"#83c167", pos:"#b189c6", acc:"#ffd166", red:"#ff4b4b", s1:"#3987e5", s2:"#d95926" };
const svgOpen = `<svg viewBox="0 0 1280 720" xmlns="http://www.w3.org/2000/svg" font-family="Google Sans, Google Sans Text, Google Sans Flex, Product Sans, Roboto, Helvetica Neue, Arial, sans-serif" style="width:100%;height:100%;display:block">`;
const T = (x, y, s, o = {}) => `<text x="${x}" y="${y}" fill="${o.fill || C.fg}" font-size="${o.size || 20}" text-anchor="${o.anchor || "start"}" font-weight="${o.w || 400}" ${o.extra || ""}>${s}</text>`;
const R = (x, y, w, h, o = {}) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${o.rx ?? 8}" fill="${o.fill || "none"}" stroke="${o.stroke || "none"}" stroke-width="${o.sw || 1.5}" ${o.extra || ""}/>`;
const L = (x1, y1, x2, y2, o = {}) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${o.stroke || C.dim}" stroke-width="${o.sw || 1.5}" ${o.dash ? `stroke-dasharray="${o.dash}"` : ""} ${o.arrow ? `marker-end="url(#arr)"` : ""}/>`;
const defs = `<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="${C.dim}"/></marker></defs>`;
const heat = (a) => { const t = Math.max(0, Math.min(1, a)); const mix = (x, y) => Math.round(x + (y - x) * t); return `rgb(${mix(43,255)},${mix(47,75)},${mix(58,75)})`; };

const FIG = {};

// ---------------------------------------------------------------- timeline
FIG.timeline = (() => {
  const ev = [
    [2013, "Kalchbrenner & Blunsom", "first neural MT model", C.dim],
    [2014, "Sutskever · Cho", "Seq2seq: sentence → one vector", C.dim],
    [2014.6, "Bahdanau · Cho · Bengio", "attention (alignment) appears", C.k],
    [2015, "Luong et al.", "dot-product scoring", C.k],
    [2016, "GNMT (Google)", "8-layer LSTM + attention, in production", C.dim],
    [2016.6, "ByteNet", "parallel via convolution", C.dim],
    [2017.3, "ConvS2S (Facebook)", "conv seq2seq", C.dim],
    [2017.5, "Transformer", "Attention Is All You Need", C.acc],
    [2018.5, "BERT · GPT", "encoder-only / decoder-only", C.q],
    [2020, "GPT-3 · ViT", "scaling · image patches", C.v],
  ];
  const x0 = 170, x1 = 1170, y = 380, yr = [2013, 2020.4];
  const X = (yr_) => x0 + (yr_ - yr[0]) / (yr[1] - yr[0]) * (x1 - x0);
  let s = svgOpen + defs + T(640, 60, "From neural MT to the Transformer, 2013–2020", { size: 30, anchor: "middle", w: 650 });
  s += L(x0, y, x1, y, { stroke: C.line, sw: 3 });
  for (let yy = 2013; yy <= 2020; yy++) s += L(X(yy), y - 8, X(yy), y + 8, { stroke: C.dim, sw: 2 }) + T(X(yy), y + 36, yy, { size: 18, anchor: "middle", fill: C.dim });
  ev.forEach(([yr_, who, what, col], i) => {
    const x = X(yr_), up = i % 2 === 0, ty = up ? y - 70 - (i % 4 === 0 ? 70 : 0) : y + 90 + (i % 4 === 3 ? 70 : 0);
    s += L(x, y, x, up ? ty + 28 : ty - 44, { stroke: col, sw: 1.5 }) + `<circle cx="${x}" cy="${y}" r="${col === C.acc ? 10 : 7}" fill="${col}"/>`;
    s += T(x, ty, who, { size: 19, anchor: "middle", w: 600, fill: col === C.dim ? C.fg : col }) + T(x, ty + 24, what, { size: 16, anchor: "middle", fill: C.dim });
  });
  s += T(640, 690, "orange: attention as a crutch for RNNs · yellow: the paper that kept only the crutch · blue/green: what followed", { size: 16, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- bottleneck vs table
FIG.bottleneck = (() => {
  const words = ["The", "animal", "crossed", "the", "street"];
  let s = svgOpen + defs;
  s += T(320, 60, "Seq2seq (2014)", { size: 28, anchor: "middle", w: 650 }) + T(960, 60, "+ Attention (2015)", { size: 28, anchor: "middle", w: 650, fill: C.k });
  // left: words -> funnel -> one box -> decoder
  words.forEach((w, i) => { const x = 60 + i * 105; s += R(x, 130, 95, 44, { stroke: C.fg, fill: "#161b24" }) + T(x + 47, 159, w, { size: 18, anchor: "middle" }); s += L(x + 47, 174, 320, 290, { stroke: C.dim, sw: 1, arrow: i === 4 }); });
  s += R(260, 290, 120, 70, { stroke: C.fg, sw: 2 }) + T(320, 333, "h_T", { size: 22, anchor: "middle" });
  s += L(320, 360, 320, 440, { stroke: C.dim, arrow: true }) + R(230, 440, 180, 50, { stroke: C.q }) + T(320, 472, "decoder", { size: 20, anchor: "middle", fill: C.q });
  s += T(320, 560, "whole source → one fixed-size vector", { size: 20, anchor: "middle" }) + T(320, 592, "capacity stays fixed as length grows", { size: 18, anchor: "middle", fill: C.red });
  s += T(320, 624, "intermediate states h_1…h_{T-1} are discarded", { size: 18, anchor: "middle", fill: C.red });
  // right: table of states kept, decoder reads weighted
  const alpha = [0.03, 0.05, 0.07, 0.10, 0.75];
  words.forEach((w, i) => { const x = 700 + i * 105; s += R(x, 130, 95, 44, { stroke: C.fg, fill: "#161b24" }) + T(x + 47, 159, w, { size: 18, anchor: "middle" }); s += R(x + 22, 200, 50, 90, { stroke: C.k, fill: "rgba(255,134,47,0.15)" }) + T(x + 47, 250, `h${i + 1}`, { size: 18, anchor: "middle", fill: C.k }); s += L(x + 47, 290, 960, 440, { stroke: heat(alpha[i] + 0.1), sw: 1 + alpha[i] * 8, dash: "6 5" }); s += T(x + 47, 315, alpha[i].toFixed(2), { size: 15, anchor: "middle", fill: C.dim }); });
  s += R(870, 440, 180, 50, { stroke: C.q }) + T(960, 472, "decoder", { size: 20, anchor: "middle", fill: C.q });
  s += T(960, 560, "keep every state as a table, read a weighted sum each step", { size: 20, anchor: "middle" }) + T(960, 592, "capacity grows with sentence length", { size: 18, anchor: "middle", fill: C.v });
  s += T(960, 624, "any word reaches the decoder in one hop", { size: 18, anchor: "middle", fill: C.v });
  s += L(640, 100, 640, 650, { stroke: C.line, sw: 1 });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- library analogy for Q/K/V
FIG.library = (() => {
  let s = svgOpen + defs + T(640, 56, "Query · Key · Value as a library card catalogue", { size: 28, anchor: "middle", w: 650 });
  // query card
  s += R(70, 140, 300, 170, { stroke: C.q, sw: 2, fill: "rgba(88,196,221,0.08)" }) + T(220, 180, "query q", { size: 24, anchor: "middle", fill: C.q, w: 650 });
  s += T(220, 220, "\"who is my subject?\"", { size: 20, anchor: "middle" }) + T(220, 252, "what this token is looking for", { size: 16, anchor: "middle", fill: C.dim }) + T(220, 280, "q = x · W^Q", { size: 16, anchor: "middle", fill: C.dim });
  // drawers: keys with values inside
  const rows = [["The", "article", "contents of 'the'", 0.05], ["cat", "noun · subject candidate", "contents of 'cat'", 0.70], ["sat", "verb", "contents of 'sat'", 0.25]];
  rows.forEach(([w, key, val, a], i) => {
    const y = 130 + i * 120;
    s += R(520, y, 330, 90, { stroke: C.k, sw: 2, fill: "rgba(255,134,47,0.08)" }) + T(540, y + 32, `key k_${w}`, { size: 18, fill: C.k, w: 650 }) + T(540, y + 62, `"${key}"`, { size: 18 });
    s += R(880, y, 300, 90, { stroke: C.v, sw: 2, fill: "rgba(131,193,103,0.08)" }) + T(900, y + 32, `value v_${w}`, { size: 18, fill: C.v, w: 650 }) + T(900, y + 62, val, { size: 18 });
    s += L(370, 225, 520, y + 45, { stroke: heat(a + 0.1), sw: 1 + a * 10 }) + T(445, (225 + y + 45) / 2 - 8, `α=${a.toFixed(2)}`, { size: 15, anchor: "middle", fill: C.dim });
    s += L(850, y + 45, 880, y + 45, { stroke: C.dim, sw: 1 });
  });
  s += T(640, 540, "1. score the query against every key (dot product)   2. softmax → a budget that sums to 1   3. blend the values by that budget", { size: 18, anchor: "middle" });
  s += T(640, 580, "like a dictionary lookup, except every drawer opens a little → soft lookup", { size: 18, anchor: "middle", fill: C.acc });
  s += T(640, 640, "key and value sit on the same drawer but do different jobs: the key is the label you search by, the value is what you take away", { size: 16, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- Figure 2 recreated
FIG.fig2 = (() => {
  let s = svgOpen + defs + T(320, 50, "Scaled Dot-Product Attention", { size: 26, anchor: "middle", w: 650 }) + T(960, 50, "Multi-Head Attention", { size: 26, anchor: "middle", w: 650 });
  const box = (x, y, w, h, label, col = C.fg) => R(x - w / 2, y - h / 2, w, h, { stroke: col, sw: 2, fill: C.panel }) + T(x, y + 7, label, { size: 18, anchor: "middle", fill: col });
  // left flow (bottom-up)
  const steps = [[640 - 320 + 0, 620, "Q", C.q], [0, 0, "", ""]];
  s += T(250, 650, "Q", { size: 22, anchor: "middle", fill: C.q, w: 650 }) + T(330, 650, "K", { size: 22, anchor: "middle", fill: C.k, w: 650 }) + T(470, 650, "V", { size: 22, anchor: "middle", fill: C.v, w: 650 });
  s += L(250, 630, 250, 575, { arrow: true }) + L(330, 630, 330, 575, { arrow: true });
  s += box(290, 550, 150, 46, "MatMul  QKᵀ");
  s += L(290, 527, 290, 475, { arrow: true }) + box(290, 450, 150, 46, "Scale  ÷√d_k");
  s += L(290, 427, 290, 375, { arrow: true }) + box(290, 350, 150, 46, "Mask (opt.)", C.dim);
  s += L(290, 327, 290, 275, { arrow: true }) + box(290, 250, 150, 46, "SoftMax", C.red);
  s += L(290, 227, 290, 175, { arrow: true }) + L(470, 630, 470, 175, { arrow: true });
  s += box(380, 150, 200, 46, "MatMul  (weights)·V", C.v);
  s += L(380, 127, 380, 90, { arrow: true }) + T(380, 80, "output", { size: 18, anchor: "middle", fill: C.dim });
  s += T(205, 345, "decoder only", { size: 14, fill: C.dim, anchor: "end" }) + T(205, 365, "future → −∞", { size: 14, fill: C.dim, anchor: "end" });
  // right flow
  s += T(860, 650, "Q", { size: 22, anchor: "middle", fill: C.q, w: 650 }) + T(960, 650, "K", { size: 22, anchor: "middle", fill: C.k, w: 650 }) + T(1060, 650, "V", { size: 22, anchor: "middle", fill: C.v, w: 650 });
  [[860, C.q], [960, C.k], [1060, C.v]].forEach(([x, col]) => { s += L(x, 630, x, 575, { arrow: true }); for (let h = 0; h < 3; h++) s += R(x - 45 + h * 6, 505 - h * 6, 90, 44, { stroke: col, sw: 1.5, fill: C.panel }); s += T(x + 6, 533 - 12, "Linear", { size: 16, anchor: "middle", fill: col }); s += L(x, 499, x, 440, { arrow: true }); });
  for (let h = 0; h < 3; h++) s += R(820 + h * 6, 370 - h * 6, 280, 60, { stroke: C.fg, sw: 1.5, fill: C.panel });
  s += T(966, 395, "Scaled Dot-Product Attention", { size: 17, anchor: "middle" }) + T(1150, 360, "× h = 8", { size: 20, fill: C.acc, w: 650 });
  s += L(960, 364, 960, 300, { arrow: true }) + box(960, 275, 200, 46, "Concat  (8 × 64 = 512)");
  s += L(960, 252, 960, 195, { arrow: true }) + box(960, 170, 160, 46, "Linear  W^O");
  s += L(960, 147, 960, 90, { arrow: true }) + T(960, 80, "output (512)", { size: 18, anchor: "middle", fill: C.dim });
  s += T(640, 700, "Figure 2 of the paper, redrawn. The left-hand unit is run eight times in parallel on the right. Each head projects 512 → 64, so total cost equals one full-width head.", { size: 15, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- Figure 1 recreated (static)
FIG.fig1 = (() => {
  let s = svgOpen + defs;
  // ordinary blocks are dimmed; the three attention blocks are filled, numbered, and get Q/K/V arrows
  const blk = (x, y, w, label) => R(x - w / 2, y - 20, w, 40, { stroke: "#3a4254", sw: 1.2, fill: C.panel }) + T(x, y + 6, label, { size: 15, anchor: "middle", fill: "#8b94a7" });
  const hot = (x, y, w, label, col, num) => R(x - w / 2, y - 22, w, 44, { stroke: col, sw: 2.5, fill: col, extra: 'fill-opacity="0.22"' })
    + `<circle cx="${x - w / 2 + 2}" cy="${y - 22}" r="15" fill="${col}"/>` + T(x - w / 2 + 2, y - 16, num, { size: 17, anchor: "middle", fill: C.bg, w: 700 })
    + T(x, y + 7, label, { size: 16, anchor: "middle", fill: col, w: 650 });
  const qkv = (x, y, labels, col) => labels.map(([dx, t]) => T(x + dx, y, t, { size: 13, anchor: "middle", fill: col, w: 650 })).join("");
  const ex = 380, dx = 860;
  // encoder
  s += R(ex - 150, 160, 300, 260, { stroke: C.q, sw: 1.2, fill: "rgba(88,196,221,0.03)" }) + T(ex - 140, 150, "Encoder  × 6", { size: 18, fill: C.q, w: 650 });
  s += hot(ex, 380, 230, "Multi-Head Self-Attention", C.q, "1") + blk(ex, 320, 220, "Add & Norm") + blk(ex, 260, 220, "Feed Forward") + blk(ex, 200, 220, "Add & Norm");
  s += L(ex, 540, ex, 404, { arrow: true }) + L(ex, 180, ex, 120, { arrow: true });
  s += qkv(ex, 445, [[-40, "Q"], [0, "K"], [40, "V"]], C.q) + T(ex + 60, 445, "all from the source", { size: 12, fill: C.dim });
  s += `<circle cx="${ex}" cy="500" r="16" fill="none" stroke="${C.pos}" stroke-width="2"/>` + T(ex, 506, "+", { size: 20, anchor: "middle", fill: C.pos }) + T(ex - 30, 506, "PE", { size: 15, anchor: "end", fill: C.pos });
  s += R(ex - 90, 560, 180, 40, { stroke: C.fg }) + T(ex, 586, "Input Embedding", { size: 15, anchor: "middle" }) + T(ex, 640, "source tokens", { size: 16, anchor: "middle", fill: C.dim });
  // decoder
  s += R(dx - 150, 100, 300, 320, { stroke: C.k, sw: 1.2, fill: "rgba(255,134,47,0.03)" }) + T(dx - 140, 90, "Decoder  × 6", { size: 18, fill: C.k, w: 650 });
  s += hot(dx, 380, 230, "Masked Multi-Head Self-Attn", C.k, "2") + blk(dx, 325, 220, "Add & Norm") + hot(dx, 270, 230, "Multi-Head Cross-Attention", C.v, "3") + blk(dx, 215, 220, "Add & Norm") + blk(dx, 160, 220, "Feed Forward") + blk(dx, 120, 220, "Add & Norm");
  s += L(dx, 540, dx, 404, { arrow: true });
  s += qkv(dx, 445, [[-40, "Q"], [0, "K"], [40, "V"]], C.k) + T(dx + 60, 445, "all from the target", { size: 12, fill: C.dim });
  s += T(dx + 160, 266, "Q from the", { size: 12, fill: C.q }) + T(dx + 160, 282, "decoder stack", { size: 12, fill: C.q });
  s += `<circle cx="${dx}" cy="500" r="16" fill="none" stroke="${C.pos}" stroke-width="2"/>` + T(dx, 506, "+", { size: 20, anchor: "middle", fill: C.pos }) + T(dx + 30, 506, "PE", { size: 15, fill: C.pos });
  s += R(dx - 90, 560, 180, 40, { stroke: C.fg }) + T(dx, 586, "Output Embedding", { size: 15, anchor: "middle" }) + T(dx, 640, "target tokens (shifted right by one)", { size: 16, anchor: "middle", fill: C.dim });
  // encoder output -> cross-attention K, V
  s += `<path d="M ${ex} 120 L ${ex} 60 L ${dx - 260} 60 L ${dx - 260} 270 L ${dx - 117} 270" fill="none" stroke="${C.v}" stroke-width="3" marker-end="url(#arr)"/>`;
  s += T(dx - 255, 250, "K, V from", { size: 12, fill: C.v, w: 650 }) + T(dx - 255, 265, "the encoder", { size: 12, fill: C.v, w: 650 });
  // output
  s += L(dx, 100, dx, 60, { arrow: true }) + R(dx - 70, 20, 140, 36, { stroke: C.v }) + T(dx, 44, "Linear + Softmax", { size: 14, anchor: "middle", fill: C.v }) + T(dx + 90, 44, "→ next-token probabilities", { size: 15, fill: C.dim });
  // legend
  const badge = (x, col, num, txt) => `<circle cx="${x}" cy="664" r="12" fill="${col}"/>` + T(x, 669, num, { size: 14, anchor: "middle", fill: C.bg, w: 700 }) + T(x + 18, 669, txt, { size: 14, fill: col });
  s += badge(50, C.q, "1", "encoder self-attention: source looks at source") + badge(455, C.k, "2", "masked self-attention: target sees only its past") + badge(870, C.v, "3", "cross-attention: Q from decoder, K·V from encoder");
  s += T(640, 705, "Figure 1 of the paper, redrawn. Only the three filled blocks are attention; everything else is add & norm or a feed-forward layer.", { size: 14, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- alignment matrix from the trained model
FIG.alignment = (A, Aalt, src, srcAlt, tgt, tgtAlt) => {
  const cell = 64;
  const grid = (M, x0, y0, cols, rows, title) => {
    let g = T(x0 + cols.length * cell / 2, y0 - 70, title, { size: 22, anchor: "middle", w: 650 });
    cols.forEach((w, j) => g += T(x0 + j * cell + cell / 2, y0 - 14, w, { size: 15, anchor: "middle", fill: C.k }));
    M.forEach((row, i) => { g += T(x0 - 12, y0 + i * cell + cell / 2 + 5, rows[i], { size: 15, anchor: "end", fill: C.q }); row.forEach((a, j) => { g += R(x0 + j * cell + 1, y0 + i * cell + 1, cell - 2, cell - 2, { rx: 4, fill: heat(a) }) + T(x0 + j * cell + cell / 2, y0 + i * cell + cell / 2 + 5, a.toFixed(2), { size: 13, anchor: "middle", fill: a > 0.5 ? "#fff" : C.dim }); }); });
    return g;
  };
  let s = svgOpen + defs + T(640, 50, "Attention maps of the trained 4-dim model (rows: output steps, columns: source words)", { size: 26, anchor: "middle", w: 650 });
  s += grid(A, 140, 180, src, tgt, "the animal crossed the street") + grid(Aalt, 760, 180, srcAlt, tgtAlt, "the animal crossed the bridge");
  s += T(640, 600, "Sharp only at the noun steps 2 (Tier) and 5 (Straße/Brücke); spread on the grammar words (das, überquerte, die)", { size: 18, anchor: "middle" });
  s += T(640, 636, "Decoder states are nearly identical across the two sentences (max diff 0.04). Rows 3–4 shift weight toward 'bridge' but keep their words. Only row 5 changes its word", { size: 17, anchor: "middle", fill: C.acc });
  s += T(640, 690, "Figures 3–5 in the paper's appendix (it → animal, etc.) are the 512-dim, 8-head version of this", { size: 15, anchor: "middle", fill: C.dim });
  return s + "</svg>";
};

// ---------------------------------------------------------------- results (Table 2)
FIG.results = (() => {
  const de = [["ByteNet", 23.75, 0], ["GNMT+RL", 24.6, 0], ["ConvS2S", 25.16, 0], ["MoE", 26.03, 0], ["GNMT+RL ens.", 26.30, 0], ["ConvS2S ens.", 26.36, 0], ["Transformer base", 27.3, 1], ["Transformer big", 28.4, 1]];
  const fr = [["Deep-Att+PosUnk", 39.2, 0], ["GNMT+RL", 39.92, 0], ["ConvS2S", 40.46, 0], ["MoE", 40.56, 0], ["GNMT+RL ens.", 41.16, 0], ["ConvS2S ens.", 41.29, 0], ["Transformer base", 38.1, 1], ["Transformer big", 41.8, 1]];
  const panel = (data, x0, title, lo, hi) => {
    const w = 440, bh = 22, gap = 34, y0 = 150, X = (v) => x0 + 190 + (v - lo) / (hi - lo) * (w - 190);
    let g = T(x0 + w / 2, 110, title, { size: 22, anchor: "middle", w: 650 });
    for (let v = lo; v <= hi; v += (hi - lo) / 4) g += L(X(v), y0 - 10, X(v), y0 + data.length * gap, { stroke: C.line, sw: 1 }) + T(X(v), y0 + data.length * gap + 22, v.toFixed(0), { size: 13, anchor: "middle", fill: C.dim });
    data.forEach(([n, v, hero], i) => { const y = y0 + i * gap; g += T(x0 + 180, y + bh / 2 + 5, n, { size: 15, anchor: "end", fill: hero ? C.fg : C.dim }); g += `<rect x="${X(lo)}" y="${y}" width="${X(v) - X(lo)}" height="${bh}" fill="${hero ? C.s2 : C.s1}" rx="0"/><rect x="${X(v) - 4}" y="${y}" width="4" height="${bh}" rx="3" fill="${hero ? C.s2 : C.s1}"/>`; g += T(X(v) + 8, y + bh / 2 + 5, v.toFixed(hero ? 1 : 2), { size: 14, fill: C.fg }); });
    return g;
  };
  let s = svgOpen + T(640, 50, "BLEU on WMT 2014 (Table 2 of the paper)", { size: 28, anchor: "middle", w: 650 });
  s += panel(de, 60, "English → German", 22, 30) + panel(fr, 760, "English → French", 36, 44);
  s += `<rect x="440" y="610" width="14" height="14" fill="${C.s1}"/>` + T(462, 622, "previous models (single · ensemble)", { size: 15, fill: C.dim }) + `<rect x="700" y="610" width="14" height="14" fill="${C.s2}"/>` + T(722, 622, "Transformer", { size: 15, fill: C.dim });
  s += T(640, 670, "big: En→De 28.4 (+2.0 over the previous best), En→Fr 41.8 — at under 1/4 of the training FLOPs (base 3.3×10¹⁸, big 2.3×10¹⁹)", { size: 16, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- heads ablation (Table 3 row A)
FIG.heads = (() => {
  const data = [[1, 24.9], [4, 25.5], [8, 25.8], [16, 25.8], [32, 25.4]];
  const x0 = 260, y0 = 560, w = 760, h = 360, lo = 24.5, hi = 26.2;
  const X = (i) => x0 + 80 + i * (w - 160) / 4, Y = (v) => y0 - (v - lo) / (hi - lo) * h;
  let s = svgOpen + T(640, 50, "BLEU vs number of heads (newstest2013 dev, Table 3 row A)", { size: 26, anchor: "middle", w: 650 });
  for (let v = 24.5; v <= 26.2; v += 0.5) s += L(x0, Y(v), x0 + w, Y(v), { stroke: C.line, sw: 1 }) + T(x0 - 12, Y(v) + 5, v.toFixed(1), { size: 14, anchor: "end", fill: C.dim });
  let path = "";
  data.forEach(([hh, v], i) => { path += (i ? "L" : "M") + `${X(i)} ${Y(v)} `; });
  s += `<path d="${path}" fill="none" stroke="${C.s1}" stroke-width="2" stroke-linejoin="round"/>`;
  data.forEach(([hh, v], i) => { const hero = hh === 8; s += `<circle cx="${X(i)}" cy="${Y(v)}" r="${hero ? 8 : 6}" fill="${hero ? C.s2 : C.s1}" stroke="${C.bg}" stroke-width="2"/>` + T(X(i), y0 + 30, `h = ${hh}`, { size: 16, anchor: "middle", fill: C.dim }) + T(X(i), Y(v) - 16, v.toFixed(1), { size: 15, anchor: "middle", fill: hero ? C.fg : C.dim }); });
  s += T(X(0) + 20, Y(24.9) + 40, "1 head: −0.9 BLEU", { size: 15, fill: C.dim }) + T(X(4) - 20, Y(25.4) + 40, "32 heads: 16 dims each → too little capacity", { size: 15, anchor: "end", fill: C.dim });
  s += T(640, 650, "d_model = 512 fixed, h·d_k = 512 throughout. The paper chose 8.", { size: 16, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- hyperparameters
FIG.hparams = (() => {
  const rows = [["N (layers)", "6", "6"], ["d_model", "512", "1024"], ["d_ff", "2048", "4096"], ["h (heads)", "8", "16"], ["d_k = d_v", "64", "64"], ["dropout", "0.1", "0.3"], ["training steps", "100k", "300k"], ["training time (8× P100)", "12 hours", "3.5 days"], ["parameters", "65M", "213M"], ["BLEU En→De / En→Fr", "27.3 / 38.1", "28.4 / 41.8"]];
  let s = svgOpen + T(640, 50, "Base vs Big (last rows of Table 3)", { size: 28, anchor: "middle", w: 650 });
  const x = [260, 640, 920], y0 = 120;
  s += T(x[1], y0, "base", { size: 22, anchor: "middle", fill: C.q, w: 650 }) + T(x[2], y0, "big", { size: 22, anchor: "middle", fill: C.k, w: 650 });
  rows.forEach(([k, a, b], i) => { const y = y0 + 48 + i * 48; s += L(220, y + 14, 1060, y + 14, { stroke: C.line, sw: 1 }) + T(x[0], y, k, { size: 19, fill: C.dim }) + T(x[1], y, a, { size: 20, anchor: "middle" }) + T(x[2], y, b, { size: 20, anchor: "middle" }); });
  s += T(640, 680, "shared: Adam (β₂ = 0.98) + 4000 warm-up steps, label smoothing 0.1, beam 4, length penalty 0.6, checkpoint averaging (5 / 20)", { size: 15, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();
