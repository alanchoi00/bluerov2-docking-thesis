"""Sigma-a trade-study bags: is the velocity state accurate at every sigma_a?"""
import glob, os, re, sys
import numpy as np
sys.path.insert(0, os.path.expanduser("~/dev/bluerov2-docking/scripts"))
from analysis.tracks import load_trial, measurement_error, measured_mask, corr
from analysis.windows import STATE_NAMES

rows = []
for bag in sorted(glob.glob(os.path.expanduser("~/dev/thesis-bags-backup/bags/sigA*"))):
    m = re.search(r"sigA([0-9.]+)_p(\d+)_", os.path.basename(bag))
    tr = load_trial(glob.glob(bag + "/*.mcap")[0])
    t = tr.t_meas
    e_world, _, _, _ = measurement_error(tr)
    g = np.arange(t[0], t[-1], 0.1); have = measured_mask(tr, g)
    vh = measured_mask(tr, tr.t_vel); gv = tr.dock.vel(tr.t_vel)[:, 1]
    veh, dock = tr.odom.pos(g)[:, 1], tr.dock.pos(g)[:, 1]
    est = tr.filt.pos(g)[:, 1] - dock; est -= np.median(est[have])
    seq = [s for _, s in tr.states]; docked = 2 in seq
    rows.append(dict(sigma_a=float(m.group(1)), period=int(m.group(2)), docked=docked, span=t[-1] - t[0], n_meas=len(t),
                     meas_err_cm=np.sqrt(np.mean(e_world[:, 1] ** 2)) * 100, track_err_cm=np.sqrt(np.mean(est[have] ** 2)) * 100,
                     vel_ratio=np.std(tr.vel[vh, 1]) / (np.std(gv[vh]) + 1e-9), vel_corr=corr(tr.vel[vh, 1], gv[vh]),
                     veh_over_dock=np.std(veh[have] - np.median(veh[have])) / np.std(dock[have]),
                     blackout=1 - have.mean(), max_est_err_cm=np.max(np.abs(est)) * 100))
print(f"{'sigma_a':>7} {'period':>6} {'docked':>6} {'span':>5} {'meas err':>9} {'track err':>9} {'vel ratio':>9} {'vel corr':>8} {'veh/dock':>8} {'blackout':>8} {'max est err':>11}")
for r in sorted(rows, key=lambda r: (r['period'], r['sigma_a'])):
    print(f"{r['sigma_a']:7.2f} {r['period']:6d} {str(r['docked']):>6} {r['span']:5.0f} {r['meas_err_cm']:8.2f}cm {r['track_err_cm']:8.1f}cm {r['vel_ratio']:9.2f} {r['vel_corr']:8.2f} {r['veh_over_dock']:8.2f} {r['blackout']:8.2f} {r['max_est_err_cm']:9.0f}cm")
import csv
with open(os.path.join(os.path.dirname(__file__), "sigA_check.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
