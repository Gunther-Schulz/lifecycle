"""The harness behind 2026-10-05-head-surface-matrix.tsv: grade x
blocker-state, graded per surface.

Runs whatever tree it sits in (the recorded run was an export of bbf6ef0).
Every cell is a fresh scratch git repo built by the tool's own fixture class;
supporting state (a closed target, a ledger answer) is written through the
tool's own verbs. Prints one row per cell: per surface, the exit code and N
(names the item) or - (does not).

RUN IT WITH TOOL STATE REDIRECTED, or every verb it drives appends to the
real fire log:
    XDG_STATE_HOME=<scratch> XDG_CONFIG_HOME=<scratch> python3 <this file>
The full outputs land in matrix.json under $XDG_STATE_HOME.
"""
import io, json, os, re, sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "plugin", "cli"))
from lifecycle_core import refusals as R, cli as cli_mod, items as I  # noqa

SUBJ = "xx-1"
NAMED = re.compile(r"\bxx-1\b")
GRADES = ("NEW", "READY", "PARKED", "STANDBY")
MIG_Q = "regrade: was READY under the old carrier: READY is judged, never inherited"

DECL = json.loads(json.dumps(R.GOOD_FULL_DECLARATION))
DECL["grades-extra"] = ["STANDBY"]


def head(n):
    return f"schema: {I.SCHEMA_FLOOR}\nbaseline: {n}\nadded: 0\ncompacted: 0\n"


def run(repo, *argv):
    here = os.getcwd()
    buf = io.StringIO()
    try:
        os.chdir(str(repo.dir))
        with redirect_stdout(buf):
            try:
                code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
            except SystemExit as e:
                code = e.code
    finally:
        os.chdir(here)
    return code, buf.getvalue()


# state -> (blocker text for the subject, extra blocks, setup verb calls,
#           files to plant, who owes the next act per the per-item verdict)
def states():
    B = R._blocked_block
    return [
        ("none", "NONE", [], [], {}),
        ("untyped-prose", "waiting for the vendor to reply", [], [], {}),
        ("untyped-none-synonym", "n/a", [], [], {}),
        ("external-waiting", "external the vendor ships 2.0", [], [], {}),
        ("evidence-quiet", "evidence test -e flag-file", [], [], {}),
        ("evidence-fired", "evidence test -e flag-file", [], [],
         {"flag-file": ""}),
        ("evidence-broken", "evidence exit 2", [], [], {}),
        ("evidence-unclearable", "evidence false", [], [], {}),
        ("decision-unanswered", "decision which window", [], [], {}),
        ("decision-answered", "decision which window", [],
         [("ledger", "add", "decision", "--question", "which window",
           "--answer", "the left one", "--no-commit")], {}),
        ("decision-moot-elsewhere", "decision which window",
         [B("xx-50", "PARKED", "decision which window")],
         [("item", "close", "xx-50", "--drop", "--reason",
           "overtaken", "--no-commit")], {}),
        ("decision-migration-regrade", "decision " + MIG_Q, [], [], {}),
        ("item-target-open", "xx-50", [B("xx-50", "PARKED",
                                         "external the world")], [], {}),
        ("item-target-DONE", "xx-50", [B("xx-50", "READY", "NONE")],
         [("item", "close", "xx-50", "--reason", "built", "--no-commit")], {}),
        ("item-target-DROPPED", "xx-50", [B("xx-50", "READY", "NONE")],
         [("item", "close", "xx-50", "--drop", "--reason", "overtaken",
           "--no-commit")], {}),
        ("item-target-absent", "xx-9999", [], [], {}),
        ("item-cycle", "xx-50", [B("xx-50", "PARKED", "xx-1")], [], {}),
        ("item-chain-to-unclearable", "xx-50",
         [B("xx-50", "PARKED", "evidence false")], [], {}),
    ]


SURFACES = [
    ("ready_id", ("item", "ready", SUBJ), False),
    ("head", ("item", "ready", "--head"), True),
    ("statusline", ("item", "statusline"), True),
    ("check", ("item", "check"), True),
    ("ratio", ("item", "ratio"), True),
    ("digest", ("kind", "list", "--digest"), True),
    ("structure", ("kind", "list", "--structure"), True),
    ("audit", ("audit",), False),
]


def cell(grade, st):
    name, blocker, extra, setup, files = st
    # a READY unblocked bystander so `head` always has a positive control
    blocks = [R._blocked_block(SUBJ, grade, blocker)] + extra + \
        [R._blocked_block("xx-70", "READY", "NONE")]
    repo = R._Repo(declaration=DECL, items=head(len(blocks)) + "".join(blocks))
    rec = {"grade": grade, "state": name, "blocker": blocker, "setup": []}
    try:
        for argv in setup:
            c, o = run(repo, *argv)
            rec["setup"].append({"argv": argv, "code": c,
                                 "out": o.strip()[-400:]})
        for f, body in files.items():
            (repo.dir / f).write_text(body, encoding="utf-8")
        for sname, argv, _unprompted in SURFACES:
            c, o = run(repo, *argv)
            lines = [ln.strip() for ln in o.splitlines() if NAMED.search(ln)]
            rec[sname] = {"code": c, "named": bool(lines),
                          "lines": [ln[:400] for ln in lines], "out": o}
            if sname == "head":
                rec["head_control"] = "xx-70" in o
    finally:
        repo.close()
    return rec


def main():
    if not os.environ.get("XDG_STATE_HOME"):
        sys.exit("refusing to run: XDG_STATE_HOME is not set, so every verb "
                 "would append to the real fire log")
    out = []
    for st in states():
        for g in GRADES:
            out.append(cell(g, st))
    json.dump(out, open(os.path.join(os.environ["XDG_STATE_HOME"],
                                     "matrix.json"), "w"), indent=1)
    cols = ["grade", "state"] + [s[0] for s in SURFACES]
    print("\t".join(cols + ["setup_codes", "head_control"]))
    for r in out:
        row = [r["grade"], r["state"]]
        for s, _, _ in SURFACES:
            row.append(f"{r[s]['code']}{'N' if r[s]['named'] else '-'}")
        row.append(",".join(str(x["code"]) for x in r["setup"]) or ".")
        row.append("Y" if r["head_control"] else "n")
        print("\t".join(row))


if __name__ == "__main__":
    main()
