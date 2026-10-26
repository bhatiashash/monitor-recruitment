#!/usr/bin/env bash
# GPT-5 mini rescore of the six frozen core cells through OpenRouter.
# Same frozen prompt and inputs as the Qwen headline pass; outputs go to
# full_scores_gpt5/ in the same file layout so score.py reads them the
# same way. The driver resumes by uid, so a rerun is safe.
set -u
cd ~/workspace/sprint/monitor
OUT=~/workspace/sprint/monitor/full_scores_gpt5
mkdir -p "$OUT"
HARNESS=~/workspace/sprint/tb/llm-trust-breaking/outputs/experiments

for COND in A B C; do
  for GAME in diners weakestlink; do
    echo "=== GPT-5 mini scoring cond $COND game $GAME ==="
    python3 monitor_openrouter.py \
      --results "$HARNESS/$GAME/2agents/Qwen_Qwen2.5-7B-Instruct_endogenous_full_cond${COND}.json" \
      --condition "$COND" --game "$GAME" \
      --out "$OUT/scores_${COND}_${GAME}.jsonl" \
      --labels "$OUT/labels_${COND}_${GAME}.jsonl" \
      > "$OUT/scoring_${COND}_${GAME}.log" 2>&1 \
      || echo "SCORING FAILED: cond $COND game $GAME"
  done
done
echo "GPT5 SCORING DONE"
