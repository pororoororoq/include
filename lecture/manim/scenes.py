"""
Manim scenes for the "Attention Is All You Need" lecture.
One class per animation in lecture/attention-is-all-you-need-story.md (A1 … A16, plus A1b).

Render everything:   bash lecture/manim/render.sh
Render one scene:    manim -qm lecture/manim/scenes.py A05SoftLookup

Colour conventions (same everywhere): queries BLUE, keys ORANGE, values GREEN,
attention weights grey→red heat, positions PURPLE.
"""
from manim import *
import numpy as np

config.background_color = "#0e1116"

Q_COL, K_COL, V_COL, POS_COL = BLUE_C, ORANGE, GREEN_C, PURPLE_B
HEAT_LO, HEAT_HI = ManimColor("#2b2f3a"), ManimColor("#ff4b4b")
TOK_COL = ManimColor("#d8dee9")
DIM = ManimColor("#5a6270")

SENT = ["The", "cat", "sat"]
Q = {"The": np.array([1., 0.]), "cat": np.array([0., 1.]), "sat": np.array([1., 1.])}
K = dict(Q)
V = {"The": np.array([1., 0., 0.]), "cat": np.array([0., 1., 0.]), "sat": np.array([0., 0., 1.])}


# ----------------------------------------------------------------- helpers
def softmax(x):
    x = np.asarray(x, dtype=float)
    e = np.exp(x - x.max())
    return e / e.sum()


def heat(a):
    return interpolate_color(HEAT_LO, HEAT_HI, float(np.clip(a, 0, 1)))


def token(word, color=TOK_COL, w=1.25, h=0.62, font_size=28):
    box = RoundedRectangle(corner_radius=0.12, width=w, height=h).set_stroke(color, 2).set_fill(color, 0.08)
    lab = Text(word, font_size=font_size, color=color).move_to(box)
    return VGroup(box, lab)


def token_row(words, buff=0.25, **kw):
    return VGroup(*[token(w, **kw) for w in words]).arrange(RIGHT, buff=buff)


def title(text, font_size=34):
    return Text(text, font_size=font_size, color=WHITE).to_edge(UP, buff=0.35)


def grid(mat, cell=0.6, fmt="{:.2f}", show_values=True, font_size=18):
    """Heat-map grid; returns VGroup of rows, each row VGroup of cells (Square + optional label)."""
    mat = np.asarray(mat, dtype=float)
    rows = VGroup()
    for r in range(mat.shape[0]):
        row = VGroup()
        for c in range(mat.shape[1]):
            sq = Square(cell).set_stroke(GREY_B, 1).set_fill(heat(mat[r, c]), 0.95)
            g = VGroup(sq)
            if show_values:
                g.add(Text(fmt.format(mat[r, c]), font_size=font_size).move_to(sq))
            row.add(g)
        row.arrange(RIGHT, buff=0)
        rows.add(row)
    rows.arrange(DOWN, buff=0)
    return rows


def matrix_block(mat, color=WHITE, fmt="{:g}", font_size=24, h_buff=0.9):
    m = Matrix([[fmt.format(v) for v in row] for row in np.asarray(mat)], h_buff=h_buff,
               element_to_mobject=lambda s: Text(s, font_size=font_size))
    m.get_brackets().set_color(color)
    return m


# =========================================================== A1  The funnel
class A01Funnel(Scene):
    def run_sentence(self, words, label):
        head = title(label)
        self.play(FadeIn(head))
        box = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.6).set_stroke(TOK_COL, 2)
        box_lab = Text("h_T", font_size=30, color=TOK_COL).next_to(box, DOWN, buff=0.15)
        box_grp = VGroup(box, box_lab).shift(DOWN * 0.3)
        row = token_row(words, buff=0.12, w=0.95, h=0.5, font_size=20)
        if row.width > 12.6:
            row.scale_to_fit_width(12.6)
        row.to_edge(UP, buff=1.2)
        self.play(Create(box), FadeIn(box_lab), FadeIn(row))
        inside = VGroup()
        for i, t in enumerate(row):
            mini = t[1].copy().scale(0.75)
            anims = [t.animate.set_opacity(0.15), mini.animate.move_to(box).scale(0.9)]
            for m in inside:
                anims.append(m.animate.set_opacity(max(0.08, m.get_fill_opacity() * 0.72)))
            self.play(*anims, run_time=0.35 if len(words) > 8 else 0.6)
            inside.add(mini)
        # arrange the survivors so it looks like a crowded box
        packed = inside.copy().arrange_in_grid(cols=5, buff=0.12)
        packed.scale_to_fit_width(box.width - 0.4)
        if packed.height > box.height - 0.3:
            packed.scale_to_fit_height(box.height - 0.3)
        packed.move_to(box)
        self.play(Transform(inside, packed), run_time=0.6)
        # decoder pulls words out
        dec = Text("decoder", font_size=24, color=DIM).next_to(box, RIGHT, buff=1.4)
        arr = Arrow(box.get_right(), dec.get_left(), buff=0.1, color=DIM)
        self.play(GrowArrow(arr), FadeIn(dec))
        outs = VGroup()
        for i, w in enumerate(words):
            op = inside[i].get_fill_opacity()
            o = Text(w, font_size=20, color=TOK_COL if op > 0.3 else RED_C).set_opacity(max(op, 0.25))
            if op < 0.3:
                o = Text("?", font_size=22, color=RED_C)
            outs.add(o)
        outs.arrange(RIGHT, buff=0.15)
        if outs.width > 12.5:
            outs.scale_to_fit_width(12.5)
        outs.to_edge(DOWN, buff=0.8)
        self.play(LaggedStart(*[FadeIn(o, shift=DOWN * 0.3) for o in outs], lag_ratio=0.08))
        self.wait(1.2)
        self.play(FadeOut(VGroup(head, box_grp, row, inside, dec, arr, outs)))

    def construct(self):
        self.run_sentence(["Take", "the", "L"], "A short sentence fits in one vector")
        long = "L shortened for loss is a newly emerging term within the gen-z community and it is used as an embarrassment ritual".split()
        self.run_sentence(long, "A long sentence: early words are overwritten")


# ======================================================= A1b  Inside the cell
class A01bInsideCell(Scene):
    def construct(self):
        head = title("One RNN cell: two inputs, one output")
        self.play(FadeIn(head))
        wx = RoundedRectangle(corner_radius=0.1, width=1.3, height=0.8).set_stroke(Q_COL, 2)
        wx_l = Text("W_x", font_size=26, color=Q_COL).move_to(wx)
        wh = RoundedRectangle(corner_radius=0.1, width=1.3, height=0.8).set_stroke(K_COL, 2)
        wh_l = Text("W_h", font_size=26, color=K_COL).move_to(wh)
        VGroup(wx, wh).arrange(DOWN, buff=1.2).shift(LEFT * 2.5)
        wx_l.move_to(wx); wh_l.move_to(wh)
        plus = Circle(radius=0.3).set_stroke(WHITE, 2); plus_l = Text("+", font_size=34).move_to(plus)
        VGroup(plus, plus_l).move_to(ORIGIN + LEFT * 0.3)
        tanh = RoundedRectangle(corner_radius=0.1, width=1.3, height=0.8).set_stroke(GREEN_C, 2).shift(RIGHT * 1.6)
        tanh_l = Text("tanh", font_size=26, color=GREEN_C).move_to(tanh)
        xin = Text("x_t  (word)", font_size=24, color=Q_COL).next_to(wx, LEFT, buff=0.9)
        hin = Text("h_{t-1}  (memory)", font_size=24, color=K_COL).next_to(wh, LEFT, buff=0.9)
        hout = Text("h_t", font_size=26, color=GREEN_C).next_to(tanh, RIGHT, buff=0.9)
        a1 = Arrow(xin.get_right(), wx.get_left(), buff=0.1, color=Q_COL)
        a2 = Arrow(hin.get_right(), wh.get_left(), buff=0.1, color=K_COL)
        a3 = Arrow(wx.get_right(), plus.get_left(), buff=0.1, color=Q_COL)
        a4 = Arrow(wh.get_right(), plus.get_left(), buff=0.1, color=K_COL)
        a5 = Arrow(plus.get_right(), tanh.get_left(), buff=0.1, color=WHITE)
        a6 = Arrow(tanh.get_right(), hout.get_left(), buff=0.1, color=GREEN_C)
        cell = VGroup(wx, wx_l, wh, wh_l, plus, plus_l, tanh, tanh_l, xin, hin, hout, a1, a2, a3, a4, a5, a6)
        cell.shift(RIGHT * 1.0 + DOWN * 0.3)
        self.play(FadeIn(xin), FadeIn(hin), GrowArrow(a1), GrowArrow(a2))
        self.play(Create(wx), Write(wx_l), Create(wh), Write(wh_l))
        self.play(GrowArrow(a3), GrowArrow(a4), Create(plus), Write(plus_l))
        note = Text("same 1000 slots: memory + word are summed, not stored side by side",
                    font_size=22, color=YELLOW).to_edge(DOWN, buff=0.9)
        self.play(FadeIn(note))
        self.play(GrowArrow(a5), Create(tanh), Write(tanh_l), GrowArrow(a6), FadeIn(hout))
        formula = MathTex(r"h_t=\tanh(W_x x_t + W_h h_{t-1} + b)", font_size=38).next_to(head, DOWN, buff=0.35)
        self.play(FadeOut(note), Write(formula))
        # loop back
        loop = CurvedArrow(hout.get_bottom() + DOWN * 0.1, hin.get_bottom() + DOWN * 0.1, angle=-TAU / 4, color=GREEN_C)
        loop_l = Text("h_t becomes the next h_{t-1}", font_size=20, color=GREEN_C).next_to(loop, DOWN, buff=0.1)
        self.play(Create(loop), FadeIn(loop_l))
        self.wait(1)
        self.play(FadeOut(VGroup(cell, loop, loop_l, formula, head)))

        # ---- unrolled with toy numbers
        head2 = title("Unrolled: one weight set, three steps")
        self.play(FadeIn(head2))
        words = ["Take", "the", "L"]
        xs = ["[1, 0]", "[0, 1]", "[1, 1]"]
        hs = ["[0.76, 0.00]", "[0.36, 0.76]", "[0.83, 0.88]"]
        trace = [0.76, 0.36, 0.18]
        cells = VGroup()
        for i in range(3):
            c = RoundedRectangle(corner_radius=0.1, width=2.3, height=1.1).set_stroke(TOK_COL, 2)
            lab = Text("tanh(W_x·x + W_h·h)", font_size=14, color=DIM).move_to(c)
            cells.add(VGroup(c, lab))
        cells.arrange(RIGHT, buff=1.1).shift(UP * 0.3)
        h0 = Text("h_0 = [0, 0]", font_size=20, color=K_COL).next_to(cells[0], LEFT, buff=0.5)
        self.play(FadeIn(cells), FadeIn(h0))
        prev_right = h0.get_right()
        hlabels = VGroup()
        for i in range(3):
            xin = Text(f"x_{words[i]} = {xs[i]}", font_size=18, color=Q_COL).next_to(cells[i], UP, buff=0.45)
            ax = Arrow(xin.get_bottom(), cells[i].get_top(), buff=0.05, color=Q_COL)
            ah = Arrow(prev_right, cells[i].get_left(), buff=0.05, color=K_COL)
            self.play(FadeIn(xin), GrowArrow(ax), GrowArrow(ah), run_time=0.6)
            hl = Text(f"h_{i+1} = {hs[i]}", font_size=18, color=GREEN_C).next_to(cells[i], DOWN, buff=0.45)
            self.play(FadeIn(hl), run_time=0.5)
            hlabels.add(hl)
            prev_right = cells[i].get_right()
        # red trace of "Take"
        bars = VGroup()
        for i, v in enumerate(trace):
            bar = Rectangle(width=0.3, height=1.2 * v).set_fill(RED_C, 0.9).set_stroke(width=0)
            bar.next_to(hlabels[i], DOWN, buff=0.25, aligned_edge=UP)
            num = Text(f"{v:.2f}", font_size=18, color=RED_C).next_to(bar, DOWN, buff=0.08)
            bars.add(VGroup(bar, num))
        tl = Text("trace of 'Take' inside h_t", font_size=20, color=RED_C).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(tl))
        for b in bars:
            self.play(GrowFromEdge(b[0], UP), FadeIn(b[1]), run_time=0.6)
        self.wait(0.8)
        # only the last state exits
        self.play(hlabels[0].animate.set_color(DIM), hlabels[1].animate.set_color(DIM),
                  cells[0].animate.set_opacity(0.35), cells[1].animate.set_opacity(0.35))
        dec = Text("→ decoder", font_size=22, color=GREEN_C).next_to(cells[2], RIGHT, buff=0.4)
        self.play(FadeIn(dec))
        self.wait(1.5)


# ======================================================= A2  Path length
class A02PathLength(Scene):
    def construct(self):
        head = title("Information travels one hop per step")
        self.play(FadeIn(head))
        n = 8
        row = VGroup(*[Circle(radius=0.32).set_stroke(TOK_COL, 2).set_fill(HEAT_LO, 1) for _ in range(n)])
        row.arrange(RIGHT, buff=0.7)
        labels = VGroup(*[Text(f"w{i+1}", font_size=20).next_to(row[i], DOWN, buff=0.15) for i in range(n)])
        edges = VGroup(*[Arrow(row[i].get_right(), row[i + 1].get_left(), buff=0.05, color=DIM) for i in range(n - 1)])
        self.play(FadeIn(row), FadeIn(labels), Create(edges))
        counter = Integer(0, font_size=44).shift(DOWN * 1.8)
        ctext = Text("steps:", font_size=30).next_to(counter, LEFT)
        self.play(FadeIn(counter), FadeIn(ctext))
        self.play(row[0].animate.set_fill(YELLOW, 1))
        for i in range(n - 1):
            self.play(edges[i].animate.set_color(YELLOW), row[i + 1].animate.set_fill(YELLOW, 1),
                      row[i].animate.set_fill(interpolate_color(YELLOW, HEAT_LO, 0.6), 1),
                      counter.animate.set_value(i + 1), run_time=0.45)
        tag = Text("path length = n − 1, and nothing runs in parallel", font_size=24, color=YELLOW).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(tag))
        self.wait(1.5)


# ======================================================= A3  The glance
class A03Glance(Scene):
    def construct(self):
        head = title("Bahdanau 2014: keep every state, look back with weights", font_size=30)
        self.play(FadeIn(head))
        src = ["The", "animal", "crossed", "the", "street"]
        row = token_row(src, buff=0.3, w=1.3).shift(UP * 1.6)
        states = VGroup(*[Rectangle(width=0.5, height=0.9).set_stroke(K_COL, 2).set_fill(K_COL, 0.15)
                          .next_to(row[i], DOWN, buff=0.25) for i in range(len(src))])
        slabels = VGroup(*[Text(f"h{i+1}", font_size=18, color=K_COL).move_to(states[i]) for i in range(len(src))])
        self.play(FadeIn(row), FadeIn(states), FadeIn(slabels))
        dec = RoundedRectangle(corner_radius=0.12, width=2.2, height=0.9).set_stroke(Q_COL, 2).shift(DOWN * 1.9 + LEFT * 2.2)
        dec_l = Text("decoder state", font_size=20, color=Q_COL).move_to(dec)
        out = Text("→ „Straße“", font_size=28, color=GREEN_C).next_to(dec, RIGHT, buff=0.5)
        self.play(Create(dec), FadeIn(dec_l))
        w = np.array([0.03, 0.05, 0.07, 0.10, 0.75])
        lines = VGroup(*[DashedLine(dec.get_top(), states[i].get_bottom(), dash_length=0.12,
                                    stroke_width=1 + 10 * w[i], color=interpolate_color(DIM, RED_C, w[i]))
                         for i in range(len(src))])
        wl = VGroup(*[Text(f"{w[i]:.2f}", font_size=16, color=heat(w[i] * 1.2 + 0.1)).next_to(states[i], RIGHT, buff=0.05)
                      for i in range(len(src))])
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.15))
        self.play(FadeIn(wl))
        sm = Text("softmax weights sum to 1.00", font_size=20, color=YELLOW).next_to(dec, DOWN, buff=0.3)
        self.play(FadeIn(sm))
        # weighted sum into context vector
        ctx = Rectangle(width=0.5, height=0.9).set_stroke(GREEN_C, 2).set_fill(GREEN_C, 0.2).next_to(dec, UP, buff=0.9)
        ctx_l = Text("context", font_size=16, color=GREEN_C).next_to(ctx, LEFT, buff=0.1)
        copies = VGroup(*[states[i].copy().set_fill(K_COL, 0.15 + 0.8 * w[i]) for i in range(len(src))])
        self.play(*[c.animate.move_to(ctx).scale(0.3 + 0.7 * w[i]) for i, c in enumerate(copies)], run_time=1.2)
        self.play(FadeOut(copies), FadeIn(ctx), FadeIn(ctx_l))
        a = Arrow(ctx.get_bottom(), dec.get_top(), buff=0.05, color=GREEN_C)
        self.play(GrowArrow(a), FadeIn(out))
        self.wait(1.5)


# ================================================= A4  Three ways to connect
class A04ThreeWays(Scene):
    def construct(self):
        head = title("From word 1 to word 9: path length by architecture")
        self.play(FadeIn(head))
        n = 9

        def nodes(y, color):
            g = VGroup(*[Circle(radius=0.2).set_stroke(color, 2).set_fill(HEAT_LO, 1) for _ in range(n)])
            return g.arrange(RIGHT, buff=0.42).shift(UP * y)

        rnn = nodes(2.0, TOK_COL); conv = nodes(0.0, TOK_COL); att = nodes(-2.3, TOK_COL)
        lab_r = Text("RNN", font_size=24).next_to(rnn, LEFT, buff=0.5)
        lab_c = Text("Conv (k=3)", font_size=24).next_to(conv, LEFT, buff=0.5)
        lab_a = Text("Attention", font_size=24).next_to(att, LEFT, buff=0.5)
        self.play(FadeIn(rnn), FadeIn(conv), FadeIn(att), FadeIn(lab_r), FadeIn(lab_c), FadeIn(lab_a))
        cr = Integer(0, font_size=34, color=YELLOW).next_to(rnn, RIGHT, buff=0.5)
        cc = Integer(0, font_size=34, color=YELLOW).next_to(conv, RIGHT, buff=0.5)
        ca = Integer(0, font_size=34, color=YELLOW).next_to(att, RIGHT, buff=0.5)
        self.play(FadeIn(cr), FadeIn(cc), FadeIn(ca))
        # conv tree: layer1 nodes above conv at positions 1,4,7 ; layer2 top node
        l1 = VGroup(*[Circle(radius=0.16).set_stroke(DIM, 2).set_fill(HEAT_LO, 1).move_to(conv[i].get_center() + UP * 0.7)
                      for i in (1, 4, 7)])
        l2 = Circle(radius=0.16).set_stroke(DIM, 2).set_fill(HEAT_LO, 1).move_to(conv[4].get_center() + UP * 1.4)
        c_edges1 = VGroup(*[Line(conv[j].get_top(), l1[k].get_bottom(), color=DIM, stroke_width=1.5)
                            for k, i in enumerate((1, 4, 7)) for j in (i - 1, i, i + 1)])
        c_edges2 = VGroup(*[Line(l1[k].get_top(), l2.get_bottom(), color=DIM, stroke_width=1.5) for k in range(3)])
        r_edges = VGroup(*[Arrow(rnn[i].get_right(), rnn[i + 1].get_left(), buff=0.03, color=DIM,
                                 max_tip_length_to_length_ratio=0.3) for i in range(n - 1)])
        a_edge = Arrow(att[0].get_top(), att[n - 1].get_top(), buff=0.03, color=DIM, path_arc=-1.2)
        self.play(Create(r_edges), Create(c_edges1), FadeIn(l1), Create(c_edges2), FadeIn(l2), Create(a_edge))
        # animate: attention 1 hop, conv 2 hops, rnn 8 hops — run simultaneously-ish
        self.play(att[0].animate.set_fill(YELLOW), conv[0].animate.set_fill(YELLOW), rnn[0].animate.set_fill(YELLOW))
        self.play(a_edge.animate.set_color(YELLOW), att[n - 1].animate.set_fill(YELLOW), ca.animate.set_value(1),
                  c_edges1[0].animate.set_color(YELLOW), l1[0].animate.set_fill(YELLOW), cc.animate.set_value(1),
                  r_edges[0].animate.set_color(YELLOW), rnn[1].animate.set_fill(YELLOW), cr.animate.set_value(1), run_time=0.6)
        self.play(c_edges2[0].animate.set_color(YELLOW), l2.animate.set_fill(YELLOW), cc.animate.set_value(2),
                  r_edges[1].animate.set_color(YELLOW), rnn[2].animate.set_fill(YELLOW), cr.animate.set_value(2), run_time=0.6)
        # conv: l2 down to word 9 via l1[2]
        self.play(c_edges2[2].animate.set_color(YELLOW), l1[2].animate.set_fill(YELLOW),
                  r_edges[2].animate.set_color(YELLOW), rnn[3].animate.set_fill(YELLOW), cr.animate.set_value(3), run_time=0.6)
        self.play(c_edges1[8].animate.set_color(YELLOW), conv[8].animate.set_fill(YELLOW),
                  r_edges[3].animate.set_color(YELLOW), rnn[4].animate.set_fill(YELLOW), cr.animate.set_value(4), run_time=0.6)
        for i in range(4, n - 1):
            self.play(r_edges[i].animate.set_color(YELLOW), rnn[i + 1].animate.set_fill(YELLOW), cr.animate.set_value(i + 1), run_time=0.45)
        tags = VGroup(Text("O(n)", font_size=22, color=YELLOW).next_to(cr, RIGHT, buff=0.3),
                      Text("O(log n) layers", font_size=22, color=YELLOW).next_to(cc, RIGHT, buff=0.3),
                      Text("O(1)", font_size=22, color=YELLOW).next_to(ca, RIGHT, buff=0.3))
        self.play(FadeIn(tags))
        self.wait(1.5)


# ================================================= A5  The soft lookup
class A05SoftLookup(Scene):
    def construct(self):
        head = title("Attention = soft lookup: score, normalise, blend")
        self.play(FadeIn(head))
        plane = NumberPlane(x_range=[-0.4, 1.6, 0.5], y_range=[-0.4, 1.6, 0.5], x_length=4.2, y_length=4.2,
                            background_line_style={"stroke_opacity": 0.25}).to_edge(LEFT, buff=0.6).shift(DOWN * 0.3)
        q = Q["sat"]
        O = plane.c2p(0, 0)
        q_arrow = Arrow(O, plane.c2p(*q), buff=0, color=Q_COL, stroke_width=6)
        q_lab = Text("q_sat", font_size=22, color=Q_COL).next_to(q_arrow.get_end(), UL, buff=0.08)
        self.play(Create(plane), GrowArrow(q_arrow), FadeIn(q_lab))
        scores, k_arrows, shadow_grp = [], VGroup(), VGroup()
        offsets = {"The": DOWN, "cat": UP, "sat": RIGHT}
        qhat = q / np.linalg.norm(q)
        for name in SENT:
            k = K[name]
            ka = Arrow(O, plane.c2p(*k), buff=0, color=K_COL, stroke_width=4)
            kl = Text(f"k_{name}", font_size=20, color=K_COL).next_to(ka.get_end(), offsets[name], buff=0.05)
            # projection of k onto q direction (dot product = |q| * shadow length along q̂)
            proj = qhat * float(k @ qhat)
            shadow = Line(O, plane.c2p(*proj), color=YELLOW, stroke_width=8).set_opacity(0.8)
            drop = DashedLine(plane.c2p(*k), plane.c2p(*proj), dash_length=0.08, color=YELLOW)
            s = float(q @ k)
            sl = Text(f"q·k = {s:.0f}", font_size=20, color=YELLOW).next_to(plane, DOWN, buff=0.15)
            self.play(GrowArrow(ka), FadeIn(kl), run_time=0.6)
            self.play(Create(drop), Create(shadow), FadeIn(sl), run_time=0.7)
            self.wait(0.3)
            self.play(FadeOut(drop), FadeOut(shadow), FadeOut(sl), run_time=0.3)
            scores.append(s); k_arrows.add(ka, kl)
        # bars
        chart = BarChart(scores, bar_names=SENT, y_range=[0, 2.2, 1], x_length=4, y_length=2.4,
                         bar_colors=[YELLOW] * 3).scale(0.9).to_edge(RIGHT, buff=0.7).shift(UP * 1.1)
        ct = Text("raw scores q·k", font_size=20, color=YELLOW).next_to(chart, UP, buff=0.15)
        self.play(Create(chart), FadeIn(ct))
        scaled = np.array(scores) / np.sqrt(2)
        w = softmax(scaled)
        ct2 = MathTex(r"\mathrm{softmax}(q\!\cdot\! k/\sqrt{d_k})", font_size=30, color=RED_C).move_to(ct)
        chart2 = BarChart(list(w), bar_names=SENT, y_range=[0, 1, 0.5], x_length=4, y_length=2.4,
                          bar_colors=[RED_C] * 3).scale(0.9).move_to(chart)
        self.play(Transform(chart, chart2), Transform(ct, ct2))
        wlabels = VGroup(*[Text(f"{v:.2f}", font_size=18, color=RED_C).next_to(chart.bars[i], UP, buff=0.05) for i, v in enumerate(w)])
        sumtxt = Text("sum = 1.00", font_size=18, color=RED_C).move_to(chart.get_corner(UL) + RIGHT * 1.6 + DOWN * 0.35)
        self.play(FadeIn(wlabels), FadeIn(sumtxt))
        # blend values
        vt = Text("blend the values with those weights", font_size=20, color=V_COL).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.6)
        self.play(FadeIn(vt))
        out = sum(w[i] * V[n] for i, n in enumerate(SENT))
        terms = VGroup(*[Text(f"{w[i]:.2f}·v_{n}", font_size=22, color=V_COL) for i, n in enumerate(SENT)])
        plus = VGroup(*[Text("+", font_size=22) for _ in range(2)])
        expr = VGroup(terms[0], plus[0], terms[1], plus[1], terms[2]).arrange(RIGHT, buff=0.15).next_to(vt, DOWN, buff=0.3)
        self.play(LaggedStart(*[FadeIn(t) for t in expr], lag_ratio=0.15))
        res = Text(f"= [{out[0]:.2f}, {out[1]:.2f}, {out[2]:.2f}]", font_size=24, color=V_COL).next_to(expr, DOWN, buff=0.25)
        self.play(FadeIn(res))
        final = MathTex(r"\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\!\left(\tfrac{QK^\top}{\sqrt{d_k}}\right)V", font_size=36)
        final.to_edge(DOWN, buff=0.3)
        final.set_color_by_tex("Q", Q_COL); final.set_color_by_tex("K", K_COL); final.set_color_by_tex("V", V_COL)
        self.play(Write(final))
        self.wait(2)


# ================================================= A6  Why divide by sqrt(d_k)
class A06WhySqrt(Scene):
    def construct(self):
        head = title("Why divide by √d_k: keep the scores' spread fixed")
        self.play(FadeIn(head))
        rng = np.random.default_rng(0)
        bins = np.linspace(-30, 30, 25)
        ax = Axes(x_range=[-30, 30, 10], y_range=[0, 0.5, 0.25], x_length=6, y_length=2.6,
                  axis_config={"include_numbers": True, "font_size": 18}).to_edge(LEFT, buff=0.6).shift(UP * 0.6)
        axl = Text("distribution of q·k (random vectors)", font_size=20).next_to(ax, UP, buff=0.1)
        self.play(Create(ax), FadeIn(axl))

        def hist_bars(dk, scaled):
            qs = rng.standard_normal((4000, dk)); ks = rng.standard_normal((4000, dk))
            s = (qs * ks).sum(1)
            if scaled:
                s = s / np.sqrt(dk)
            h, _ = np.histogram(s, bins=bins, density=True)
            g = VGroup()
            for i in range(len(h)):
                x0, x1 = bins[i], bins[i + 1]
                r = Rectangle(width=ax.c2p(x1, 0)[0] - ax.c2p(x0, 0)[0], height=max(1e-3, ax.c2p(0, h[i])[1] - ax.c2p(0, 0)[1]))
                r.set_fill(RED_C if scaled else YELLOW, 0.8).set_stroke(width=0)
                r.move_to(ax.c2p((x0 + x1) / 2, 0), aligned_edge=DOWN)
                g.add(r)
            return g

        # softmax spike panel
        sax = Axes(x_range=[0, 6, 1], y_range=[0, 1, 0.5], x_length=4, y_length=2.2,
                   axis_config={"include_numbers": False}).to_edge(RIGHT, buff=0.8).shift(UP * 0.6)
        saxl = Text("softmax of one row of 6 scores", font_size=20).next_to(sax, UP, buff=0.1)
        self.play(Create(sax), FadeIn(saxl))
        base = rng.standard_normal(6)

        def soft_bars(scale):
            p = softmax(base * scale)
            g = VGroup()
            for i in range(6):
                r = Rectangle(width=0.45, height=max(1e-3, sax.c2p(0, p[i])[1] - sax.c2p(0, 0)[1]))
                r.set_fill(interpolate_color(GREEN_C, RED_C, p.max()), 0.85).set_stroke(width=0)
                r.move_to(sax.c2p(i + 0.5, 0), aligned_edge=DOWN)
                g.add(r)
            return g

        dk_label = Text("d_k = 4", font_size=28, color=YELLOW).to_edge(DOWN, buff=1.2).shift(LEFT * 3)
        grad = Text("softmax gradient ≈ 1 − max p", font_size=20, color=DIM).to_edge(DOWN, buff=1.2).shift(RIGHT * 2.5)
        hb = hist_bars(4, False); sb = soft_bars(1.0)
        self.play(FadeIn(hb), FadeIn(sb), FadeIn(dk_label), FadeIn(grad))
        for dk in (16, 64, 256):
            nb = hist_bars(dk, False); ns = soft_bars(np.sqrt(dk) / 2)
            nl = Text(f"d_k = {dk}", font_size=28, color=YELLOW).move_to(dk_label)
            self.play(Transform(hb, nb), Transform(sb, ns), Transform(dk_label, nl), run_time=0.9)
            self.wait(0.3)
        spike = Text("spread grows like √d_k → softmax saturates → gradients ≈ 0", font_size=22, color=RED_C).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(spike))
        self.wait(1.2)
        # now scaled
        fix = Text("divide by √d_k", font_size=28, color=GREEN_C).move_to(dk_label)
        self.play(Transform(dk_label, fix), FadeOut(spike))
        for dk in (4, 16, 64, 256):
            nb = hist_bars(dk, True); ns = soft_bars(1.0)
            nl = Text(f"scaled, d_k = {dk}", font_size=26, color=GREEN_C).move_to(dk_label)
            self.play(Transform(hb, nb), Transform(sb, ns), Transform(dk_label, nl), run_time=0.7)
        ok = Text("variance 1 at every width: softmax stays soft, gradients flow", font_size=22, color=GREEN_C).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(ok))
        self.wait(1.5)


# ================================================= A7  Matrix view
class A07MatrixView(Scene):
    def construct(self):
        head = title("The same lookup as matrices: QKᵀ → row softmax → ×V")
        self.play(FadeIn(head))
        Qm = np.array([Q[w] for w in SENT]); Km = np.array([K[w] for w in SENT]); Vm = np.array([V[w] for w in SENT])
        S = Qm @ Km.T
        A = np.array([softmax(r / np.sqrt(2)) for r in S])
        Out = A @ Vm
        qM = matrix_block(Qm, Q_COL, h_buff=0.7); kM = matrix_block(Km.T, K_COL, h_buff=0.7)
        qlab = Text("Q", font_size=26, color=Q_COL).next_to(qM, UP, buff=0.1)
        klab = Text("Kᵀ", font_size=26, color=K_COL).next_to(kM, UP, buff=0.1)
        rown = VGroup(*[Text(w, font_size=18, color=Q_COL).next_to(qM.get_rows()[i], LEFT, buff=0.55) for i, w in enumerate(SENT)])
        coln = VGroup(*[Text(w, font_size=18, color=K_COL).next_to(kM.get_columns()[i], DOWN, buff=0.25) for i, w in enumerate(SENT)])
        left = VGroup(qM, qlab, rown).to_edge(LEFT, buff=0.7).shift(UP * 0.8)
        VGroup(kM, klab, coln).next_to(left, RIGHT, buff=0.6)
        self.play(FadeIn(left), FadeIn(kM), FadeIn(klab), FadeIn(coln))
        G = grid(S / 2.0, cell=0.62, fmt="{:.0f}").next_to(kM, RIGHT, buff=0.8)
        for r in G:
            for c in r:
                c[0].set_fill(HEAT_LO, 1)
        glab = Text("QKᵀ", font_size=26).next_to(G, UP, buff=0.1)
        self.play(FadeIn(glab), FadeIn(VGroup(*[c[0] for r in G for c in r])))
        for i in range(3):
            for j in range(3):
                hr = SurroundingRectangle(qM.get_rows()[i], color=Q_COL, buff=0.08)
                hc = SurroundingRectangle(kM.get_columns()[j], color=K_COL, buff=0.08)
                val = Text(f"{S[i, j]:.0f}", font_size=18).move_to(G[i][j][0])
                self.play(Create(hr), Create(hc), run_time=0.2)
                self.play(FadeIn(val), G[i][j][0].animate.set_fill(heat(S[i, j] / 2)), FadeOut(hr), FadeOut(hc), run_time=0.3)
                self.remove(val)
                G[i][j][1].become(val)
                self.add(G[i][j][1])
        self.wait(0.4)
        # row softmax
        sm = MathTex(r"\text{softmax}(\cdot/\sqrt{2})\ \text{per row}", font_size=28, color=RED_C).next_to(G, DOWN, buff=0.3)
        self.play(Write(sm))
        anims = []
        for i in range(3):
            for j in range(3):
                nv = Text(f"{A[i, j]:.2f}", font_size=16).move_to(G[i][j][0])
                anims += [G[i][j][0].animate.set_fill(heat(A[i, j])), Transform(G[i][j][1], nv)]
        self.play(*anims, run_time=1.0)
        sums = VGroup(*[Text("1.00", font_size=16, color=RED_C).next_to(G[i], RIGHT, buff=0.12) for i in range(3)])
        self.play(FadeIn(sums))
        self.wait(0.5)
        # times V -> output rows
        vM = matrix_block(Vm, V_COL, h_buff=0.6).scale(0.85)
        vlab = Text("V", font_size=24, color=V_COL).next_to(vM, UP, buff=0.1)
        VGroup(vM, vlab).to_edge(LEFT, buff=0.7).shift(DOWN * 2.1)
        oM = matrix_block(Out, V_COL, fmt="{:.2f}", h_buff=1.1).scale(0.85)
        olab = Text("output = A·V", font_size=22, color=V_COL).next_to(oM, UP, buff=0.1)
        VGroup(oM, olab).next_to(vM, RIGHT, buff=1.6)
        self.play(FadeIn(vM), FadeIn(vlab))
        self.play(FadeIn(olab))
        for i in range(3):
            hr = SurroundingRectangle(G[i], color=RED_C, buff=0.03)
            hv = SurroundingRectangle(vM, color=V_COL, buff=0.05)
            self.play(Create(hr), Create(hv), run_time=0.25)
            self.play(FadeIn(oM.get_rows()[i]), FadeOut(hr), FadeOut(hv), run_time=0.4)
        self.play(FadeIn(oM.get_brackets()))
        self.wait(0.6)
        # overlay as word-to-word links
        note = Text("each row = one word's mix of the others", font_size=22, color=YELLOW).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(note))
        self.wait(1.5)


# ================================================= A8  Multi-head
class A08MultiHead(Scene):
    def construct(self):
        head = title("Multi-head: split the width, run 8 lookups in parallel")
        self.play(FadeIn(head))
        cols = [BLUE_C, TEAL_C, GREEN_C, YELLOW_C, ORANGE, RED_C, PURPLE_B, PINK]
        tall = VGroup(*[Rectangle(width=0.5, height=0.42).set_fill(TOK_COL, 0.9).set_stroke(width=0) for _ in range(8)]).arrange(DOWN, buff=0)
        tall.to_edge(LEFT, buff=1.0)
        tl = Text("x  (512)", font_size=22).next_to(tall, UP, buff=0.15)
        self.play(FadeIn(tall), FadeIn(tl))
        self.play(*[tall[i].animate.set_fill(cols[i], 0.9) for i in range(8)])
        brace = Brace(tall[0], RIGHT, buff=0.1); bl = brace.get_text("64 dims / head").scale(0.6)
        self.play(FadeIn(brace), FadeIn(bl))
        self.wait(0.4)
        self.play(FadeOut(brace), FadeOut(bl))
        # three heads with different maps
        words = ["The", "animal", "didn't", "cross", "it", "was", "tired"]
        n = len(words)
        diag = np.eye(n) * 0.5 + np.eye(n, k=1) * 0.25 + np.eye(n, k=-1) * 0.25
        verb = np.zeros((n, n)); verb[:, 3] = 0.7; verb += np.eye(n) * 0.3
        coref = np.eye(n) * 0.6; coref[4, 1] = 0.9; coref[4, 4] = 0.1
        maps = [(0, "adjacent", diag), (3, "all → verb", verb), (6, "it → animal", coref)]
        shown = VGroup()
        for idx, (hi, name, m) in enumerate(maps):
            g = grid(m, cell=0.3, show_values=False)
            g.shift(RIGHT * (idx * 3.0 - 3.3) + DOWN * 0.1)
            lab = Text(f"head {hi+1}: {name}", font_size=18, color=cols[hi]).next_to(g, UP, buff=0.12)
            frame = SurroundingRectangle(g, color=cols[hi], buff=0.04)
            band = tall[hi].copy()
            self.play(band.animate.move_to(g.get_center()).set_opacity(0.3), run_time=0.5)
            self.play(FadeOut(band), FadeIn(g), Create(frame), FadeIn(lab), run_time=0.6)
            shown.add(g, frame, lab)
        rowl = VGroup(*[Text(w, font_size=11, color=DIM).next_to(shown[6][i], LEFT, buff=0.05) for i, w in enumerate(words)])
        self.play(FadeIn(rowl))
        self.wait(0.8)
        # concat + W^O
        outs = VGroup(*[Rectangle(width=0.5, height=0.42).set_fill(cols[i], 0.9).set_stroke(width=0) for i in range(8)]).arrange(DOWN, buff=0)
        outs.to_edge(RIGHT, buff=1.4)
        ol = Text("concat (512)", font_size=20).next_to(outs, UP, buff=0.15)
        self.play(LaggedStart(*[FadeIn(o, shift=LEFT * 0.3) for o in outs], lag_ratio=0.08), FadeIn(ol))
        wo = RoundedRectangle(corner_radius=0.08, width=0.9, height=0.7).set_stroke(WHITE, 2).next_to(outs, RIGHT, buff=0.3)
        wol = Text("W^O", font_size=22).move_to(wo)
        self.play(Create(wo), Write(wol))
        f = MathTex(r"\mathrm{MultiHead}=\mathrm{Concat}(\mathrm{head}_1,\dots,\mathrm{head}_8)\,W^O", font_size=30).to_edge(DOWN, buff=0.35)
        self.play(Write(f))
        self.wait(1.5)


# ================================================= A9  Shuffle test
class A09ShuffleTest(Scene):
    def construct(self):
        head = title("Attention alone is a bag of words")
        self.play(FadeIn(head))
        words = ["dog", "bites", "man"]
        cols = [BLUE_C, YELLOW_C, GREEN_C]
        row = token_row(words, buff=0.4).shift(UP * 1.5 + LEFT * 1.8)
        for i, t in enumerate(row):
            t[0].set_stroke(cols[i], 2); t[1].set_color(cols[i])
        att = RoundedRectangle(corner_radius=0.12, width=2.0, height=0.8).set_stroke(WHITE, 2).next_to(row, DOWN, buff=0.8)
        attl = Text("self-attention", font_size=20).move_to(att)
        outs = VGroup(*[Rectangle(width=0.9, height=0.5).set_fill(cols[i], 0.7).set_stroke(width=0) for i in range(3)]).arrange(RIGHT, buff=0.5)
        outs.next_to(att, DOWN, buff=0.8)
        arrows_in = VGroup(*[Arrow(row[i].get_bottom(), att.get_top(), buff=0.05, color=DIM) for i in range(3)])
        arrows_out = VGroup(*[Arrow(att.get_bottom(), outs[i].get_top(), buff=0.05, color=DIM) for i in range(3)])
        self.play(FadeIn(row), Create(att), FadeIn(attl), Create(arrows_in))
        self.play(Create(arrows_out), FadeIn(outs))
        ol = Text("outputs", font_size=18, color=DIM).next_to(outs, LEFT, buff=0.3)
        self.play(FadeIn(ol))
        # shuffle
        perm = [2, 1, 0]
        self.play(row[0].animate.move_to(row[2].get_center()), row[2].animate.move_to(row[0].get_center()), run_time=0.8)
        self.play(outs[0].animate.move_to(outs[2].get_center()), outs[2].animate.move_to(outs[0].get_center()), run_time=0.8)
        msg = VGroup(Text("same set of outputs, just permuted:", font_size=22, color=RED_C),
                     Text("no notion of order", font_size=22, color=RED_C)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        msg.move_to(RIGHT * 4.1 + UP * 1.5)
        self.play(FadeIn(msg))
        self.wait(1)
        # add positions
        pe = VGroup(*[Rectangle(width=1.25, height=0.25).set_fill(POS_COL, 0.3 + 0.3 * i).set_stroke(POS_COL, 1) for i in range(3)])
        for i in range(3):
            pe[i].next_to(row[i], DOWN, buff=0.05)
        pel = Text("+ position vector", font_size=20, color=POS_COL).next_to(pe, LEFT, buff=0.3)
        self.play(FadeIn(pe), FadeIn(pel))
        self.play(*[outs[i].animate.set_fill(interpolate_color(cols[i], POS_COL, 0.4)) for i in range(3)])
        self.play(row[0].animate.move_to(row[2].get_center()), row[2].animate.move_to(row[0].get_center()),
                  pe[0].animate.next_to(row[2], DOWN, buff=0.05), pe[2].animate.next_to(row[0], DOWN, buff=0.05), run_time=0.8)
        self.play(*[outs[i].animate.set_fill(interpolate_color(cols[i], POS_COL, 0.7 if i != 1 else 0.4)) for i in range(3)])
        msg2 = VGroup(Text("with positions added the outputs change:", font_size=22, color=GREEN_C),
                      Text("order is visible", font_size=22, color=GREEN_C)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        msg2.next_to(msg, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(FadeIn(msg2))
        self.wait(1.5)


# ================================================= A10 Sinusoidal positions
class A10Sinusoids(Scene):
    def construct(self):
        head = title("Sinusoidal positions: many clocks at different speeds")
        self.play(FadeIn(head))
        d, L = 32, 24
        pe = np.zeros((L, d))
        pos = np.arange(L)[:, None]
        div = 10000 ** (np.arange(0, d, 2) / d)
        pe[:, 0::2] = np.sin(pos / div); pe[:, 1::2] = np.cos(pos / div)
        cell = 0.17
        hm = VGroup()
        for c in range(d):
            col = VGroup(*[Square(cell).set_stroke(width=0).set_fill(interpolate_color(BLUE_E, YELLOW, (pe[r, c] + 1) / 2), 1) for r in range(L)]).arrange(DOWN, buff=0)
            hm.add(col)
        hm.arrange(RIGHT, buff=0).to_edge(LEFT, buff=0.7).shift(DOWN * 0.3)
        xl = Text("dimension →", font_size=18).next_to(hm, DOWN, buff=0.1)
        yl = Text("position ↓", font_size=18).rotate(PI / 2).next_to(hm, LEFT, buff=0.1)
        f = MathTex(r"PE_{(pos,2i)}=\sin\!\left(\tfrac{pos}{10000^{2i/d}}\right)", font_size=26, color=POS_COL).next_to(hm, UP, buff=0.15)
        self.play(FadeIn(xl), FadeIn(yl), Write(f))
        self.play(LaggedStart(*[FadeIn(c) for c in hm], lag_ratio=0.05, run_time=3))
        note = Text("left: fast stripes (fine position)   right: slow (coarse)", font_size=18, color=DIM).next_to(xl, DOWN, buff=0.1)
        self.play(FadeIn(note))
        # clock hands
        circ = Circle(radius=1.3).set_stroke(GREY_B, 1).to_edge(RIGHT, buff=2.4).shift(UP * 0.3)
        cl = Text("one (sin, cos) pair = a clock hand", font_size=20, color=POS_COL).next_to(circ, UP, buff=0.2)
        self.play(Create(circ), FadeIn(cl))
        tr = ValueTracker(0)
        omega = 0.5
        hand = always_redraw(lambda: Arrow(circ.get_center(), circ.get_center() + 1.3 * np.array([np.cos(omega * tr.get_value()), np.sin(omega * tr.get_value()), 0]), buff=0, color=POS_COL))
        plab = always_redraw(lambda: Text(f"pos = {int(round(tr.get_value()))}", font_size=22).next_to(circ, DOWN, buff=0.2))
        self.add(hand, plab)
        self.play(tr.animate.set_value(3), run_time=1.2)
        arc1 = Arc(radius=0.6, start_angle=0, angle=omega * 3, arc_center=circ.get_center(), color=YELLOW)
        a1l = Text("+3 → rotate θ", font_size=18, color=YELLOW).next_to(circ, RIGHT, buff=0.15).shift(UP * 0.7)
        self.play(Create(arc1), FadeIn(a1l))
        self.play(tr.animate.set_value(10), run_time=1.2)
        self.play(tr.animate.set_value(13), run_time=1.0)
        arc2 = Arc(radius=0.6, start_angle=omega * 10, angle=omega * 3, arc_center=circ.get_center(), color=YELLOW)
        a2l = Text("+3 → same θ", font_size=18, color=YELLOW).next_to(circ, RIGHT, buff=0.15).shift(DOWN * 0.7)
        self.play(Create(arc2), FadeIn(a2l))
        msg = Text("a fixed offset is the same rotation anywhere → relative position is linear", font_size=20, color=GREEN_C).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(msg))
        self.wait(1.5)


# ================================================= A11 The mask
class A11Mask(Scene):
    def construct(self):
        head = title("Decoder self-attention: mask the future")
        self.play(FadeIn(head))
        n = 6
        rng = np.random.default_rng(1)
        S = rng.uniform(0.2, 2.0, (n, n))
        G = grid(S / 2, cell=0.62, fmt="{:.1f}").shift(LEFT * 1.5 + DOWN * 0.2)
        words = ["<s>", "Die", "Katze", "saß", "auf", "der"]
        rl = VGroup(*[Text(w, font_size=16, color=Q_COL).next_to(G[i], LEFT, buff=0.15) for i, w in enumerate(words)])
        cl = VGroup(*[Text(w, font_size=16, color=K_COL).next_to(G[0][j], UP, buff=0.15) for j, w in enumerate(words)])
        self.play(FadeIn(G), FadeIn(rl), FadeIn(cl))
        tri = Polygon(G[0][1][0].get_corner(UL), G[0][n - 1][0].get_corner(UR), G[n - 2][n - 1][0].get_corner(DR)).set_fill(BLACK, 0.75).set_stroke(RED_C, 2)
        self.play(FadeIn(tri, shift=DOWN * 0.6), run_time=0.9)
        anims = []
        for i in range(n):
            for j in range(i + 1, n):
                anims.append(Transform(G[i][j][1], Text("−∞", font_size=16, color=RED_C).move_to(G[i][j][0])))
                anims.append(G[i][j][0].animate.set_fill(HEAT_LO))
        self.play(*anims, run_time=0.8)
        msg = Text("future scores → −∞ before the softmax", font_size=22, color=RED_C).to_edge(RIGHT, buff=0.5).shift(UP * 1.2)
        self.play(FadeIn(msg), FadeOut(tri))
        self.wait(0.6)
        A = np.zeros((n, n))
        for i in range(n):
            A[i, :i + 1] = softmax(S[i, :i + 1] / np.sqrt(64) * 8)
        anims = []
        for i in range(n):
            for j in range(n):
                anims.append(Transform(G[i][j][1], Text(f"{A[i, j]:.2f}" if j <= i else "0", font_size=14, color=WHITE if j <= i else DIM).move_to(G[i][j][0])))
                anims.append(G[i][j][0].animate.set_fill(heat(A[i, j])))
        self.play(*anims, run_time=0.9)
        msg2 = Text("after softmax: exactly 0 weight on the future", font_size=22, color=GREEN_C).next_to(msg, DOWN, buff=0.3)
        self.play(FadeIn(msg2))
        r1 = SurroundingRectangle(G[0], color=YELLOW, buff=0.02); r6 = SurroundingRectangle(G[n - 1], color=YELLOW, buff=0.02)
        t1 = Text("row 1: only itself", font_size=18, color=YELLOW).next_to(msg2, DOWN, buff=0.4)
        t6 = Text("row 6: everything so far", font_size=18, color=YELLOW).next_to(t1, DOWN, buff=0.15)
        self.play(Create(r1), FadeIn(t1)); self.play(ReplacementTransform(r1, r6), FadeIn(t6))
        msg3 = Text("so the whole target trains in one parallel pass", font_size=20, color=DIM).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(msg3))
        self.wait(1.5)


# ================================================= A12 Residual + LayerNorm
class A12Residual(Scene):
    def construct(self):
        head = title("Residual highway and LayerNorm")
        self.play(FadeIn(head))
        x = Arrow(LEFT * 5.5, LEFT * 3.8, buff=0, color=TOK_COL, stroke_width=6)
        xl = Text("x", font_size=28).next_to(x, UP, buff=0.1)
        block = RoundedRectangle(corner_radius=0.12, width=2.9, height=1.0).set_stroke(Q_COL, 2).shift(LEFT * 1.8 + UP * 1.0)
        bl = Text("sublayer (attn / FFN)", font_size=18, color=Q_COL).move_to(block)
        split = Dot(LEFT * 3.8, color=TOK_COL)
        up = Line(LEFT * 3.8, LEFT * 3.8 + UP * 1.0, color=TOK_COL)
        into = Arrow(LEFT * 3.8 + UP * 1.0, block.get_left(), buff=0, color=TOK_COL)
        rail = Line(LEFT * 3.8, RIGHT * 0.4, color=GREEN_C, stroke_width=6)
        rail_l = Text("skip (identity)", font_size=18, color=GREEN_C).next_to(rail, DOWN, buff=0.1)
        outb = Arrow(block.get_right(), RIGHT * 0.4 + UP * 1.0, buff=0, color=Q_COL)
        down = Arrow(RIGHT * 0.4 + UP * 1.0, RIGHT * 0.4 + UP * 0.05, buff=0, color=Q_COL)
        plus = Circle(radius=0.28).set_stroke(WHITE, 2).move_to(RIGHT * 0.4); pl = Text("+", font_size=30).move_to(plus)
        ln = RoundedRectangle(corner_radius=0.12, width=1.6, height=0.8).set_stroke(YELLOW, 2).move_to(RIGHT * 2.3)
        lnl = Text("LayerNorm", font_size=20, color=YELLOW).move_to(ln)
        toln = Arrow(plus.get_right(), ln.get_left(), buff=0.05, color=WHITE)
        outa = Arrow(ln.get_right(), RIGHT * 5.0, buff=0.05, color=TOK_COL, stroke_width=6)
        ol = Text("x + Sublayer(x), normalised", font_size=18).next_to(outa, DOWN, buff=0.12).shift(RIGHT * 0.4)
        self.play(GrowArrow(x), FadeIn(xl), FadeIn(split))
        self.play(Create(up), GrowArrow(into), Create(block), FadeIn(bl))
        self.play(Create(rail), FadeIn(rail_l))
        self.play(GrowArrow(outb), GrowArrow(down), Create(plus), Write(pl))
        self.play(GrowArrow(toln), Create(ln), Write(lnl), GrowArrow(outa), FadeIn(ol))
        # pulse along both paths
        p1 = Dot(color=Q_COL).move_to(LEFT * 3.8); p2 = Dot(color=GREEN_C).move_to(LEFT * 3.8)
        self.add(p1, p2)
        self.play(MoveAlongPath(p1, VMobject().set_points_as_corners([LEFT * 3.8, LEFT * 3.8 + UP, block.get_left(), block.get_right(), RIGHT * 0.4 + UP, RIGHT * 0.4])),
                  MoveAlongPath(p2, Line(LEFT * 3.8, RIGHT * 0.4)), run_time=1.6)
        self.play(FadeOut(p1), FadeOut(p2))
        g = Text("gradient has a straight road back through 6 layers", font_size=20, color=GREEN_C).shift(DOWN * 1.3)
        self.play(FadeIn(g))
        self.wait(0.8)
        # LayerNorm scatter -> sphere
        self.play(FadeOut(g))
        rng = np.random.default_rng(2)
        pts = rng.normal(0, 1, (14, 2)) * np.array([1.4, 0.6]) + np.array([0.5, 0.3])
        center = DOWN * 2.3 + LEFT * 2.2
        dots = VGroup(*[Dot(center + np.array([p[0], p[1], 0]) * 0.55, color=YELLOW, radius=0.06) for p in pts])
        circ = Circle(radius=0.9).set_stroke(YELLOW, 1).move_to(center)
        lab = Text("LayerNorm: re-centre & rescale each token", font_size=20, color=YELLOW).next_to(circ, RIGHT, buff=0.5)
        self.play(FadeIn(dots), FadeIn(lab))
        mean = pts.mean(0)
        targets = []
        for p in pts:
            v = p - mean; v = v / (np.linalg.norm(v) + 1e-9)
            targets.append(center + np.array([v[0], v[1], 0]) * 0.9)
        self.play(Create(circ), *[d.animate.move_to(t) for d, t in zip(dots, targets)], run_time=1.4)
        self.wait(1.5)


# ================================================= A13 Full data flow
class A13FullFlow(Scene):
    def construct(self):
        head = title("The whole machine: encoder, decoder, cross-attention", font_size=30)
        self.play(FadeIn(head))

        def stack(x, colour, labels):
            boxes = VGroup()
            for lab in labels:
                b = RoundedRectangle(corner_radius=0.08, width=2.6, height=0.42).set_stroke(colour, 1.5).set_fill(colour, 0.08)
                t = Text(lab, font_size=14, color=colour).move_to(b)
                boxes.add(VGroup(b, t))
            boxes.arrange(UP, buff=0.08)
            layer = SurroundingRectangle(boxes, color=colour, buff=0.12).set_stroke(width=1)
            return VGroup(boxes, layer).shift(RIGHT * x)

        enc_layer = stack(-3.6, Q_COL, ["self-attention", "add & norm", "feed-forward", "add & norm"])
        dec_layer = stack(2.0, K_COL, ["masked self-attn", "add & norm", "cross-attention", "add & norm", "feed-forward", "add & norm"])
        enc_layer.shift(UP * 0.1); dec_layer.shift(UP * 0.1)
        n6e = Text("× 6", font_size=22, color=Q_COL).next_to(enc_layer, LEFT, buff=0.2)
        n6d = Text("× 6", font_size=22, color=K_COL).next_to(dec_layer, RIGHT, buff=0.2)
        src = token_row(["The", "cat", "sat"], buff=0.1, w=0.8, h=0.45, font_size=18).next_to(enc_layer, DOWN, buff=0.7)
        pe1 = Text("+ positions", font_size=14, color=POS_COL).next_to(src, DOWN, buff=0.08)
        tgt = token_row(["<s>", "Die", "Katze"], buff=0.1, w=0.8, h=0.45, font_size=18).next_to(dec_layer, DOWN, buff=0.7)
        pe2 = Text("+ positions (shifted right)", font_size=14, color=POS_COL).next_to(tgt, DOWN, buff=0.08)
        self.play(FadeIn(src), FadeIn(pe1))
        self.play(GrowArrow(Arrow(src.get_top(), enc_layer.get_bottom(), buff=0.05, color=Q_COL)), FadeIn(enc_layer), FadeIn(n6e))
        self.play(FadeIn(tgt), FadeIn(pe2))
        self.play(GrowArrow(Arrow(tgt.get_top(), dec_layer.get_bottom(), buff=0.05, color=K_COL)), FadeIn(dec_layer), FadeIn(n6d))
        # cross attention arrows: from encoder top to decoder cross-attention box
        enc_out = enc_layer[1].get_top() + UP * 0.25
        eo = Arrow(enc_layer[1].get_top(), enc_out, buff=0, color=Q_COL)
        kv = Text("K, V", font_size=16, color=K_COL).next_to(enc_out, UP, buff=0.05)
        cross_box = dec_layer[0][2]
        c1 = Arrow(enc_out, cross_box.get_left(), buff=0.05, color=V_COL, stroke_width=3)
        self.play(GrowArrow(eo), FadeIn(kv))
        self.play(GrowArrow(c1), Indicate(cross_box, color=V_COL))
        # output
        lin = RoundedRectangle(corner_radius=0.08, width=2.2, height=0.4).set_stroke(GREEN_C, 1.5).next_to(dec_layer, UP, buff=0.4)
        linl = Text("linear + softmax", font_size=14, color=GREEN_C).move_to(lin)
        outw = Text("saß", font_size=22, color=GREEN_C).next_to(lin, UP, buff=0.2)
        self.play(GrowArrow(Arrow(dec_layer.get_top(), lin.get_bottom(), buff=0.05, color=K_COL)), FadeIn(lin), FadeIn(linl))
        self.play(FadeIn(outw))
        # feed back
        fb = CurvedArrow(outw.get_right(), tgt.get_right() + RIGHT * 0.1, angle=-TAU / 4, color=GREEN_C)
        fbl = Text("feed back", font_size=14, color=GREEN_C).next_to(fb.point_from_proportion(0.8), RIGHT, buff=0.1)
        self.play(Create(fb), FadeIn(fbl))
        new = token("saß", w=0.8, h=0.45, font_size=18).next_to(tgt, RIGHT, buff=0.1)
        self.play(FadeIn(new))
        msg = Text("Figure 1 of the paper, built piece by piece", font_size=20, color=DIM).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(msg))
        self.wait(2)


# ================================================= A14 Complexity tiles
class A14Complexity(Scene):
    def construct(self):
        head = title("Cost per layer: n²·d (attention) vs n·d² (recurrence), d = 512", font_size=28)
        self.play(FadeIn(head))
        ax = Axes(x_range=[1, 4, 1], y_range=[6, 12, 1], x_length=7, y_length=3.8,
                  axis_config={"include_numbers": False}).shift(DOWN * 0.4 + LEFT * 0.5)
        xl = VGroup(*[Text(f"{10**k}", font_size=18).next_to(ax.c2p(k, 6), DOWN, buff=0.15) for k in (1, 2, 3, 4)])
        xname = Text("sequence length n (log scale)", font_size=18).next_to(ax, DOWN, buff=0.5)
        yname = Text("FLOPs (log10)", font_size=18).rotate(PI / 2).next_to(ax, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(xl), FadeIn(xname), FadeIn(yname))
        d = 512
        att = ax.plot(lambda k: np.log10((10 ** k) ** 2 * d), x_range=[1, 4], color=RED_C)
        rnn = ax.plot(lambda k: np.log10((10 ** k) * d * d), x_range=[1, 4], color=Q_COL)
        al = Text("self-attention  n²d", font_size=20, color=RED_C).next_to(att.get_end(), UR, buff=0.1).shift(LEFT * 1.5)
        rl = Text("recurrent  nd²", font_size=20, color=Q_COL).next_to(rnn.get_end(), DR, buff=0.1).shift(LEFT * 1.2)
        self.play(Create(rnn), FadeIn(rl)); self.play(Create(att), FadeIn(al))
        kx = np.log10(d)
        cross = Dot(ax.c2p(kx, np.log10(d ** 3)), color=YELLOW)
        cl = Text("n = d = 512: equal", font_size=20, color=YELLOW).next_to(cross, UP, buff=0.15).shift(LEFT * 1.0)
        vline = DashedLine(ax.c2p(kx, 6), cross.get_center(), color=YELLOW, dash_length=0.1)
        self.play(Create(vline), FadeIn(cross), FadeIn(cl))
        # tiles illustration on the right
        tr = ValueTracker(2.0)
        unit = 2.0 / 1000  # scene units per token / per channel

        def tiles():
            n = 10 ** tr.get_value()
            sq = Square(n * unit).set_fill(RED_C, 0.5).set_stroke(RED_C, 1)
            rect = Rectangle(width=n * unit, height=d * unit).set_fill(Q_COL, 0.5).set_stroke(Q_COL, 1)
            g = VGroup(sq, rect).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
            g.move_to(RIGHT * 5.2 + DOWN * 0.3)
            l1 = Text("n × n", font_size=16, color=RED_C).next_to(sq, RIGHT, buff=0.1)
            l2 = Text("n × d", font_size=16, color=Q_COL).next_to(rect, RIGHT, buff=0.1)
            lab = Text(f"n = {int(n)}", font_size=18).next_to(g, UP, buff=0.15)
            return VGroup(g, lab, l1, l2)

        t = always_redraw(tiles)
        mover = always_redraw(lambda: Dot(ax.c2p(tr.get_value(), np.log10((10 ** tr.get_value()) ** 2 * d)), color=RED_C, radius=0.07))
        self.add(t, mover)
        self.play(tr.animate.set_value(3.0), run_time=3.5, rate_func=linear)
        msg = Text("attention is cheaper while n < d; past that, the n² grid is the price of O(1) path length",
                   font_size=18, color=DIM).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(msg))
        self.wait(1.5)


# ================================================= A15 Warmup schedule
class A15Warmup(Scene):
    def construct(self):
        head = title("Learning rate: 4000 warm-up steps, then decay as 1/√step", font_size=30)
        self.play(FadeIn(head))
        d, warm = 512, 4000
        f = lambda s: d ** -0.5 * min(s ** -0.5, s * warm ** -1.5) if s > 0 else 0
        ax = Axes(x_range=[0, 40000, 10000], y_range=[0, 0.0008, 0.0002], x_length=9, y_length=4,
                  axis_config={"include_numbers": True, "font_size": 18, "decimal_number_config": {"num_decimal_places": 0}},
                  y_axis_config={"decimal_number_config": {"num_decimal_places": 4}}).shift(DOWN * 0.3)
        xl = Text("step", font_size=20).next_to(ax.x_axis, DOWN, buff=0.3); yl = Text("lr", font_size=20).next_to(ax.y_axis, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        curve = ax.plot(f, x_range=[1, 40000, 50], color=YELLOW)
        eq = MathTex(r"lr = d_{model}^{-0.5}\cdot\min\!\left(step^{-0.5},\ step\cdot warmup^{-1.5}\right)", font_size=30).to_edge(DOWN, buff=0.3)
        self.play(Write(eq))
        tr = ValueTracker(1)
        dot = always_redraw(lambda: Dot(ax.c2p(tr.get_value(), f(tr.get_value())), color=RED_C))
        self.add(dot)
        self.play(Create(curve), tr.animate.set_value(40000), run_time=4, rate_func=linear)
        w1 = Text("linear warm-up", font_size=20, color=GREEN_C).move_to(ax.c2p(10500, 0.00074))
        w2 = Text("∝ 1/√step", font_size=20, color=RED_C).move_to(ax.c2p(22000, 0.00045))
        vl = DashedLine(ax.c2p(4000, 0), ax.c2p(4000, f(4000)), color=GREEN_C, dash_length=0.08)
        self.play(Create(vl), FadeIn(w1), FadeIn(w2))
        self.wait(1.5)


# ================================================= A16 Morph into BERT / GPT / ViT
class A16Morph(Scene):
    def construct(self):
        head = title("The block outlived the task")
        self.play(FadeIn(head))

        def tower(x, colour, n=4, w=2.2):
            g = VGroup(*[RoundedRectangle(corner_radius=0.08, width=w, height=0.5).set_stroke(colour, 1.5).set_fill(colour, 0.12) for _ in range(n)])
            return g.arrange(UP, buff=0.1).shift(RIGHT * x)

        enc = tower(-2.5, Q_COL); dec = tower(2.5, K_COL)
        el = Text("encoder", font_size=22, color=Q_COL).next_to(enc, DOWN, buff=0.2)
        dl = Text("decoder", font_size=22, color=K_COL).next_to(dec, DOWN, buff=0.2)
        cross = VGroup(*[Arrow(enc[i].get_right(), dec[i].get_left(), buff=0.05, color=V_COL, stroke_width=2) for i in range(4)])
        toks = token_row(["The", "cat", "sat"], buff=0.08, w=0.7, h=0.4, font_size=16).next_to(el, DOWN, buff=0.3)
        self.play(FadeIn(enc), FadeIn(dec), FadeIn(el), FadeIn(dl), Create(cross), FadeIn(toks))
        tag = Text("2017: Transformer (translation)", font_size=24).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(tag))
        self.wait(0.8)
        # BERT
        t2 = Text("2018: BERT — encoder only, masked-token pretraining", font_size=24, color=Q_COL).move_to(tag)
        self.play(dec.animate.set_opacity(0.12), dl.animate.set_opacity(0.12), cross.animate.set_opacity(0.1), Transform(tag, t2))
        self.wait(1)
        # GPT
        t3 = Text("2018→: GPT — decoder only, next-token prediction", font_size=24, color=K_COL).move_to(tag)
        self.play(dec.animate.set_opacity(1), dl.animate.set_opacity(1), enc.animate.set_opacity(0.12), el.animate.set_opacity(0.12),
                  toks.animate.next_to(dl, DOWN, buff=0.3), Transform(tag, t3))
        self.wait(1)
        # ViT
        patches = VGroup(*[Square(0.4).set_stroke(WHITE, 1).set_fill(interpolate_color(BLUE_E, YELLOW, (i % 3 + i // 3) / 4), 0.8) for i in range(9)]).arrange_in_grid(rows=3, buff=0.03)
        patches.move_to(toks)
        t4 = Text("2020: ViT — image patches are the tokens", font_size=24, color=YELLOW).move_to(tag)
        self.play(Transform(toks, patches), Transform(tag, t4))
        row = VGroup(*[Square(0.4).set_stroke(WHITE, 1).set_fill(interpolate_color(BLUE_E, YELLOW, (i % 3 + i // 3) / 4), 0.8) for i in range(9)]).arrange(RIGHT, buff=0.03)
        row.move_to(toks)
        self.play(Transform(toks, row))
        self.wait(0.8)
        # scale up
        t5 = Text("and then: stack it taller, feed it more", font_size=24, color=WHITE).move_to(tag)
        scene_grp = VGroup(enc, dec, el, dl, cross, toks)
        self.play(scene_grp.animate.scale(0.5).shift(DOWN * 1.4), Transform(tag, t5))
        more = VGroup(*[RoundedRectangle(corner_radius=0.04, width=1.1, height=0.25).set_stroke(K_COL, 1.5).set_fill(K_COL, 0.12) for _ in range(10)]).arrange(UP, buff=0.05)
        more.next_to(dec, UP, buff=0.05)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in more], lag_ratio=0.1, run_time=2.5))
        self.wait(1.5)
