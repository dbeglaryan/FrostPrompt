"""
Ultrasound Pulse Timing Diagram
Generates a professional textbook-style diagram showing pulse timing concepts
for sonography education.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
DPI = 100
WIDTH_PX, HEIGHT_PX = 800, 350
fig_w = WIDTH_PX / DPI
fig_h = HEIGHT_PX / DPI

TEAL = "#2BBCC4"
BLACK = "#000000"

CYCLES_PER_BURST = 3
NUM_BURSTS = 3

# Time units (arbitrary but visually tuned)
BURST_WIDTH = 1.0                       # width of one burst in x-units
GAP_WIDTH = BURST_WIDTH * 2.0           # silent gap = 2x burst
MARGIN_LEFT = 0.7
MARGIN_RIGHT = 0.4

TOTAL = MARGIN_LEFT + NUM_BURSTS * BURST_WIDTH + (NUM_BURSTS - 1) * GAP_WIDTH + GAP_WIDTH + MARGIN_RIGHT

AMPLITUDE = 0.20          # sine amplitude (axis coords)
BASELINE_Y = 0.05         # shift waveform slightly above center for label room below

LABEL_SIZE = 8
SMALL_SIZE = 7

# ---------------------------------------------------------------------------
# Build the waveform
# ---------------------------------------------------------------------------
samples_per_burst = 500
samples_per_gap = int(samples_per_burst * (GAP_WIDTH / BURST_WIDTH))

x_all = []
y_all = []
burst_starts = []
burst_ends = []
gap_starts = []
gap_ends = []

cursor = MARGIN_LEFT
for i in range(NUM_BURSTS):
    # --- burst ---
    burst_starts.append(cursor)
    xb = np.linspace(cursor, cursor + BURST_WIDTH, samples_per_burst)
    t_norm = (xb - cursor) / BURST_WIDTH
    yb = BASELINE_Y + AMPLITUDE * np.sin(2 * np.pi * CYCLES_PER_BURST * t_norm)
    x_all.append(xb)
    y_all.append(yb)
    cursor += BURST_WIDTH
    burst_ends.append(cursor)

    # --- gap (or trailing flat) ---
    gap_starts.append(cursor)
    gap_len = GAP_WIDTH
    xg = np.linspace(cursor, cursor + gap_len, samples_per_gap)
    yg = np.full_like(xg, BASELINE_Y)
    x_all.append(xg)
    y_all.append(yg)
    cursor += gap_len
    gap_ends.append(cursor)

x_wave = np.concatenate(x_all)
y_wave = np.concatenate(y_all)

# ---------------------------------------------------------------------------
# Figure setup
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=DPI)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.set_xlim(0, TOTAL)
ax.set_ylim(-0.58, 0.60)
ax.axis("off")

# ---------------------------------------------------------------------------
# Baseline axis with arrowheads at both ends
# ---------------------------------------------------------------------------
arrow_kw = dict(arrowstyle="-|>", color=BLACK, lw=0.7, mutation_scale=7)
ax.annotate("", xy=(TOTAL - 0.05, BASELINE_Y), xytext=(0.08, BASELINE_Y),
            arrowprops=arrow_kw)
ax.annotate("", xy=(0.08, BASELINE_Y), xytext=(TOTAL - 0.05, BASELINE_Y),
            arrowprops=arrow_kw)

# ---------------------------------------------------------------------------
# Draw waveform
# ---------------------------------------------------------------------------
ax.plot(x_wave, y_wave, color=TEAL, linewidth=1.6, solid_capstyle="round")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def draw_bracket(ax, x0, x1, y, height, label, fontsize=LABEL_SIZE,
                 side="top", color=BLACK, label_offset=0.03, label_ha=None):
    """Draw a square bracket with centred label."""
    sign = 1 if side == "top" else -1
    h = abs(height) * sign
    verts_x = [x0, x0, x1, x1]
    verts_y = [y, y + h, y + h, y]
    ax.plot(verts_x, verts_y, color=color, linewidth=0.8, solid_capstyle="butt")
    txt_y = y + h + label_offset * sign
    va = "bottom" if side == "top" else "top"
    ha = label_ha if label_ha else "center"
    txt_x = x0 if ha == "left" else (x0 + x1) / 2
    ax.text(txt_x, txt_y, label, ha=ha, va=va,
            fontsize=fontsize, fontfamily="sans-serif", color=color)


def draw_double_arrow(ax, x0, x1, y, label, fontsize=SMALL_SIZE, color=BLACK,
                      label_offset=0.03, side="bottom"):
    """Horizontal double-headed arrow with label."""
    arr = dict(arrowstyle="<->", color=color, lw=0.7, mutation_scale=6)
    ax.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=arr)
    sign = -1 if side == "bottom" else 1
    va = "top" if side == "bottom" else "bottom"
    ax.text((x0 + x1) / 2, y + label_offset * sign, label,
            ha="center", va=va, fontsize=fontsize,
            fontfamily="sans-serif", color=color)


# ---------------------------------------------------------------------------
# Annotations
# ---------------------------------------------------------------------------
b1s, b1e = burst_starts[0], burst_ends[0]
g1s, g1e = gap_starts[0], gap_ends[0]
b2s = burst_starts[1]
top = BASELINE_Y + AMPLITUDE
bot = BASELINE_Y - AMPLITUDE

# 1. "ON" bracket above burst 1
draw_bracket(ax, b1s, b1e, top + 0.04, 0.05, "ON",
             fontsize=LABEL_SIZE, side="top")

# 2. "OFF" bracket above gap 1
draw_bracket(ax, g1s, g1e, top + 0.04, 0.05, "OFF",
             fontsize=LABEL_SIZE, side="top")

# 3. "SPL (Spatial Pulse Length)" -- topmost bracket over burst 1
draw_bracket(ax, b1s, b1e, top + 0.19, 0.05,
             "SPL (Spatial Pulse Length)", fontsize=SMALL_SIZE, side="top",
             label_ha="left")

# 4. "Pulse Duration (PD)" -- bracket below burst 1
draw_bracket(ax, b1s, b1e, bot - 0.04, 0.05,
             "Pulse Duration (PD)", fontsize=SMALL_SIZE, side="bottom")

# 5. "Listening Time" -- double arrow below gap 1
draw_double_arrow(ax, g1s, g1e, bot - 0.14,
                  "Listening Time", fontsize=SMALL_SIZE, side="bottom")

# 6. "Pulse Repetition Period (PRP)" -- long bracket from burst1 start to burst2 start
draw_bracket(ax, b1s, b2s, bot - 0.24, 0.05,
             "Pulse Repetition Period (PRP)", fontsize=SMALL_SIZE, side="bottom")

# 7. Duty Factor equation at bottom centre
mid_x = TOTAL / 2
ax.text(mid_x, -0.54, "Duty Factor = PD / PRP",
        ha="center", va="bottom", fontsize=LABEL_SIZE,
        fontfamily="sans-serif", color=BLACK, style="italic")

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "output", "starprep-sonography")
os.makedirs(output_dir, exist_ok=True)
out_path = os.path.join(output_dir, "2n-pulse-timing.png")

fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.savefig(out_path, dpi=DPI, facecolor="white")
plt.close(fig)
print(f"Saved: {out_path}")
