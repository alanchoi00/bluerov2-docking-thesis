# Autonomous Visual Docking of a ROV onto a Moving Dock

**Terminal Guidance in Simulation and Empirical Limits of ArUco Perception Underwater**

Chak Wang (Alan) Choi
Bachelor of Engineering thesis, School of Mechanical and Manufacturing Engineering, UNSW Sydney
Supervisor: Will Midgley
Submitted 7 August 2026

## Abstract

This thesis focuses on the optical terminal stage of underwater docking using passive markers and computer vision, the approach available to low-cost ROV platforms that cannot carry learning-based perception. In simulation, a position-based visual servoing pipeline docks a BlueROV2 autonomously onto a swaying dock through a coarse approach phase followed by fine alignment. In parallel, the operating envelope of passive ArUco perception is measured from real underwater imagery through analysis of detection range, pose error, and degradation with distance and turbidity. Together, these bound the operating range of marker-based terminal docking and identify where a paired complementary far-field cue becomes necessary.

## Documents

| Document | PDF | Source |
| --- | --- | --- |
| Final report (Thesis C) | [final/main.pdf](final/main.pdf) | [final/](final/) |
| Proposal (Thesis A) | [proposal/main.pdf](proposal/main.pdf) | [proposal/](proposal/) |
| UT27 full paper | built on Overleaf | [ut27/paper/](ut27/paper/) |
| UT27 two-page abstract (accepted) | built on Overleaf | [ut27/abstract/](ut27/abstract/) |

## UT27 conference paper

The thesis work continues as a full paper for IEEE Underwater Technology 2027
(UT27, Tokyo, 28 February to 3 March 2027): *Visual Dock-Velocity Feedforward
for ROV Docking to a Swaying Station: Failure Mechanism, Velocity-Closed
Feedforward and Estimator Robustness*. The two-page abstract (paper 2059) was
accepted on 23 October 2026; the full paper is due 28 December 2026.

The paper is written in LaTeX with the IEEEtran class and reviewed on Overleaf,
which is synchronised with this repository's `main` branch through Overleaf's
GitHub integration. Edit on either side, then pull or push from the Overleaf
menu; no built PDF is kept in the repository.

| Path | Content |
| --- | --- |
| [ut27/paper/](ut27/paper/) | Full paper: `main.tex`, `sections/`, `figures/`, `refs.bib` |
| [ut27/abstract/](ut27/abstract/) | The accepted two-page abstract, `abstract_v2.tex` |
| [ut27/t1-leak-diagnosis.md](ut27/t1-leak-diagnosis.md) | Working report behind the paper: the feedforward failure diagnosis, the fix and every sweep's reading |
| [ut27/t1/](ut27/t1/) | Per-trial metrics of the sweeps (CSV) and the scripts that draw the paper figures from them |

The simulation sweeps, the trial driver and the analysis scripts live in the
companion code repository below.

## Companion code

The simulation, perception, and control software described in the report and the
paper lives in [bluerov2-docking](https://github.com/UNSWROV/bluerov2-docking);
the underwater imagery analysis (Part B) lives in its validation repository linked
from there.

## Building

Requires a full TeX Live (or MiKTeX) install with `latexmk`. Each document is a
standalone project; from `final/` or `proposal/`:

```sh
latexmk
```

The `.latexmkrc` in each folder selects `pdflatex` and teaches `latexmk` the
`nomencl` step (`makeindex` on `main.nlo`), so the bibliography and, where the
document uses one, the list of symbols build in a single pass. `latexmk -C`
removes all generated files.

The UT27 paper in `ut27/paper/` builds the same way with `latexmk`, or by hand
with `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`. The abstract in
`ut27/abstract/` has no `.latexmkrc`; build `abstract_v2.tex` by hand with the
same four commands. On Overleaf set the compiler to pdfLaTeX and the main
document to `ut27/paper/main.tex`.

## License

The thesis text, figures, and LaTeX sources in this repository are licensed under
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/);
see [LICENSE](LICENSE). You may share and adapt this work, including in your own
thesis, provided you cite it.

Third-party figures reproduced under citation remain the copyright of their
respective owners and are not covered by this license.
