# Does inviting agents to speak to their monitor change their behavior and make the monitor easier to mislead?

Experiment code, frozen logs, scores, and the report for a study of
monitor awareness and monitor invitation, run at the Apart Research
AI Collusion Research Sprint, October 23 to 25, 2026.

## Summary

Two Qwen2.5-7B agents play repeated trust games (Diners and Weakest
Link) in the Shi et al. llm-trust-breaking harness under three
conditions: A, no oversight disclosure; B, disclosure of a named
monitor; C, disclosure plus an invitation to address the monitor
inside the public message. Ground truth is the harness's mechanical
typology (premeditated_deception is the positive class). A frozen
Qwen2.5-14B monitor scores the public record only, at a threshold
calibrated on condition A trials 0 to 2 for a 5 percent false
positive rate. The same frozen logs were rescored by GPT-5 mini and
Claude Haiku 4.5, each at its own calibrated threshold. A second
dataset (the pact extension) builds collusion by instruction in
Diners: both agents instructed to deceive (pact), one agent
instructed (solo), or both instructed to be honest (innocent).

## Headline results

- Awareness raised the Diners premeditated deception rate from 0.030
  to 0.305. The invitation raised it further, to 0.440, while no
  agent ever wrote to the monitor (1 monitor-mentioning message in
  400, on an honest round).
- Recall at the frozen operating point fell from B to C under the
  Qwen monitor (0.918 to 0.846) and under Haiku (0.755 to 0.631),
  and rose under GPT-5 mini (0.245 to 0.354). AUROC moved little
  for all three. The invitation effect on detection is monitor
  dependent and works mainly through score placement against the
  calibrated threshold.
- On the pact test, the Qwen monitor and Haiku flag nearly all
  executed colluding pairs (Qwen 100 of 100 in B and 88 of 88 in C;
  Haiku 100 of 100 and 84 of 88) with at most 2 of 100 innocent
  pairs flagged. GPT-5 mini flags 21 of 100 (B) and 34 of 88 (C)
  executed pact pairs and no innocent pairs. The pact pattern is
  maximally overt, so this is a positive control, not evidence
  about covert collusion.

The full report is in report/ (PDF and LaTeX source).

## Layout

- FREEZE.md: the frozen design, recorded before the runs, with its
  dated amendments.
- code/: the monitor, the scorer, the uptake and evidence-view
  analyses, the pact analyses, the Modal serving app for the
  monitor, and the run scripts.
- harness_patch/: harness.patch applies the monitor disclosure and
  the pact instructions to the starter repository, plus the patched
  prompt_builders.py for reference.
- data/logs/: the frozen game logs for the core (both games,
  conditions A, B, C) and the pact (Diners, six cells).
- results/: the score and label files for every monitor pass, and
  the result tables the report is built from.
- report/: the submission report (report.pdf, report.tex,
  report-draft.md).

## Reproduce

1. Clone the starter repository at the pinned commit:
   https://github.com/poseidon-research/collusion_hackathon
   (commit e6fb1308dae9cf97ae42aec1c5f7889d9e2291e8).
2. Apply harness_patch/harness.patch inside the clone.
3. Serve Qwen2.5-7B-Instruct for generation and
   Qwen2.5-14B-Instruct for monitoring (code/modal_serve_monitor.py
   is the monitor app used here; both ran on Modal).
4. Generate: code/run_pilot.sh, then code/run_full.sh. Pact:
   code/run_pact.sh.
5. Score: code/run_scoring_parallel.sh, then code/score.py. Pact:
   code/run_scoring_pact.sh, then code/analyze_pact.py.
6. OpenRouter rescoring passes: code/monitor_openrouter.py driven
   by code/run_scoring_gpt5.sh and code/run_scoring_haiku_max.sh.

API keys are read from environment variables at run time. No key is
stored in this repository; the LLM_API_KEY values in the run
scripts are placeholders for the unauthenticated local endpoints
used during the sprint.

## License

MIT, see LICENSE.
