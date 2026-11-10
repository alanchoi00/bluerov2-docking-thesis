"""Paper figures from the per-trial metrics of the core sweep (all four arms, one host).

Usage: python3 paper_figures.py <metrics.csv> <out_dir> [nav_metrics.csv] [prefix_metrics.csv]
Needs numpy < 2 with the host matplotlib; run with the scratch scipy/numpy on PYTHONPATH.
"""
import csv
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ARMS = ["A", "B", "Bgt", "C", "D", "Cnone", "Cgains", "Cnoff"]
MAIN_ARMS = ["A", "B", "Bgt", "C", "D"]
ABLATION_ARMS = ["Cnone", "Cgains", "Cnoff", "C"]
NAMES = {"A": "A reactive", "B": "B original feedforward", "Bgt": "B$_{\mathrm{GT}}$ oracle, true dock velocity", "C": "C velocity-closed feedforward", "Cnoff": "C without model feedforward", "D": "D rescaled open loop", "Cnone": "C, units unconverted", "Cgains": "C, gains converted only"}
PERIODS = [20, 16, 12, 10, 8, 6]
G, T = 2.7, 0.40                       # identified plant, m/s per unit and s
KP, KD = 0.8, 0.3                      # fine-phase position feedback


def load(path):
    rows = [r for r in csv.DictReader(open(path)) if r.get("nav", "") in ("", "none")]
    by = defaultdict(list)
    for r in rows:
        by[(r["arm"], int(float(r["period"])))].append(r)
    return by


def frac(rs, key):
    return np.mean([key(r) for r in rs]) if rs else np.nan


def loop_model(period, kff):
    """|x_v / x_d| of the open-loop feedforward law on the identified plant at the sway
    frequency: (K_ff s G + C G) / (s + C G) with G = g / (1 + sT), C = kp + kd s."""
    w = 2 * np.pi / period
    s = 1j * w
    Gp = G / (1 + s * T)
    C = KP + KD * s
    return abs((kff * s * Gp + C * Gp) / (s + C * Gp))


def fig_success(by, out):
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6), sharey=True)
    arms = [a for a in MAIN_ARMS if any(by[(a, p)] for p in PERIODS)]
    x = np.arange(len(PERIODS)); wdt = 0.8 / len(arms)
    for i, arm in enumerate(arms):
        docked = [frac(by[(arm, p)], lambda r: r["docked"] in ("True", "1", "true")) for p in PERIODS]
        clean = [frac(by[(arm, p)], lambda r: r["outcome"] == "CLEAN") for p in PERIODS]
        ax[0].bar(x + (i - (len(arms) - 1) / 2) * wdt, docked, wdt, label=NAMES[arm])
        ax[1].bar(x + (i - (len(arms) - 1) / 2) * wdt, clean, wdt)
    for a, title in zip(ax, ("Docked", "Docked without contact")):
        a.set_xticks(x); a.set_xticklabels([str(p) for p in PERIODS]); a.set_xlabel("sway period [s]")
        a.set_ylim(0, 1.05); a.set_title(title, fontsize=9); a.grid(axis="y", lw=0.3)
    ax[0].set_ylabel("fraction of trials")
    handles, labels = ax[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=6.5, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig(out, dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_overswing(by, out):
    fig, ax = plt.subplots(figsize=(3.5, 3.3))
    f = np.array([1.0 / p for p in PERIODS])
    ff = np.linspace(1 / 22, 1 / 5.5, 200)
    ax.plot(ff, [loop_model(1 / v, 1.0) for v in ff], "k-", lw=1, label="loop model, fine phase (unit gain)")
    ax.plot(ff, [loop_model(1 / v, 0.6) for v in ff], "k--", lw=1, label="loop model, coarse phase (gain 0.6)")
    marks = {"A": "s", "B": "o", "Bgt": "D", "C": "^", "D": "v", "Cnone": "P", "Cgains": "*", "Cnoff": "X"}
    for arm in [a for a in MAIN_ARMS if any(by[(a, p)] for p in PERIODS)]:
        vals = [[float(r["veh_over_dock"]) for r in by[(arm, p)] if r["veh_over_dock"] not in ("nan", "")] for p in PERIODS]
        med = [np.median(v) if v else np.nan for v in vals]
        lo = [np.min(v) if v else np.nan for v in vals]; hi = [np.max(v) if v else np.nan for v in vals]
        ax.errorbar(f, med, yerr=[np.array(med) - np.array(lo), np.array(hi) - np.array(med)], fmt=marks[arm], ms=4, capsize=2, lw=0.8, label=NAMES[arm])
    ax.set_xlabel("sway frequency [Hz]"); ax.set_ylabel("vehicle / dock lateral amplitude")
    ax.set_ylim(0.6, 2.1); ax.grid(lw=0.3)
    sec = ax.secondary_xaxis("top", functions=(lambda v: 1 / np.maximum(v, 1e-6), lambda v: 1 / np.maximum(v, 1e-6)))
    sec.set_xticks(PERIODS); sec.set_xlabel("period [s]", fontsize=8)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=5.5, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.17, 1, 1)); fig.savefig(out, dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_capture(by, out):
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
    marks = {"A": "s", "B": "o", "Bgt": "D", "C": "^", "D": "v", "Cnone": "P", "Cgains": "*", "Cnoff": "X"}
    for arm in [a for a in MAIN_ARMS if any(by[(a, p)] for p in PERIODS)]:
        cap = [[abs(float(r["capture_lateral_m"])) * 100 for r in by[(arm, p)] if r["capture_lateral_m"] not in ("nan", "")] for p in PERIODS]
        tdk = [[float(r["t_dock_s"]) for r in by[(arm, p)] if r["docked"] in ("True", "1", "true") and r["t_dock_s"] not in ("nan", "")] for p in PERIODS]
        for a, series in zip(ax, (cap, tdk)):
            med = [np.median(v) if v else np.nan for v in series]
            lo = [np.min(v) if v else np.nan for v in series]; hi = [np.max(v) if v else np.nan for v in series]
            a.errorbar(PERIODS, med, yerr=[np.array(med) - np.array(lo), np.array(hi) - np.array(med)], fmt=marks[arm] + "-", ms=4, capsize=2, lw=0.8, label=NAMES[arm])
    ax[0].set_ylabel("entry-plane lateral offset [cm]"); ax[1].set_ylabel("time to seat [s]")
    for a in ax:
        a.set_xlabel("sway period [s]"); a.set_xticks(PERIODS); a.invert_xaxis(); a.grid(lw=0.3)
    for arm in ARMS:
        for p in PERIODS:
            rs = [r for r in by[(arm, p)] if r["outcome"] == "CONTACT" and r["capture_lateral_m"] not in ("nan", "")]
            if rs:
                ax[0].plot([p] * len(rs), [abs(float(r["capture_lateral_m"])) * 100 for r in rs], marks[arm], ms=4, mfc="white", mec="k", mew=0.6, lw=0)
    ax[0].plot([], [], "o", ms=4, mfc="white", mec="k", mew=0.6, lw=0, label="contact trial")
    ax[0].axhline(3.0, color="grey", lw=0.6, ls=":"); ax[0].text(6.2, 3.15, "seat tolerance", fontsize=6, color="grey", ha="right")
    ax[0].legend(fontsize=6, loc="upper left", framealpha=0.9)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


def fig_prefix_sweep(path, out):
    """The sweep that exposed the failure (July host, arms A and B): docked and
    contact-free fractions per period, with n per cell."""
    rows = list(csv.DictReader(open(path)))
    by = defaultdict(list)
    for r in rows:
        by[({"static": "A", "sway": "B"}[r["arm"]], int(float(r["period"])))].append(r)
    fig, ax = plt.subplots(figsize=(3.5, 2.2))
    x = np.arange(len(PERIODS)); wdt = 0.36
    for i, arm in enumerate("AB"):
        docked = [frac(by[(arm, p)], lambda r: r["docked"] in ("True", "1", "true")) for p in PERIODS]
        clean = [frac(by[(arm, p)], lambda r: r["outcome"] == "CLEAN") for p in PERIODS]
        ax.bar(x + (i - 0.5) * wdt, docked, wdt, color=f"C{i}", alpha=0.35, label=f"{NAMES[arm]}, docked")
        ax.bar(x + (i - 0.5) * wdt, clean, wdt, color=f"C{i}", label=f"{NAMES[arm]}, without contact")
        for j, p in enumerate(PERIODS):
            n = len(by[(arm, p)])
            if n != 3:
                ax.text(x[j] + (i - 0.5) * wdt, max(docked[j], 0) + 0.03, f"n={n}", ha="center", va="bottom", fontsize=6)
    ax.set_xticks(x); ax.set_xticklabels([str(p) for p in PERIODS]); ax.set_xlabel("sway period [s]")
    ax.set_ylim(0, 1.12); ax.set_ylabel("fraction of trials"); ax.grid(axis="y", lw=0.3)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=6, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.10, 1, 1)); fig.savefig(out, dpi=200, bbox_inches="tight"); plt.close(fig)


def table_core(by, arms=None):
    """Table I rows: docked (clean), median |lateral offset| at the entry plane, median seat time."""
    def med(vals, fmt):
        return fmt % np.median(vals) if vals else "--"
    lines = []
    if arms is not None:
        ARMS[:] = arms
    for arm in [a for a in ARMS if any(by[(a, p)] for p in PERIODS)]:
        cells = []
        for p in PERIODS:
            rs = by[(arm, p)]; d = sum(r["docked"] in ("True", "1", "true") for r in rs); c = sum(r["outcome"] == "CLEAN" for r in rs)
            cells.append(f"{d} ({c}) of {len(rs)}" if len(rs) != 3 else f"{d} ({c})")
        lines.append(f"{arm} docked (clean) & " + " & ".join(cells) + r" \\")
    for arm in [a for a in ARMS if any(by[(a, p)] for p in PERIODS)]:
        cells = [med([abs(float(r["capture_lateral_m"])) * 100 for r in by[(arm, p)] if r["capture_lateral_m"] not in ("nan", "")], "%.1f") for p in PERIODS]
        lines.append(f"{arm} offset [cm] & " + " & ".join(cells) + r" \\")
    for arm in [a for a in ARMS if any(by[(a, p)] for p in PERIODS)]:
        cells = [med([float(r["t_dock_s"]) for r in by[(arm, p)] if r["docked"] in ("True", "1", "true") and r["t_dock_s"] not in ("nan", "")], "%.0f") for p in PERIODS]
        lines.append(f"{arm} seat time [s] & " + " & ".join(cells) + r" \\")
    return "\n".join(lines)


LEVELS = ["none", "low", "medium", "high"]
LEVEL_SIGMA = {"none": "0", "low": "0.01", "medium": "0.03", "high": "0.10"}


def load_nav(*paths):
    """Navigation-error cells grouped by (arm, period, level) from one or more metrics
    files; the core sweep's cells supply the level-none column."""
    rows = [r for p in paths for r in csv.DictReader(open(p))]
    by = defaultdict(list)
    for r in rows:
        if r["cell"].startswith("navtest"):
            continue  # the injector test cells of 2026-09-21 are not part of either sweep
        lvl = r.get("nav", "") or "none"
        if int(float(r["period"])) in (10, 8) and r["arm"] in ("A", "B", "C", "D", "Cnone", "Cgains", "Cnoff"):
            by[(r["arm"], int(float(r["period"])), lvl)].append(r)
    return by


def fig_nav_heatmap(by, out):
    """Docked fraction per arm and bias level, one panel per period."""
    arms = [a for a in ("A", "B", "C", "D") if any(by.get((a, p, l)) for p in (10, 8) for l in LEVELS)]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.2 + 0.45 * len(arms)), sharey=True)
    for ax, per in zip(axes, (10, 8)):
        grid = np.full((len(arms), len(LEVELS)), np.nan)
        for i, arm in enumerate(arms):
            for j, lvl in enumerate(LEVELS):
                rs = by.get((arm, per, lvl), [])
                if rs:
                    grid[i, j] = np.mean([r["docked"] in ("True", "1", "true") for r in rs])
        im = ax.imshow(grid, vmin=0, vmax=1, cmap="Greens", aspect="auto")
        for i in range(len(arms)):
            for j in range(len(LEVELS)):
                rs = by.get((arms[i], per, LEVELS[j]), [])
                if rs:
                    n = len(rs); k = int(round(grid[i, j] * n))
                    ax.text(j, i, f"{k}/{n}", ha="center", va="center", fontsize=8,
                            color="white" if grid[i, j] > 0.6 else "black")
        ax.set_xticks(range(len(LEVELS))); ax.set_xticklabels([f"{l}\n{LEVEL_SIGMA[l]} m/s" for l in LEVELS], fontsize=7)
        ax.set_yticks(range(len(arms))); ax.set_yticklabels([NAMES[a].split(" ")[0] + " " + " ".join(NAMES[a].split(" ")[1:]) for a in arms], fontsize=7)
        ax.set_title(f"{per} s sway period", fontsize=9); ax.set_xlabel("navigation velocity bias (stationary std)", fontsize=8)
    cb = fig.colorbar(im, ax=axes, fraction=0.03, pad=0.02); cb.set_label("docked fraction", fontsize=8)
    fig.savefig(out, dpi=200, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    # usage: paper_figures.py <core.csv>[,<more.csv>] <out_dir> [nav.csv[,<more.csv>]] [prefix.csv]
    cores = sys.argv[1].split(","); out = sys.argv[2]
    by = load(cores[0])
    for extra in cores[1:]:
        for k, v in load(extra).items():
            by[k].extend(v)
    fig_success(by, f"{out}/success_vs_period.png")
    fig_overswing(by, f"{out}/overswing_vs_frequency.png")
    fig_capture(by, f"{out}/capture_and_time.png")
    if len(sys.argv) > 3:
        fig_nav_heatmap(load_nav(*sys.argv[3].split(",")), f"{out}/nav_heatmap.png")
    if len(sys.argv) > 4:
        fig_prefix_sweep(sys.argv[4], f"{out}/clean_pdock.png")
    print("% main arms"); print(table_core(by, list(MAIN_ARMS)))
    print("% ablation arms"); print(table_core(by, list(ABLATION_ARMS)))
    for p in PERIODS:
        print(f"model {p:2d} s: fine {loop_model(p, 1.0):.2f}, coarse {loop_model(p, 0.6):.2f}")
    print("written")
