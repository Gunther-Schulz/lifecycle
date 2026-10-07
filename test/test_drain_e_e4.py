"""Drain wave E, lane E4 — what a roster row declares, and what the prover
proves (lc-327, lc-326, lc-178, lc-328, lc-74).

One class per item, in the lane's order. Each class states the arrangement
its red was taken under, because a red whose arrangement nobody wrote down is
a red nobody can re-take.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "plugin" / "cli"))


def _export(dst: Path, *, git: bool) -> None:
    """This tree's TRACKED files, copied to `dst` from the working tree.

    From the working tree rather than from HEAD, so the arm grades the code
    under test and not the last commit. `git=True` makes the copy a real
    checkout with one commit; the machine's hooks are kept out of it, as
    `refusals._Scratch` keeps them out of every row's scratch repo.
    """
    listed = subprocess.run(["git", "-C", str(REPO), "ls-files"],
                            capture_output=True, text=True)
    assert listed.returncode == 0, listed.stderr
    for rel in filter(None, listed.stdout.split("\n")):
        src = REPO / rel
        if not src.is_file():
            continue
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst / rel)
    if git:
        for argv in (["init", "-q", "-b", "main"],
                     ["config", "core.hooksPath", str(dst / ".nohooks")],
                     ["config", "user.email", "row@lifecycle.invalid"],
                     ["config", "user.name", "lane e4"],
                     ["add", "-A"], ["commit", "-qm", "export"]):
            done = subprocess.run(["git", "-C", str(dst)] + argv,
                                  capture_output=True, text=True)
            assert done.returncode == 0, (argv, done.stderr)


#: The production reach and the coverage check over it, exactly as
#: `roster.cmd_test` assembles them — run in a child so the package imported
#: is the EXPORT's and the cwd is the child's own.
_COVERAGE_CHILD = (
    "import sys\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "from lifecycle_core import roster, declaration as d\n"
    "res = d.read(roster.PACKAGE_REPO)\n"
    "reach = roster.reach_paths(repo=roster.PACKAGE_REPO,\n"
    "                           doc=res.declaration)\n"
    "buf = []\n"
    "code = roster.check_coverage(buf.append, reach=reach)\n"
    "print('REACH-COUNT', len(reach))\n"
    "print('CODE', code)\n"
    "print('\\n'.join(buf))\n"
)

_ONLY_THERE = "lane_e4_only_in_the_other_checkout"


class TheRosterReadsTheTreeItWasLaunchedFrom(unittest.TestCase):
    """lc-327: `--test` graded whatever checkout the process stood in.

    THE ARRANGEMENT IS THE ITEM'S OWN: this tree exported to a scratch
    directory, and the export's coverage pass run with the cwd inside a
    checkout that DIFFERS from it — the other checkout carries one emit site
    the export does not. Both sides of the pair come from one fixture: the
    same child, the same export, the cwd alone moved.

    THE THIRD CWD IS THE SILENT ONE. Standing in no checkout at all the reach
    came back EMPTY and the check printed CLEAN over zero files — a clean
    board over a population nothing opened. It is asserted beside the loud
    case because it is the direction nobody would have reported.
    """

    def _fixture(self, *, git: bool):
        export = Path(tempfile.mkdtemp(prefix="lane-e4-export-"))
        other = Path(tempfile.mkdtemp(prefix="lane-e4-other-"))
        nowhere = Path(tempfile.mkdtemp(prefix="lane-e4-nowhere-"))
        for d in (export, other, nowhere):
            self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        _export(export, git=git)
        _export(other, git=True)
        target = other / "plugin" / "cli" / "lifecycle_core" / "exits.py"
        target.write_text(
            target.read_text(encoding="utf-8")
            + "\n\ndef _planted(out):\n"
              f'    out("FINDING [{_ONLY_THERE}] planted")\n',
            encoding="utf-8")
        return export, other, nowhere

    def _coverage(self, export: Path, cwd: Path):
        done = subprocess.run(
            [sys.executable, "-c", _COVERAGE_CHILD,
             str(export / "plugin" / "cli")],
            cwd=str(cwd), capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr[-2000:])
        lines = done.stdout.split("\n")
        count = int(lines[0].split()[1])
        code = int(lines[1].split()[1])
        return count, code, done.stdout

    def _assert_cwd_is_not_an_input(self, *, git: bool):
        export, other, nowhere = self._fixture(git=git)
        home_count, home_code, home_out = self._coverage(export, export)
        self.assertGreater(
            home_count, 0,
            "the export's own reach is empty, so this arm has no reference "
            f"to compare the moved-cwd runs with:\n{home_out}")
        self.assertEqual(home_code, 0, home_out)

        count, code, out = self._coverage(export, other)
        self.assertNotIn(
            _ONLY_THERE, out,
            "the export's coverage pass reported an emit site that exists "
            "only in the checkout the process was STANDING in — it read "
            f"that tree's files, not its own:\n{out}")
        self.assertEqual((count, code), (home_count, home_code), out)

        count, code, out = self._coverage(export, nowhere)
        self.assertEqual(
            count, home_count,
            "standing in no checkout at all, the reach collapsed — and the "
            "check then reports CLEAN over files it never opened:\n" + out)
        self.assertEqual(code, home_code, out)

    def test_an_exported_tree_reads_its_own_files_from_another_checkout(self):
        self._assert_cwd_is_not_an_input(git=False)

    def test_the_same_holds_when_the_export_is_itself_a_git_checkout(self):
        """The item's own question: was a non-git export the whole cause?
        It was not — the defect is a repo-relative path resolved against the
        cwd, and git never enters it."""
        self._assert_cwd_is_not_an_input(git=True)


def _row(ident, **kw):
    """A constructed roster row whose arms answer a fixed pair.

    The arms pass the roster's own grading (plant FINDING and named, control
    CLEAN), so an arm driving `cmd_test` over it measures the READOUT under
    test and not a failing row.
    """
    from lifecycle_core import exits, refusals
    return refusals.Row(
        ident=ident,
        refusal=kw.pop("refusal", "a constructed row — this arm grades the "
                                  "roster's own readout, never a refusal"),
        firing_input="not a real input",
        expect=exits.FINDING,
        fire=kw.pop("fire", lambda: refusals.Fired(
            exits.FINDING, f"FINDING [{kw.get('finding_row') or ident}] x")),
        control=kw.pop("control", lambda: refusals.Fired(exits.CLEAN, "")),
        **kw)


def _run_readout(name, rows):
    """One roster readout over a SWAPPED roster: its printed text.

    `None` where this build has no such readout — asserted by the caller, so
    a missing mechanism is an assertion failure and not an AttributeError.
    """
    from unittest import mock
    from lifecycle_core import refusals, roster
    fn = getattr(roster, name, None)
    if fn is None:
        return None
    buf = []
    with mock.patch.object(refusals, "ROWS", list(rows)):
        fn(buf.append)
    return "\n".join(buf)


class EveryRosterRowDeclaresItsInputClass(unittest.TestCase):
    """lc-326: the class of input that fires a row is DECLARED and graded.

    THE DEFECT: a refusal whose text names malformed, unreadable or absent
    input could be proven on a well-formed plant alone, and nothing said so.
    A green pair proves the refusal fires on the input it was GIVEN.

    WHAT IS COMPUTABLE AND WHAT IS NOT. The class of a plant, and the classes
    a refusal's text names, are both DECLARED on the row — no predicate reads
    prose, because a word-presence test fires on text that merely discusses
    the word. What is computed is the comparison: per refusal, the classes
    named against the classes planted.
    """

    VOCABULARY = ("well-formed", "malformed", "unreadable", "absent")

    def test_the_vocabulary_is_closed_at_the_four_the_criterion_names(self):
        from lifecycle_core import refusals
        self.assertEqual(getattr(refusals, "INPUT_CLASSES", None),
                         self.VOCABULARY)

    def test_every_real_row_declares_a_class_from_the_vocabulary(self):
        from lifecycle_core import refusals
        bad = [(r.ident, getattr(r, "input_class", None))
               for r in refusals.ROWS
               if getattr(r, "input_class", None) not in self.VOCABULARY]
        self.assertEqual(
            bad, [],
            f"{len(bad)} of {len(refusals.ROWS)} roster row(s) declare no "
            "input class from the closed vocabulary. A row added without one "
            "takes the field's default, which is the UNDECLARED value: add "
            "`input_class=` beside its `ident=`.")

    def test_every_class_a_real_row_NAMES_is_in_the_vocabulary_too(self):
        from lifecycle_core import refusals
        bad = [(r.ident, c) for r in refusals.ROWS
               for c in getattr(r, "names_input", ())
               if c not in self.VOCABULARY]
        self.assertEqual(bad, [])

    def test_a_refusal_naming_a_class_no_plant_carries_is_reported_by_name(self):
        out = _run_readout("check_input_classes", [
            _row("reads_a_file", input_class="well-formed",
                 names_input=("unreadable",)),
            _row("quiet_neighbour", input_class="well-formed"),
        ])
        self.assertIsNotNone(out, "the roster has no input-class readout")
        named = [l for l in out.split("\n") if "UNPLANTED" in l]
        self.assertEqual(len(named), 1, out)
        self.assertIn("reads_a_file", named[0])
        self.assertIn("unreadable", named[0])
        self.assertNotIn("quiet_neighbour", "\n".join(named))

    def test_a_SIBLING_plant_of_that_class_silences_the_report(self):
        """The control, and the reason the comparison is per REFUSAL: two
        roster rows can prove two firing inputs of one refusal, so the class
        one row names may be planted by its sibling."""
        out = _run_readout("check_input_classes", [
            _row("reads_a_file", input_class="well-formed",
                 names_input=("unreadable",)),
            _row("reads_a_file_unreadable", finding_row="reads_a_file",
                 input_class="unreadable"),
        ])
        self.assertIsNotNone(out, "the roster has no input-class readout")
        self.assertNotIn("UNPLANTED", out)

    def test_an_UNCLASSED_row_is_named_and_never_counted_as_well_formed(self):
        """The field's default is the undeclared value. A row another lane
        adds without it must not read as a well-formed plant."""
        out = _run_readout("check_input_classes", [
            _row("classed", input_class="malformed"),
            _row("arrived_without_one"),
        ])
        self.assertIsNotNone(out, "the roster has no input-class readout")
        named = [l for l in out.split("\n") if "UNCLASSED" in l]
        self.assertEqual(len(named), 1, out)
        self.assertIn("arrived_without_one", named[0])
        self.assertNotIn("classed,", named[0])
        self.assertIn("well-formed: 0", out)

    def test_a_class_outside_the_vocabulary_is_named_as_such(self):
        out = _run_readout("check_input_classes", [
            _row("typo", input_class="mal-formed"),
        ])
        self.assertIsNotNone(out, "the roster has no input-class readout")
        self.assertIn("OUTSIDE THE VOCABULARY", out)
        self.assertIn("typo", out)

    def test_the_readout_rides_the_roster_run_and_moves_no_exit_code(self):
        """MUST NOT MOVE: reported by name is a READOUT. An unplanted class
        is a statement about what the roster has NOT proven, as the prover's
        unproven list is, and a roster of passing rows stays CLEAN."""
        from unittest import mock
        from lifecycle_core import exits, refusals, roster
        rows = [_row("reads_a_file", input_class="well-formed",
                     names_input=("unreadable",))]
        buf = []
        with mock.patch.object(refusals, "ROWS", rows), \
                mock.patch.object(roster, "check_coverage",
                                  lambda out, root=None, reach=None:
                                  exits.CLEAN), \
                mock.patch.object(roster, "check_routes",
                                  lambda out: exits.CLEAN):
            code = roster.cmd_test(buf.append)
        text = "\n".join(buf)
        self.assertIn("UNPLANTED", text,
                      "the roster run does not carry the readout")
        self.assertEqual(code, exits.CLEAN, text)

    def test_the_real_roster_names_exactly_the_refusals_it_leaves_unplanted(self):
        """The readout over the REAL rows, pinned to what was measured when
        the classes were declared. ONE refusal: `--retire-source`'s laws
        refusal names a laws file that is NOT THERE and is planted only on a
        declaration carrying no `laws` value. A refusal that starts naming a
        class it does not plant shows up here by name."""
        from lifecycle_core import refusals
        out = _run_readout("check_input_classes", refusals.ROWS)
        self.assertIsNotNone(out, "the roster has no input-class readout")
        lines = [l.split() for l in out.split("\n")]
        self.assertEqual(
            sorted(l[1] for l in lines if l[:1] == ["UNPLANTED"]),
            ["retire_source_laws_absent"], out)
        self.assertEqual([l for l in lines if l[:1] == ["UNCLASSED"]], [],
                         out)


class TheControlsThroughADoorAreListable(unittest.TestCase):
    """lc-178: a demand at a write door contaminates every control walking
    through it, and that population was found only by running the suite.

    THE INCIDENT IS THE FIXTURE. lc-169 put a derivability demand on booking
    a `decision` blocker and four neighbours' controls went red at once,
    because each proved its own row with a clean control that books one. The
    listing for that door must name those four, and must NOT name the rows
    whose control walks `item add` with no decision blocker — a listing that
    names every `item add` row, or none, discriminates nothing.

    THE DOOR IS READ OFF THE ARM, never restated beside it: an arm is data
    (`refusals.Call`) and its door is the argv it runs.
    """

    #: The four controls lc-169 contaminated, from the item's own criterion.
    INCIDENT = {"blocker_untyped", "blocker_unstorable",
                "parked_without_typed_blocker", "new_without_typed_blocker"}

    @staticmethod
    def _through(**kw):
        from lifecycle_core import roster
        fn = getattr(roster, "controls_through", None)
        return None if fn is None else fn(**kw)

    def test_the_decision_blocker_door_names_the_four_contaminated_controls(self):
        got = self._through(flag="--blocked-by", blocker="decision")
        self.assertIsNotNone(got, "the roster cannot list a door's controls")
        self.assertEqual(
            self.INCIDENT - set(got), set(),
            "the listing for the decision-blocker door leaves out a control "
            f"lc-169's demand contaminated. Listed: {sorted(got)}")

    def test_that_listing_is_not_every_control_through_item_add(self):
        """The discriminating half. `item add` is the widest door on the
        roster; the decision-blocker door is a small part of it."""
        narrow = self._through(flag="--blocked-by", blocker="decision")
        wide = self._through(verb="item add")
        self.assertIsNotNone(narrow, "the roster cannot list a door's controls")
        self.assertGreater(len(wide), len(narrow))
        self.assertIn("unknown_grade_write", wide)
        self.assertNotIn(
            "unknown_grade_write", narrow,
            "a control that books NO blocker was listed at the decision "
            "door — the listing is naming a verb, not a door")
        self.assertNotIn("blocker_predicate_broken", narrow,
                         "an EVIDENCE blocker's control was listed at the "
                         "decision door")

    def test_the_rows_listed_beyond_the_four_all_book_a_decision_blocker(self):
        """The world moved since lc-169: its own row and later ones also
        book a decision blocker in their control. Each extra name is checked
        at the argv it runs, so the listing is never wider than its door."""
        from lifecycle_core import refusals
        got = self._through(flag="--blocked-by", blocker="decision")
        self.assertIsNotNone(got, "the roster cannot list a door's controls")
        rows = {r.ident: r for r in refusals.ROWS}
        for ident in got:
            argv = rows[ident].control.argv
            value = argv[argv.index("--blocked-by") + 1]
            self.assertTrue(value.startswith("decision "), (ident, value))

    def test_an_arm_that_is_not_one_invocation_is_named_as_undeclared(self):
        """Three answers: a control whose door could not be read is listed
        under its own heading, never dropped and never counted at a door."""
        out = _run_readout("check_doors", [
            _row("opaque_control"),
        ])
        self.assertIsNotNone(out, "the roster has no door listing")
        named = [l for l in out.split("\n") if "DOOR UNDECLARED" in l]
        self.assertEqual(len(named), 1, out)
        self.assertIn("opaque_control", named[0])

    def test_a_declared_arm_runs_exactly_the_argv_it_declares(self):
        """MUST NOT MOVE (2): the door is the roster's own structure. The
        argv a `Call` shows is the argv its runner receives."""
        from lifecycle_core import refusals
        seen = []

        def runner(argv, **kw):
            seen.append((list(argv), kw))
            return refusals.Fired(0, "")

        arm = refusals.Call(runner, ["item", "add", "--goal", "g"], items="X")
        arm()
        self.assertEqual(seen, [(arm.argv, {"items": "X"})])

    def test_the_listing_is_printed_by_the_rosters_list_and_runs_no_row(self):
        """MUST NOT MOVE (1): a READOUT. It rides `--test --list`, which
        executes nothing and exits CLEAN."""
        from lifecycle_core import exits, roster
        buf = []
        code = roster.cmd_test(buf.append, list_only=True)
        text = "\n".join(buf)
        self.assertEqual(code, exits.CLEAN)
        self.assertIn("DOORS (lc-178)", text,
                      "`--test --list` carries no door listing")
        self.assertIn("    control door:", text,
                      "no row's entry states the door its control walks")


if __name__ == "__main__":
    unittest.main()
