"""Frozen 14B monitor server for Project 1 on Modal.

Dedicated copy of the starter modal_serve.py with three changes, all
infrastructure only:
- App name is "monitor-serve", so deploying it does not replace the 7B
  "hackathon-serve" endpoint that agent generation still uses.
- Model and GPU are hardcoded to the frozen headline monitor
  (Qwen/Qwen2.5-14B-Instruct on A100-40GB), so no deploy-time environment
  variable can silently change which model answers.
- max_containers=6, so six parallel monitor.py clients (one per condition
  by game cell) can each run on their own GPU. The user confirmed on
  Oct 25 that the workspace has access to 10 GPUs.
The vLLM launch settings match the proven 7B deployment: max-model-len
8192 and gpu-memory-utilization 0.95.
"""
import subprocess

import modal

MODEL = "Qwen/Qwen2.5-14B-Instruct"
GPU = "A100-40GB"
VLLM_PORT = 8000

app = modal.App("monitor-serve")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("vllm==0.6.6", "huggingface_hub[hf_transfer]==0.26.2")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

_secrets = []
for name in ("huggingface", "modal-serve"):
    try:
        _secrets.append(modal.Secret.from_name(name, create_if_missing=True))
    except Exception:
        print(f"[modal_serve_monitor] note: Modal secret '{name}' not found, skipping.")


@app.function(
    image=image,
    gpu=GPU,
    timeout=24 * 3600,
    scaledown_window=300,
    secrets=_secrets,
    max_containers=6,
)
@modal.web_server(port=VLLM_PORT, startup_timeout=900)
def serve():
    """Launch vLLM's OpenAI-compatible server; Modal proxies it to a public URL."""
    cmd = [
        "python", "-m", "vllm.entrypoints.openai.api_server",
        "--model", MODEL,
        "--host", "0.0.0.0",
        "--port", str(VLLM_PORT),
        "--served-model-name", MODEL,
        "--max-model-len", "8192",
        "--gpu-memory-utilization", "0.95",
    ]
    subprocess.Popen(" ".join(cmd), shell=True)
