#!/usr/bin/env bash
# Waits for the Haiku refill pass, then rewrites the Haiku headline
# results and the Haiku pact analysis from the completed files.
# Same rules as finish_haiku_max.sh: score.py calibration on
# condition A trials 0 to 2 at the 5 percent target, and the pact
# analysis at the threshold from that calibration.
set -u
cd ~/workspace/sprint/monitor

while ! grep -q "HAIKU REFILL DONE" haiku_refill_main.log 2>/dev/null; do
  sleep 20
done

echo "core counts:"
wc -l full_scores_haiku/scores_*.jsonl
echo "pact counts:"
wc -l full_scores_haiku_pact/scores_*.jsonl
echo "refill cell log tails:"
tail -n 1 full_scores_haiku/scoring_refill_*.log full_scores_haiku_pact/scoring_refill_*.log

python3 score.py \
  --scores "full_scores_haiku/scores_*.jsonl" \
  --labels "full_scores_haiku/labels_*.jsonl" \
  --calibration-condition A --fpr 0.05 \
  > haiku_headline_results.txt 2>&1
echo "haiku headline results rewritten"
cat haiku_headline_results.txt

THRESH=$(grep -o "threshold [0-9]*" haiku_headline_results.txt | head -1 | awk '{print $2}')
echo "haiku calibrated threshold: $THRESH"
if [ -n "$THRESH" ]; then
  sed -e "s/^THRESH = 51/THRESH = $THRESH/" \
      -e 's#full_scores_pact"#full_scores_haiku_pact"#' \
      analyze_pact.py > analyze_pact_haiku.py
  python3 analyze_pact_haiku.py > haiku_pact_results.txt 2>&1
  echo "haiku pact analysis rewritten"
  cat haiku_pact_results.txt
fi
echo "HAIKU REFILL FINISHER DONE"
