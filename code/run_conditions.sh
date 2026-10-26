#!/usr/bin/env bash
# Monitor-recruitment experiment runner.
# Prerequisite: ~/workspace/sprint/tb/compute.env holds the participant key
# (poseidon_compute finds it by walking up from the harness directory).
#
# Usage:
#   ./run_conditions.sh pilot    # 2 trials x 3 conditions x 2 games
#   ./run_conditions.sh full     # 10 trials x 3 conditions x 2 games
#
# Agent model and monitor display name are set here; keep them in sync with
# FREEZE.md once frozen.
set -euo pipefail

AGENT_MODEL="${AGENT_MODEL:-openai/gpt-4o-mini}"
MONITOR_NAME="${MONITOR_NAME:-GPT-5 Monitor}"
MODE="${1:-pilot}"
if [ "$MODE" = "pilot" ]; then TRIALS=2; else TRIALS=10; fi

export PATH="$HOME/.local/bin:$PATH"
cd ~/workspace/sprint/tb/llm-trust-breaking

for COND in A B C; do
  for GAME in diners weakestlink; do
    echo "=== condition $COND, game $GAME, trials $TRIALS ==="
    MONITOR_CONDITION=$COND MONITOR_NAME="$MONITOR_NAME" \
      uv run python experiments/run_endogenous.py \
        --game "$GAME" --agents 2 --trials "$TRIALS" --rounds 10 \
        --model "$AGENT_MODEL" --use-queue \
        --run-suffix "cond${COND}"
  done
done
echo "All runs finished. Results under outputs/experiments/<game>/2agents/."
