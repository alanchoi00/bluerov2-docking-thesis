"""Empirical feedforward gain per phase: regress the lateral command on the
estimated dock velocity and the lateral relative error inside each state segment."""
import sys, glob
# needs scipy >= 1.11 on sys.path (host has 1.8): pip install --target <dir> scipy
sys.path.insert(0, "/home/alan/dev/bluerov2-docking/scripts")
import numpy as np
from analysis.tracks import load_trial

NAMES = {0: "COARSE", 1: "FINE", 2: "DOCKED", 3: "IDLE"}
bags = sorted(glob.glob("/home/alan/dev/thesis-bags-backup/bags/clamped_sway_sway_p*_ph0.0_*/*.mcap"))
for bag in bags:
    tr = load_trial(bag)
    print("==", bag.split("/")[-1], "rtf %.2f" % tr.rtf)
    comp = [tr.states[0]] + [(t, v) for (t, v), (_, pv) in zip(tr.states[1:], tr.states[:-1]) if v != pv]
    st = comp + [(tr.t_cmd[-1], -1)]
    for (ta, sa), (tb, _) in zip(st[:-1], st[1:]):
        if NAMES.get(sa) not in ("COARSE", "FINE") or tb - ta < 8:
            continue
        g = np.arange(ta + 1.0, tb - 0.5, 0.05)
        cmd = np.interp(g, tr.t_cmd, tr.cmd[:, 1])
        ev = np.interp(g, tr.t_vel, tr.vel[:, 1])
        err = tr.filt.pos(g)[:, 1] - tr.odom.pos(g)[:, 1]
        derr = np.gradient(err, g)
        A = np.c_[ev, err, derr, np.ones_like(g)]
        c, res, *_ = np.linalg.lstsq(A, cmd, rcond=None)
        pred = A @ c
        r2 = 1 - np.var(cmd - pred) / np.var(cmd) if np.var(cmd) > 0 else float("nan")
        # feedforward-only fit for comparison
        a1 = np.linalg.lstsq(np.c_[ev, np.ones_like(g)], cmd, rcond=None)[0][0]
        print(f"  {NAMES[sa]:6s} {ta - tr.t0:6.1f}..{tb - tr.t0:6.1f} s  ff gain {c[0]:5.2f}  kp {c[1]:5.2f}  kd {c[2]:5.2f}  R2 {r2:4.2f}   (ff-only slope {a1:5.2f})  cmd amp {np.std(cmd)*np.sqrt(2):.3f}")
