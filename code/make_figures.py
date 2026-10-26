#!/usr/bin/env python3
"""Draw the study figures from results/numbers.json into figures/.

Added after the sprint (Oct 26, 2026). Reads only numbers.json, so run
collect_numbers.py first. Needs matplotlib.

    python3 code/collect_numbers.py && python3 code/make_figures.py
"""
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
N = json.loads((ROOT / "results" / "numbers.json").read_text())
OUT = ROOT / "figures"

# One color per condition, used in every figure.
COLOR = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a"}
NAME = {"A": "A: no disclosure", "B": "B: awareness", "C": "C: invitation"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
MONITORS = [("qwen", "Qwen2.5-14B"), ("haiku", "Claude Haiku 4.5"), ("gpt5", "GPT-5 mini")]

plt.rcParams.update({
    "font.size": 10, "text.color": INK, "axes.labelcolor": INK2,
    "axes.edgecolor": GRID, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "legend.frameon": False, "savefig.dpi": 200,
})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def deception_rates():
    beh = N["core"]["behaviour"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    width = 0.26
    for i, c in enumerate("ABC"):
        xs = [g + (i - 1) * width for g in range(2)]
        vals = [beh[game][c]["all"]["rate"] for game in ("diners", "weakestlink")]
        ks = [beh[game][c]["all"]["premeditated"] for game in ("diners", "weakestlink")]
        ax.bar(xs, vals, width * 0.92, color=COLOR[c], label=NAME[c])
        for x, v, k in zip(xs, vals, ks):
            ax.text(x, v + 0.012, f"{v:.1%}\n({k}/200)", ha="center", va="bottom",
                    fontsize=8, color=INK2)
    ax.set_xticks([0, 1], ["Diners", "Weakest Link"])
    ax.set_ylim(0, 0.56)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("Premeditated deception rate")
    ax.set_title("Telling agents about the monitor raised deception in Diners",
                 loc="left", fontsize=11)
    ax.legend(loc="upper right", fontsize=8.5)
    save(fig, "fig1_deception_rates")


def recall_by_monitor():
    rows = [("qwen", N["core"]["monitor"])] + [(k, N["panel"][k]) for k in ("haiku", "gpt5")]
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.2), sharey=True)
    for ax, metric, title in ((axes[0], "recall", "Recall at each monitor's threshold"),
                              (axes[1], "auroc", "AUROC (note: axis starts at 0.9)")):
        for y, (key, m) in enumerate(rows):
            for c, dy in (("B", 0.13), ("C", -0.13)):
                e = m["by_condition"][c]
                x = e[metric]
                if metric == "recall":
                    lo, hi = e["ci95"]
                    ax.plot([lo, hi], [y + dy] * 2, color=COLOR[c], lw=2, solid_capstyle="round")
                ax.plot([x], [y + dy], "o", ms=8, color=COLOR[c], mec="white", mew=1.5,
                        label=NAME[c] if y == 0 else None)
                ax.text(x, y + dy + 0.16, f"{x:.2f}", ha="center", fontsize=7.5, color=INK2)
        ax.set_xlim(*((0, 1.02) if metric == "recall" else (0.9, 1.0)))
        ax.set_title(title, loc="left", fontsize=10)
        ax.grid(axis="x", color=GRID)
        ax.grid(axis="y", visible=False)
    labels = [f"{dict(MONITORS)[k]}\n(threshold {m['threshold']})" for k, m in rows]
    axes[0].set_yticks(range(len(rows)), labels)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Lines: 95% trial-cluster bootstrap interval", fontsize=8)
    axes[1].legend(loc="lower left", fontsize=8.5)
    axes[1].set_xlabel("Ranking barely moves; threshold placement does", fontsize=8)
    fig.suptitle("The invitation's effect on detection depends on the monitor",
                 x=0.01, ha="left", fontsize=11)
    save(fig, "fig2_recall_by_monitor")


def pact_detection():
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.0), sharey=True)
    width = 0.36
    for ax, arm, title in ((axes[0], "pact", "Executed pact pairs flagged"),
                           (axes[1], "innocent", "Innocent pairs flagged")):
        for i, c in enumerate("BC"):
            xs, vals, txt = [], [], []
            for j, (key, _) in enumerate(MONITORS):
                cell = N["pact"][key]["cells"][arm][c]
                den = cell["pairs_both_premeditated"] if arm == "pact" else cell["pairs"]
                num = cell["executed_pairs_flagged"] if arm == "pact" else cell["pairs_flagged"]
                xs.append(j + (i - 0.5) * width)
                vals.append(num / den)
                txt.append(f"{num}/{den}")
            ax.bar(xs, vals, width * 0.9, color=COLOR[c], label=NAME[c])
            for x, v, t in zip(xs, vals, txt):
                ax.text(x, v + 0.02, t, ha="center", va="bottom", fontsize=7.5, color=INK2)
        ax.set_xticks(range(3), [name.replace(" ", "\n", 1) if len(name) > 12 else name
                                 for _, name in MONITORS], fontsize=8.5)
        ax.set_title(title, loc="left", fontsize=10)
        ax.set_ylim(0, 1.15)
    axes[0].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    axes[1].legend(loc="upper right", fontsize=8.5)
    fig.suptitle("Pact extension: constructed collusion against coordinated honesty",
                 x=0.01, ha="left", fontsize=11)
    save(fig, "fig3_pact_detection")


def positive_scores():
    dist = N["core"]["positive_scores_diners_heldout"]
    thr = N["core"]["monitor"]["threshold"]
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    # Bars sit just left of their score so none straddles the threshold line.
    for c, dx in (("B", -2.0), ("C", -0.1)):
        counts = {int(k): v for k, v in dist[c].items()}
        total = sum(counts.values())
        missed = sum(v for k, v in counts.items() if k < thr)
        xs = [k + dx for k in counts]
        vals = [v / total for v in counts.values()]
        ax.bar(xs, vals, 1.8, color=COLOR[c],
               label=f"{NAME[c]} ({total} rounds, {missed} below threshold)")
        for x, v, k in zip(xs, vals, counts.values()):
            ax.text(x, v + 0.012, str(k), ha="center", va="bottom", fontsize=7.5, color=INK2)
    ax.axvline(thr, color=INK2, lw=1, ls="--")
    ax.text(thr + 1.5, 0.40, f"threshold {thr}:\nscores below it\nare missed", ha="left", va="top",
            fontsize=8, color=INK2)
    ax.set_xlim(-4, 100)
    ax.set_ylim(0, 0.72)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("Qwen monitor score")
    ax.set_ylabel("Share of deceptive rounds")
    ax.set_title("Under the invitation, more deceptive rounds scored 75 or below",
                 loc="left", fontsize=11)
    ax.legend(loc="upper left", fontsize=8)
    save(fig, "fig4_positive_scores")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    deception_rates()
    recall_by_monitor()
    pact_detection()
    positive_scores()
    print(f"wrote 4 figures to {OUT}")
