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

## Companion code

The simulation, perception, and control software described in the report lives in
[bluerov2-docking](https://github.com/alanchoi00/bluerov2-docking); the underwater
imagery analysis (Part B) lives in its validation repository linked from there.

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

## License

The thesis text, figures, and LaTeX sources in this repository are licensed under
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/);
see [LICENSE](LICENSE). You may share and adapt this work, including in your own
thesis, provided you cite it.

Third-party figures reproduced under citation remain the copyright of their
respective owners and are not covered by this license.
