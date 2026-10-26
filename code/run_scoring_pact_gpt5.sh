#!/usr/bin/env bash
# GPT-5 mini rescore of the pact extension logs through OpenRouter.
# All six cells in parallel, rule declared in gpt5_pact_plan.md before
# the run. Outputs to full_scores_pact_gpt5/ in the same layout as
# full_scores_pact/ so the pact analysis reads them the same way.
# Every cell resumes by uid.
set -u
cd ~/workspace/sprint/monitor
OUT=~/workspace/sprint/monitor/full_scores_pact_gpt5
mkdir -p "$OUT"
HARNESS=~/workspace/sprint/tb/llm-trust-breaking/outputs/experiments

pids=""
for ARM in pact solo innocent; do
  for COND in B C; do
    python3 monitor_openrouter.py \
      --results "$HARNESS/diners/2agents/Qwen_Qwen2.5-7B-Instruct_endogenous_pact_${ARM}_cond${COND}.json" \
      --condition "$COND" --game diners \
      --out "$OUT/scores_${ARM}_${COND}.jsonl" \
      --labels "$OUT/labels_${ARM}_${COND}.jsonl" \
      > "$OUT/scoring_${ARM}_${COND}.log" 2>&1 &
    pids="$pids $!"
  done
done

fail=0
for p in $pids; do
  wait "$p" || fail=1
done
echo "GPT5 PACT SCORING DONE fail=$fail"
