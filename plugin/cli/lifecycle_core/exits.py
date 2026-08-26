"""The `lifecycle` verb exit-code contract — ONE of the two in this system.

    0  CLEAN              nothing to report
    2  FINDING            something is wrong, and the tool can say what
    3  COULD_NOT_VERIFY   the tool could not form a verdict at all

A finding and an unreadable input MUST NOT share a code. That is the whole
reason `3` exists: an absence of evidence wearing a verdict's clothes is the
failure this contract is designed against, and folding could-not-verify into
either neighbour re-creates it. `1` is deliberately unused here, so a python
traceback's exit 1 is never mistaken for a verdict of ours.

THE OTHER CONTRACT — a lane's `Trigger:` predicate, a command `lane list`
EXECUTES rather than a verb of ours — is 0 fire / 1 quiet / >=2 broken. Do not
unify them and do not translate one into the other. `2` means "a finding"
here and "broken" there, and `lane list` is the one place both meet: it EXITS
under this contract while READING that one. A `lane list` run that finds a
broken predicate exits 2 because it FOUND something, not because it saw a 2.
"""

CLEAN = 0
FINDING = 2
COULD_NOT_VERIFY = 3

#: The three, in the order a report lists them. Named so a caller can assert
#: over the set rather than restating three literals.
ALL = (CLEAN, FINDING, COULD_NOT_VERIFY)

_WORDS = {CLEAN: "CLEAN", FINDING: "FINDING", COULD_NOT_VERIFY: "COULD NOT VERIFY"}


def word(code: int) -> str:
    """The human name of an exit code, for a report line."""
    return _WORDS.get(code, f"UNKNOWN({code})")


def worst(codes) -> int:
    """The code a run reports when several checks answered.

    COULD_NOT_VERIFY outranks FINDING, which outranks CLEAN.

    CLEAN losing to both is obvious. FINDING losing to COULD_NOT_VERIFY is
    the deliberate half, and it was decided rather than inherited: when a run
    both found something AND failed to classify something, the caller most at
    risk is the one that reads exit 2 as "here is the complete list of what
    is wrong" and acts on the list. Reporting 3 tells that caller the list is
    NOT complete; the findings themselves are still printed in full, so
    nothing is hidden by the code — only the promise of completeness is
    withdrawn, which is exactly what could-not-verify means.

    The ordering is explicit rather than `max()`: max would rank FINDING(2)
    below COULD_NOT_VERIFY(3) by accident of the numbers — the right answer
    for the wrong reason, and one that would silently invert the day the
    numbers changed.
    """
    rank = {CLEAN: 0, FINDING: 1, COULD_NOT_VERIFY: 2}
    out = CLEAN
    for c in codes:
        if rank.get(c, 2) > rank.get(out, 2):
            out = c
    return out
