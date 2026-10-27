"""
A tiny attention encoder-decoder (Bahdanau-style glance) small enough to show every number.

d = 4 dimensional states, per-word encoder states, a tanh RNN decoder, bilinear attention.
Trained by plain gradient descent (numerical gradients, it's ~240 parameters) on nine
English→German pairs of the form "the <subj> crossed the <obj>" so the decoder is forced
to look at the source for the two nouns.

    python lecture/manim/tiny_nmt.py [seed] [out.json]   # trains, prints the trace, writes JSON if it fits all pairs

The JSON holds the encoder states, every decoder step (scores, weights, context, state,
output distribution) for the sentence used in the animation, plus the "bridge" variant.
"""
import json, sys, numpy as np
from pathlib import Path

D = 4
SRC = ["the", "animal", "child", "horse", "crossed", "street", "bridge", "border"]
TGT = ["<s>", "das", "tier", "kind", "pferd", "überquerte", "die", "straße", "brücke", "grenze"]
SUBJ = {"animal": "tier", "child": "kind", "horse": "pferd"}
OBJ = {"street": "straße", "bridge": "brücke", "border": "grenze"}
PAIRS = [([ "the", s, "crossed", "the", o], ["das", SUBJ[s], "überquerte", "die", OBJ[o]]) for s in SUBJ for o in OBJ]
si = {w: i for i, w in enumerate(SRC)}; ti = {w: i for i, w in enumerate(TGT)}

SHAPES = {"E_src": (len(SRC), D), "E_tgt": (len(TGT), D), "W_x": (D, D), "b_init": (D,),
          "W_s": (D, D), "W_y": (D, D), "W_c": (D, D), "b": (D,), "W_a": (D, D), "W_out": (D, len(TGT)), "b_out": (len(TGT),)}


def unpack(theta):
    P, k = {}, 0
    for n, sh in SHAPES.items():
        sz = int(np.prod(sh)); P[n] = theta[k:k + sz].reshape(sh); k += sz
    return P


def softmax(x):
    e = np.exp(x - x.max()); return e / e.sum()


def forward(P, src, tgt=None, trace=False):
    """Teacher-forced forward pass. Returns (loss, trace dict)."""
    # ---- encoder: keep every state
    # per-word states (no recurrence) so the decoder can only get a word by attending to its position;
    # a bidirectional RNN encoder would add context to each h_j but also lets information leak sideways
    H = np.array([np.tanh(P["W_x"] @ P["E_src"][si[w]]) for w in src])
    # ---- decoder
    s = np.tanh(P["b_init"])              # learned constant start: no h_T shortcut, everything must come through attention
    y_prev = "<s>"; loss = 0.0; steps = []; out = []
    T = len(tgt) if tgt is not None else 5
    for t in range(T):
        e = H @ (P["W_a"] @ s)                 # score each encoder state against the current decoder state
        a = softmax(e)                         # normalise
        c = a @ H                              # blend → context
        s_new = np.tanh(P["W_s"] @ s + P["W_y"] @ P["E_tgt"][ti[y_prev]] + P["W_c"] @ c + P["b"])
        p = softmax(P["W_out"].T @ s_new + P["b_out"])
        pred = TGT[int(p.argmax())]
        if tgt is not None:
            loss -= np.log(p[ti[tgt[t]]] + 1e-12)
        if trace:
            steps.append({"t": t + 1, "s_prev": s.tolist(), "y_prev": y_prev, "scores": e.tolist(), "alpha": a.tolist(),
                          "context": c.tolist(), "s_new": s_new.tolist(), "probs": p.tolist(), "pred": pred,
                          "target": tgt[t] if tgt is not None else None})
        out.append(pred)
        y_prev = tgt[t] if tgt is not None else pred
        s = s_new
    return loss, {"src": src, "H": H.tolist(), "s0": np.tanh(P["b_init"]).tolist(), "steps": steps, "output": out}


def total_loss(theta):
    P = unpack(theta); return sum(forward(P, s, t)[0] for s, t in PAIRS)


def train(seed=0, iters=1500, lr=0.05, eps=1e-6, verbose=True):
    rng = np.random.default_rng(seed)
    n = sum(int(np.prod(sh)) for sh in SHAPES.values())
    theta = rng.normal(0, 0.5, n)
    m = np.zeros(n); v = np.zeros(n)            # Adam
    for it in range(1, iters + 1):
        base = total_loss(theta); g = np.zeros(n)
        for i in range(n):                       # forward-difference gradient
            th = theta.copy(); th[i] += eps; g[i] = (total_loss(th) - base) / eps
        m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g * g
        theta -= lr * (m / (1 - 0.9 ** it)) / (np.sqrt(v / (1 - 0.999 ** it)) + 1e-8)
        if verbose and (it % 100 == 0 or it == 1):
            print(f"iter {it:5d}  loss {base:8.4f}", file=sys.stderr)
        if base < 0.05:
            break
    return theta


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    theta = train(seed=seed, iters=2500)
    P = unpack(theta)
    acc = sum(forward(P, s, t)[1]["output"] == t for s, t in PAIRS)
    print(f"train pairs exact match: {acc}/{len(PAIRS)}", file=sys.stderr)
    demo_src = ["the", "animal", "crossed", "the", "street"]; demo_tgt = ["das", "tier", "überquerte", "die", "straße"]
    alt_src = ["the", "animal", "crossed", "the", "bridge"]; alt_tgt = ["das", "tier", "überquerte", "die", "brücke"]
    _, tr = forward(P, demo_src, demo_tgt, trace=True)
    _, tr_alt = forward(P, alt_src, alt_tgt, trace=True)
    out = {"D": D, "src_vocab": SRC, "tgt_vocab": TGT, "params": {k: v.tolist() for k, v in P.items()}, "demo": tr, "bridge": tr_alt}
    out["seed"] = seed
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).with_name("tiny_nmt.json")
    if acc == len(PAIRS):
        dest.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    else:
        print("not writing JSON: model did not fit all pairs", file=sys.stderr)
    # readable trace
    print("encoder states")
    for w, h in zip(demo_src, tr["H"]):
        print(f"  h_{w:<8} {np.round(h, 2)}")
    print(f"s_0 = {np.round(tr['s0'], 2)}")
    for st in tr["steps"]:
        print(f"step {st['t']}  s_prev={np.round(st['s_prev'],2)}  scores={np.round(st['scores'],2)}")
        print(f"        alpha={np.round(st['alpha'],2)}  c={np.round(st['context'],2)}")
        print(f"        s_new={np.round(st['s_new'],2)}  → '{st['pred']}' (p={max(st['probs']):.2f}, target {st['target']})")
    print("bridge variant step 5 alpha:", np.round(tr_alt["steps"][-1]["alpha"], 2), "→", tr_alt["steps"][-1]["pred"])
