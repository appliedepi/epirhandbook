"""For every workflow step, list shell variables used in its run: body that
nothing defines: not the step env:, not the job env:, not the workflow env:,
not assigned earlier in that same body, and not a GitHub-provided default."""
import re
import sys
import yaml

GITHUB_PROVIDED = {
    "GITHUB_SHA", "GITHUB_REF", "GITHUB_ACTOR", "GITHUB_TOKEN", "GITHUB_OUTPUT",
    "GITHUB_ENV", "GITHUB_WORKSPACE", "GITHUB_REPOSITORY", "GITHUB_EVENT_NAME",
    "GITHUB_RUN_ID", "GITHUB_STEP_SUMMARY", "HOME", "PATH", "PWD", "RUNNER_OS",
    "RUNNER_TEMP", "CI",
}

def used(body):
    out = set()
    for m in re.finditer(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)', body):
        out.add(m.group(1))
    return out

def assigned(body):
    out = set()
    for m in re.finditer(r'^\s*([A-Za-z_][A-Za-z0-9_]*)=', body, re.M):
        out.add(m.group(1))
    for m in re.finditer(r'\bfor\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\b', body):
        out.add(m.group(1))
    for m in re.finditer(r'\bread\b[^\n]*?\s([A-Za-z_][A-Za-z0-9_]*)\s*$', body, re.M):
        out.add(m.group(1))
    return out

bad = 0
for path in sys.argv[1:]:
    wf = yaml.safe_load(open(path))
    wf_env = set((wf.get("env") or {}).keys())
    for jname, job in (wf.get("jobs") or {}).items():
        job_env = set((job.get("env") or {}).keys())
        for step in job.get("steps") or []:
            body = step.get("run")
            if not body:
                continue
            step_env = set((step.get("env") or {}).keys())
            known = wf_env | job_env | step_env | assigned(body) | GITHUB_PROVIDED
            missing = sorted(v for v in used(body) if v not in known)
            if missing:
                bad += 1
                print(f"UNDEFINED  {path} :: {jname} :: {step.get('name')!r} -> {missing}")
print("OK — every run: variable has a definer" if not bad else f"{bad} step(s) with undefined variables")
