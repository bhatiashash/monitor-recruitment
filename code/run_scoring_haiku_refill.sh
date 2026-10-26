#!/usr/bin/env bash
# Refill pass for the Haiku cells that finished with failed calls in
# the max run (18 to 23 failed calls per cell, recorded in the main3
# cell logs). Same files, resume by uid, one writer per file, lower
# concurrency (3 workers per cell, 30 in flight) to stay under the
# provider rate limit that exhausted the retries. Cell logs go to
# separate refill logs so the main3 record stays intact.
set -u
cd ~/workspace/sprint/monitor
HARNESS=~/workspace/sprint/tb/llm-trust-breaking/outputs/experiments
CORE=~/workspace/sprint/monitor/full_scores_haiku
PACT=~/workspace/sprint/monitor/full_scores_haiku_pact
W=3
pids=""
for CELL in "B diners" "B weakestlink" "C diners" "C weakestlink"; do
  set -- $CELL; COND=$1; GAME=$2
  python3 monitor_openrouter.py \
    --results "$HARNESS/$GAME/2agents/Qwen_Qwen2.5-7B-Instruct_endogenous_full_cond${COND}.json" \
    --condition "$COND" --game "$GAME" \
    --model anthropic/claude-haiku-4.5 --workers $W \
    --out "$CORE/scores_${COND}_${GAME}.jsonl" \
    --labels "$CORE/labels_${COND}_${GAME}.jsonl" \
    > "$CORE/scoring_refill_${COND}_${GAME}.log" 2>&1 &
  pids="$pids $!"
done
for ARM in pact solo innocent; do
  for COND in B C; do
    python3 monitor_openrouter.py \
      --results "$HARNESS/diners/2agents/Qwen_Qwen2.5-7B-Instruct_endogenous_pact_${ARM}_cond${COND}.json" \
      --condition "$COND" --game diners \
      --model anthropic/claude-haiku-4.5 --workers $W \
      --out "$PACT/scores_${ARM}_${COND}.jsonl" \
      --labels "$PACT/labels_${ARM}_${COND}.jsonl" \
      > "$PACT/scoring_refill_${ARM}_${COND}.log" 2>&1 &
    pids="$pids $!"
  done
done
fail=0
for p in $pids; do wait "$p" || fail=1; done
echo "HAIKU REFILL DONE fail=$fail"
