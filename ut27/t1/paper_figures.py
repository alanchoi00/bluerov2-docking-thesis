"""Paper figures from the per-trial metrics of the core sweep (all four arms, one host).

Usage: python3 paper_figures.py <metrics.csv> <out_dir>
Needs numpy < 2 with the host matplotlib; run with the scratch scipy/numpy on PYTHONPATH.
"""
import csv
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ARMS = ["A", "B", "C", "D"]
NAMES = {"A": "A reactive", "B": "B original feedforward", "C": "C velocity-closed feedforward", "D": "D oracle feedforward"}
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
    x = np.arange(len(PERIODS)); wdt = 0.2
    for i, arm in enumerate(ARMS):
        docked = [frac(by[(arm, p)], lambda r: r["docked"] in ("True", "1", "true")) for p in PERIODS]
        clean = [frac(by[(arm, p)], lambda r: r["outcome"] == "CLEAN") for p in PERIODS]
        ax[0].bar(x + (i - 1.5) * wdt, docked, wdt, label=NAMES[arm])
        ax[1].bar(x + (i - 1.5) * wdt, clean, wdt)
    for a, title in zip(ax, ("Docked", "Docked without contact")):
        a.set_xticks(x); a.set_xticklabels([str(p) for p in PERIODS]); a.set_xlabel("sway period [s]")
        a.set_ylim(0, 1.05); a.set_title(title, fontsize=9); a.grid(axis="y", lw=0.3)
    ax[0].set_ylabel("fraction of trials")
    ax[0].legend(fontsize=6.5, loc="lower left", framealpha=0.9)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


def fig_overswing(by, out):
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    f = np.array([1.0 / p for p in PERIODS])
    ff = np.linspace(1 / 22, 1 / 5.5, 200)
    ax.plot(ff, [loop_model(1 / v, 1.0) for v in ff], "k-", lw=1, label="loop model, fine phase (unit gain)")
    ax.plot(ff, [loop_model(1 / v, 0.6) for v in ff], "k--", lw=1, label="loop model, coarse phase (gain 0.6)")
    marks = {"A": "s", "B": "o", "C": "^", "D": "D"}
    for arm in ARMS:
        vals = [[float(r["veh_over_dock"]) for r in by[(arm, p)] if r["veh_over_dock"] not in ("nan", "")] for p in PERIODS]
        med = [np.median(v) if v else np.nan for v in vals]
        lo = [np.min(v) if v else np.nan for v in vals]; hi = [np.max(v) if v else np.nan for v in vals]
        ax.errorbar(f, med, yerr=[np.array(med) - np.array(lo), np.array(hi) - np.array(med)], fmt=marks[arm], ms=4, capsize=2, lw=0.8, label=NAMES[arm])
    ax.set_xlabel("sway frequency [Hz]"); ax.set_ylabel("vehicle / dock lateral amplitude")
    ax.set_ylim(0.6, 2.1); ax.grid(lw=0.3); ax.legend(fontsize=5.5, loc="lower right", framealpha=0.9)
    sec = ax.secondary_xaxis("top", functions=(lambda v: 1 / np.maximum(v, 1e-6), lambda v: 1 / np.maximum(v, 1e-6)))
    sec.set_xticks(PERIODS); sec.set_xlabel("period [s]", fontsize=8)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


def fig_capture(by, out):
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
    marks = {"A": "s", "B": "o", "C": "^", "D": "D"}
    for arm in ARMS:
        cap = [[abs(float(r["capture_lateral_m"])) * 100 for r in by[(arm, p)] if r["capture_lateral_m"] not in ("nan", "")] for p in PERIODS]
        tdk = [[float(r["t_dock_s"]) for r in by[(arm, p)] if r["docked"] in ("True", "1", "true") and r["t_dock_s"] not in ("nan", "")] for p in PERIODS]
        for a, series in zip(ax, (cap, tdk)):
            med = [np.median(v) if v else np.nan for v in series]
            lo = [np.min(v) if v else np.nan for v in series]; hi = [np.max(v) if v else np.nan for v in series]
            a.errorbar(PERIODS, med, yerr=[np.array(med) - np.array(lo), np.array(hi) - np.array(med)], fmt=marks[arm] + "-", ms=4, capsize=2, lw=0.8, label=NAMES[arm])
    ax[0].set_ylabel("entry-plane lateral offset [cm]"); ax[1].set_ylabel("time to seat [s]")
    for a in ax:
        a.set_xlabel("sway period [s]"); a.invert_xaxis(); a.grid(lw=0.3)
    ax[0].axhline(3.0, color="grey", lw=0.6, ls=":"); ax[0].text(6.2, 3.15, "seat tolerance", fontsize=6, color="grey", ha="right")
    ax[0].legend(fontsize=6, loc="upper left", framealpha=0.9)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


if __name__ == "__main__":
    by = load(sys.argv[1]); out = sys.argv[2]
    fig_success(by, f"{out}/success_vs_period.png")
    fig_overswing(by, f"{out}/overswing_vs_frequency.png")
    fig_capture(by, f"{out}/capture_and_time.png")
    for p in PERIODS:
        print(f"model {p:2d} s: fine {loop_model(p, 1.0):.2f}, coarse {loop_model(p, 0.6):.2f}")
    print("written")
