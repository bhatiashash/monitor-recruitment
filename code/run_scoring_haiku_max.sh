#!/usr/bin/env bash
# Unified max-parallel Haiku pass: remaining core cells and all pact
# cells side by side, 5 workers per cell (50 concurrent calls; 160 overshot the provider rate limit and died on 429s).
# Every cell resumes by uid; one writer per output file.
set -u
cd ~/workspace/sprint/monitor
HARNESS=~/workspace/sprint/tb/llm-trust-breaking/outputs/experiments
CORE=~/workspace/sprint/monitor/full_scores_haiku
PACT=~/workspace/sprint/monitor/full_scores_haiku_pact
mkdir -p "$CORE" "$PACT"
W=5
pids=""
for CELL in "B diners" "B weakestlink" "C diners" "C weakestlink"; do
  set -- $CELL; COND=$1; GAME=$2
  python3 monitor_openrouter.py \
    --results "$HARNESS/$GAME/2agents/Qwen_Qwen2.5-7B-Instruct_endogenous_full_cond${COND}.json" \
    --condition "$COND" --game "$GAME" \
    --model anthropic/claude-haiku-4.5 --workers $W \
    --out "$CORE/scores_${COND}_${GAME}.jsonl" \
    --labels "$CORE/labels_${COND}_${GAME}.jsonl" \
    > "$CORE/scoring_${COND}_${GAME}.log" 2>&1 &
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
      > "$PACT/scoring_${ARM}_${COND}.log" 2>&1 &
    pids="$pids $!"
  done
done
fail=0
for p in $pids; do wait "$p" || fail=1; done
echo "HAIKU MAX SCORING DONE fail=$fail"
