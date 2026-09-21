import json
import os
import re
import subprocess
import sys
import time
import urllib.request

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ["GITHUB_REPOSITORY"]
SHA = os.environ["GITHUB_SHA"]
RUN_ID = os.environ["GITHUB_RUN_ID"]

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODELS = [m.strip() for m in os.environ.get("GEMINI_MODELS", "").split(",") if m.strip()]
if not MODELS:
    MODELS = [
        os.environ.get("GEMINI_MODEL", "").strip(),
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-flash-latest",
    ]
MODELS = [m for m in MODELS if m]

MAX_FIX_ATTEMPTS = int(os.environ.get("AUTOFIX_MAX_ATTEMPTS", "3"))
MODE = os.environ.get("AUTOFIX_MODE", "test")

SYSTEM_PROMPT = (
    "You are an expert Python/FastAPI engineer fixing a farm management backend "
    "(FastAPI, SQLAlchemy, Pydantic, PostgreSQL/PostGIS). Reply with ONLY a unified "
    "diff (git diff style). Do not explain. The diff must fix the reported problem "
    "and nothing else."
)

MODE_CONTEXT = {
    "test": (
        "The CI test job failed. Repo layout: backbone/app/ (api/, services/, schemas/, models/, "
        "repositories/), backbone/tests/ (pytest). Fix the errors in the log."
    ),
    "deploy": (
        "The production deployment fails its health check (the FastAPI web container on "
        "EC2 does not respond on port 8000, or the container is crashing). Below are the "
        "container logs from EC2. Repo layout: backbone/app/ (api/, services/, schemas/, models/, "
        "repositories/), backbone/tests/ (pytest). Identify the root cause from the logs and "
        "produce a code/config fix so the app starts and serves / correctly."
    ),
}


def api_call(history, system_prompt):
    if not API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY not configured; cannot call Gemini"
        )
    max_retries = int(os.environ.get("GEMINI_MAX_RETRIES", "5"))
    backend_wait = float(os.environ.get("GEMINI_RETRY_WAIT", "2"))
    last_err = None
    for model in MODELS:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
            f":generateContent?key={API_KEY}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": history,
            "generationConfig": {"temperature": 0.2},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        for attempt in range(1, max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read())
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    raise RuntimeError(f"Gemini returned unexpected payload: {json.dumps(data)[:1000]}")
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                if exc.code in (429, 500, 502, 503, 504):
                    # Transient errors (throttled/temporarily unavailable): retry with backoff
                    last_err = f"HTTP {exc.code} on model {model}: {body[:300]}"
                    if attempt < max_retries:
                        delay = backend_wait * attempt
                        print(f"[autofix] {last_err} (attempt {attempt}/{max_retries}, retrying in {delay}s)")
                        time.sleep(delay)
                        continue
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_err = f"{exc}"
                if attempt < max_retries:
                    delay = backend_wait * attempt
                    print(f"[autofix] connection failed: {last_err} (attempt {attempt}/{max_retries}, retrying in {delay}s)")
                    time.sleep(delay)
                    continue
            except Exception as exc:
                last_err = f"{exc}"
                print(f"[autofix] call failed: {last_err}")
                break
            last_err = last_err or "request failed"
            print(f"[autofix] {last_err}")
            break
    raise RuntimeError(f"All Gemini models failed. Last error: {last_err}")


def extract_diff(text):
    block = re.search(r"```(?:diff)?\s*(.*?)```", text, re.DOTALL)
    candidate = block.group(1) if block else text
    # Strip leading "+ " style prompt artifacts and keep lines that form a diff.
    lines = [ln for ln in candidate.splitlines() if not ln.startswith(("+negative:", "+++ ", "--- "))]
    return "\n".join(lines)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    log_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pytest_log.txt"
    try:
        with open(log_path, encoding="utf-8") as f:
            log_text = f.read()
    except FileNotFoundError:
        log_text = "(no log captured)"

    # Trim long logs to the tail (errors/tracebacks are at the end)
    MAX_LOG = 20000
    if len(log_text) > MAX_LOG:
        log_text = log_text[-MAX_LOG:]

    history = [
        {
            "role": "user",
            "parts": [
                {
                    "text": (
                        f"CI tests failed on commit {SHA} (run {RUN_ID}). "
                        f"{MODE_CONTEXT[MODE]}\n\n"
                        f"{log_text}"
                    )
                }
            ],
        }
    ]

    for attempt in range(1, MAX_FIX_ATTEMPTS + 1):
        print(f"[autofix] attempt {attempt}/{MAX_FIX_ATTEMPTS}: requesting patch from model")
        try:
            response = api_call(history, SYSTEM_PROMPT)
        except Exception as exc:
            print(f"[autofix] LLM call failed: {exc}")
            _gh("issue", f"Autofix failed: LLM unavailable", f"```\n{exc}\n```\n\nFull run: .../actions/runs/{RUN_ID}")
            sys.exit(1)

        patch = extract_diff(response)
        if not patch.strip():
            print("[autofix] Model returned empty patch")
            history.append({"role": "model", "parts": [{"text": response}]})
            history.append({"role": "user", "parts": [{"text": "Your reply contained no diff. Return a unified diff only."}]})
            continue

        with open("/tmp/autofix.patch", "w", encoding="utf-8") as f:
            f.write(patch)

        res = run(["git", "apply", "--check", "/tmp/autofix.patch"])
        if res.returncode != 0:
            print("[autofix] patch does not apply cleanly")
            history.append({"role": "model", "parts": [{"text": response}]})
            history.append({"role": "user", "parts": [{"text": f"The patch failed to apply:\n{res.stderr}\nReturn a corrected unified diff only."}]})
            continue

        run(["git", "apply", "/tmp/autofix.patch"])
        print("[autofix] patch applied; running tests")
        test_res = run(["pytest", "backbone/tests/", "-q"])
        if test_res.returncode == 0:
            print("[autofix] tests pass — creating PR")
            _create_pr()
            sys.exit(0)

        # Tests still fail: feed the new tail back and retry
        tail = test_res.stdout + test_res.stderr
        tail = tail[-MAX_LOG:]
        history.append({"role": "model", "parts": [{"text": response}]})
        history.append({"role": "user", "parts": [{"text": f"Patch applied but tests still fail:\n{tail}\nReturn a corrected unified diff only."}]})

    # Exhausted attempts
    _gh(
        "issue",
        f"Autofix could not fix failing tests ({SHA})",
        f"Autofix exhausted {MAX_FIX_ATTEMPTS} attempts on commit {SHA} (run {RUN_ID}).\n\nSee the run for error details.",
    )
    print("[autofix] gave up after max attempts")
    sys.exit(1)


def _gh(kind, title, body):
    if kind == "pr":
        url = f"https://api.github.com/repos/{REPO}/pulls"
        data = {
            "title": title,
            "head": "autofix",
            "base": "master",
            "body": body,
            "maintainer_can_modify": True,
        }
    else:
        url = f"https://api.github.com/repos/{REPO}/issues"
        data = {"title": title, "body": body}
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"[autofix] created {kind}: {resp.status}")
    except Exception as exc:
        print(f"[autofix] failed to create {kind}: {exc}")


def _create_pr():
    run(["git", "checkout", "-b", "autofix"])
    run(["git", "add", "-A"])
    commit = run(["git", "commit", "-m", f"fix: automated patch for failing tests ({SHA[:7]})"])
    if commit.returncode != 0:
        print("[autofix] nothing to commit; opening issue")
        _gh("issue", f"No changes from autofix ({SHA[:7]})", "Model produced a patch but nothing changed on disk.")
        return
    push = run(["git", "push", "-f", "origin", "autofix"])
    if push.returncode != 0:
        print(f"[autofix] push failed: {push.stderr}")
        _gh("issue", f"Autofix push failed ({SHA[:7]})", f"```\n{push.stderr}\n```")
        return
    _gh(
        "pr",
        f"Autofix: fix failing tests ({SHA[:7]})",
        f"Automated fix produced by CI. Triggering commit: {SHA}\n\nRun: https://github.com/{REPO}/actions/runs/{RUN_ID}",
    )


if __name__ == "__main__":
    main()