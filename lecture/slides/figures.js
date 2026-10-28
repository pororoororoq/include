// Static figures for the deck, as inline SVG (viewBox 1280×720). Loaded before the deck script.
// Colours follow the deck: queries blue, keys orange, values green, positions purple.
const C = { bg:"#0e1116", panel:"#161b24", line:"#2a3344", fg:"#e6eaf2", dim:"#8b94a7", q:"#58c4dd", k:"#ff862f", v:"#83c167", pos:"#b189c6", acc:"#ffd166", red:"#ff4b4b", s1:"#3987e5", s2:"#d95926" };
const svgOpen = `<svg viewBox="0 0 1280 720" xmlns="http://www.w3.org/2000/svg" font-family="Pretendard, Apple SD Gothic Neo, Noto Sans KR, Segoe UI, system-ui, sans-serif" style="width:100%;height:100%;display:block">`;
const T = (x, y, s, o = {}) => `<text x="${x}" y="${y}" fill="${o.fill || C.fg}" font-size="${o.size || 20}" text-anchor="${o.anchor || "start"}" font-weight="${o.w || 400}" ${o.extra || ""}>${s}</text>`;
const R = (x, y, w, h, o = {}) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${o.rx ?? 8}" fill="${o.fill || "none"}" stroke="${o.stroke || "none"}" stroke-width="${o.sw || 1.5}" ${o.extra || ""}/>`;
const L = (x1, y1, x2, y2, o = {}) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${o.stroke || C.dim}" stroke-width="${o.sw || 1.5}" ${o.dash ? `stroke-dasharray="${o.dash}"` : ""} ${o.arrow ? `marker-end="url(#arr)"` : ""}/>`;
const defs = `<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="${C.dim}"/></marker></defs>`;
const heat = (a) => { const t = Math.max(0, Math.min(1, a)); const mix = (x, y) => Math.round(x + (y - x) * t); return `rgb(${mix(43,255)},${mix(47,75)},${mix(58,75)})`; };

const FIG = {};

// ---------------------------------------------------------------- timeline
FIG.timeline = (() => {
  const ev = [
    [2013, "Kalchbrenner & Blunsom", "첫 신경망 번역 모델", C.dim],
    [2014, "Sutskever · Cho", "Seq2seq: 문장 → 벡터 하나", C.dim],
    [2014.6, "Bahdanau · Cho · Bengio", "Attention (alignment) 등장", C.k],
    [2015, "Luong et al.", "내적으로 점수 매기기", C.k],
    [2016, "GNMT (Google)", "8층 LSTM + attention, 실서비스", C.dim],
    [2016.6, "ByteNet", "convolution으로 병렬화", C.dim],
    [2017.3, "ConvS2S (Facebook)", "conv seq2seq", C.dim],
    [2017.5, "Transformer", "Attention Is All You Need", C.acc],
    [2018.5, "BERT · GPT", "encoder-only / decoder-only", C.q],
    [2020, "GPT-3 · ViT", "scaling · 이미지 패치", C.v],
  ];
  const x0 = 170, x1 = 1170, y = 380, yr = [2013, 2020.4];
  const X = (yr_) => x0 + (yr_ - yr[0]) / (yr[1] - yr[0]) * (x1 - x0);
  let s = svgOpen + defs + T(640, 60, "신경망 번역에서 Transformer까지, 2013–2020", { size: 30, anchor: "middle", w: 650 });
  s += L(x0, y, x1, y, { stroke: C.line, sw: 3 });
  for (let yy = 2013; yy <= 2020; yy++) s += L(X(yy), y - 8, X(yy), y + 8, { stroke: C.dim, sw: 2 }) + T(X(yy), y + 36, yy, { size: 18, anchor: "middle", fill: C.dim });
  ev.forEach(([yr_, who, what, col], i) => {
    const x = X(yr_), up = i % 2 === 0, ty = up ? y - 70 - (i % 4 === 0 ? 70 : 0) : y + 90 + (i % 4 === 3 ? 70 : 0);
    s += L(x, y, x, up ? ty + 28 : ty - 44, { stroke: col, sw: 1.5 }) + `<circle cx="${x}" cy="${y}" r="${col === C.acc ? 10 : 7}" fill="${col}"/>`;
    s += T(x, ty, who, { size: 19, anchor: "middle", w: 600, fill: col === C.dim ? C.fg : col }) + T(x, ty + 24, what, { size: 16, anchor: "middle", fill: C.dim });
  });
  s += T(640, 690, "주황: attention이 RNN의 목발로 쓰이던 시기 · 노랑: 목발만 남긴 논문 · 파랑/초록: 그 이후", { size: 16, anchor: "middle", fill: C.dim });
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
  s += T(320, 560, "소스 전체 → 고정 크기 벡터 하나", { size: 20, anchor: "middle" }) + T(320, 592, "길이가 늘어도 용량은 그대로", { size: 18, anchor: "middle", fill: C.red });
  s += T(320, 624, "중간 상태 h_1…h_{T-1}은 버려진다", { size: 18, anchor: "middle", fill: C.red });
  // right: table of states kept, decoder reads weighted
  const alpha = [0.03, 0.05, 0.07, 0.10, 0.75];
  words.forEach((w, i) => { const x = 700 + i * 105; s += R(x, 130, 95, 44, { stroke: C.fg, fill: "#161b24" }) + T(x + 47, 159, w, { size: 18, anchor: "middle" }); s += R(x + 22, 200, 50, 90, { stroke: C.k, fill: "rgba(255,134,47,0.15)" }) + T(x + 47, 250, `h${i + 1}`, { size: 18, anchor: "middle", fill: C.k }); s += L(x + 47, 290, 960, 440, { stroke: heat(alpha[i] + 0.1), sw: 1 + alpha[i] * 8, dash: "6 5" }); s += T(x + 47, 315, alpha[i].toFixed(2), { size: 15, anchor: "middle", fill: C.dim }); });
  s += R(870, 440, 180, 50, { stroke: C.q }) + T(960, 472, "decoder", { size: 20, anchor: "middle", fill: C.q });
  s += T(960, 560, "모든 상태를 표로 보관, 매 단계 가중합으로 읽는다", { size: 20, anchor: "middle" }) + T(960, 592, "용량이 문장 길이에 비례해 늘어난다", { size: 18, anchor: "middle", fill: C.v });
  s += T(960, 624, "어느 단어든 디코더까지 한 번의 연결", { size: 18, anchor: "middle", fill: C.v });
  s += L(640, 100, 640, 650, { stroke: C.line, sw: 1 });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- library analogy for Q/K/V
FIG.library = (() => {
  let s = svgOpen + defs + T(640, 56, "Query · Key · Value — 도서관 카드 목록으로 읽기", { size: 28, anchor: "middle", w: 650 });
  // query card
  s += R(70, 140, 300, 170, { stroke: C.q, sw: 2, fill: "rgba(88,196,221,0.08)" }) + T(220, 180, "query q", { size: 24, anchor: "middle", fill: C.q, w: 650 });
  s += T(220, 220, "\"내 주어가 누구지?\"", { size: 20, anchor: "middle" }) + T(220, 252, "지금 이 토큰이 찾는 것", { size: 16, anchor: "middle", fill: C.dim }) + T(220, 280, "q = x · W^Q", { size: 16, anchor: "middle", fill: C.dim });
  // drawers: keys with values inside
  const rows = [["The", "관사", "'the'의 내용", 0.05], ["cat", "명사 · 주어 후보", "'cat'의 내용", 0.70], ["sat", "동사", "'sat'의 내용", 0.25]];
  rows.forEach(([w, key, val, a], i) => {
    const y = 130 + i * 120;
    s += R(520, y, 330, 90, { stroke: C.k, sw: 2, fill: "rgba(255,134,47,0.08)" }) + T(540, y + 32, `key k_${w}`, { size: 18, fill: C.k, w: 650 }) + T(540, y + 62, `"${key}"`, { size: 18 });
    s += R(880, y, 300, 90, { stroke: C.v, sw: 2, fill: "rgba(131,193,103,0.08)" }) + T(900, y + 32, `value v_${w}`, { size: 18, fill: C.v, w: 650 }) + T(900, y + 62, val, { size: 18 });
    s += L(370, 225, 520, y + 45, { stroke: heat(a + 0.1), sw: 1 + a * 10 }) + T(445, (225 + y + 45) / 2 - 8, `α=${a.toFixed(2)}`, { size: 15, anchor: "middle", fill: C.dim });
    s += L(850, y + 45, 880, y + 45, { stroke: C.dim, sw: 1 });
  });
  s += T(640, 540, "1. query와 모든 key의 궁합(내적)을 잰다   2. softmax로 합이 1인 예산을 나눈다   3. 그 예산대로 value를 섞어 가져온다", { size: 18, anchor: "middle" });
  s += T(640, 580, "사전 검색과 같지만, 한 서랍만 여는 게 아니라 모든 서랍을 조금씩 연다 → soft lookup", { size: 18, anchor: "middle", fill: C.acc });
  s += T(640, 640, "key와 value는 같은 서랍에 붙어 있지만 역할이 다르다: key는 '찾을 때 쓰는 라벨', value는 '꺼내 가는 내용'", { size: 16, anchor: "middle", fill: C.dim });
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
  s += T(205, 345, "decoder에서만", { size: 14, fill: C.dim, anchor: "end" }) + T(205, 365, "미래를 −∞로", { size: 14, fill: C.dim, anchor: "end" });
  // right flow
  s += T(860, 650, "Q", { size: 22, anchor: "middle", fill: C.q, w: 650 }) + T(960, 650, "K", { size: 22, anchor: "middle", fill: C.k, w: 650 }) + T(1060, 650, "V", { size: 22, anchor: "middle", fill: C.v, w: 650 });
  [[860, C.q], [960, C.k], [1060, C.v]].forEach(([x, col]) => { s += L(x, 630, x, 575, { arrow: true }); for (let h = 0; h < 3; h++) s += R(x - 45 + h * 6, 505 - h * 6, 90, 44, { stroke: col, sw: 1.5, fill: C.panel }); s += T(x + 6, 533 - 12, "Linear", { size: 16, anchor: "middle", fill: col }); s += L(x, 499, x, 440, { arrow: true }); });
  for (let h = 0; h < 3; h++) s += R(820 + h * 6, 370 - h * 6, 280, 60, { stroke: C.fg, sw: 1.5, fill: C.panel });
  s += T(966, 395, "Scaled Dot-Product Attention", { size: 17, anchor: "middle" }) + T(1150, 360, "× h = 8", { size: 20, fill: C.acc, w: 650 });
  s += L(960, 364, 960, 300, { arrow: true }) + box(960, 275, 200, 46, "Concat  (8 × 64 = 512)");
  s += L(960, 252, 960, 195, { arrow: true }) + box(960, 170, 160, 46, "Linear  W^O");
  s += L(960, 147, 960, 90, { arrow: true }) + T(960, 80, "output (512)", { size: 18, anchor: "middle", fill: C.dim });
  s += T(640, 700, "논문 Figure 2를 다시 그린 것. 왼쪽 부품 하나를 오른쪽에서 여덟 번 병렬로 쓴다. 각 head는 512 → 64로 투영하므로 총 연산은 head 하나와 같다.", { size: 15, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- Figure 1 recreated (static)
FIG.fig1 = (() => {
  let s = svgOpen + defs;
  const blk = (x, y, w, label, col) => R(x - w / 2, y - 20, w, 40, { stroke: col, sw: 1.5, fill: C.panel }) + T(x, y + 6, label, { size: 15, anchor: "middle", fill: col });
  // encoder
  const ex = 380, dx = 860;
  s += R(ex - 150, 160, 300, 260, { stroke: C.q, sw: 1.5, fill: "rgba(88,196,221,0.04)" }) + T(ex - 140, 150, "Encoder  × 6", { size: 18, fill: C.q, w: 650 });
  s += blk(ex, 380, 220, "Multi-Head Self-Attention", C.q) + blk(ex, 320, 220, "Add & Norm", C.dim) + blk(ex, 260, 220, "Feed Forward", C.q) + blk(ex, 200, 220, "Add & Norm", C.dim);
  s += L(ex, 540, ex, 402, { arrow: true }) + L(ex, 180, ex, 120, { arrow: true });
  s += `<circle cx="${ex}" cy="500" r="16" fill="none" stroke="${C.pos}" stroke-width="2"/>` + T(ex, 506, "+", { size: 20, anchor: "middle", fill: C.pos }) + T(ex - 30, 506, "PE", { size: 15, anchor: "end", fill: C.pos });
  s += R(ex - 90, 560, 180, 40, { stroke: C.fg }) + T(ex, 586, "Input Embedding", { size: 15, anchor: "middle" }) + T(ex, 640, "소스 토큰", { size: 16, anchor: "middle", fill: C.dim });
  // decoder
  s += R(dx - 150, 100, 300, 320, { stroke: C.k, sw: 1.5, fill: "rgba(255,134,47,0.04)" }) + T(dx - 140, 90, "Decoder  × 6", { size: 18, fill: C.k, w: 650 });
  s += blk(dx, 380, 220, "Masked Multi-Head Self-Attn", C.k) + blk(dx, 325, 220, "Add & Norm", C.dim) + blk(dx, 270, 220, "Multi-Head Cross-Attention", C.v) + blk(dx, 215, 220, "Add & Norm", C.dim) + blk(dx, 160, 220, "Feed Forward", C.k) + blk(dx, 120, 220, "Add & Norm", C.dim);
  s += L(dx, 540, dx, 402, { arrow: true });
  s += `<circle cx="${dx}" cy="500" r="16" fill="none" stroke="${C.pos}" stroke-width="2"/>` + T(dx, 506, "+", { size: 20, anchor: "middle", fill: C.pos }) + T(dx + 30, 506, "PE", { size: 15, fill: C.pos });
  s += R(dx - 90, 560, 180, 40, { stroke: C.fg }) + T(dx, 586, "Output Embedding", { size: 15, anchor: "middle" }) + T(dx, 640, "타깃 토큰 (한 칸 오른쪽으로 민 것)", { size: 16, anchor: "middle", fill: C.dim });
  // cross arrows encoder -> decoder cross-attn
  s += `<path d="M ${ex} 120 L ${ex} 60 L ${dx - 260} 60 L ${dx - 260} 270 L ${dx - 112} 270" fill="none" stroke="${C.v}" stroke-width="2" marker-end="url(#arr)"/>` + T(dx - 250, 255, "K, V", { size: 15, fill: C.v });
  s += T(dx + 125, 292, "Q", { size: 15, fill: C.q });
  // output
  s += L(dx, 100, dx, 60, { arrow: true }) + R(dx - 70, 20, 140, 36, { stroke: C.v }) + T(dx, 44, "Linear + Softmax", { size: 14, anchor: "middle", fill: C.v }) + T(dx + 90, 44, "→ 다음 토큰 확률", { size: 15, fill: C.dim });
  // legend of the three attentions
  s += T(100, 670, "① encoder self-attn: 소스가 소스를 본다", { size: 15, fill: C.q }) + T(480, 670, "② masked self-attn: 타깃이 자기 앞만 본다", { size: 15, fill: C.k }) + T(900, 670, "③ cross-attn: Q는 디코더, K·V는 인코더", { size: 15, fill: C.v });
  s += T(640, 705, "논문 Figure 1을 다시 그린 것", { size: 14, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- alignment matrix from the trained model
FIG.alignment = (A, Aalt, src, srcAlt, tgt) => {
  const cell = 64;
  const grid = (M, x0, y0, cols, title) => {
    let g = T(x0 + cols.length * cell / 2, y0 - 70, title, { size: 22, anchor: "middle", w: 650 });
    cols.forEach((w, j) => g += T(x0 + j * cell + cell / 2, y0 - 14, w, { size: 15, anchor: "middle", fill: C.k }));
    M.forEach((row, i) => { g += T(x0 - 12, y0 + i * cell + cell / 2 + 5, tgt[i], { size: 15, anchor: "end", fill: C.q }); row.forEach((a, j) => { g += R(x0 + j * cell + 1, y0 + i * cell + 1, cell - 2, cell - 2, { rx: 4, fill: heat(a) }) + T(x0 + j * cell + cell / 2, y0 + i * cell + cell / 2 + 5, a.toFixed(2), { size: 13, anchor: "middle", fill: a > 0.5 ? "#fff" : C.dim }); }); });
    return g;
  };
  let s = svgOpen + defs + T(640, 50, "학습된 4차원 모델의 attention map (행: 출력 단계, 열: 소스 단어)", { size: 26, anchor: "middle", w: 650 });
  s += grid(A, 140, 180, src, "the animal crossed the street") + grid(Aalt, 760, 180, srcAlt, "the animal crossed the bridge");
  s += T(640, 600, "명사를 내는 2단계(tier)와 5단계(Straße/Brücke)에서만 날카롭고, 문법어(das, überquerte, die)에서는 흩어진다", { size: 18, anchor: "middle" });
  s += T(640, 636, "두 표의 1~4행은 같다: 디코더 상태가 같으므로. 5행만 소스 명사를 따라간다", { size: 18, anchor: "middle", fill: C.acc });
  s += T(640, 690, "논문 부록 Figure 3–5(it → animal 등)가 이것의 512차원·8 head 버전이다", { size: 15, anchor: "middle", fill: C.dim });
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
  let s = svgOpen + T(640, 50, "BLEU on WMT 2014 (논문 Table 2)", { size: 28, anchor: "middle", w: 650 });
  s += panel(de, 60, "English → German", 22, 30) + panel(fr, 760, "English → French", 36, 44);
  s += `<rect x="440" y="610" width="14" height="14" fill="${C.s1}"/>` + T(462, 622, "이전 모델 (단일 · ensemble)", { size: 15, fill: C.dim }) + `<rect x="700" y="610" width="14" height="14" fill="${C.s2}"/>` + T(722, 622, "Transformer", { size: 15, fill: C.dim });
  s += T(640, 670, "big: En→De 28.4 (이전 최고 +2.0), En→Fr 41.8 — 학습 FLOPs는 이전 최고의 1/4 미만 (base 3.3×10¹⁸, big 2.3×10¹⁹)", { size: 16, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- heads ablation (Table 3 row A)
FIG.heads = (() => {
  const data = [[1, 24.9], [4, 25.5], [8, 25.8], [16, 25.8], [32, 25.4]];
  const x0 = 260, y0 = 560, w = 760, h = 360, lo = 24.5, hi = 26.2;
  const X = (i) => x0 + 80 + i * (w - 160) / 4, Y = (v) => y0 - (v - lo) / (hi - lo) * h;
  let s = svgOpen + T(640, 50, "Head 수에 따른 BLEU (newstest2013 dev, Table 3 row A)", { size: 26, anchor: "middle", w: 650 });
  for (let v = 24.5; v <= 26.2; v += 0.5) s += L(x0, Y(v), x0 + w, Y(v), { stroke: C.line, sw: 1 }) + T(x0 - 12, Y(v) + 5, v.toFixed(1), { size: 14, anchor: "end", fill: C.dim });
  let path = "";
  data.forEach(([hh, v], i) => { path += (i ? "L" : "M") + `${X(i)} ${Y(v)} `; });
  s += `<path d="${path}" fill="none" stroke="${C.s1}" stroke-width="2" stroke-linejoin="round"/>`;
  data.forEach(([hh, v], i) => { const hero = hh === 8; s += `<circle cx="${X(i)}" cy="${Y(v)}" r="${hero ? 8 : 6}" fill="${hero ? C.s2 : C.s1}" stroke="${C.bg}" stroke-width="2"/>` + T(X(i), y0 + 30, `h = ${hh}`, { size: 16, anchor: "middle", fill: C.dim }) + T(X(i), Y(v) - 16, v.toFixed(1), { size: 15, anchor: "middle", fill: hero ? C.fg : C.dim }); });
  s += T(X(0) + 20, Y(24.9) + 40, "head 1개: 0.9 BLEU 손실", { size: 15, fill: C.dim }) + T(X(4) - 20, Y(25.4) + 40, "32개: 각 head가 16차원 → 용량 부족", { size: 15, anchor: "end", fill: C.dim });
  s += T(640, 650, "d_model=512 고정, h·d_k=512 유지. 논문은 8을 택했다.", { size: 16, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();

// ---------------------------------------------------------------- hyperparameters
FIG.hparams = (() => {
  const rows = [["N (층 수)", "6", "6"], ["d_model", "512", "1024"], ["d_ff", "2048", "4096"], ["h (heads)", "8", "16"], ["d_k = d_v", "64", "64"], ["dropout", "0.1", "0.3"], ["학습 step", "100k", "300k"], ["학습 시간 (8× P100)", "12시간", "3.5일"], ["파라미터", "65M", "213M"], ["BLEU En→De / En→Fr", "27.3 / 38.1", "28.4 / 41.8"]];
  let s = svgOpen + T(640, 50, "Base vs Big (논문 Table 3 마지막 행)", { size: 28, anchor: "middle", w: 650 });
  const x = [260, 640, 920], y0 = 120;
  s += T(x[1], y0, "base", { size: 22, anchor: "middle", fill: C.q, w: 650 }) + T(x[2], y0, "big", { size: 22, anchor: "middle", fill: C.k, w: 650 });
  rows.forEach(([k, a, b], i) => { const y = y0 + 48 + i * 48; s += L(220, y + 14, 1060, y + 14, { stroke: C.line, sw: 1 }) + T(x[0], y, k, { size: 19, fill: C.dim }) + T(x[1], y, a, { size: 20, anchor: "middle" }) + T(x[2], y, b, { size: 20, anchor: "middle" }); });
  s += T(640, 680, "공통: Adam(β₂=0.98) + warmup 4000, label smoothing 0.1, beam 4, length penalty 0.6, checkpoint averaging(5 / 20)", { size: 15, anchor: "middle", fill: C.dim });
  return s + "</svg>";
})();
