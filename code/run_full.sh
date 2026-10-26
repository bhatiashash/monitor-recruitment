#!/usr/bin/env bash
# Full run: 10 trials x 10 rounds x 2 agents, conditions A/B/C, games diners
# and weakestlink (1,200 agent-rounds), against the deployed Modal endpoint.
# Frozen design v3; decision amendment Oct 25 4:26pm EDT (proceed despite
# the failed pilot positives criterion).
set -u
export PATH="$HOME/.local/bin:$PATH"
cd ~/workspace/sprint/tb/llm-trust-breaking

for COND in A B C; do
  for GAME in diners weakestlink; do
    echo "=== full condition $COND game $GAME ==="
    MONITOR_CONDITION=$COND MONITOR_NAME="Qwen2.5-14B" \
      uv run python experiments/run_endogenous.py \
        --game "$GAME" --agents 2 --trials 10 --rounds 10 \
        --model Qwen/Qwen2.5-7B-Instruct \
        --run-suffix "full_cond${COND}" \
      || echo "RUN FAILED: cond $COND game $GAME"
  done
done
echo "FULL RUN DONE"
