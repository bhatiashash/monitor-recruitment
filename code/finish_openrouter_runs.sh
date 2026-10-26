#!/usr/bin/env bash
# Waits for the two parallel OpenRouter passes launched Oct 25 about
# 8:50pm EDT, then writes their headline result files. Runs once.
set -u
cd ~/workspace/sprint/monitor

while ! grep -q "GPT5 PACT SCORING DONE" gpt5_pact_scoring_main.log 2>/dev/null; do
  sleep 20
done
python3 analyze_pact_gpt5.py > gpt5_pact_results.txt 2>&1
echo "gpt5 pact analysis written"

while ! grep -q "HAIKU PARALLEL SCORING DONE" haiku_parallel_main.log 2>/dev/null; do
  sleep 20
done
python3 score.py \
  --scores "full_scores_haiku/scores_*.jsonl" \
  --labels "full_scores_haiku/labels_*.jsonl" \
  --calibration-condition A --fpr 0.05 \
  > haiku_headline_results.txt 2>&1
echo "haiku headline results written"
echo "FINISHER DONE"
