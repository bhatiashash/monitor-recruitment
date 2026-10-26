#!/usr/bin/env bash
# Evidence-format comparison (secondary analysis, plan v3). Three extra
# views (messages_only, actions_only, structured) scored with the same
# frozen monitor prompt and 14B model over the same 1,200 agent-rounds.
# The headline view (messages plus actions) is already scored by
# run_scoring_parallel.sh. All 18 view by condition by game passes run in
# parallel against the monitor-serve app (cap 6 GPU containers).
# Each view is then calibrated separately with score.py on the same
# split (condition A, trials 0 to 2, 5 percent target), using the
# headline labels file. evidence_views.py resumes from existing output.
set -u
cd ~/workspace/sprint/monitor

export LLM_BASE_URL="https://bhatiashash--monitor-serve-serve.us-east.modal.run/v1"
export LLM_API_KEY="EMPTY"

OUT=~/workspace/sprint/monitor/full_scores/views
mkdir -p "$OUT"
HARNESS=~/workspace/sprint/tb/llm-trust-breaking/outputs/experiments
LABELS=~/workspace/sprint/monitor/full_scores/labels_all.jsonl

pids=""
for VIEW in messages_only actions_only structured; do
  for COND in A B C; do
    for GAME in diners weakestlink; do
      python3 evidence_views.py \
        --results "$HARNESS/$GAME/2agents/Qwen_Qwen2.5-7B-Instruct_endogenous_full_cond${COND}.json" \
        --condition "$COND" --game "$GAME" --view "$VIEW" \
        --model Qwen/Qwen2.5-14B-Instruct \
        --out "$OUT/scores_${VIEW}_${COND}_${GAME}.jsonl" \
        > "$OUT/view_${VIEW}_${COND}_${GAME}.log" 2>&1 &
      pids="$pids $!"
    done
  done
done

fail=0
for p in $pids; do
  wait "$p" || fail=1
done
if [ "$fail" -ne 0 ]; then
  echo "AT LEAST ONE VIEW CELL FAILED; see $OUT/view_*.log"
  exit 1
fi

for VIEW in messages_only actions_only structured; do
  cat "$OUT"/scores_${VIEW}_*.jsonl > "$OUT/scores_${VIEW}_all.jsonl"
  echo "===== VIEW $VIEW ====="
  python3 score.py --scores "$OUT/scores_${VIEW}_all.jsonl" --labels "$LABELS" \
    --calibration-condition A --calibration-trials 0,1,2 --fpr 0.05
done
echo "EVIDENCE VIEWS DONE"
