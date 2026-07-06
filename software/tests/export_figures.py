"""Export architecture diagram and twiddle comparison tables as PNG figures."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import ConnectionPatch, FancyBboxPatch, FancyArrowPatch

from software.tests.twiddle_stats import analyze, pct

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "docs" / "figures"
SIZES = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]

COLORS = {
    "shift": "#2ecc71",
    "full": "#e74c3c",
    "trivial": "#95a5a6",
    "box_input": "#d6eaf8",
    "box_mem": "#fdebd0",
    "box_pipe": "#d5f5e3",
    "box_ntt": "#ebdef0",
    "box_alu": "#fadbd8",
    "box_out": "#d6eaf8",
    "arrow": "#2c3e50",
}


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def collect_stats():
    return [analyze(N) for N in SIZES if 65536 % N == 0]


def plot_architecture():
    """Clean two-panel architecture diagram: system pipeline + NTT engine detail."""

    palette = {
        "input": ("#E8F4FD", "#2471A3"),
        "memory": ("#FEF9E7", "#B7950B"),
        "pipe": ("#E9F7EF", "#1E8449"),
        "twiddle": ("#F4ECF7", "#7D3C98"),
        "ntt": ("#EBF5FB", "#1F618D"),
        "alu": ("#FDEDEC", "#C0392B"),
        "future": ("#FDFEFE", "#85929E"),
        "current": ("#E8F8F5", "#117A65"),
        "edge": "#566573",
        "arrow": "#2C3E50",
    }

    fig = plt.figure(figsize=(26, 13), facecolor="white")
    gs = fig.add_gridspec(
        2, 2,
        width_ratios=[3.15, 1],
        height_ratios=[1.05, 0.95],
        hspace=0.08,
        wspace=0.06,
    )
    ax_sys = fig.add_subplot(gs[0, 0])
    ax_ntt = fig.add_subplot(gs[1, 0])
    ax_road = fig.add_subplot(gs[:, 1])

    for ax in (ax_sys, ax_ntt):
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")

    ax_road.set_xlim(0, 100)
    ax_road.set_ylim(0, 100)
    ax_road.axis("off")

    fig.suptitle(
        "Fermat Convolution Accelerator  |  q = 65537  |  Software Reference Model",
        fontsize=18,
        fontweight="bold",
        y=0.97,
    )

    def rounded_box(ax, x, y, w, h, lines, face, edge, fontsize=11, lw=1.5, linestyle="-"):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=1.2",
            linewidth=lw,
            edgecolor=edge,
            facecolor=face,
            linestyle=linestyle,
        )
        ax.add_patch(patch)
        if isinstance(lines, str):
            lines = [lines]
        line_h = fontsize * 0.38
        total_h = line_h * len(lines)
        start_y = y + h / 2 + total_h / 2 - line_h / 2
        for i, line in enumerate(lines):
            ax.text(
                x + w / 2,
                start_y - i * line_h,
                line,
                ha="center",
                va="center",
                fontsize=fontsize,
                color="#1C2833",
                fontweight="semibold" if i == 0 else "normal",
            )
        return {
            "cx": x + w / 2,
            "cy": y + h / 2,
            "left": x,
            "right": x + w,
            "top": y + h,
            "bottom": y,
        }

    def section(ax, x, y, w, h, title, color):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.01,rounding_size=1.5",
            linewidth=1.2,
            edgecolor=palette["edge"],
            facecolor=color,
            alpha=0.35,
        )
        ax.add_patch(patch)
        ax.text(
            x + w / 2,
            y + h - 3.5,
            title,
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            color="#1B2631",
        )

    def arrow(ax, p1, p2, text=None, style="angle3,angleA=0,angleB=90", rad=0.0):
        if rad:
            style = f"arc3,rad={rad}"
        arr = FancyArrowPatch(
            p1,
            p2,
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=1.6,
            color=palette["arrow"],
            connectionstyle=style,
            shrinkA=6,
            shrinkB=6,
        )
        ax.add_patch(arr)
        if text:
            mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            ax.text(mx, my + 2.2, text, ha="center", fontsize=9, color="#566573")

    # ── TOP PANEL: system-level dataflow ──────────────────────────────────
    ax_sys.text(
        50, 96, "System Dataflow — Polynomial Multiplication",
        ha="center",
        fontsize=14,
        fontweight="bold",
        color="#1B2631",
    )

    section(ax_sys, 2, 8, 18, 78, "Inputs", palette["input"][0])
    section(ax_sys, 22, 8, 14, 78, "Coefficient SRAM", palette["memory"][0])
    section(ax_sys, 38, 8, 48, 78, "Multiply Pipeline", palette["pipe"][0])
    section(ax_sys, 88, 8, 10, 78, "Output", palette["input"][0])

    pa = rounded_box(
        ax_sys, 5, 58, 12, 14,
        ["Polynomial A", "coeff[0..N-1]"],
        *palette["input"],
    )
    pb = rounded_box(
        ax_sys, 5, 28, 12, 14,
        ["Polynomial B", "coeff[0..N-1]"],
        *palette["input"],
    )
    buf_a = rounded_box(ax_sys, 25, 60, 8, 10, ["Buffer A"], *palette["memory"])
    buf_b = rounded_box(ax_sys, 25, 30, 8, 10, ["Buffer B"], *palette["memory"])
    buf_c = rounded_box(ax_sys, 25, 12, 8, 10, ["Buffer C"], *palette["memory"], fontsize=10)

    stages = []
    x0, sw, gap = 41, 8.5, 1.2
    stage_defs = [
        ("1. Preprocess", "coeff x pre_twiddle"),
        ("2. Forward NTT", "bit-rev, stages, bit-rev"),
        ("3. Pointwise", "A_hat[i] x B_hat[i]"),
        ("4. Inverse NTT", "stages, scale N^-1"),
        ("5. Postprocess", "coeff x post_twiddle"),
    ]
    for i, (title, sub) in enumerate(stage_defs):
        x = x0 + i * (sw + gap)
        stages.append(
            rounded_box(ax_sys, x, 32, sw, 22, [title, sub], *palette["pipe"], fontsize=10)
        )

    out = rounded_box(ax_sys, 89.5, 38, 7, 18, ["Polynomial C"], *palette["input"])

    arrow(ax_sys, (pa["right"], pa["cy"]), (buf_a["left"], buf_a["cy"]))
    arrow(ax_sys, (pb["right"], pb["cy"]), (buf_b["left"], buf_b["cy"]))
    arrow(ax_sys, (buf_a["right"], buf_a["cy"]), (stages[0]["left"], stages[0]["cy"] + 6))
    arrow(ax_sys, (buf_b["right"], buf_b["cy"]), (stages[0]["left"], stages[0]["cy"] - 6))

    for i in range(len(stages) - 1):
        arrow(
            ax_sys,
            (stages[i]["right"], stages[i]["cy"]),
            (stages[i + 1]["left"], stages[i + 1]["cy"]),
        )
    arrow(ax_sys, (stages[-1]["right"], stages[-1]["cy"]), (out["left"], out["cy"]))
    arrow(ax_sys, (stages[-1]["cx"], stages[-1]["bottom"]), (buf_c["cx"], buf_c["top"]))

    # Twiddle ROM — below pipeline, clean vertical feeds
    section(ax_sys, 38, 8, 48, 20, "Twiddle ROM  (offline / synthesis-time tables)", palette["twiddle"][0])
    tw = []
    tw_labels = [
        "Preprocess table",
        "Forward stage tables",
        "Inverse stage tables",
        "Postprocess table",
    ]
    tw_x = [40, 52.5, 65, 77.5]
    for x, label in zip(tw_x, tw_labels):
        tw.append(rounded_box(ax_sys, x, 11, 10, 10, [label], *palette["twiddle"], fontsize=9))

    arrow(ax_sys, (tw[0]["cx"], tw[0]["top"]), (stages[0]["cx"], stages[0]["bottom"]))
    arrow(ax_sys, (tw[1]["cx"], tw[1]["top"]), (stages[1]["cx"], stages[1]["bottom"]))
    arrow(ax_sys, (tw[2]["cx"], tw[2]["top"]), (stages[3]["cx"], stages[3]["bottom"]))
    arrow(ax_sys, (tw[3]["cx"], tw[3]["top"]), (stages[4]["cx"], stages[4]["bottom"]))

    # ── BOTTOM PANEL: NTT engine internals ────────────────────────────────
    ax_ntt.text(
        50, 96, "NTT Engine Internals  (used by Forward & Inverse transforms)",
        ha="center",
        fontsize=14,
        fontweight="bold",
        color="#1B2631",
    )

    section(ax_ntt, 2, 10, 96, 80, "", palette["ntt"][0])

    ntt_flow = []
    ntt_defs = [
        ("Bit-reverse", "permute input"),
        ("Stage scheduler", "log2(N) stages"),
        ("Radix-2 butterfly", "N/2 butterflies / stage  [current]"),
        ("Modular ALU", "add, sub, mul, reduce"),
    ]
    nx = [8, 30, 52, 78]
    for x, (title, sub) in zip(nx, ntt_defs):
        ntt_flow.append(
            rounded_box(ax_ntt, x, 48, 16, 20, [title, sub], *palette["ntt"], fontsize=11)
        )

    for i in range(len(ntt_flow) - 1):
        arrow(
            ax_ntt,
            (ntt_flow[i]["right"], ntt_flow[i]["cy"]),
            (ntt_flow[i + 1]["left"], ntt_flow[i + 1]["cy"]),
        )

    # Butterfly PE detail
    section(ax_ntt, 8, 12, 58, 30, "Butterfly Processing Element", palette["pipe"][0])
    tw_lookup = rounded_box(
        ax_ntt, 12, 22, 13, 12,
        ["Twiddle lookup", "(stage, offset)"],
        *palette["twiddle"],
        fontsize=10,
    )
    shift = rounded_box(
        ax_ntt, 30, 30, 12, 10,
        ["Shift network", "x 2^k  (pow2)"],
        *palette["pipe"],
        fontsize=10,
    )
    full = rounded_box(
        ax_ntt, 30, 16, 12, 10,
        ["Full multiplier", "x w  (non-pow2)"],
        *palette["alu"],
        fontsize=10,
    )
    bfly = rounded_box(
        ax_ntt, 48, 22, 12, 12,
        ["Butterfly", "a' = a + t", "b' = a - t"],
        *palette["ntt"],
        fontsize=10,
    )

    arrow(ax_ntt, (tw_lookup["right"], tw_lookup["cy"] + 3), (shift["left"], shift["cy"]))
    arrow(ax_ntt, (tw_lookup["right"], tw_lookup["cy"] - 3), (full["left"], full["cy"]))
    arrow(ax_ntt, (shift["right"], shift["cy"]), (bfly["left"], bfly["cy"] + 3))
    arrow(ax_ntt, (full["right"], full["cy"]), (bfly["left"], bfly["cy"] - 3))
    arrow(ax_ntt, (ntt_flow[2]["cx"], ntt_flow[2]["bottom"]), (bfly["cx"], bfly["top"] + 2))
    arrow(ax_ntt, (bfly["right"], bfly["cy"]), (ntt_flow[3]["left"], ntt_flow[3]["cy"] - 8))

    # Legend — bottom-right, clear of PE detail
    ax_ntt.text(78, 38, "Legend", ha="center", fontsize=11, fontweight="bold", color="#1B2631")
    legend_items = [
        (palette["input"][0], palette["input"][1], "I/O"),
        (palette["memory"][0], palette["memory"][1], "Memory"),
        (palette["pipe"][0], palette["pipe"][1], "Pipeline"),
        (palette["twiddle"][0], palette["twiddle"][1], "Twiddles"),
        (palette["ntt"][0], palette["ntt"][1], "NTT logic"),
        (palette["alu"][0], palette["alu"][1], "Full mult"),
    ]
    ly = 32
    for i, (face, edge, label) in enumerate(legend_items):
        col, row = i % 2, i // 2
        rounded_box(ax_ntt, 70 + col * 14, ly - row * 8, 12, 6, [label], face, edge, fontsize=9)

    # ── RIGHT SIDEBAR: hardware roadmap (from README) ─────────────────────
    road_bg = FancyBboxPatch(
        (2, 2), 96, 96,
        boxstyle="round,pad=0.02,rounding_size=2",
        linewidth=1.5,
        edgecolor=palette["edge"],
        facecolor="#F8F9F9",
    )
    ax_road.add_patch(road_bg)

    ax_road.text(
        50, 96, "Hardware Roadmap",
        ha="center", fontsize=15, fontweight="bold", color="#1B2631",
    )
    ax_road.text(
        50, 92.5,
        "Python golden model  -->  RTL / FPGA / ASIC",
        ha="center", fontsize=10, color="#566573", style="italic",
    )

    def road_section(y, h, title, color):
        patch = FancyBboxPatch(
            (6, y), 88, h,
            boxstyle="round,pad=0.01,rounding_size=1.2",
            linewidth=1.0,
            edgecolor=palette["edge"],
            facecolor=color,
            alpha=0.45,
        )
        ax_road.add_patch(patch)
        ax_road.text(50, y + h - 4, title, ha="center", fontsize=11, fontweight="bold", color="#1B2631")

    def road_item(y, lines, face, edge, planned=False):
        rounded_box(
            ax_road, 10, y, 80, 6, lines, face, edge,
            fontsize=9, lw=1.4, linestyle="--" if planned else "-",
        )

    road_section(74, 22, "Current — verified (radix-2 reference)", palette["current"][0])
    current_items = [
        "Radix-2 DIT negacyclic NTT pipeline",
        "Fermat mod-65537 modular ALU",
        "Pow2 shift twiddle path + full mult fallback",
        "Stage-wise twiddle memory abstraction",
    ]
    cy = 84
    for item in current_items:
        road_item(cy, [f"[done]  {item}"], *palette["current"])
        cy -= 5

    road_section(40, 31, "Next — hardware optimizations", palette["future"][0])
    planned_items = [
        ("D1 arithmetic", "hardware-aligned coefficient datapath"),
        ("Radix-32 fused stages", "fewer stages, higher throughput"),
        ("Mixed-radix decomposition", "radix-2 + radix-32 NTT path"),
        ("Bit-reversed twiddle ROM", "RTL-friendly memory layout"),
        ("Shift-dominant butterfly network", "minimize non-pow2 mults"),
    ]
    py = 61
    for title, sub in planned_items:
        road_item(py, [title, sub], *palette["future"], planned=True)
        py -= 5.5

    road_section(7, 30, "RTL bring-up & validation", palette["ntt"][0])
    rtl_items = [
        ("Cycle-accurate simulator", "match Python stage-by-stage"),
        ("SystemVerilog RTL", "1:1 module mapping from software"),
        ("FPGA validation", "timing + functional sign-off"),
        ("ASIC implementation", "PQC / FHE accelerator target"),
    ]
    ry = 28
    for title, sub in rtl_items:
        road_item(ry, [title, sub], *palette["ntt"], planned=True)
        ry -= 5.5

    # Dashed arrow: reference model evolves toward hardware roadmap
    fig.add_artist(
        ConnectionPatch(
            xyA=(99, 58), coordsA=ax_ntt.transData,
            xyB=(6, 55), coordsB=ax_road.transData,
            arrowstyle="-|>",
            linestyle=(0, (6, 4)),
            color="#85929E",
            lw=1.8,
            shrinkA=4,
            shrinkB=4,
        )
    )
    ax_road.text(
        50, 3.5,
        "Each software module maps to a future RTL block",
        ha="center", fontsize=8.5, color="#7F8C8D",
    )

    fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.03)
    path = OUTPUT_DIR / "architecture.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_stacked_bars(stats, category_fn, title, filename, ylabel="Share of operations (%)"):
    labels = [str(s["N"]) for s in stats]
    shift = [category_fn(s)["shift_pct"] for s in stats]
    full = [category_fn(s)["full_pct"] for s in stats]
    trivial = [category_fn(s)["trivial_pct"] for s in stats]

    fig, ax = plt.subplots(figsize=(14, 6))
    x = range(len(labels))
    ax.bar(x, shift, label="Shift (pow2 twiddle)", color=COLORS["shift"])
    ax.bar(x, full, bottom=shift, label="Full multiply (non-pow2)", color=COLORS["full"])
    ax.bar(
        x,
        trivial,
        bottom=[shift[i] + full[i] for i in range(len(labels))],
        label="Trivial (w=1)",
        color=COLORS["trivial"],
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=45)
    ax.set_xlabel("NTT size N")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 100)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    path = OUTPUT_DIR / filename
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_line_comparison(stats):
    fig, ax = plt.subplots(figsize=(14, 6))

    def line(yvals, label, color, marker):
        ax.plot(
            [s["N"] for s in stats],
            yvals,
            marker=marker,
            linewidth=2,
            label=label,
            color=color,
        )

    line(
        [pct(s["forward"]["full"], s["forward"]["total"]) for s in stats],
        "Butterfly twiddles (forward NTT)",
        COLORS["full"],
        "o",
    )
    line(
        [pct(s["preprocess"]["full"], s["preprocess"]["total"]) for s in stats],
        "Pre/post twiddles (one pass)",
        "#8e44ad",
        "s",
    )
    line(
        [pct(s["pipe_full"], s["pipe_total"]) for s in stats],
        "Full pipeline twiddles",
        "#2980b9",
        "^",
    )
    line(
        [pct(s["all_full"], s["all_total"]) for s in stats],
        "All ops (incl. pointwise + N⁻¹)",
        "#d35400",
        "D",
    )

    ax.set_xscale("log", base=2)
    ax.set_xticks([s["N"] for s in stats])
    ax.set_xticklabels([str(s["N"]) for s in stats])
    ax.set_xlabel("NTT size N")
    ax.set_ylabel("Full multiply share (%)")
    ax.set_title(
        "Full-Multiply Share vs N (q = 65537, radix-2 DIT NTT)",
        fontsize=13,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left")
    fig.tight_layout()
    path = OUTPUT_DIR / "full_mult_comparison.png"
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def make_table_rows(stats, row_fn, headers):
    return [headers] + [row_fn(s) for s in stats]


def plot_table(title, rows, filename, col_widths=None):
    fig, ax = plt.subplots(figsize=(16, 0.45 * len(rows) + 1.2))
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)

    table = ax.table(
        cellText=rows[1:],
        colLabels=rows[0],
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.35)

    if col_widths:
        for i, w in enumerate(col_widths):
            for row in range(len(rows)):
                table[(row, i)].set_width(w)

    for col in range(len(rows[0])):
        table[(0, col)].set_facecolor("#d5dbdb")
        table[(0, col)].set_text_props(fontweight="bold")

    for row in range(1, len(rows)):
        if row % 2 == 0:
            for col in range(len(rows[0])):
                table[(row, col)].set_facecolor("#f8f9f9")

    fig.tight_layout()
    path = OUTPUT_DIR / filename
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def export_tables(stats):
    paths = []

    butterfly_rows = make_table_rows(
        stats,
        lambda s: [
            str(s["N"]),
            str(s["forward"]["total"]),
            str(s["forward"]["shift"]),
            str(s["forward"]["full"]),
            str(s["forward"]["trivial"]),
            f"{pct(s['forward']['shift'], s['forward']['total']):.1f}%",
            f"{pct(s['forward']['full'], s['forward']['total']):.1f}%",
        ],
        ["N", "Butterflies", "Shift", "Full", "Trivial", "Shift %", "Full %"],
    )
    paths.append(
        plot_table(
            "Butterfly Twiddles — One Forward NTT",
            butterfly_rows,
            "table_butterfly_twiddles.png",
        )
    )

    prepost_rows = make_table_rows(
        stats,
        lambda s: [
            str(s["N"]),
            str(s["preprocess"]["shift"]),
            str(s["preprocess"]["full"]),
            str(s["preprocess"]["trivial"]),
            f"{pct(s['preprocess']['full'], s['preprocess']['total']):.1f}%",
        ],
        ["N", "Shift", "Full", "Trivial", "Full %"],
    )
    paths.append(
        plot_table(
            "Pre/Post Twiddles — One Pass (N coefficients)",
            prepost_rows,
            "table_prepost_twiddles.png",
        )
    )

    pipeline_rows = make_table_rows(
        stats,
        lambda s: [
            str(s["N"]),
            str(s["pipe_total"]),
            str(s["pipe_shift"]),
            str(s["pipe_full"]),
            str(s["pipe_trivial"]),
            f"{pct(s['pipe_shift'], s['pipe_total']):.1f}%",
            f"{pct(s['pipe_full'], s['pipe_total']):.1f}%",
            f"{pct(s['pipe_trivial'], s['pipe_total']):.1f}%",
        ],
        ["N", "Total", "Shift", "Full", "Trivial", "Shift %", "Full %", "Triv %"],
    )
    paths.append(
        plot_table(
            "Full Polynomial Multiply Pipeline — Twiddle Operations",
            pipeline_rows,
            "table_pipeline_twiddles.png",
        )
    )

    all_ops_rows = make_table_rows(
        stats,
        lambda s: [
            str(s["N"]),
            str(s["all_total"]),
            str(s["pipe_shift"]),
            str(s["all_full"]),
            f"{pct(s['pipe_shift'], s['all_total']):.1f}%",
            f"{pct(s['all_full'], s['all_total']):.1f}%",
        ],
        ["N", "Total ops", "Shift", "Full mult", "Shift %", "Full %"],
    )
    paths.append(
        plot_table(
            "All Operations — Twiddles + Pointwise + N⁻¹ Scale",
            all_ops_rows,
            "table_all_operations.png",
        )
    )

    return paths


def export_charts(stats):
    paths = []

    def butterfly(s):
        t = s["forward"]["total"]
        return {
            "shift_pct": pct(s["forward"]["shift"], t),
            "full_pct": pct(s["forward"]["full"], t),
            "trivial_pct": pct(s["forward"]["trivial"], t),
        }

    def prepost(s):
        t = s["preprocess"]["total"]
        return {
            "shift_pct": pct(s["preprocess"]["shift"], t),
            "full_pct": pct(s["preprocess"]["full"], t),
            "trivial_pct": pct(s["preprocess"]["trivial"], t),
        }

    def pipeline(s):
        t = s["pipe_total"]
        return {
            "shift_pct": pct(s["pipe_shift"], t),
            "full_pct": pct(s["pipe_full"], t),
            "trivial_pct": pct(s["pipe_trivial"], t),
        }

    paths.append(
        plot_stacked_bars(
            stats,
            butterfly,
            "Butterfly Twiddles — Shift vs Full vs Trivial (one forward NTT)",
            "chart_butterfly_twiddles.png",
        )
    )
    paths.append(
        plot_stacked_bars(
            stats,
            prepost,
            "Pre/Post Twiddles — Shift vs Full vs Trivial (one pass)",
            "chart_prepost_twiddles.png",
        )
    )
    paths.append(
        plot_stacked_bars(
            stats,
            pipeline,
            "Full Multiply Pipeline — Twiddle Operation Mix",
            "chart_pipeline_twiddles.png",
        )
    )
    paths.append(plot_line_comparison(stats))
    return paths


def main():
    ensure_output_dir()
    stats = collect_stats()
    exported = []
    exported.append(plot_architecture())
    exported.extend(export_charts(stats))
    exported.extend(export_tables(stats))

    print(f"Exported {len(exported)} figures to {OUTPUT_DIR}:")
    for path in exported:
        print(f"  {path.name}")


if __name__ == "__main__":
    main()
