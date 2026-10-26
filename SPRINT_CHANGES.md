# Sprint changes: starter code, new code, and run log

Author of new work: Shash Bhatia, Apart Research AI Collusion Research
Sprint, October 23 to 25, 2026.

Base: [poseidon-research/collusion_hackathon](https://github.com/poseidon-research/collusion_hackathon)
at commit `e6fb1308dae9cf97ae42aec1c5f7889d9e2291e8`, folder
`llm-trust-breaking/` (Shi et al. 2026, arXiv:2607.05132), plus
`util/poseidon_compute/modal_serve.py`.

## Starter code used as is

- Game rules for Diners and Weakest Link.
- The three-stage protocol (private plan, public announcement, final
  action) and the runner `experiments/run_endogenous.py`.
- The mechanical typology in `src/endogenous/core/trial_runner.py`,
  which supplies the ground truth (`premeditated_deception` is the
  positive class).

## Starter files modified

All changes are in [harness_patch/harness.patch](harness_patch/harness.patch).
The patched `prompt_builders.py` is included for reference.

| File | Change | Why |
|---|---|---|
| `src/endogenous/core/prompt_builders.py` | Adds `_monitor_disclosure()` (conditions A, B, C via `MONITOR_CONDITION`, monitor name via `MONITOR_NAME`) and `_pact_instruction()` (`PACT_ARM`, `PACT_SOLO_AGENT`), appended to the system prompt of all three stages. | The experiment itself. |
| `src/endogenous/core/trial_runner.py` | The built-in judge model reads `JUDGE_MODEL` from the environment instead of the hardcoded `openai/gpt-5-mini`. | The served endpoint could not answer the hardcoded judge model. Judge labels are auxiliary; they are never ground truth. |
| `src/llm/providers/queued_openrouter.py` | `aiohttp.ClientSession(..., trust_env=True)`. | The clients ignored the egress proxy and failed TLS. |
| `src/llm/providers/parallel_openrouter_async.py` | Same `trust_env=True` change, plus a debug print of the response body on HTTP errors. | Same proxy issue; the print was added while debugging it. |
| `util/poseidon_compute/modal_serve.py` | vLLM launched with `--max-model-len 8192` and `--gpu-memory-utilization 0.95` (overridable by env var); Modal secrets created if missing. | Qwen2.5-7B's default 32,768-token context did not fit the KV cache on an A10G. |

## New code

All in [code/](code/). Each script was written during the sprint unless
marked as added after it.

### Serving

| File | Purpose |
|---|---|
| `modal_serve_monitor.py` | Dedicated Modal app (`monitor-serve`) for the frozen Qwen2.5-14B monitor on A100-40GB, up to 6 containers. Model and GPU are hardcoded so no environment variable can change which model scores. |

### Game generation (Qwen2.5-7B agents)

| File | Purpose |
|---|---|
| `run_pilot.sh` | Pilot: 2 trials per cell, conditions A/B/C, both games. |
| `run_full.sh` | Full run: 10 trials per cell, 1,200 agent-rounds. |
| `run_full_resume.sh` | Resumes the full run after a runtime restart at about 5:02pm EDT on Oct 25 killed it. Condition A diners had finished; this runs the other five cells. |
| `run_pact.sh` | Pact extension: arms pact, solo, innocent by conditions B and C, diners only, six cells in parallel. |
| `run_conditions.sh` | Early runner written before the model choice was frozen. Its defaults (`openai/gpt-4o-mini` agents, monitor named "GPT-5 Monitor") and its run suffix (`cond{A,B,C}`) do not match the reported logs, which carry the `full_cond` suffix from `run_full.sh`. Not used for any reported result. |

### Monitoring (frozen monitor)

| File | Purpose |
|---|---|
| `monitor.py` | The frozen monitor: system prompt, user prompt built from the public record only (stage 2 announcements and stage 3 actions), temperature 0. Writes scores and ground-truth labels to separate files. Resumes by uid. |
| `run_scoring.sh` | Sequential monitor pass over the six core cells. Superseded by `run_scoring_parallel.sh`. |
| `run_scoring_parallel.sh` | The same pass, six cells in parallel against `monitor-serve`, then `score.py`. |
| `run_scoring_pact.sh` | Frozen monitor over the six pact cells. |
| `evidence_views.py`, `run_evidence_parallel.sh` | Secondary analysis: the same frozen system prompt with three other inputs (messages only, actions only, structured report). |

### Monitor panel (OpenRouter rescoring of the same logs)

| File | Purpose |
|---|---|
| `monitor_openrouter.py` | Calls the frozen prompt through OpenRouter for GPT-5 mini (default) or Claude Haiku 4.5 (`--model`). It imports the prompt and parser from `monitor.py`. Credentials came from the sprint assistant's connector (`/opt/muse/...`), not from an environment variable; see Reproduce in the README. |
| `run_scoring_gpt5.sh` | GPT-5 mini over the six core cells. |
| `run_scoring_pact_gpt5.sh` | GPT-5 mini over the six pact cells. |
| `run_scoring_haiku.sh` | First Haiku pass, sequential. |
| `run_scoring_haiku_parallel.sh` | Parallel restart of the Haiku core cells B and C (Oct 25, about 8:50pm EDT). |
| `run_scoring_haiku_max.sh` | Haiku core B/C and all pact cells at 5 workers per cell. A first attempt at 160 concurrent calls hit the provider rate limit. |
| `run_scoring_haiku_refill.sh` | Refills the Haiku calls that failed in the max pass, at 3 workers per cell. |
| `finish_openrouter_runs.sh`, `finish_haiku_max.sh`, `finish_haiku_refill.sh` | Wait for a pass to finish, then run `score.py` and the pact analysis. The Haiku finishers write `analyze_pact_haiku.py` by substituting Haiku's calibrated threshold into `analyze_pact.py`. |

### Analysis

| File | Purpose |
|---|---|
| `score.py` | Calibrates the threshold (condition A trials 0 to 2, 5 percent target FPR), then reports held-out recall, trial-cluster bootstrap CI, observed FPR, AUROC, and premeditated rates. |
| `uptake.py` | Counts monitor-directed public messages per condition. |
| `analyze_pact.py` | Pair-level pact analysis at threshold 51 (Qwen). |
| `analyze_pact_gpt5.py`, `analyze_pact_haiku.py` | The same analysis at threshold 91 (GPT-5 mini) and 79 (Haiku), pointed at those score folders. |
| `collect_numbers.py` | Added Oct 26, after the sprint. Recomputes every report number from `data/` and `results/` into `results/numbers.json`, and writes the panel, evidence-view and pact summaries. |
| `make_figures.py` | Added Oct 26, after the sprint. Draws the figures in `figures/` from `numbers.json`. |

### Report

| File | Purpose |
|---|---|
| `build_tex.py` | Converts `report-draft.md` to `report.tex` with pypandoc. The submitted `report.pdf` was compiled from `report.tex` with pdfTeX (see the PDF metadata). |
| `build_pdf.py` | An earlier direct markdown-to-PDF builder using fpdf. Not used for the submitted PDF. |

## Paths during the sprint

The scripts keep the paths they ran with. Map them to this repo as
follows.

| Sprint path | This repo |
|---|---|
| `~/workspace/sprint/tb/` | a clone of the starter repo with the patch applied |
| `~/workspace/sprint/tb/llm-trust-breaking/outputs/experiments/<game>/2agents/` | `data/logs/<game>/` |
| `~/workspace/sprint/monitor/` | `code/` (scripts) and `results/` (outputs) |
| `.../monitor/full_scores/` | `results/core/scores/` |
| `.../monitor/full_scores/views/` | `results/evidence_views/scores/` |
| `.../monitor/full_scores_gpt5/` | `results/panel/gpt5/scores/` |
| `.../monitor/full_scores_haiku/` | `results/panel/haiku/scores/` |
| `.../monitor/full_scores_pact/` | `results/pact/qwen/scores/` |
| `.../monitor/full_scores_pact_gpt5/` | `results/pact/gpt5/scores/` |
| `.../monitor/full_scores_haiku_pact/` | `results/pact/haiku/scores/` |
| `.../monitor/analysis_summary.md` | `results/core/SUMMARY.md` |
| `.../monitor/extension_results.md` | `results/extension_log.md` |
| `.../monitor/*_results.txt` | next to the matching scores folder |
| `/home/hatch/workspace/sprint/monitor/report*` | `report/` |

## Run log

Infrastructure changes during the sprint are recorded with times in
[FREEZE.md](FREEZE.md). Items below are not covered there.

- Oct 25, about 5:02pm EDT: a runtime restart killed the first full
  run after condition A diners finished. `run_full_resume.sh` ran the
  other five cells in the original order with the same settings.
- The debug print in `parallel_openrouter_async.py` was added while
  fixing the proxy issue and stayed in the patch. It only prints on
  HTTP errors.
- Haiku rescoring took four passes (sequential, parallel, max, refill)
  because of provider rate limits. Every pass resumed by uid, so no
  completed call was repeated. The final files cover all 1,200 core
  and 1,200 pact rounds. `results/extension_log.md` has a Haiku section
  written before the last refill finished; a note there marks it.
- The GPT-5 mini pact rule was written in `gpt5_pact_plan.md` before
  that run (Oct 25, about 8:50pm EDT). That file is not in this repo.
  Its rule is restated in `results/extension_log.md`.
- Pilot logs are not in this repo. Pilot counts are in
  `results/pilot/NOTES.md`.

## Costs

- OpenRouter: GPT-5 mini core rescoring cost $0.99 for 1,200 calls.
  All OpenRouter rescoring (GPT-5 mini and Haiku, core and pact) cost
  about $6 in total (`results/extension_log.md`).
- Modal GPU time for generation and the Qwen monitor was not recorded.

## Changes after the sprint (Oct 26, 2026)

No script that produced a reported result was edited in this
cleanup. One later exception, logged under Post-deadline fixes
below: on Oct 26 the live Modal URL in
`code/run_scoring_parallel.sh`, `code/run_scoring_pact.sh`, and
`code/run_evidence_parallel.sh` was replaced with a placeholder.
That change came after every run and does not affect any result.
Changes:

- `results/` regrouped into `core/`, `evidence_views/`, `panel/`,
  `pact/` and `pilot/` (mapping above). The evidence-view score files
  were stored twice, once in `full_scores/` and once in
  `full_scores/views/`. The copies were byte-identical; only the
  `views/` copy was kept.
- Added `code/collect_numbers.py`, `code/make_figures.py`,
  `results/numbers.json`, `figures/`, the generated `SUMMARY.md` files,
  `results/pilot/NOTES.md`, this file, and `SHA256SUMS`.
- The report's Code and Data section said code and data were available
  on request. It now points to this repository (`report-draft.md` and
  `report.tex`). At cleanup time `report.pdf` was still the
  submitted version. It was rebuilt on Oct 26 from the corrected
  sources; see Post-deadline fixes below. The PDF held by the
  organizers is still the submitted one.
- A dated note in `results/extension_log.md` marks its Haiku section
  as written before the last refill.

## Post-deadline fixes (October 26, 2026)

- Stopped the Modal apps monitor-serve and hackathon-serve. The
  monitor-serve URL appeared in three run scripts and the app had
  no authentication; the scripts now carry a YOUR-WORKSPACE
  placeholder instead of the live address.
- README: added the submitted-version pointer (tag `submission`),
  the sprint questions (2.2 primary, 2.3 secondary), and the
  preexisting-code statement.
- Report: added the two missing reference entries (Say, Do, or
  Both?; the AgentEval entry), the agent sampling settings in
  Methods (temperature 1.0, request seed 42, harness random seed
  42), and the preexisting-code line in Code and Data. The PDF was
  rebuilt from the corrected source.
- `code/build_tex.py` now resolves its input and output paths from
  its own location inside this repo. It pointed at the sprint
  workspace before, so the report rebuild failed on any other
  machine. The README rebuild step now lists the pandoc and
  pypandoc dependencies. The script produced no results, and its
  output is unchanged.
