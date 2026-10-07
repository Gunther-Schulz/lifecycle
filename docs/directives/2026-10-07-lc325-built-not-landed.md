# lc-325 — built, not landed (2026-10-07)

Wave D lane D1 built booking-time write-set resolution under the desk
ruling "a path whose PARENT DIRECTORY is not tracked does not book READY"
and stopped: with it applied the suite shows 66 failures in 13 modules,
every opened one an existing booking naming `tools/<x>` in a scratch repo
that tracks no `tools/`. That is evidence about the ruling: an entry that
creates a file in a directory it also creates is an ordinary booking, and
a door refusing it fires on honest work.

For the pickup: keep the resolution and the "read as a file the entry
CREATES" line; where no parent directory is tracked, STATE it (creates
the directory too) instead of changing the grade. An explicit
`--grade READY` over an unresolved path is a second, unbuilt half.

The patch applies on the lane commit `edb4d2e` (main carries it as the
lc-322 change).

```diff
diff --git a/plugin/cli/lifecycle_core/refusals.py b/plugin/cli/lifecycle_core/refusals.py
index 2421feb..0ba1923 100644
--- a/plugin/cli/lifecycle_core/refusals.py
+++ b/plugin/cli/lifecycle_core/refusals.py
@@ -1459,7 +1459,7 @@ GOOD_ADD = [
     "item", "add",
     "--requirement", "the serving config is read from defaults — docs/x.md",
     "--goal", "verify",
-    "--write-set", "tools/replay.mjs",
+    "--write-set", "replay.mjs",
     "--done-criterion", "the gate reads what is serving",
     # MARKED, since lc-167: the shared plant books a real item through the
     # real door, so it carries what every real booking now carries. `none
diff --git a/plugin/cli/lifecycle_core/verbs.py b/plugin/cli/lifecycle_core/verbs.py
index c8458b6..a92212d 100644
--- a/plugin/cli/lifecycle_core/verbs.py
+++ b/plugin/cli/lifecycle_core/verbs.py
@@ -965,6 +965,32 @@ def _collect_slots(args, ctx: Ctx, out):
                    ("requirement", "goal", "write-set", "done-criterion",
                     "evidence")) and slots["write-set"].upper() != "UNKNOWN"
 
+    # A PATH THAT NAMES NOTHING HERE IS NOT A FILLED SLOT EITHER (lc-325).
+    # The grade was decided on the slot's PRESENCE, so a misspelled directory
+    # booked READY — the grade that promises a fresh context can execute the
+    # entry — and the wave join then gave it a tidy lane of its own. Asked
+    # only where the answer can move the DERIVED grade: an incomplete entry
+    # is NEW already, and an explicit `--grade` is the desk's judgment, which
+    # this door has never graded for completeness (`item check` does).
+    lost = []
+    if complete and not args.grade:
+        lost, creates, tree_why = _write_set_resolution(ctx,
+                                                        slots["write-set"])
+        if tree_why:
+            out(f"COULD NOT VERIFY: {tree_why}, so whether the write-set "
+                f"({slots['write-set']!r}) names anything in this repo is "
+                "unknown. A complete entry is graded READY, and READY over a "
+                "path nobody resolved is the grade this door must not hand "
+                "out on a guess. Nothing was written.")
+            return None, exits.COULD_NOT_VERIFY
+        for path in creates:
+            out(f"write-set: {path!r} is not tracked here and is read as a "
+                "file this entry CREATES, because its parent directory is "
+                "tracked — that is how an entry says so; there is no slot "
+                "for it. A misspelled file name reads the same way, so check "
+                "the spelling if no new file was meant.")
+        complete = not lost
+
     if args.grade:
         grade = args.grade
         # THE ARM IS PART OF THE VOCABULARY, so the door admits it (D-3). A
@@ -1015,6 +1041,14 @@ def _collect_slots(args, ctx: Ctx, out):
                        if not slots[s]]
             if slots["write-set"].upper() == "UNKNOWN":
                 missing.append("write-set (UNKNOWN)")
+            if lost:
+                missing.append(
+                    "write-set (names nothing in this repo: "
+                    + ", ".join(repr(p) for p in lost)
+                    + " — not tracked, and under no tracked parent "
+                      "directory; an entry that CREATES a file names it "
+                      "under a directory that already exists, so this is a "
+                      "misspelling or a tree nothing has made yet)")
             out("FINDING [new_without_typed_blocker] slots are incomplete "
                 f"({', '.join(missing)}), so this item is NEW — and a NEW "
                 "item carries a TYPED blocker saying what it is waiting for: "
@@ -1044,6 +1078,56 @@ def _collect_slots(args, ctx: Ctx, out):
     return slots, exits.CLEAN
 
 
+def _write_set_resolution(ctx: Ctx, value: str):
+    """`(lost, creates, why-not)` for a write-set at BOOKING (lc-325).
+
+    `lost` are path entries naming nothing here; `creates` are entries read
+    as new files; `why-not` is git being unable to list the tree — the third
+    answer, never folded into "everything resolves".
+
+    WHICH SLOTS ARE ASKED is `items.classify_write_set`'s answer, not a
+    second reading of the slot: only one it calls path-valued has paths to
+    resolve. A venue, a `<path>@<repo>` boundary and prose are graded by
+    their own checks (`check_write_set_venues`, `item waves`) and are left
+    exactly as they were here.
+
+    THE PREDICATE IS THE PARENT DIRECTORY, by ruling (drain wave D): an
+    entry resolves when it is a tracked file or a tracked directory, and it
+    CREATES a file when the path does not exist while its parent directory
+    holds tracked files. A parent that is tracked nowhere is a misspelling
+    or a tree nothing has made, and the two read alike — so neither is READY.
+
+    STRICTER THAN THE WAVE JOIN, deliberately and visibly: `TrackedTree
+    .resolves` passes any path under a tracked TOP-LEVEL directory, which
+    is the right grain for "may this be joined" and too wide for "may this
+    be called READY" — `plugin/cli/lifecycle_cor/x.py` passes the first.
+    The tree itself is that module's (`items.tracked_tree`), asked once.
+
+    WHAT THIS STILL CANNOT SEE: a misspelled BASENAME under a real
+    directory. It is read as a new file, and the caller SAYS so at the
+    booking, which is where the author can still see the spelling.
+    """
+    bucket, paths, _why = items_mod.classify_write_set(value)
+    if bucket != items_mod.WAVE_PATHS:
+        return [], [], ""
+    tree, tree_why = items_mod.tracked_tree(ctx.repo)
+    if tree is None:
+        return [], [], tree_why
+    dirs = {""}
+    for f in tree.files:
+        parent = posixpath.dirname(f)
+        while parent and parent not in dirs:
+            dirs.add(parent)
+            parent = posixpath.dirname(parent)
+    lost, creates = [], []
+    for path in paths:
+        e = path.rstrip("/")
+        if e in tree.files or e in dirs:
+            continue
+        (creates if posixpath.dirname(e) in dirs else lost).append(path)
+    return lost, creates, ""
+
+
 #: How long the mint's PARSE check may take. `sh -n` reads a program and
 #: executes nothing, so it answers in milliseconds; the bound is here because
 #: an unbounded child on a write path turns a refusal into a hang. The RUN's
diff --git a/test/test_drain_d_d1.py b/test/test_drain_d_d1.py
index eb66853..bcef74a 100644
--- a/test/test_drain_d_d1.py
+++ b/test/test_drain_d_d1.py
@@ -323,5 +323,131 @@ class ACloseSpeaksForAnExternalBlocker(unittest.TestCase):
         self.assertIn("FINDING [blocked_in_done_home]", outp)
 
 
+# --- lc-325 -------------------------------------------------------------------
+#
+# `item add` DECIDED THE GRADE WITHOUT RESOLVING THE WRITE-SET. A slot reading
+# as paths was "filled", so a misspelled directory booked READY — the grade
+# that promises a fresh context can execute the entry — and the wave join
+# then handed that entry a tidy standalone lane.
+#
+# THE RULING (drain wave D): an entry says it CREATES a file by naming a path
+# that does not exist while its PARENT DIRECTORY is tracked. A path whose
+# parent directory is not tracked either is not graded READY.
+
+TRACKED = "plugin/cli/core/thing.py"
+ADD_ROW = "FINDING [new_without_typed_blocker]"
+
+
+def add_argv(write_set: str, *extra) -> list:
+    """`R.GOOD_ADD` with its write-set replaced — one slot differs."""
+    argv = list(R.GOOD_ADD)
+    argv[argv.index("--write-set") + 1] = write_set
+    return argv + ["--join", "new"] + list(extra)
+
+
+class AddResolvesTheWriteSetBeforeItGradesREADY(unittest.TestCase):
+
+    def _repo(self) -> Path:
+        r = R._Repo()
+        self.addCleanup(r.close)
+        target = r.dir / TRACKED
+        target.parent.mkdir(parents=True)
+        target.write_text("x = 1\n", encoding="utf-8")
+        git(r.dir, "add", "--", TRACKED)
+        git(r.dir, "commit", "-qm", "a tracked tree")
+        return r.dir
+
+    def _items(self, repo: Path) -> str:
+        return (repo / "ITEMS.md").read_text(encoding="utf-8")
+
+    # --- the red-first pair: one directory, spelled right and wrong -----------
+
+    def test_a_MISSPELLED_top_directory_is_not_graded_READY(self):
+        repo = self._repo()
+        before = self._items(repo)
+        code, outp = run(repo, *add_argv("plugni/cli/core/thing.py"))
+        self.assertEqual(code, exits.FINDING, outp)
+        self.assertIn(ADD_ROW, outp)
+        self.assertIn("plugni/cli/core/thing.py", outp)
+        self.assertEqual(self._items(repo), before, "refused, and written")
+
+    def test_a_MISSPELLED_inner_directory_is_not_graded_READY(self):
+        """The half the wave join cannot see: `plugin/` is tracked, so a
+        top-level test resolves this path."""
+        repo = self._repo()
+        before = self._items(repo)
+        code, outp = run(repo, *add_argv("plugin/cli/cor/thing.py"))
+        self.assertEqual(code, exits.FINDING, outp)
+        self.assertIn(ADD_ROW, outp)
+        self.assertIn("plugin/cli/cor/thing.py", outp)
+        self.assertEqual(self._items(repo), before, "refused, and written")
+
+    def test_CONTROL_the_same_path_SPELLED_RIGHT_books_READY(self):
+        repo = self._repo()
+        code, outp = run(repo, *add_argv(TRACKED))
+        self.assertEqual(code, exits.CLEAN, outp)
+        self.assertIn("[READY]", outp)
+
+    # --- the other answers ------------------------------------------------------
+
+    def test_one_unresolved_entry_demotes_a_slot_of_SEVERAL(self):
+        repo = self._repo()
+        code, outp = run(repo, *add_argv(f"{TRACKED},plugni/cli/x.py"))
+        self.assertEqual(code, exits.FINDING, outp)
+        self.assertIn(ADD_ROW, outp)
+        self.assertIn("plugni/cli/x.py", outp)
+
+    def test_an_unresolved_path_BEHIND_A_TYPED_BLOCKER_books_NEW(self):
+        """Not refused — an entry waiting on something may not know its
+        boundary yet. It is simply not READY."""
+        repo = self._repo()
+        code, outp = run(repo, *add_argv(
+            "plugni/cli/core/thing.py",
+            "--blocked-by", "external the tree is created upstream"))
+        self.assertEqual(code, exits.CLEAN, outp)
+        self.assertIn("[NEW]", outp)
+        self.assertNotIn("[READY]", outp)
+
+    def test_a_NEW_FILE_under_a_tracked_parent_books_READY_and_SAYS_SO(self):
+        """How an entry says it creates a file, stated at the booking."""
+        repo = self._repo()
+        code, outp = run(repo, *add_argv("plugin/cli/core/new_thing.py"))
+        self.assertEqual(code, exits.CLEAN, outp)
+        self.assertIn("[READY]", outp)
+        self.assertIn("plugin/cli/core/new_thing.py", outp)
+        self.assertIn("CREATES", outp)
+
+    def test_git_unable_to_list_the_tree_is_COULD_NOT_VERIFY(self):
+        from unittest import mock
+        repo = self._repo()
+        before = self._items(repo)
+        with mock.patch.object(R.items_mod, "tracked_tree",
+                               return_value=(None, "the listing failed")):
+            code, outp = run(repo, *add_argv(TRACKED))
+        self.assertEqual(code, exits.COULD_NOT_VERIFY, outp)
+        self.assertIn("the listing failed", outp)
+        self.assertEqual(self._items(repo), before)
+
+    # --- controls: what the grade must NOT start refusing ---------------------
+
+    def test_CONTROL_a_tracked_DIRECTORY_entry_books_READY(self):
+        repo = self._repo()
+        code, outp = run(repo, *add_argv("plugin/cli/core/"))
+        self.assertEqual(code, exits.CLEAN, outp)
+        self.assertIn("[READY]", outp)
+        self.assertNotIn("CREATES", outp)
+
+    def test_CONTROL_a_tracked_FILE_is_not_announced_as_created(self):
+        repo = self._repo()
+        code, outp = run(repo, *add_argv(TRACKED))
+        self.assertNotIn("CREATES", outp)
+
+    def test_CONTROL_a_VENUE_is_not_a_path_and_is_not_resolved(self):
+        repo = self._repo()
+        code, outp = run(repo, *add_argv("decision:who-seeds-the-carrier"))
+        self.assertEqual(code, exits.CLEAN, outp)
+        self.assertIn("[READY]", outp)
+
+
 if __name__ == "__main__":
     unittest.main()
```
