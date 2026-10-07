#!/usr/bin/env python3
"""Execute CLAUDE.md's `## Verify` section and DERIVE its stated numbers (lc-95).

The section documents commands and counts. Three defects of one class were
found in it by a human reading it against reality: a command that did not run
(`-t .`), a count that drifted (51 node bites where the runner said 62), and a
command spelling that prints `fatal:` (`--git-range ..HEAD`). Nothing graded
the section, so it could drift red again with no check saying so. This is
that check, and it carries no copy of any number it grades.

WHAT IT DOES
  * extracts every command of the section's fenced ```bash block;
  * EXECUTES each (cwd = the repo root; `XDG_STATE_HOME` on a scratch dir so
    the live fire log is not written), except those named by `--skip`;
  * FINDING (exit 2): a command exits non-zero; a command's output carries a
    line starting `fatal:` (a documented command that runs "green" over a
    fatal is the lc-89 spelling defect); a number the section STATES for a
    runner (`All N node bites`, `N pass, M fail, K skipped`, `Ran N tests`)
    differs from the figure the run just DERIVED;
  * COULD NOT VERIFY (exit 3): a command was skipped, the section or its
    block is missing, or a stated number belongs to a runner that did not run
    — each named, never folded into a clean. A skipped command is therefore
    never a quiet pass.
  * CLEAN (exit 0): every command ran, none failed or printed `fatal:`, every
    stated number agreed with its derivation.

The tolerance question: nothing here tolerates a failing command. A suite
that carries one expected failure documents it in the section; this check
reports the non-zero exit and leaves the judgment to the reader, because a
check that goes green by tolerating failures is the defect with the sign
flipped.

USAGE: python3 tools/verify-claude-md.py [--file CLAUDE.md] [--repo .]
           [--section '## Verify'] [--skip SUBSTRING ...]
Reads only; writes no tracked file.
"""

import argparse
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "plugin" / "cli"))

from lifecycle_core import exits  # noqa: E402


def section_text(md: str, heading: str):
    """The body from `heading` to the next heading of the same level."""
    level = len(heading) - len(heading.lstrip("#"))
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == heading:
            body = []
            for nxt in lines[i + 1:]:
                m = re.match(r"^(#+)\s", nxt)
                if m and len(m.group(1)) <= level:
                    break
                body.append(nxt)
            return "\n".join(body)
    return None


def commands_of(section: str):
    """Commands of the first fenced block, comments and continuation
    comment-lines stripped. A line with no command text is dropped."""
    m = re.search(r"```[a-z]*\n(.*?)```", section, re.S)
    if not m:
        return None
    out = []
    for line in m.group(1).splitlines():
        cmd = line.split("  #")[0].strip()
        if cmd and not cmd.startswith("#"):
            out.append(cmd)
    return out


# (runner prefix, derivation of {label: figure} from that run's output)
def _derive_node(out: str):
    figs = {}
    for key in ("tests", "pass", "fail", "skipped"):
        m = re.search(rf"^ℹ {key} (\d+)", out, re.M)
        if m:
            figs[key] = int(m.group(1))
    return figs


def _derive_unittest(out: str):
    m = re.search(r"^Ran (\d+) tests?", out, re.M)
    return {"tests": int(m.group(1))} if m else {}


RUNNERS = (
    ("node --test", _derive_node),
    ("python3 -m unittest", _derive_unittest),
)

# What the section may STATE, per runner: (regex, group -> derived label).
STATED = {
    "node --test": (
        (re.compile(r"\b[Aa]ll (\d+) node bites"), {1: "tests"}),
        (re.compile(r"\bone of the (\d+) node bites"), {1: "tests"}),
        (re.compile(r"(\d+) pass, (\d+) fail, (\d+) skipped"),
         {1: "pass", 2: "fail", 3: "skipped"}),
    ),
    "python3 -m unittest": (
        (re.compile(r"\bRan (\d+) tests?"), {1: "tests"}),
    ),
}


def run(cmd: str, repo: Path, state: str):
    # Scratch state only for the python commands, which drive lifecycle verbs
    # and would append to the live fire log. NOT for node: the leak scan's own
    # bite `foreign-path: a path under each known XDG root (env default)`
    # reads XDG_STATE_HOME and FAILS when it points at a scratch path
    # (measured 2026-10-07: 61 pass, 1 fail with it set, 62 pass without), so
    # overriding it there would make the check disagree with the documented
    # command's own result.
    env = dict(os.environ)
    if cmd.startswith("python"):
        env["XDG_STATE_HOME"] = state
    p = subprocess.run(shlex.split(cmd), cwd=repo, env=env,
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def check(md_path: Path, repo: Path, heading: str, skips, out=print) -> int:
    md = md_path.read_text(encoding="utf-8")
    section = section_text(md, heading)
    if section is None:
        out(f"COULD NOT VERIFY: no section {heading!r} in {md_path}")
        return exits.COULD_NOT_VERIFY
    cmds = commands_of(section)
    if not cmds:
        out(f"COULD NOT VERIFY: {heading!r} carries no fenced command block")
        return exits.COULD_NOT_VERIFY

    codes = []
    derived = {}  # runner prefix -> figures
    state = tempfile.mkdtemp(prefix="lane-verify-md-")
    for cmd in cmds:
        if any(s in cmd for s in skips):
            out(f"SKIPPED  {cmd}  (named by --skip)")
            codes.append(exits.COULD_NOT_VERIFY)
            continue
        rc, so, se = run(cmd, repo, state)
        text = so + se
        fatal = [l for l in text.splitlines() if l.startswith("fatal:")]
        status = []
        if rc != 0:
            status.append(f"exit {rc}")
            codes.append(exits.FINDING)
        if fatal:
            status.append(f"prints {fatal[0]!r}")
            codes.append(exits.FINDING)
        out(f"{'FINDING' if status else 'RAN    '}  {cmd}"
            + (f"  [{'; '.join(status)}]" if status else "  [exit 0]"))
        for prefix, derive in RUNNERS:
            if cmd.startswith(prefix):
                derived[prefix] = derive(text)

    for prefix, patterns in STATED.items():
        for rx, groups in patterns:
            for m in rx.finditer(section):
                if prefix not in derived:
                    out(f"COULD NOT VERIFY: the section states {m.group(0)!r} "
                        f"for `{prefix}`, which did not run")
                    codes.append(exits.COULD_NOT_VERIFY)
                    continue
                for g, label in groups.items():
                    want, got = int(m.group(g)), derived[prefix].get(label)
                    if got is None:
                        out(f"COULD NOT VERIFY: `{prefix}` output carried no "
                            f"{label!r} figure to compare with {m.group(0)!r}")
                        codes.append(exits.COULD_NOT_VERIFY)
                    elif want != got:
                        out(f"FINDING  stated {m.group(0)!r}: the run derived "
                            f"{label}={got}, the section says {want}")
                        codes.append(exits.FINDING)
                    else:
                        out(f"AGREES   stated {m.group(0)!r} == derived "
                            f"{label}={got}")
    code = exits.worst(codes)
    out(f"{exits.word(code)}: {len(cmds)} documented command(s), "
        f"{sum(1 for c in codes if c != exits.CLEAN)} non-clean answer(s)")
    return code


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--file", default=None)
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--section", default="## Verify")
    ap.add_argument("--skip", action="append", default=[])
    args = ap.parse_args(argv)
    repo = Path(args.repo)
    md = Path(args.file) if args.file else repo / "CLAUDE.md"
    return check(md, repo, args.section, args.skip)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
