"""`lifecycle verify` — the declared verify block, EXECUTED and COUNTED.

MECHANISM #1 of the answerable-not-felt arc (docs/answerable-not-felt.md,
lc-157), and the one ranked most real because it is wholly deterministic. A
repo's CLAUDE.md declares the exact commands that make work in it
trustworthy. Nothing has ever checked that those commands RAN.

THE DEFECT CLASS IT CLOSES, from the arc's own evidence pile, all measured in
one session: a verify entry at mode 644 that could never execute; an
unquoted `$t` loop where 8 of 9 checks never ran and the failure was shaped
exactly like a pass (a grep for FAILED finds none in either case). Both are
the arc's signature — the wrong answer shaped exactly like the right one —
and both are invisible to every existing check because a check that does not
run emits nothing to notice.

SO THE ASSERTION IS A COUNT, NOT AN ABSENCE. `verify` reports EXECUTED
against REGISTERED, and a command that could not START is COULD NOT VERIFY,
never a pass. That distinction is the whole verb: a quiet pass and a check
that never ran are identical in every output except this one.

WHY IT LIVES HERE. The plugin already owns what a repo persists and already
reads the declared laws file. The verify block is a registered thing in that
file, and nothing else in the stack knows it exists.

THE BOUNDARY, stated because the verb must not be believed wider than it is:
this proves the commands RAN and what they returned. It does not prove they
CHECK anything — a registered command that is green by construction passes
here exactly as a real one does. Proving a check discriminates is
`tools/prove-rows.py`'s job, red-first, and no count can substitute for it.
"""

import re
import subprocess
from pathlib import Path

from . import exits

#: Exit codes a SHELL returns when the command never started. 127 is "not
#: found", 126 is "found and not executable" — which is the mode-644 case
#: this verb exists for. Neither is a test result and neither may be booked
#: as one.
COULD_NOT_START = (126, 127)

VERIFY_HEADING = re.compile(r'^##+\s*Verify\s*$', re.I | re.M)


def parse_block(laws_text: str) -> list[str]:
    """The commands in the laws file's `## Verify` fenced block, in order.

    A trailing `# comment` is stripped — the block's commands carry inline
    notes, and running one with its comment attached still works in a shell
    but makes the reported command a different string from the one a reader
    would type. Continuation lines (a comment alone on its own line, which
    the block uses to wrap a long note) are dropped rather than run.
    """
    m = VERIFY_HEADING.search(laws_text)
    if not m:
        return []
    rest = laws_text[m.end():]
    fence = re.search(r'```[a-zA-Z]*\n(.*?)```', rest, re.S)
    if not fence:
        return []
    cmds = []
    for raw in fence.group(1).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        cmds.append(re.sub(r'\s+#.*$', '', line).strip())
    return [c for c in cmds if c]


def run_one(cmd: str, repo: Path, timeout: int) -> tuple[str, int, str]:
    """`(verdict, code, detail)` for one registered command.

    Three verdicts and never two: `ran-clean`, `ran-failed`, `did-not-run`.
    A timeout is `did-not-run` rather than a failure: the command produced no
    verdict, and booking a timeout as a red is the same error one level down
    as booking a check that never started as a pass.
    """
    try:
        r = subprocess.run(cmd, shell=True, cwd=str(repo), capture_output=True,
                           text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "did-not-run", -1, f"timed out after {timeout}s"
    except OSError as e:
        return "did-not-run", -1, f"could not start: {e}"
    if r.returncode in COULD_NOT_START:
        tail = (r.stderr or r.stdout or "").strip().splitlines()
        return ("did-not-run", r.returncode,
                (tail[-1] if tail else f"exit {r.returncode}"))
    if r.returncode == 0:
        return "ran-clean", 0, ""
    tail = (r.stderr or r.stdout or "").strip().splitlines()
    return "ran-failed", r.returncode, (tail[-1] if tail else "")


def cmd_verify(args, out, repo: Path, declaration: dict) -> int:
    # THE TOP-LEVEL `laws` KEY IS THE DECLARATION'S OWN NAME FOR THE FILE,
    # and it is what `kind list` prints. The kinds entry's `home` is the same
    # fact in its stage table and can be absent; reading only the latter sent
    # this verb looking for CLAUDE.md in a repo that declares LAWS.md, which
    # its own refusal row caught on first run.
    laws_name = (declaration.get("laws")
                 or (declaration.get("kinds", {}).get("laws", {})
                     or {}).get("home"))
    laws = repo / (laws_name or "CLAUDE.md")
    if not laws.exists():
        out(f"COULD NOT VERIFY: no laws file at {laws.name} — the verify "
            "block is declared there, so there is nothing to run and this "
            "is not a clean result.")
        return exits.COULD_NOT_VERIFY

    cmds = parse_block(laws.read_text(encoding="utf-8"))
    if not cmds:
        out(f"COULD NOT VERIFY: {laws.name} declares no `## Verify` block, "
            "or the block is empty. A repo with nothing registered cannot "
            "report a clean verify — it reports that it registered nothing.")
        return exits.COULD_NOT_VERIFY

    out(f"registered: {len(cmds)} command(s) in {laws.name}")
    if getattr(args, "list", False):
        for i, c in enumerate(cmds, 1):
            out(f"  {i}. {c}")
        return exits.CLEAN

    timeout = getattr(args, "timeout", 900)
    ran = failed = never = 0
    for i, c in enumerate(cmds, 1):
        verdict, code, detail = run_one(c, repo, timeout)
        if verdict == "ran-clean":
            ran += 1
            out(f"  {i}. RAN, clean       {c}")
        elif verdict == "ran-failed":
            ran += 1
            failed += 1
            out(f"  {i}. RAN, FAILED ({code})  {c}")
            if detail:
                out(f"       {detail[:200]}")
        else:
            never += 1
            out(f"  {i}. DID NOT RUN      {c}")
            out(f"       {detail[:200]}")

    out(f"executed: {ran} of {len(cmds)} registered   "
        f"(failed {failed}, never ran {never})")

    # THE ORDER OF THESE TWO IS THE VERB'S POINT. A check that never ran is
    # reported BEFORE a failure, because a run that is missing checks cannot
    # say what the remaining ones would have found — the suite's verdict is
    # could-not-verify whatever the checks that DID run returned.
    if never:
        out(f"COULD NOT VERIFY [verify_check_did_not_run] {never} registered "
            "command(s) never executed. This is not a pass with fewer "
            "checks: a check that did not run emits nothing, so its silence "
            "is identical to a clean result. Repair the command or remove "
            "it from the block — a registered check that cannot run is a "
            "claim the repo is making and not keeping.")
        return exits.COULD_NOT_VERIFY
    if failed:
        out(f"FINDING [verify_check_failed] {failed} of {len(cmds)} "
            "registered command(s) ran and returned non-zero.")
        return exits.FINDING
    out(f"verify: CLEAN — all {len(cmds)} registered command(s) executed "
        "and returned zero. This says they RAN, never that they "
        "discriminate; red-first proof is `tools/prove-rows.py`'s job.")
    return exits.CLEAN
