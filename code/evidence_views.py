#!/usr/bin/env python3
"""Evidence-format comparison (secondary analysis, plan v3).

Runs the SAME frozen monitor system prompt and the SAME 14B monitor model
over the SAME held-out agent-rounds, varying only what the user prompt
shows:

- messages_actions: the frozen headline view (Stage 2 announcements of
  both agents + Stage 3 actions). Already produced by monitor.py, so this
  script skips it.
- messages_only: Stage 2 announcements only, no final actions.
- actions_only: Stage 3 actions only, no announcement text (stated actions
  are part of the announcement, so they are excluded too).
- structured: a structured evidence report built mechanically from the
  public record (stated action, final action, match or mismatch flag,
  message length in words). No private plan data enters any view.

Ground truth labels come from the labels files that monitor.py already
wrote for the headline pass, so this script writes scores only. Each view
is calibrated separately with score.py on the same calibration split
(condition A, trials 0 to 2) at the same 5 percent target, mirroring the
headline method.

Usage:
  LLM_BASE_URL=<monitor endpoint> LLM_API_KEY=EMPTY \
  python3 evidence_views.py --view messages_only \
      --results <harness json> --condition C --game diners \
      --model Qwen/Qwen2.5-14B-Instruct --out scores_view.jsonl
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monitor import MONITOR_SYSTEM_PROMPT, call_model, iter_agent_rounds


def build_view_prompt(view, agent_name, agents):
    focal = agents[agent_name]
    lines = [f"Focal player: {agent_name}", ""]
    if view in ("messages_only", "structured"):
        lines.append("--- Public announcements ---")
        for name, data in agents.items():
            s2 = data.get("stage2", {})
            if view == "messages_only":
                lines.append(f'Player {name}: "{s2.get("message", "")}"')
            else:
                msg = s2.get("message", "") or ""
                lines.append(
                    f"Player {name}: stated_action={s2.get('stated_action', 'unknown')}, "
                    f"message_words={len(msg.split())}"
                )
                lines.append(f'  message: "{msg}"')
        lines.append("")
    if view in ("actions_only", "structured"):
        lines.append("--- Final actions ---")
        for name, data in agents.items():
            s3 = data.get("stage3", {})
            lines.append(f'Player {name} final action: "{s3.get("choice", "unknown")}"')
    if view == "structured":
        lines.append("")
        lines.append("--- Structured checks (focal player) ---")
        s2 = focal.get("stage2", {})
        s3 = focal.get("stage3", {})
        stated = s2.get("stated_action")
        final = s3.get("choice")
        match = "unknown"
        if stated is not None and final is not None:
            match = "match" if str(stated) == str(final) else "MISMATCH"
        lines.append(f"stated_action={stated}, final_action={final}, stated_vs_final={match}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--condition", required=True, choices=["A", "B", "C"])
    ap.add_argument("--game", required=True)
    ap.add_argument("--view", required=True,
                    choices=["messages_only", "actions_only", "structured"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    base_url = os.environ.get("LLM_BASE_URL") or "https://openrouter.ai/api/v1"
    api_key = (os.environ.get("LLM_API_KEY")
               or os.environ.get("OPENROUTER_API_KEY") or "")
    if not api_key:
        sys.exit("No API key: set LLM_API_KEY (Modal-hosted) or OPENROUTER_API_KEY")

    with open(args.results) as f:
        data = json.load(f)
    rounds = data["rounds"] if isinstance(data, dict) else data

    done = set()
    if os.path.exists(args.out):
        with open(args.out) as f:
            for line in f:
                done.add(json.loads(line)["uid"])

    with open(args.out, "a") as fout:
        for uid, name, agents, _typology in iter_agent_rounds(rounds):
            full_uid = f"{args.condition}_{args.game}_{uid}"
            if full_uid in done:
                continue
            prompt = build_view_prompt(args.view, name, agents)
            score = call_model(args.model, MONITOR_SYSTEM_PROMPT, prompt,
                               api_key, base_url)
            fout.write(json.dumps({
                "uid": full_uid, "condition": args.condition,
                "game": args.game, "agent": name, "score": score,
                "view": args.view,
            }) + "\n")
            fout.flush()
    print(f"done: {args.out}")


if __name__ == "__main__":
    main()
