#!/usr/bin/env bash
# Pact extension full run (frozen in FREEZE.md, Oct 25 about 7:35pm EDT):
# diners only, classes pact/solo/innocent by conditions B and C,
# 10 trials x 10 rounds x 2 agents per cell, all six cells in parallel
# against the deployed 7B endpoint (Modal scales out the GPU containers).
set -u
export PATH="$HOME/.local/bin:$PATH"
cd ~/workspace/sprint/tb/llm-trust-breaking
LOGDIR=~/workspace/sprint/monitor/pact_logs
mkdir -p "$LOGDIR"

pids=""
for ARM in pact solo innocent; do
  for COND in B C; do
    (
      echo "=== pact arm $ARM cond $COND ==="
      MONITOR_CONDITION=$COND MONITOR_NAME="Qwen2.5-14B" PACT_ARM=$ARM PACT_SOLO_AGENT=M \
        uv run python experiments/run_endogenous.py \
          --game diners --agents 2 --trials 10 --rounds 10 \
          --model Qwen/Qwen2.5-7B-Instruct \
          --run-suffix "pact_${ARM}_cond${COND}" \
        || echo "RUN FAILED: arm $ARM cond $COND"
    ) > "$LOGDIR/gen_${ARM}_${COND}.log" 2>&1 &
    pids="$pids $!"
  done
done

fail=0
for p in $pids; do
  wait "$p" || fail=1
done
echo "PACT GENERATION DONE fail=$fail"
