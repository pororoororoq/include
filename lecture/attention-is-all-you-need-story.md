# Attention Is All You Need — a 60‑minute story

A lecture plan built as a narrative, with a worked numeric example and a shot list of
Manim animations for each idea. Paper: Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez,
Kaiser, Polosukhin. *Attention Is All You Need.* NeurIPS 2017 (arXiv 1706.03762, June 2017).

---

## 0. The story in one paragraph

For years, machines read sentences the way a person reads a scroll through a keyhole: one
word at a time, carrying everything they had seen so far in a single, ever‑more‑crowded
memory. Attention was first invented in 2014 as a crutch for that reader, a way to glance
back at the scroll. In 2017 a team at Google asked a reckless question: what if the glance
*is* the reading? Throw away the keyhole, let every word look at every other word at once,
and give the model a cheap trick so it still knows what order the words came in. The result
trained in twelve hours on eight GPUs, beat every translation system before it, and became the
blueprint for essentially every large AI model that followed.

Tell the lecture as four acts: **the bottleneck**, **the glance**, **the leap**, **the aftermath**.

---

## Timing (60 min)

| Minutes | Act | Beat |
|---|---|---|
| 0–8 | 1. The bottleneck | Seq2seq, the single vector, the two curses of recurrence |
| 8–15 | 2. The glance | Bahdanau/Luong attention, convolutions, the dangerous question |
| 15–40 | 3. The leap | Self‑attention mechanics (10), multi‑head (5), position (4), full block & decoder (6) |
| 40–48 | 3b. Proof | Training recipe, results, ablations |
| 48–55 | 4. The aftermath | BERT/GPT/ViT, what was kept and what was replaced |
| 55–60 | Q&A | |

---

## Act 1 — The bottleneck (2014)

**Scene.** Translate "The animal didn't cross the street because it was too tired" into German.
A sentence is a *sequence*; its length varies; meaning depends on words far apart ("it" ↔ "animal").

**Seq2seq (Sutskever et al. 2014; Cho et al. 2014).** An encoder RNN (LSTM/GRU) eats the
source one token at a time and updates a hidden state. The *last* hidden state is handed to a
decoder RNN that emits the target one token at a time.

Two curses follow directly from the design:

1. **The single vector.** The whole sentence must be squeezed into one fixed‑size vector.
   Ray Mooney, 2014: *"You can't cram the meaning of a whole %&!$# sentence into a single
   $&!#* vector."* Quality collapses on long sentences.
2. **The sequential path.** Information from word 1 reaches word 50 only by passing through
   49 state updates. Gradients shrink along the path (LSTMs soften but do not remove this),
   and nothing can be computed in parallel across time: the GPU idles.

Hold onto both curses; the whole paper is the answer to them.

> **Animation A1 — The funnel.** Words of a long sentence slide one by one into a single box
> labelled `h_T`. Each arrival dims the earlier words inside the box. Then the decoder tries
> to pull words back out of the box and the far‑away ones come out blurred or wrong.
> Run it twice: a 5‑word sentence (fine) and a 40‑word sentence (collapse).

> **Animation A2 — Path length.** Tokens in a row. A pulse of light travels from token 1 to
> token n, lighting one node per frame while a counter ticks `1, 2, …, n`. Keep this on the
> shelf; you will replay it in Act 3 with one direct edge and the counter stuck at `1`.

---

## Act 2 — The glance (2014–2016)

**Bahdanau, Cho, Bengio (2014, ICLR 2015).** Keep *all* encoder states, not just the last.
At each decoding step the decoder computes a relevance score between its current state and
each encoder state, turns the scores into weights with a softmax, and reads a weighted sum.
They called it "alignment"; we call it attention. The single‑vector curse is lifted:
long‑sentence quality stops collapsing. Their scoring function was a tiny feed‑forward net
("additive attention").

**Luong et al. 2015.** Showed a plain dot product between decoder and encoder states works
("multiplicative attention"): cheaper, one matrix multiply.

**What everyone still believed.** Attention was a *patch bolted onto an RNN*. The recurrence
was the model; attention was the glance back. Google's production system (GNMT, 2016) was
8‑layer LSTMs + attention. The sequential curse was untouched.

**The convolution camp (ByteNet 2016, ConvS2S 2017).** Replace recurrence with stacked
convolutions: parallel across time, but a kernel of width k needs about `log_k(n)` layers
before two distant words can interact. Shorter path than an RNN, still not direct.

**Self‑attention already existed in small ways** (Cheng et al. 2016 "intra‑attention";
Parikh et al. 2016 decomposable attention; Lin et al. 2017). People had let a sentence attend
to itself, but always alongside something else.

**The dangerous question** (Jakob Uszkoreit's idea at Google): if attention is what fixes the
RNN, what happens if we delete the RNN and keep *only* attention? Most colleagues expected
it to fail. The title, suggested by Llion Jones, is a Beatles joke. The eight authors are
listed in random order with a footnote that everyone contributed equally.

> **Animation A3 — The glance.** Decoder box producing the German word `Straße`. Dotted lines
> fan back to every English token; line thickness animates to the attention weights so
> `street` becomes thick and the rest fade. Then the weighted encoder vectors slide together
> and sum into one context vector that feeds the decoder.

> **Animation A4 — Three ways to connect word 1 to word n.** Three rows of tokens:
> RNN (chain, path n), Conv (tree of width‑3 kernels, path log₃n), Attention (one edge, path 1).
> Animate the path on all three simultaneously with a counter per row. This is Table 1 of the
> paper made visual.

---

## Act 3 — The leap (the paper)

### 3.1 Self‑attention as a soft lookup (10 min)

Set up the metaphor before any symbols. Every token writes three things about itself:

- a **query** `q`: *what am I looking for?*
- a **key** `k`: *what do I contain, as seen by others?*
- a **value** `v`: *what will I hand over if someone picks me?*

All three are learned linear maps of the same input vector: `q = xW^Q`, `k = xW^K`, `v = xW^V`.
A token's output is a weighted average of everyone's values, weighted by how well its query
matches their keys. It is a dictionary lookup, except the match is *soft*: you get a bit of
every entry instead of exactly one.

```
Attention(Q, K, V) = softmax( Q Kᵀ / √d_k ) V
```

Read the formula right‑to‑left as a three‑step story:

1. **Score** — `Q Kᵀ`: every query dotted with every key. Dot product = "how aligned are we?"
2. **Normalise** — `softmax(· / √d_k)`, row by row: scores become positive weights summing to 1.
3. **Blend** — `(weights) V`: each token's new vector is a mixture of the values it chose.

**Why divide by √d_k?** A dot product of two random `d_k`‑dimensional unit‑variance vectors
has variance `d_k`. At `d_k = 64` raw scores are ~8× wider than at `d_k = 1`. Big scores push
softmax into a near one‑hot spike where its gradient is almost zero and learning stalls.
Dividing by `√d_k` brings the variance back to 1 regardless of width. (The paper notes
additive attention beat *unscaled* dot‑product attention at large `d_k`; the scaling closes
the gap while keeping the speed of a matrix multiply.)

#### A worked micro‑example (put real numbers on the slide)

Three tokens, `d_k = 2`, so people can check arithmetic by eye.

```
        q            k            v
The   [1, 0]       [1, 0]       [1, 0, 0]
cat   [0, 1]       [0, 1]       [0, 1, 0]
sat   [1, 1]       [1, 1]       [0, 0, 1]
```

Query of `sat` against all keys: `sat·The = 1`, `sat·cat = 1`, `sat·sat = 2`.
Scale by `√2 ≈ 1.414`: `[0.71, 0.71, 1.41]`.
Softmax: `[0.26, 0.26, 0.48]`.
Output for `sat` = `0.26·v_The + 0.26·v_cat + 0.48·v_sat = [0.26, 0.26, 0.48]`.

The new `sat` is "half itself, a quarter each of the others". Then show the same thing as the
full matrix: a 3×3 score grid, row‑softmax to a 3×3 heat map, times the 3×3 `V`.

> **Animation A5 — The lookup (the centrepiece).** Left: one query arrow `q_sat`. Three key
> arrows `k_The, k_cat, k_sat` appear. For each key, drop the perpendicular from `q` onto `k`
> so the dot product is literally the shadow's length; a number pops up at the shadow.
> The three numbers fly right and become bars. Bars pass through a `softmax` gate: negative
> bars flip positive, all rescale so their total height is one stacked unit. Then three value
> arrows shrink by their weights and add tip‑to‑tail into the output arrow. Land on the
> formula with each term coloured to match the step it just performed.

> **Animation A6 — Why √d_k.** A histogram of dot products between random vectors as a `d_k`
> slider moves 4 → 16 → 64 → 256: the histogram widens like a bell being stretched.
> Beside it, the softmax of a sample row collapses into one spike. Then switch the divisor on
> and the histogram snaps back to a fixed width at every `d_k`.

> **Animation A7 — Matrix view.** `Q` (rows) and `Kᵀ` (columns) on screen. Highlight one row
> and one column; their dot product fills one cell of `QKᵀ`. Sweep through the grid. Then each
> row of the grid normalises into a heat map (cells recolour; row sums display `1.00`).
> Finally each heat‑map row reaches across to `V` and pulls a blend of its rows into one
> output row. End by overlaying the heat map on the sentence so cells become word‑to‑word
> links, and show the paper's own figure: `it` lighting up `animal`.

### 3.2 Multi‑head attention (5 min)

One attention pattern is one relationship: "who is my subject?" But a word also wants
"who modifies me?", "who do I refer to?", "who is adjacent?". Averaging all of those into a
single softmax blurs them. So run `h = 8` attentions in parallel, each with its own small
`W^Q_i, W^K_i, W^V_i` projecting 512 dims down to `d_k = d_v = 64`, then concatenate the eight
64‑dim outputs back to 512 and mix with `W^O`.

```
MultiHead(Q,K,V) = Concat(head_1, …, head_h) W^O,   head_i = Attention(QW^Q_i, KW^K_i, VW^V_i)
```

Crucially the cost is the same as one 512‑dim head: you split the width, you do not multiply
it. The appendix figures show heads that specialise: one tracks coreference (`its` → `Law`),
one tracks local syntax, one looks almost diagonal.

> **Animation A8 — Splitting the vector.** A 512‑tall vector splits into 8 colour bands.
> Each band flows into its own tiny copy of A7 and produces its own small heat map; show three
> with visibly different patterns (adjacent diagonal, "all to the verb", "pronoun → noun").
> The eight outputs stack back into one tall vector and pass through `W^O`.

### 3.3 Position: the bag‑of‑words problem (4 min)

Here is the catch nobody mentions until it bites: the attention formula has no idea where a
token is. Shuffle the input rows and the output rows shuffle identically; the model sees a
*bag* of words. "Dog bites man" and "man bites dog" are the same input.

Fix: add a position vector to each embedding before the first layer. The paper uses fixed
sinusoids:

```
PE(pos, 2i)   = sin( pos / 10000^(2i/d_model) )
PE(pos, 2i+1) = cos( pos / 10000^(2i/d_model) )
```

Intuition: each pair of dimensions is a clock hand turning at its own speed; early dimensions
spin fast (fine position), late dimensions crawl (coarse position). It is a smooth analogue
of counting in binary. Two reasons they chose this: (1) moving from position `pos` to
`pos + k` is a *rotation* of each (sin, cos) pair by a fixed angle that depends only on `k`,
so a linear layer can learn "look 3 tokens back"; (2) it might extrapolate to lengths longer
than training. Learned positional embeddings gave nearly identical BLEU (Table 3, row E).

> **Animation A9 — Shuffle test.** Run A7 on a sentence, record the output. Shuffle the input
> words, run again: the output rows are the same set, just permuted. Flash "no notion of
> order". Then add the position waves and re‑shuffle: now the outputs differ.

> **Animation A10 — Clock hands / sinusoid heat map.** Draw the `position × dimension` heat
> map of `PE` building column by column: leftmost columns stripe rapidly, rightmost barely
> change. Then pick dimensions (2i, 2i+1) and show them as a rotating unit vector; step `pos`
> by `+3` and show the same rotation angle regardless of start position.

### 3.4 The full block and the decoder (6 min)

**Encoder layer** (×6): `x → MultiHeadSelfAttn → add & LayerNorm → FFN → add & LayerNorm`.

- **Position‑wise FFN**: `FFN(x) = max(0, xW₁ + b₁)W₂ + b₂`, 512 → 2048 → 512, applied to every
  token independently. Story: attention *gathers* information from others; the FFN is where
  each token *thinks about* what it gathered. Same weights at every position, different per layer.
- **Residual connection**: the input is added back to the output (`x + Sublayer(x)`). A highway
  that lets gradients and the original signal pass straight through six layers.
- **LayerNorm**: re‑centre and re‑scale each token vector so activations stay in a healthy range.
  (Modern models moved the norm *before* the sublayer, "pre‑norm"; the paper is post‑norm.)

**Decoder layer** (×6) has three sublayers:

1. **Masked self‑attention** over the target so far. The mask sets future positions' scores to
   `−∞` before the softmax, so weights on the future are exactly 0. This is what lets the
   whole target be trained in one parallel pass while behaving as if generated left‑to‑right.
2. **Cross‑attention**: queries come from the decoder, keys and values from the encoder output.
   This is Bahdanau's glance, now built from the same primitive as everything else.
3. **FFN**, as above.

Then a linear layer + softmax over the vocabulary. The paper shares the weights between the
input embedding, output embedding and the final softmax, and multiplies embeddings by
`√d_model`.

Model sizes: **base** `d_model=512, h=8, d_ff=2048, N=6, dropout 0.1`, 65M params.
**big** `d_model=1024, h=16, d_ff=4096, dropout 0.3`, 213M params.

> **Animation A11 — The mask.** A 6×6 score grid; a triangle slides over the upper‑right half
> and its cells turn to `−∞`, then after softmax to `0`. Show the first row attending only to
> itself, the last row attending to everything.

> **Animation A12 — Residual highway.** A token vector approaches a block; it splits into two
> copies, one goes through the block (changes colour/shape), one bypasses on a straight rail,
> they rejoin and add. Then LayerNorm: a scatter of vectors with different magnitudes all
> snap onto a common sphere.

> **Animation A13 — Full data flow.** Build Figure 1 live. Source tokens rise through six
> encoder blocks. Target tokens rise through decoder blocks; at each decoder block, arrows
> for cross‑attention reach *left* into the encoder's final output. Emit one output token,
> feed it back to the bottom of the decoder, repeat.

### 3b. Training recipe and proof (8 min)

- **Data**: WMT 2014 English→German, 4.5M sentence pairs, byte‑pair encoding, 37k shared
  vocabulary. English→French, 36M pairs, 32k word‑piece vocabulary.
- **Hardware**: one machine, 8 NVIDIA P100s. Base: 100k steps ≈ 12 hours. Big: 300k steps ≈ 3.5 days.
- **Optimiser**: Adam (β₁=0.9, β₂=0.98, ε=1e‑9) with the now‑famous warmup‑then‑decay schedule
  `lr = d_model^(-0.5) · min(step^(-0.5), step · warmup^(-1.5))`, warmup 4000 steps.
- **Regularisation**: dropout 0.1 on every sublayer output and on embeddings+PE; label smoothing
  0.1 (hurts perplexity, improves BLEU).
- **Inference**: beam search size 4, length penalty α=0.6; average the last 5 (base) or 20 (big)
  checkpoints.

**Results (Table 2).** En→De: big 28.4 BLEU, about 2 BLEU above the previous best including
ensembles; base 27.3 already beats all prior single models. En→Fr: big 41.8, at under a
quarter of the training FLOPs of the previous best.

**Ablations (Table 3), told as what the authors learned:**
- 1 head is 0.9 BLEU worse than 8; 32 heads is also worse: too many tiny heads lose capacity.
- Shrinking `d_k` hurts: matching queries to keys is not a trivial job.
- Bigger is better (this is the sentence that launched the scaling era).
- Dropout matters a lot; learned positions ≈ sinusoids.

**Generalisation.** Trained on Penn Treebank constituency parsing (40k sentences) with no
task‑specific tuning, it beat most prior parsers (91.3 F1 WSJ‑only; 92.7 semi‑supervised).

> **Animation A14 — Complexity tiles.** For n tokens and width d, tile the cost of one layer:
> self‑attention draws an `n × n` grid of thickness d; recurrence draws `n` tiles of size `d × d`.
> Slide n from 10 to 1000 with d = 512 fixed: attention wins while `n < d`, loses after. This
> seeds the "long context" discussion in Act 4.

> **Animation A15 — Warmup curve.** Plot the learning‑rate schedule being drawn as a curve,
> with the two regimes labelled; a dot rides along as the step counter increases.

---

## Act 4 — The aftermath (2018 → today)

The architecture outlived its task. Translation turned out to be the least of it.

- **2018, encoder only**: BERT keeps the encoder stack, pretrains with masked tokens, fine‑tunes
  for everything. **2018, decoder only**: GPT keeps the masked decoder, pretrains by predicting
  the next token. GPT‑2 (2019), GPT‑3 (2020) show "bigger is better" has a very long runway.
- **2020**: Vision Transformer treats 16×16 image patches as tokens; the same block works on
  pixels. AlphaFold2 uses attention over residue pairs. Audio, protein, code, robotics follow.
- **Today**: essentially every frontier model is a decoder‑only Transformer.

What the field kept and what it replaced (good closing slide):

| Kept | Replaced |
|---|---|
| Scaled dot‑product attention, Q/K/V | Sinusoidal PE → rotary (RoPE) / ALiBi |
| Multi‑head, residuals, FFN | Post‑norm → pre‑norm, LayerNorm → RMSNorm |
| Warmup schedule, Adam | ReLU FFN → SwiGLU |
| Masked decoding | Encoder‑decoder → decoder only |
| | Full KV per head → multi‑query / grouped‑query attention |
| | Naive O(n²) memory → FlashAttention (exact, IO‑aware) |

The one genuine limit the paper names is quadratic cost in sequence length; a decade of
"efficient attention" research is the footnote to that sentence.

Closing beat: all eight authors have since left Google to found or join companies built on
the paper. The title was a joke that turned out to be a prophecy.

> **Animation A16 — Morph.** Take the Figure‑1 encoder‑decoder from A13. Fade the decoder:
> BERT. Restore it and fade the encoder, cross‑attention vanishes: GPT. Replace the word
> tokens with image patches: ViT. Stack the blocks taller and taller until they leave the frame.

---

## Visual conventions to keep every animation consistent

- One colour per role, everywhere: **queries** blue, **keys** orange, **values** green,
  **attention weights** a grey→red heat ramp, **positions** purple.
- Always show the softmax row sum as a live `1.00` so the "weights are a budget" idea sticks.
- Use the same 3‑token example (`The cat sat`) in A5, A7, A9, A11 so viewers never re‑learn the data.
- Reuse A2's path counter in A4 and A14: callbacks make the story feel designed, not listed.

## Manim starter skeleton for A5 (untested; Manim Community syntax)

```python
from manim import *
import numpy as np

Q_COLOR, K_COLOR, V_COLOR = BLUE, ORANGE, GREEN

class SoftLookup(Scene):
    def construct(self):
        q = np.array([1, 1]); keys = [np.array([1, 0]), np.array([0, 1]), np.array([1, 1])]
        names = ["The", "cat", "sat"]
        plane = NumberPlane(x_range=[-0.5, 2], y_range=[-0.5, 2], x_length=4, y_length=4).to_edge(LEFT)
        q_arrow = Arrow(plane.c2p(0, 0), plane.c2p(*q), buff=0, color=Q_COLOR)
        self.play(Create(plane), GrowArrow(q_arrow))

        scores = []
        for k, name in zip(keys, names):
            k_arrow = Arrow(plane.c2p(0, 0), plane.c2p(*k), buff=0, color=K_COLOR)
            s = float(q @ k)
            label = MathTex(f"q\\cdot k_{{{name}}}={s:.0f}").scale(0.6).next_to(k_arrow.get_end(), UR, buff=0.1)
            self.play(GrowArrow(k_arrow), FadeIn(label))
            scores.append(s)

        scaled = np.array(scores) / np.sqrt(2)
        weights = np.exp(scaled) / np.exp(scaled).sum()
        raw_chart = BarChart(scores, bar_names=names, y_range=[0, 2.2, 1]).scale(0.5).to_edge(RIGHT).shift(UP)
        self.play(Create(raw_chart))
        soft_chart = BarChart(list(weights), bar_names=names, y_range=[0, 1, 0.5]).scale(0.5).move_to(raw_chart)
        self.play(Transform(raw_chart, soft_chart),
                  Write(MathTex("\\text{softmax}(\\cdot/\\sqrt{d_k})").scale(0.6).next_to(soft_chart, UP)))

        vals = [np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])]
        out = sum(w * v for w, v in zip(weights, vals))
        out_tex = MathTex(*(f"{w:.2f}\\,v_{{{n}}} +" for w, n in zip(weights, names)))
        out_tex[-1][-1].set_opacity(0)
        out_tex.scale(0.6).to_edge(DOWN)
        self.play(Write(out_tex))
        self.play(Write(MathTex(f"= [{out[0]:.2f}, {out[1]:.2f}, {out[2]:.2f}]").scale(0.6).next_to(out_tex, RIGHT)))
        self.wait()
```

## Sources to cite on the slides

- Vaswani et al. 2017, *Attention Is All You Need*, NeurIPS.
- Sutskever, Vinyals, Le 2014, *Sequence to Sequence Learning with Neural Networks*.
- Cho et al. 2014, *Learning Phrase Representations using RNN Encoder–Decoder*.
- Bahdanau, Cho, Bengio 2015, *Neural Machine Translation by Jointly Learning to Align and Translate*.
- Luong, Pham, Manning 2015, *Effective Approaches to Attention‑based NMT*.
- Wu et al. 2016, *Google's Neural Machine Translation System* (GNMT).
- Gehring et al. 2017, *Convolutional Sequence to Sequence Learning*; Kalchbrenner et al. 2016, *ByteNet*.
- Devlin et al. 2018 (BERT); Radford et al. 2018 (GPT); Dosovitskiy et al. 2020 (ViT).
