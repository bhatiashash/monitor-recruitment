#!/usr/bin/env bash
# Waits for the unified Haiku max pass (run_scoring_haiku_max.sh,
# main log haiku_max_main3.log), then writes the Haiku headline
# results for the core and the Haiku pact analysis. The pact analysis
# uses the threshold from Haiku's own core calibration, extracted
# from the score.py output, under the same rule as the GPT-5 mini
# pact pass. Runs once.
set -u
cd ~/workspace/sprint/monitor

while ! grep -q "HAIKU MAX SCORING DONE" haiku_max_main3.log 2>/dev/null; do
  sleep 20
done

echo "core counts:"
wc -l full_scores_haiku/scores_*.jsonl
echo "pact counts:"
wc -l full_scores_haiku_pact/scores_*.jsonl

python3 score.py \
  --scores "full_scores_haiku/scores_*.jsonl" \
  --labels "full_scores_haiku/labels_*.jsonl" \
  --calibration-condition A --fpr 0.05 \
  > haiku_headline_results.txt 2>&1
echo "haiku headline results written"
cat haiku_headline_results.txt

THRESH=$(grep -o "threshold [0-9]*" haiku_headline_results.txt | head -1 | awk '{print $2}')
echo "haiku calibrated threshold: $THRESH"
if [ -n "$THRESH" ]; then
  sed -e "s/^THRESH = 51/THRESH = $THRESH/" \
      -e 's#full_scores_pact"#full_scores_haiku_pact"#' \
      analyze_pact.py > analyze_pact_haiku.py
  python3 analyze_pact_haiku.py > haiku_pact_results.txt 2>&1
  echo "haiku pact analysis written"
  cat haiku_pact_results.txt
fi
echo "HAIKU FINISHER DONE"
