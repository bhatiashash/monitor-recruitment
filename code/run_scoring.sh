#!/usr/bin/env bash
# Monitor pass over the full-run logs with the frozen 14B monitor, then the
# frozen scoring analysis. Run AFTER run_full.sh completes and AFTER the
# serve app has been redeployed with the 14B model (same URL).
set -u
cd ~/workspace/sprint/monitor
set -a && source ~/workspace/sprint/tb/compute.env && set +a

OUT=~/workspace/sprint/monitor/full_scores
mkdir -p "$OUT"
HARNESS=~/workspace/sprint/tb/llm-trust-breaking/outputs/experiments

for COND in A B C; do
  for GAME in diners weakestlink; do
    echo "=== scoring cond $COND game $GAME ==="
    python3 monitor.py \
      --results "$HARNESS/$GAME/2agents/Qwen_Qwen2.5-7B-Instruct_endogenous_full_cond${COND}.json" \
      --condition "$COND" --game "$GAME" \
      --model Qwen/Qwen2.5-14B-Instruct \
      --out "$OUT/scores_${COND}_${GAME}.jsonl" \
      --labels "$OUT/labels_${COND}_${GAME}.jsonl" \
      || echo "SCORING FAILED: cond $COND game $GAME"
  done
done

cat "$OUT"/scores_*.jsonl > "$OUT/scores_all.jsonl"
cat "$OUT"/labels_*.jsonl > "$OUT/labels_all.jsonl"
python3 score.py --scores "$OUT/scores_all.jsonl" --labels "$OUT/labels_all.jsonl" \
  --calibration-condition A --calibration-trials 0,1,2 --fpr 0.05
echo "SCORING DONE"
