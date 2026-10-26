#!/usr/bin/env bash
# Parallel version of run_scoring_haiku.sh, launched Oct 25 about
# 8:50pm EDT at the user's request to speed up the OpenRouter passes.
# The sequential run was stopped cleanly first; every cell resumes by
# uid, so no completed call repeats. All remaining cells run at the
# same time, each with the script default of 6 workers.
set -u
cd ~/workspace/sprint/monitor
OUT=~/workspace/sprint/monitor/full_scores_haiku
mkdir -p "$OUT"
HARNESS=~/workspace/sprint/tb/llm-trust-breaking/outputs/experiments

pids=""
for CELL in "B diners" "B weakestlink" "C diners" "C weakestlink"; do
  set -- $CELL
  COND=$1; GAME=$2
  python3 monitor_openrouter.py \
    --results "$HARNESS/$GAME/2agents/Qwen_Qwen2.5-7B-Instruct_endogenous_full_cond${COND}.json" \
    --condition "$COND" --game "$GAME" \
    --model anthropic/claude-haiku-4.5 \
    --out "$OUT/scores_${COND}_${GAME}.jsonl" \
    --labels "$OUT/labels_${COND}_${GAME}.jsonl" \
    > "$OUT/scoring_${COND}_${GAME}.log" 2>&1 &
  pids="$pids $!"
done

fail=0
for p in $pids; do
  wait "$p" || fail=1
done
echo "HAIKU PARALLEL SCORING DONE fail=$fail"
