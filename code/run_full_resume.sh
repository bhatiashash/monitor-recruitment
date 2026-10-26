#!/usr/bin/env bash
# Resume after the Oct 25 ~5:02pm runtime restart killed the first full-run
# attempt. Condition A diners completed and its file is saved; this script
# runs the five remaining cells in the original order.
set -u
export PATH="$HOME/.local/bin:$PATH"
cd ~/workspace/sprint/tb/llm-trust-breaking

run_cell() {
  local COND=$1 GAME=$2
  echo "=== full condition $COND game $GAME ==="
  MONITOR_CONDITION=$COND MONITOR_NAME="Qwen2.5-14B" \
    uv run python experiments/run_endogenous.py \
      --game "$GAME" --agents 2 --trials 10 --rounds 10 \
      --model Qwen/Qwen2.5-7B-Instruct \
      --run-suffix "full_cond${COND}" \
    || echo "RUN FAILED: cond $COND game $GAME"
}

run_cell A weakestlink
run_cell B diners
run_cell B weakestlink
run_cell C diners
run_cell C weakestlink
echo "FULL RUN RESUME DONE"
