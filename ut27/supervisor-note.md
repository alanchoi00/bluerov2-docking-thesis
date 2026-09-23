# Note for the supervisor: what the data settled since the abstract

Draft for the email or meeting, 2026-09-22. Plain summary first, evidence after.

## Summary

The submitted abstract said the feedforward failure at 8 and 6 s came from the estimator (ego-motion leaking into the dock-velocity estimate) and proposed a relative-frame estimator as the fix. Rebuilding every measurement from the recorded trials shows that reading was wrong: the measurement and the velocity estimate are accurate, and the failure is control. The feedforward was scaled for a plant gain of 1.3 to 1.6 where the command channel delivers 2.7 with a 0.4 s time constant (open-loop step tests), so the vehicle over-swings the dock by 1.6 to 1.9 at short periods; the apparent phantom velocity is dead-reckoning during the marker blackout the over-swing causes.

The fix is a velocity-closed feedforward (the dock velocity becomes a body-velocity setpoint closed on the vehicle's navigation velocity) plus a bounded velocity state during blackout. It is implemented and swept: 82 trials, four arms, six periods, one host, one code revision.

| Period | A reactive | B original | C fix | D oracle |
| --- | --- | --- | --- | --- |
| 20 to 12 s | docks | docks | docks cleanly | docks |
| 10 s | docks | 2 of 3 | docks cleanly | docks |
| 8 s | docks, contacts | 0 of 6 | 4 of 4 cleanly | docks, over-swings |
| 6 s | docks, contacts | 0 of 3 | 1 of 3 | 0 of 3 |

The oracle arm (true dock velocity through the original law) over-swings exactly like the original, which places the over-swing in the law and the plant rather than the estimate; the fix is the only arm with no over-swing at any period and the smallest capture errors from 12 s down. Under Gauss-Markov navigation error, world-frame and relative-frame estimators both absorb a slow velocity bias one for one (a camera measuring relative position cannot separate it from dock velocity); the relative frame removes only the fast error, and the velocity loop is what cancels the bias.

## What changes in the paper

- Title and story: "failure mechanism, feedforward redesign and estimator robustness" rather than "relative-frame estimator". The relative-frame estimator is kept in a supporting role for the navigation-error result.
- Contributions: (1) the mechanism established from recorded trials against the system's own diagnostics; (2) the velocity-closed feedforward, evaluated against the baseline, the original and an oracle; (3) the observability result under correlated navigation error.
- The two-page abstract for re-upload (deadline 28 September) already carries this; the full paper draft (nine pages) is written through the results and discussion.

## Open items I would like your view on

1. The navigation-error live sweep: the injector's white position noise (5 mm at 100 Hz, a placeholder) defeats the coarse handoff gate before the bias matters. I propose 1 mm, which is a smooth navigation solution; the offline replay result stands either way.
2. The 6 s limit of the fix is the handoff gate reading the velocity loop's phase lag as relative motion, not tracking. I propose to report it as a limit and leave the gate unchanged, rather than tune the gate inside the comparison.
3. Whether to keep the July envelope figure in Section IV as the discovery narrative, with the one-host four-arm sweep in Section VII, or replace it.

Evidence: `ut27/t1-leak-diagnosis.md` (Sections 11, 13, 16, 17), metrics `ut27/t1/core_metrics_20260922.csv`, PRs UNSWROV/bluerov2-docking#85 (fix) and alanchoi00/bluerov2-docking-thesis#11 (paper).
