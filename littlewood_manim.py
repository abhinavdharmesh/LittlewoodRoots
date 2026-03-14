"""
littlewood_manim.py  —  Manim animation of Littlewood polynomial roots, degrees 1–10
Each degree: all 2^n polynomials are computed, roots plotted as dots,
then the next degree layers on top, showing density building toward |z|=1.

Install:
    pip install manim numpy

Run (renders MP4, ~1080p):
    manim -pqh littlewood_manim.py LittlewoodRoots

Run faster preview (720p, lower quality):
    manim -pql littlewood_manim.py LittlewoodRoots

Run just a PNG frame at degree 10:
    manim -s littlewood_manim.py LittlewoodRoots

Output lands in ./media/videos/littlewood_manim/
"""

from manim import *
import numpy as np
from itertools import product


# ─────────────────────────────────────────────
# Root computation (pure numpy, fast enough for degree ≤ 10)
# ─────────────────────────────────────────────

def littlewood_roots(degree: int) -> np.ndarray:
    """
    Return all roots of all Littlewood polynomials of the given degree.
    Polynomial form: a_0 + a_1*x + ... + a_n*x^n,  a_i ∈ {-1, +1}
    Returns complex numpy array of shape (degree * 2^degree,)
    """
    roots = []
    for coeffs in product([-1, 1], repeat=degree + 1):
        # numpy wants highest degree first
        r = np.roots(list(reversed(coeffs)))
        roots.append(r)
    return np.concatenate(roots)


def all_roots_up_to(max_degree: int):
    """Returns dict {degree: roots_array} for degrees 1..max_degree."""
    result = {}
    for d in range(1, max_degree + 1):
        print(f"  Computing degree {d}...")
        result[d] = littlewood_roots(d)
    return result


# ─────────────────────────────────────────────
# Color ramp: maps degree to a colour
# Low degree = dim blue, high degree = bright amber/white
# ─────────────────────────────────────────────

DEGREE_COLORS = [
    "#1a2a4a",  # degree 1  — near-black blue
    "#1e3f7a",  # degree 2
    "#1a5fa8",  # degree 3
    "#0e7fc2",  # degree 4
    "#0a9fd4",  # degree 5
    "#12b89e",  # degree 6  — teal
    "#3eca6a",  # degree 7  — green
    "#c8a020",  # degree 8  — amber
    "#e07020",  # degree 9  — orange
    "#f0f0e0",  # degree 10 — near-white
]

DOT_OPACITIES = [
    0.25, 0.28, 0.30, 0.35, 0.40,
    0.45, 0.50, 0.55, 0.65, 0.80,
]

DOT_RADII = [
    0.025, 0.022, 0.020, 0.018, 0.016,
    0.014, 0.012, 0.011, 0.010, 0.009,
]


# ─────────────────────────────────────────────
# Scene
# ─────────────────────────────────────────────

class LittlewoodRoots(Scene):
    MAX_DEGREE = 10

    def construct(self):
        # ── Background ──
        self.camera.background_color = "#050810"

        # ── Title (top) ──
        title = Text(
            "Littlewood Polynomial Roots",
            font="CMU Serif",
            font_size=32,
            color="#c8d8f0",
        ).to_edge(UP, buff=0.3)

        subtitle = Text(
            "P(z) = a₀ + a₁z + … + aₙzⁿ,   aₖ ∈ {−1, +1}",
            font="CMU Serif",
            font_size=18,
            color="#6080a0",
        ).next_to(title, DOWN, buff=0.12)

        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.8)
        self.play(FadeIn(subtitle), run_time=0.5)

        # ── Complex plane ──
        plane = ComplexPlane(
            x_range=[-2.2, 2.2, 1],
            y_range=[-2.2, 2.2, 1],
            x_length=6.5,
            y_length=6.5,
            background_line_style={
                "stroke_color": "#1a2540",
                "stroke_width": 0.8,
                "stroke_opacity": 0.7,
            },
            axis_config={
                "stroke_color": "#2a4070",
                "stroke_width": 1.2,
            },
        ).shift(DOWN * 0.3)

        # Axis labels
        re_label = Text("Re(z)", font="CMU Serif", font_size=14, color="#3a5a80")
        im_label = Text("Im(z)", font="CMU Serif", font_size=14, color="#3a5a80")
        re_label.next_to(plane.get_right(), RIGHT, buff=0.15)
        im_label.next_to(plane.get_top(), UP, buff=0.1)

        # Unit circle — the key object
        unit_circle = Circle(
            radius=plane.get_x_unit_size(),   # matches plane scale
            color="#304080",
            stroke_width=1.2,
            stroke_opacity=0.6,
        ).move_to(plane.get_origin())

        self.play(
            Create(plane, run_time=1.2),
            FadeIn(re_label), FadeIn(im_label),
        )
        self.play(Create(unit_circle, run_time=0.8))
        self.wait(0.3)

        # ── Degree counter (bottom right) ──
        degree_label = always_redraw(lambda: Text(
            "", font="CMU Serif", font_size=22, color="#8090b0"
        ))  # placeholder; we'll update manually

        # ── Precompute all roots ──
        print("Pre-computing roots for degrees 1–10...")
        all_roots = all_roots_up_to(self.MAX_DEGREE)
        print("Done.")

        # ── Animate degree by degree ──
        running_dot_groups = VGroup()

        for d in range(1, self.MAX_DEGREE + 1):
            roots = all_roots[d]
            color = DEGREE_COLORS[d - 1]
            opacity = DOT_OPACITIES[d - 1]
            radius = DOT_RADII[d - 1]

            # Convert complex roots → Manim plane coordinates
            dots = VGroup()
            for z in roots:
                x, y = z.real, z.imag
                # skip roots far outside our view
                if abs(x) > 2.15 or abs(y) > 2.15:
                    continue
                pt = plane.number_to_point(complex(x, y))
                dot = Dot(point=pt, radius=radius, color=color)
                dot.set_opacity(opacity)
                dots.add(dot)

            # Degree label update
            deg_text = Text(
                f"n = {d}   ({len(roots):,} roots)",
                font="CMU Serif",
                font_size=20,
                color=color,
            ).to_corner(DR, buff=0.4)

            # Count label (cumulative)
            total_polys = sum(2 ** k for k in range(1, d + 1))
            poly_text = Text(
                f"{total_polys:,} polynomials total",
                font="CMU Serif",
                font_size=14,
                color="#405060",
            ).next_to(deg_text, UP, buff=0.1)

            # Animate dots appearing
            # For low degrees: Create each dot individually (few dots)
            # For high degrees: just FadeIn the group (too many for per-dot)
            if len(dots) <= 200:
                anim = LaggedStart(
                    *[GrowFromCenter(dot, run_time=0.15) for dot in dots],
                    lag_ratio=0.05,
                )
            else:
                anim = FadeIn(dots, run_time=0.6)

            if d == 1:
                self.play(
                    anim,
                    FadeIn(deg_text),
                    FadeIn(poly_text),
                )
            else:
                self.play(
                    anim,
                    Transform(prev_deg_text, deg_text),
                    Transform(prev_poly_text, poly_text),
                )

            running_dot_groups.add(dots)

            # Hold longer on early degrees so viewer can see structure
            hold_time = max(0.2, 1.8 - d * 0.15)
            self.wait(hold_time)

            prev_deg_text = deg_text if d == 1 else prev_deg_text
            prev_poly_text = poly_text if d == 1 else prev_poly_text

        # ── Final hold: highlight unit circle ──
        self.play(
            unit_circle.animate.set_stroke(color="#f0c060", width=2.0, opacity=0.9),
            run_time=1.0,
        )

        # Annotation: |z| = 1
        circle_label = Text("|z| = 1", font="CMU Serif", font_size=16, color="#f0c060")
        circle_label.next_to(
            plane.number_to_point(complex(0, 1.05)),
            RIGHT, buff=0.15,
        )
        self.play(FadeIn(circle_label, shift=RIGHT * 0.1), run_time=0.6)

        # Final caption
        caption = Text(
            "As n → ∞, roots concentrate on the unit circle",
            font="CMU Serif",
            font_size=18,
            color="#8090b0",
        ).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(caption, shift=UP * 0.1), run_time=0.8)

        self.wait(3.0)

        # ── Outro fade ──
        self.play(
            FadeOut(VGroup(running_dot_groups, unit_circle, plane,
                           title, subtitle, circle_label, caption,
                           prev_deg_text, prev_poly_text,
                           re_label, im_label)),
            run_time=1.5,
        )


# ─────────────────────────────────────────────
# Bonus scene: zoom into unit circle boundary at degree 10
# Run with: manim -pqh littlewood_manim.py LittlewoodBoundary
# ─────────────────────────────────────────────

class LittlewoodBoundary(Scene):
    """
    Zoomed view near |z| = 1, showing the lattice/fractal structure
    that appears in your wallpaper crop.
    """

    def construct(self):
        self.camera.background_color = "#050810"

        title = Text(
            "Boundary structure near |z| = 1  (n = 10)",
            font="CMU Serif", font_size=26, color="#c8d8f0",
        ).to_edge(UP, buff=0.35)
        self.play(FadeIn(title), run_time=0.6)

        # Zoomed plane — only show a strip near the unit circle
        plane = ComplexPlane(
            x_range=[-0.3, 0.3, 0.1],
            y_range=[0.85, 1.15, 0.1],
            x_length=7.0,
            y_length=3.5,
            background_line_style={
                "stroke_color": "#1a2540",
                "stroke_width": 0.6,
                "stroke_opacity": 0.5,
            },
        ).shift(DOWN * 0.5)

        self.play(Create(plane), run_time=0.8)

        print("Computing degree 10 roots for boundary scene...")
        roots = littlewood_roots(10)
        print(f"  {len(roots)} roots")

        # Filter to the zoomed region
        strip_roots = [z for z in roots
                       if -0.28 < z.real < 0.28 and 0.87 < z.imag < 1.13]
        print(f"  {len(strip_roots)} roots in zoomed region")

        dots = VGroup()
        for z in strip_roots:
            pt = plane.number_to_point(complex(z.real, z.imag))
            dot = Dot(point=pt, radius=0.04, color="#f0a030")
            dot.set_opacity(0.7)
            dots.add(dot)

        # Unit circle arc in this zoomed view
        # At this zoom, the arc is nearly a horizontal line at Im(z)=1
        arc_pts = [
            plane.number_to_point(np.exp(1j * theta))
            for theta in np.linspace(np.pi / 2 - 0.35, np.pi / 2 + 0.35, 80)
        ]
        arc = VMobject(stroke_color="#4060c0", stroke_width=1.5, stroke_opacity=0.5)
        arc.set_points_as_corners(arc_pts)

        self.play(Create(arc), run_time=0.5)
        self.play(FadeIn(dots, run_time=1.2))

        arc_label = Text("|z| = 1", font="CMU Serif", font_size=14, color="#4060c0")
        arc_label.next_to(plane.number_to_point(complex(0.25, 1.0)), RIGHT, buff=0.1)
        self.play(FadeIn(arc_label))

        caption = Text(
            "Self-similar lattice structure — the pattern in your wallpaper",
            font="CMU Serif", font_size=16, color="#607080",
        ).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(caption))

        self.wait(4.0)
