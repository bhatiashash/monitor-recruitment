#!/usr/bin/env python3
"""GPT-5 mini rescore of the frozen core logs through OpenRouter.

Same frozen monitor system prompt, same public-record inputs, same output
format as monitor.py. The credential comes from the Muse vault connector
custom.openrouter via the surrogate exchange; no key is read from disk or
environment. Temperature 0, verified accepted by the service on Oct 25.
Concurrency 6 with retry and backoff on 429/5xx. Resumes from existing
output by uid, exactly like monitor.py.
"""
import argparse
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dynamic_credentials import add_surrogate_to_request, read_json_response  # noqa: E402
import monitor as M  # noqa: E402

URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-5-mini"


def call_gpt5(system_prompt, user_prompt, model=MODEL):
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
    }
    last_err = None
    for attempt in range(6):
        req = urllib.request.Request(
            URL, data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json"})
        add_surrogate_to_request(req, "custom.openrouter",
                                 allowed_hosts=["openrouter.ai"])
        try:
            with urllib.request.urlopen(req, timeout=240) as resp:
                payload = read_json_response(resp)
            return M.parse_score(payload["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(15 * (attempt + 1))
                continue
            raise
        except Exception as e:  # noqa: BLE001 - transient network/reasoning errors
            last_err = e
            time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"GPT-5 mini call failed after retries: {last_err}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--condition", required=True, choices=["A", "B", "C"])
    ap.add_argument("--game", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--model", default=MODEL)
    args = ap.parse_args()

    with open(args.results) as f:
        data = json.load(f)
    rounds = data["rounds"] if isinstance(data, dict) else data

    done = set()
    if os.path.exists(args.out):
        with open(args.out) as f:
            for line in f:
                done.add(json.loads(line)["uid"])

    tasks = []
    for uid, name, agents, typology in M.iter_agent_rounds(rounds):
        full_uid = f"{args.condition}_{args.game}_{uid}"
        if full_uid in done:
            continue
        tasks.append((full_uid, name, M.build_monitor_user_prompt(name, agents),
                      typology))
    print(f"{args.condition}/{args.game}: {len(tasks)} calls to make", flush=True)

    lock = threading.Lock()
    counter = {"n": 0, "fail": 0}

    def work(task):
        full_uid, name, prompt, typology = task
        try:
            score = call_gpt5(M.MONITOR_SYSTEM_PROMPT, prompt, model=args.model)
        except Exception:  # noqa: BLE001 - one bad call must not kill the cell
            with lock:
                counter["fail"] += 1
            return
        with lock:
            with open(args.out, "a") as fout, open(args.labels, "a") as flab:
                fout.write(json.dumps({
                    "uid": full_uid, "condition": args.condition,
                    "game": args.game, "agent": name, "score": score,
                }) + "\n")
                flab.write(json.dumps({
                    "uid": full_uid, "typology": typology,
                }) + "\n")
            counter["n"] += 1
            if counter["n"] % 50 == 0:
                print(f"  {counter['n']}/{len(tasks)}", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, tasks))
    print(f"done: {args.out} failed_calls={counter['fail']}", flush=True)


if __name__ == "__main__":
    main()
