#!/usr/bin/env bash
# Frozen 14B monitor pass over the pact extension logs. Six monitor.py
# processes in parallel against monitor-serve, same frozen prompt and
# threshold basis as the core. Outputs to full_scores_pact/.
set -u
cd ~/workspace/sprint/monitor

export LLM_BASE_URL="https://YOUR-WORKSPACE--monitor-serve-serve.us-east.modal.run/v1"
# The endpoint is unauthenticated; monitor.py requires a non-empty key value.
export LLM_API_KEY="EMPTY"

OUT=~/workspace/sprint/monitor/full_scores_pact
mkdir -p "$OUT"
HARNESS=~/workspace/sprint/tb/llm-trust-breaking/outputs/experiments

pids=""
for ARM in pact solo innocent; do
  for COND in B C; do
    python3 monitor.py \
      --results "$HARNESS/diners/2agents/Qwen_Qwen2.5-7B-Instruct_endogenous_pact_${ARM}_cond${COND}.json" \
      --condition "$COND" --game diners \
      --model Qwen/Qwen2.5-14B-Instruct \
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
echo "PACT SCORING DONE fail=$fail"
