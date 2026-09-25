"""The registered-closed-vocabulary contract (round decision D-3).

WHAT THIS IS FOR. A closed vocabulary cannot say that it cannot say
something. Every state a repo can reach and cannot express therefore renders
as its nearest MEMBER, and the neighbour is always the benign one: a
malformed `when` reads as UNDECLARED, an untypeable wait reads as an ordinary
park, a never-run predicate reads as one that ran quiet. The wrong answer is
shaped exactly like the right one, so nothing prompts a second look.

THE MECHANISM. Every closed VALUE vocabulary is REGISTERED with four things:
its name, its members, the IMPORTABLE consumer that renders it, and the PROOF
PATH — the sanctioned write/read route an out-of-vocabulary value must
actually traverse. The proof path is not decoration. A renderer can pass a
test while the operational path never reaches it, so a registration that
proved only "the registry field is set" would certify precisely the
disconnected mechanism this contract exists to prevent.

THE OOV ARM IS DATED AT BIRTH. `cannot-express(<date>): <reason>` carries its
own date because the first mark anyone writes has no comparison input — an
undated form has no computable absence at exactly the case that matters, and
"when did this become inexpressible" is the question the widening signal is
read from. A recorded OOV instance WITH ITS REASON is the widening signal:
new members are minted from recorded reasons, never guessed.

REGISTRATION IS ON CONTACT, never by a sweep. A big-bang registration pass
over every vocabulary in the package would be the Collector's Fallacy arm —
it would produce a registry nobody had exercised, which is the same
unread-instrument failure one level up. Vocabularies register when a gap is
found in one or when one is next touched.

DEFERRED IMPORTS, and the reason is structural rather than stylistic:
`items` and `declaration` are where the accepting predicates live, and both
are imported by the verbs that consume this registry. A module-level import
here would close the cycle. `declaration.read_moments` already defers its
`lanes` import for the same reason and says so.
"""

import re
from dataclasses import dataclass

#: The OOV arm's spelling. The DATE is part of the form, not an optional
#: annotation: an OOV instance's age is what the drain reads, and a form that
#: made the date optional would make the oldest instance unfindable exactly
#: when the count stopped being zero.
OOV_PREFIX = "cannot-express"

#: `cannot-express(2026-09-19): the reason, in the author's words`.
#: The reason is REQUIRED and non-empty — an OOV instance with no reason is a
#: silent park wearing the contract's own label, which is the state this
#: mechanism exists to make impossible rather than to relabel.
OOV_FORM = f"{OOV_PREFIX}(<date>): <reason>"

_OOV = re.compile(
    r"^" + re.escape(OOV_PREFIX) + r"\((\d{4}-\d{2}-\d{2})\)\s*:\s*(\S.*)$"
)


@dataclass(frozen=True)
class OOV:
    """One out-of-vocabulary instance, parsed."""
    date: str
    reason: str


def parse_oov(value) -> OOV | None:
    """`OOV(date, reason)` for a well-formed OOV value, else None.

    ANCHORED AT BOTH ENDS. The pattern is `^…$` over the stripped value
    rather than a containment test, because a substring match here would be a
    prefix match in an equality's costume: any longer body beginning with the
    same characters would read as an OOV instance, and a member whose own text
    quoted the form would be re-typed by the reader that was supposed to
    classify it.
    """
    if not isinstance(value, str):
        return None
    m = _OOV.match(value.strip())
    if m is None:
        return None
    return OOV(m.group(1), m.group(2).strip())


def is_oov(value) -> bool:
    """Is this value the OOV arm of its vocabulary, well-formed?"""
    return parse_oov(value) is not None


def looks_oov(value) -> bool:
    """Does this value CLAIM to be the OOV arm, well-formed or not?

    The malformed case needs its own answer. A value spelled
    `cannot-express: no date` is not a member, and it is not a well-formed
    OOV instance either — folding it into "unknown" would hide a broken
    instance of this very mechanism inside the bucket the mechanism exists to
    empty, and folding it into OOV would let an undated instance age
    invisibly. Callers that must tell the two apart ask both predicates.
    """
    return isinstance(value, str) and value.strip().startswith(OOV_PREFIX)


@dataclass(frozen=True)
class Vocabulary:
    """One registered closed vocabulary.

    `consumer` names the importable thing that RENDERS the value, and
    `proof_path` the route an OOV value travels to reach it. Both are prose
    read by a person; what makes them more than prose is that the roster row
    for this registration exercises the route and asserts the OOV rendering
    DIFFERS from every member's. A registration whose row asserted only that
    `oov_form` is set would be proving a data field.
    """
    name: str
    members: tuple
    oov_form: str
    consumer: str
    proof_path: str
    #: Members minted AFTER the vocabulary was registered, each as
    #: `(member, date, recorded reason)`. D-3 says new members are minted from
    #: recorded reasons; this is where the reason stays readable at run time
    #: instead of only in a commit message.
    minted: tuple = ()

    def renders_distinctly(self, rendered_oov: str) -> bool:
        """Is this rendering distinct from every member's own spelling?

        The contract's whole claim in one predicate: an OOV value must never
        render as a neighbour. Compared over the member SET rather than over a
        joined string — a substring test against a rendered list is satisfied
        by any value that happens to contain a member's name.
        """
        return all(str(m) != rendered_oov for m in self.members)


def registry() -> tuple:
    """The registered vocabularies, built on call.

    ON CALL rather than at import: the members live in `items` and
    `declaration`, both of which sit upstream of this module's consumers, and
    binding them at import time would freeze a copy of each tuple here — a
    second body for a fact whose home is the module that enforces it, which
    is the label-over-body class aimed at a registry whose whole job is to be
    the single source.
    """
    from . import declaration as decl
    from . import items as items_mod

    return (
        Vocabulary(
            name="grades",
            members=items_mod.GRADES,
            oov_form=OOV_FORM,
            consumer="items.census / verbs.cmd_item_ready",
            proof_path=("written at the admission door (`item add --grade`), "
                        "counted by `items.census`, rendered by `item ready` "
                        "as unschedulable-with-reason, and refused by the "
                        "move at `item close`"),
            minted=(
                (items_mod.STANDBY, "2026-09-25",
                 "LEDGER.md decision \"operator: grant a freeze exception "
                 "for the third READY grade and its demote and return "
                 "triggers\" (LEDGER:159): decision-complete but not on "
                 "the scheduled head. Opt-in per repo via `grades-extra`; "
                 "written by `item bench`, returned by `item promote` "
                 "(lc-294)"),
            ),
        ),
        Vocabulary(
            name="reader-when modes",
            members=decl.READER_WHEN_MODES,
            oov_form=OOV_FORM,
            consumer="declaration.read_moments",
            proof_path=("declared on a kind's reader entry and evaluated by "
                        "`declaration.read_moments`, whose per-entry answer "
                        "carries the state"),
        ),
        Vocabulary(
            name="reader moment states",
            members=(decl.READ_MOMENT_NONE, decl.READ_MOMENT_UNDECLARED,
                      decl.READ_MOMENT_MALFORMED, decl.READ_MOMENT_DERIVED),
            oov_form=OOV_FORM,
            consumer="declaration.read_moments / verbs.cmd_kind_moments",
            proof_path=("computed per reader entry by `read_moments` from "
                        "the entry's `when` presence/validity and, absent a "
                        "`when`, the ref's own shape (O6 §4 Part A); "
                        "rendered per-entry by `kind moments` and folded "
                        "into its `declared=`/`derived=`/`executed=` fire-"
                        "log tally. NOT this vocabulary: `lanes."
                        "evaluate_trigger`'s own FIRE/QUIET/BROKEN, which "
                        "is the ONE trigger evaluator's separate, untouched "
                        "contract (CLAUDE.md)."),
        ),
        Vocabulary(
            name="trigger modes",
            members=decl.TRIGGER_MODES,
            oov_form=OOV_FORM,
            consumer="declaration._check_trigger",
            proof_path=("declared as a kind's seventh stage and validated by "
                        "`kind check`"),
        ),
        Vocabulary(
            name="growth modes",
            members=decl.GROWTH_MODES,
            oov_form=OOV_FORM,
            consumer="declaration._validate_kind's growth stage",
            proof_path=("declared as a kind's sixth stage and validated by "
                        "`kind check`, which accepts the arm and refuses a "
                        "word that is neither member nor arm"),
        ),
        Vocabulary(
            name="evidence marks",
            members=items_mod.EVIDENCE_MARKS,
            oov_form=OOV_FORM,
            consumer=("items.evidence_mark_problem / "
                      "items.perishable_grammar_problem"),
            proof_path=("written into an evidence slot at the admission door "
                        "and graded by `items.evidence_mark_problem`, which "
                        "is PRESENCE-only; `PERISHABLE` is the one member "
                        "carrying arguments, so its FORM is graded beside it "
                        "by `items.perishable_grammar_problem` at both write "
                        "doors — named here because a proof path that "
                        "stopped at the presence check would be an assurance "
                        "wider than what it establishes, over the one member "
                        "presence cannot check (lc-244)"),
        ),
    )


def by_name(name: str) -> Vocabulary | None:
    """One registration, or None. Callers state which vocabulary they mean."""
    for v in registry():
        if v.name == name:
            return v
    return None
