#!/usr/bin/env python3
"""Test cloud models' ability to recognize ASCII art."""

import json
import subprocess
import sys
import time

CLOUD_MODELS = [
    "deepseek-v4-pro:cloud",
    "deepseek-v4-flash:cloud",
    "kimi-k2.6:cloud",
    "glm-5.1:cloud",
    "gemma4:31b-cloud",
    "qwen3.5:397b-cloud",
    "qwen3.5:cloud",
    "gpt-oss:120b-cloud",
    "glm-5.2:cloud",
    "glm-5.3:cloud",
]

PROMPT_TEMPLATE = (
    "Look at this ASCII art carefully and tell me what it depicts. "
    "Be specific - describe the subject, pose, and any recognizable features. "
    "If you cannot determine what it is, say so.\n\n```\n{content}\n```\n\n"
    "What does this ASCII art show?"
)

RESULTS_FILE = "tests/cloud_model_results.json"


def load_existing():
    """Load any existing results to skip already-tested models."""
    try:
        with open(RESULTS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_results(results):
    """Save results after each model."""
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)


def log(msg):
    """Print with flush for real-time output."""
    print(msg, flush=True)


def query_model(model, content, timeout=300):
    """Query a model via ollama API."""
    prompt = PROMPT_TEMPLATE.format(content=content)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", str(timeout),
             "http://localhost:11434/api/generate",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=timeout + 30
        )
        if result.returncode != 0:
            return f"ERROR: curl failed (rc={result.returncode})"
        data = json.loads(result.stdout)
        if "error" in data:
            return f"ERROR: {data['error']}"
        return data.get("response", "NO RESPONSE").strip()
    except subprocess.TimeoutExpired:
        return "ERROR: timeout"
    except Exception as e:
        return f"ERROR: {e}"


def main():
    files = ["tests/image1.txt", "tests/image2.txt"]
    results = load_existing()

    for fpath in files:
        with open(fpath) as f:
            content = f.read()
        fname = fpath.split("/")[-1]

        if fname not in results:
            results[fname] = {}

        log(f"\n{'='*60}")
        log(f"FILE: {fname} ({len(content)} chars, {content.count(chr(10))+1} lines)")
        log(f"{'='*60}")

        for model in CLOUD_MODELS:
            # Skip already tested
            if model in results[fname]:
                log(f"\n--- {model} --- [SKIP, already tested]")
                continue

            log(f"\n--- {model} ---")
            start = time.time()
            response = query_model(model, content, timeout=300)
            elapsed = time.time() - start
            display = response[:200] + "..." if len(response) > 200 else response
            log(f"[{elapsed:.1f}s] {display}")

            results[fname][model] = {
                "response": response,
                "time": round(elapsed, 1)
            }
            save_results(results)  # Save after each model

    # Summary
    log(f"\n\n{'='*60}")
    log("SUMMARY")
    log(f"{'='*60}")
    for fname in results:
        log(f"\n{fname}:")
        for model in CLOUD_MODELS:
            r = results.get(fname, {}).get(model, {})
            if not r:
                log(f"  {model:40s} [NOT TESTED]")
                continue
            resp = r.get("response", "N/A")
            t = r.get("time", "N/A")
            first = resp.split(".")[0][:80] if resp else "N/A"
            status = "OK" if not resp.startswith("ERROR") else resp[:50]
            log(f"  {model:40s} [{t:>5}s] {first}")

    log(f"\nFull results saved to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
