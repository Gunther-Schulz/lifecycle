"""The judgment register (design §3.11) — six rules, DESIGNED NOW.

WHY THEY EXIST BEFORE THE EVIDENCE DOES. Waiting for use to show a rule wrong
is what produces drift: the rule is never written, so nothing fires, so
nothing is ever learned, and the absence reads as "no problem here". So each
rule below is stated CONCRETELY, and what is deferred is its RETIREMENT rather
than its existence.

THREE PROPERTIES EVERY RULE HERE HAS, and they are what separate a judgment
rule from a refusal:

  * it emits a FINDING, never a refusal. A judgment-shaped condition
    mechanized as a block over- and under-fires, and a guard that fires on
    legitimate work trains the override reflex that kills it. These report.
  * its CORRECTION PATH is a ledger line. A rule found wrong is not argued
    with — the decision is recorded where the next session looks.
  * it records USE-EVIDENCE — fired / fired on legitimate work / overridden —
    for the fire-rate review the retire lane runs. A rule with no
    use-evidence at all is not "working", it is UNOBSERVED, and the register
    prints that as its own answer rather than as a clean line.

WHAT A SITED RULE IS. A rule is SITED when a place in the code actually
evaluates it. Three of the six are sited today; the other three name the wave
that sites them and are printed as NOT SITED. That distinction is the whole
honesty of this file: a rule declared and never evaluated produces exactly the
same silence as a rule that never fires, and only one of those is fine.
"""

from dataclasses import dataclass, field

from . import exits, firelog

#: The three use-evidence outcomes §3.11 names, closed.
#:
#:   fired       the rule's condition held and it reported
#:   legitimate  it fired on work that was CORRECT — the over-firing signal,
#:               and the one that decides retirement
#:   overridden  a caller went ahead anyway
USES = ("fired", "legitimate", "overridden")


@dataclass(frozen=True)
class Rule:
    ident: str
    #: §3.11's own sentence, concretely — never a paraphrase of it.
    statement: str
    #: Where in this build the rule is EVALUATED, or "" when nothing does.
    site: str = ""
    #: The wave that sites it, for a rule nothing evaluates yet.
    sited_in: str = ""
    #: The finding row it emits, where it emits one.
    row: str = ""
    #: The ledger line kind that corrects it.
    correction: str = "decision"
    notes: str = ""

    @property
    def sited(self) -> bool:
        return bool(self.site)


RULES = [
    Rule(
        ident="staleness-per-kind",
        statement="items: no grade movement across N retire passes AND no "
                  "blocker (nobody's court) -> stale; PARKED on `decision` -> "
                  "never stale, surfaced. done bodies: uncited since close -> "
                  "compact. journal entries: cited by no law or workflow -> "
                  "stale. lanes: trigger never fired AND no use-evidence since "
                  "mint -> stale. workflows: no lane routes to it -> stale. "
                  "directives: a cited file changed past the citation -> stale "
                  "(change-coupling). audits: never. templates: no binder -> "
                  "stale. N = 3 passes, a placeholder the first walk replaces.",
        sited_in="the retire lane's SECOND pass. The predicate is 'no grade "
                 "movement across N passes', and nothing persists what the "
                 "last pass saw — so on a first walk it can only return "
                 "'nothing is stale', over every repo, which is a number "
                 "shaped like a pass. `retire` prints NOT RUN for it rather "
                 "than answering.",
        notes="N=3 IS A PLACEHOLDER AND IT SAYS SO IN ITS OWN OUTPUT. A "
              "placeholder printed as a threshold is a number nobody chose "
              "wearing a measurement's clothes; the first full walk replaces "
              "it with one the passes themselves produced. Calling this rule "
              "SITED because the walk names it would be the assurance wider "
              "than its predicate: the walk reads the declaration's staleness "
              "string and prints it, which is not evaluating it.",
    ),
    Rule(
        ident="intake-cost-test",
        statement="write-set <= 1 file AND session live AND no typed blocker "
                  "-> the tool asks \"do it now?\"; any other shape -> NEW. "
                  "Never a silent decision either way.",
        site="verbs.cost_test — called by every `item add --join new`",
        row="cost_test_veto",
        notes="The 'never silent' half is the one with a mechanism: an add "
              "that names one file and states no hunk count is COULD NOT "
              "VERIFY, never a pass, because a cost test that silently "
              "cleared what it could not evaluate would clear exactly the "
              "adds worth vetoing.",
    ),
    Rule(
        ident="decision-weight",
        statement="loud-failure = a verifier is named; fast-check = the "
                  "verifier runs under one minute (declared); small blast "
                  "radius = write-set <= 3 files, none live-on-write, none in "
                  "a public repo's outward surface; one-session = the blocker "
                  "type is not `decision`. Four yes -> light; each no -> its "
                  "paired step (verifier built / fresh verdict / enumeration / "
                  "ledger entry); four no -> the heavy workflow. The mapping "
                  "prints with the pick line.",
        sited_in="wave 2 — the drain lane's pick, which is where the mapping "
                 "prints. No verb in this build produces a pick line, so "
                 "there is nowhere for it to print.",
        notes="Two of the four axes are already computable from an item's own "
              "slots today (write-set size, blocker type); the other two need "
              "a declared verifier and its runtime, which no slot carries. "
              "That gap is the rule's, not the wave's.",
    ),
    Rule(
        ident="auto-apply-class",
        statement="only a disposition that is REVERSIBLE (rollback command "
                  "printed), LOCAL (touches this machine only) and RE-RUNNABLE "
                  "(idempotent). Initial members: the plugin update, "
                  "plugin-cache cleanup past three. Every addition is a ledger "
                  "decision line.",
        sited_in="wave 3 — the detector registry, which is what carries a "
                 "disposition at all.",
        notes="The membership rule is the mechanism and the members are data; "
              "neither has a home until a detector registers a disposition.",
    ),
    Rule(
        ident="laws-file-deciding-rule",
        statement="a tracked `CLAUDE.md` whose git author set is only ours -> "
                  "`CLAUDE.md`; any foreign author in its history -> the local "
                  "overlay; `init` prints which and why.",
        sited_in="wave 2 — `lifecycle init`, the verb that WRITES a laws "
                 "declaration. This build validates a declaration that "
                 "already names one and never chooses.",
        notes="`kind check` already answers COULD NOT VERIFY where the named "
              "laws file is absent, which is the half of this rule that has a "
              "site today: it does not decide the name, it refuses to pass "
              "over a name that resolves to nothing.",
    ),
    Rule(
        ident="trigger-policy-default",
        statement="`on-demand` is the default; `init` writes it explicitly and "
                  "names `advise` as the recommended next step once the router "
                  "has run clean for a week — a suggestion in the file, never "
                  "a silent switch.",
        site="declaration.validate — the closed TRIGGER_POLICIES vocabulary, "
             "and `lane list` printing the policy per repo",
        row="declaration_malformed",
        notes="The DEFAULT half is `init`'s (wave 2). What is sited today is "
              "the closed vocabulary and the longhand print, which is what "
              "stops an unrecognised policy reading as on-demand.",
    ),
]

RULES_BY_ID = {r.ident: r for r in RULES}


def record_use(rule_ident: str, use: str, *, repo=None, detail: str = "") -> bool:
    """Record one use-evidence event at the EFFECT SITE.

    The fire log is the recorder because it is the one file that already sees
    every verb invocation — reconstructing a fire rate from git or from memory
    is the shape this design replaced everywhere else. Failing to log is not a
    verdict: the rule still reported, and the caller's answer is unchanged.
    """
    if rule_ident not in RULES_BY_ID:
        raise ValueError(f"unknown judgment rule {rule_ident!r}; the register "
                         f"is closed: {', '.join(RULES_BY_ID)}")
    if use not in USES:
        raise ValueError(f"unknown use-evidence {use!r}; the outcomes are "
                         f"{', '.join(USES)}")
    return firelog.fire(f"judgment:{rule_ident}", repo=repo, outcome=None,
                        detail=f"use={use}" + (f" {detail}" if detail else ""))


def fire_rates(records) -> dict:
    """`{rule: {use: n}}` over fire-log records — zeros INCLUDED.

    Every rule appears whether or not it has ever fired, and every outcome
    appears whether or not it has ever happened. A register that listed only
    what had fired would render an unobserved rule and a well-behaved one
    identically, and those are the two answers a fire-rate review exists to
    separate.
    """
    out = {r.ident: {u: 0 for u in USES} for r in RULES}
    for rec in records:
        verb = str(rec.get("verb", ""))
        if not verb.startswith("judgment:"):
            continue
        ident = verb.split(":", 1)[1]
        if ident not in out:
            continue
        detail = str(rec.get("detail", ""))
        for u in USES:
            if detail.startswith(f"use={u}"):
                out[ident][u] += 1
                break
    return out


def report(out, records) -> int:
    """The register's own screen — every rule, sited or not, fired or not."""
    rates = fire_rates(records)
    out("")
    out("THE JUDGMENT REGISTER (design §3.11) — six rules, each a FINDING "
        "never a refusal, each correctable by a ledger line.")
    unsited = [r for r in RULES if not r.sited]
    unobserved = []
    for r in RULES:
        counts = rates[r.ident]
        total = sum(counts.values())
        out("")
        out(f"  {r.ident}")
        out(f"      rule:      {r.statement}")
        if r.sited:
            out(f"      site:      {r.site}")
        else:
            out(f"      NOT SITED: {r.sited_in}")
        if r.row:
            out(f"      finding:   [{r.row}]")
        out(f"      correction path: a `{r.correction}:` ledger line")
        out("      use-evidence: "
            + "  ".join(f"{u} {counts[u]}" for u in USES)
            + f"   (total {total})")
        if r.notes:
            out(f"      note:      {r.notes}")
        if r.sited and total == 0:
            unobserved.append(r.ident)
            out("      -> UNOBSERVED: this rule is sited and has never been "
                "recorded firing. That is not the same answer as 'it never "
                "fires' — nothing here distinguishes a quiet rule from a "
                "recorder that is not reaching it, and the fire-rate review "
                "cannot price a retirement on silence.")
    out("")
    out(f"register: {len(RULES)} rule(s), {len(RULES) - len(unsited)} sited, "
        f"{len(unsited)} awaiting a site, {len(unobserved)} sited-but-"
        f"unobserved.")
    if unsited:
        out("A rule with NO SITE produces exactly the silence a rule that "
            "never fires produces. It is listed with the wave that sites it, "
            "never counted as working.")
    return exits.COULD_NOT_VERIFY if (unsited or unobserved) else exits.CLEAN
