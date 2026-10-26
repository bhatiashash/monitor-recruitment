#!/usr/bin/env bash
# Parallel monitor pass over the full-run logs with the frozen 14B monitor.
# Six monitor.py processes run at once, one per condition by game cell, all
# against the dedicated monitor-serve endpoint. Modal scales that app to up
# to 6 containers (one A100-40GB GPU each). Frozen prompts, labels, and
# scoring rules are unchanged from run_scoring.sh; only the execution is
# parallel. monitor.py resumes from existing output, so a rerun is safe.
set -u
cd ~/workspace/sprint/monitor

export LLM_BASE_URL="https://YOUR-WORKSPACE--monitor-serve-serve.us-east.modal.run/v1"
# The endpoint is unauthenticated; monitor.py requires a non-empty key value.
export LLM_API_KEY="EMPTY"

OUT=~/workspace/sprint/monitor/full_scores
mkdir -p "$OUT"
HARNESS=~/workspace/sprint/tb/llm-trust-breaking/outputs/experiments

pids=""
for COND in A B C; do
  for GAME in diners weakestlink; do
    echo "=== scoring cond $COND game $GAME (parallel) ==="
    python3 monitor.py \
      --results "$HARNESS/$GAME/2agents/Qwen_Qwen2.5-7B-Instruct_endogenous_full_cond${COND}.json" \
      --condition "$COND" --game "$GAME" \
      --model Qwen/Qwen2.5-14B-Instruct \
      --out "$OUT/scores_${COND}_${GAME}.jsonl" \
      --labels "$OUT/labels_${COND}_${GAME}.jsonl" \
      > "$OUT/scoring_${COND}_${GAME}.log" 2>&1 &
    pids="$pids $!"
  done
done

fail=0
for p in $pids; do
  wait "$p" || fail=1
done
if [ "$fail" -ne 0 ]; then
  echo "AT LEAST ONE SCORING CELL FAILED; see $OUT/scoring_*.log"
  exit 1
fi

cat "$OUT"/scores_*.jsonl > "$OUT/scores_all.jsonl"
cat "$OUT"/labels_*.jsonl > "$OUT/labels_all.jsonl"
python3 score.py --scores "$OUT/scores_all.jsonl" --labels "$OUT/labels_all.jsonl" \
  --calibration-condition A --calibration-trials 0,1,2 --fpr 0.05
echo "SCORING DONE"
