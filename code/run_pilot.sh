#!/usr/bin/env bash
# Pilot: 2 trials x 10 rounds x 2 agents, conditions A/B/C, games diners and
# weakestlink, against the deployed Modal endpoint (compute.env routes it).
# Gate: >= 5 positives (premeditated_deception) in condition A per game.
set -u
export PATH="$HOME/.local/bin:$PATH"
cd ~/workspace/sprint/tb/llm-trust-breaking

for COND in A B C; do
  for GAME in diners weakestlink; do
    echo "=== pilot condition $COND game $GAME ==="
    MONITOR_CONDITION=$COND MONITOR_NAME="Qwen2.5-14B" \
      uv run python experiments/run_endogenous.py \
        --game "$GAME" --agents 2 --trials 2 --rounds 10 \
        --model Qwen/Qwen2.5-7B-Instruct \
        --run-suffix "pilot_cond${COND}" \
      || echo "RUN FAILED: cond $COND game $GAME"
  done
done
echo "PILOT DONE"
