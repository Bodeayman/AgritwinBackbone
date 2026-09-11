import json
import os
import re
import subprocess
import sys
import urllib.request

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ["GITHUB_REPOSITORY"]
SHA = os.environ["GITHUB_SHA"]
RUN_ID = os.environ["GITHUB_RUN_ID"]

ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
API_KEY = os.environ.get("AZURE_OPENAI_KEY", "")
DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")
API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21")
MODEL = os.environ.get("AUTOFIX_MODEL", "gpt-4o")

MAX_FIX_ATTEMPTS = int(os.environ.get("AUTOFIX_MAX_ATTEMPTS", "3"))

SYSTEM_PROMPT = (
    "You are an expert Python/FastAPI engineer fixing failing tests in a farm "
    "management backend (FastAPI, SQLAlchemy, Pydantic, PostgreSQL/PostGIS). "
    "Reply with ONLY a unified diff (git diff style). Do not explain. "
    "The diff must fix the reported test failures and nothing else."
)


def api_call(messages):
    if not ENDPOINT or not API_KEY:
        raise RuntimeError(
            "AZURE_OPENAI_ENDPOINT/AZURE_OPENAI_KEY not configured; cannot call LLM"
        )
    url = (
        f"{ENDPOINT}/openai/deployments/{DEPLOYMENT}/chat/completions"
        f"?api-version={API_VERSION}"
    )
    payload = {
        "messages": messages,
        "temperature": 0.2,
    }
    if MODEL:
        payload["model"] = MODEL
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "api-key": API_KEY,
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


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

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"CI tests failed on commit {SHA} (run {RUN_ID}). "
                "Repo layout: app/ (FastAPI app: api/, services/, schemas/, models/, "
                "repositories/), tests/ (pytest). Fix the errors in the following log:\n\n"
                f"{log_text}"
            ),
        },
    ]

    for attempt in range(1, MAX_FIX_ATTEMPTS + 1):
        print(f"[autofix] attempt {attempt}/{MAX_FIX_ATTEMPTS}: requesting patch from model")
        try:
            response = api_call(messages)
        except Exception as exc:
            print(f"[autofix] LLM call failed: {exc}")
            _gh("issue", f"Autofix failed: LLM unavailable", f"```\n{exc}\n```\n\nFull run: .../actions/runs/{RUN_ID}")
            sys.exit(1)

        patch = extract_diff(response)
        if not patch.strip():
            print("[autofix] Model returned empty patch")
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": "Your reply contained no diff. Return a unified diff only."})
            continue

        with open("/tmp/autofix.patch", "w", encoding="utf-8") as f:
            f.write(patch)

        res = run(["git", "apply", "--check", "/tmp/autofix.patch"])
        if res.returncode != 0:
            print("[autofix] patch does not apply cleanly")
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": f"The patch failed to apply:\n{res.stderr}\nReturn a corrected unified diff only."})
            continue

        run(["git", "apply", "/tmp/autofix.patch"])
        print("[autofix] patch applied; running tests")
        test_res = run(["pytest", "tests/", "-q"])
        if test_res.returncode == 0:
            print("[autofix] tests pass — creating PR")
            _create_pr()
            sys.exit(0)

        # Tests still fail: feed the new tail back and retry
        tail = test_res.stdout + test_res.stderr
        tail = tail[-MAX_LOG:]
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": f"Patch applied but tests still fail:\n{tail}\nReturn a corrected unified diff only."})

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