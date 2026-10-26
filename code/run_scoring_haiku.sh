#!/usr/bin/env bash
# Claude Haiku 4.5 rescore of the six frozen core cells through
# OpenRouter. Same frozen prompt, inputs, and output layout as the
# GPT-5 mini pass; outputs to full_scores_haiku/. Resumes by uid.
set -u
cd ~/workspace/sprint/monitor
OUT=~/workspace/sprint/monitor/full_scores_haiku
mkdir -p "$OUT"
HARNESS=~/workspace/sprint/tb/llm-trust-breaking/outputs/experiments

for COND in A B C; do
  for GAME in diners weakestlink; do
    echo "=== Haiku scoring cond $COND game $GAME ==="
    python3 monitor_openrouter.py \
      --results "$HARNESS/$GAME/2agents/Qwen_Qwen2.5-7B-Instruct_endogenous_full_cond${COND}.json" \
      --condition "$COND" --game "$GAME" \
      --model anthropic/claude-haiku-4.5 \
      --out "$OUT/scores_${COND}_${GAME}.jsonl" \
      --labels "$OUT/labels_${COND}_${GAME}.jsonl" \
      > "$OUT/scoring_${COND}_${GAME}.log" 2>&1 \
      || echo "SCORING FAILED: cond $COND game $GAME"
  done
done
echo "HAIKU SCORING DONE"
