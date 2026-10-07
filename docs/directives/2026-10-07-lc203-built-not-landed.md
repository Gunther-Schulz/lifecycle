# lc-203 — built, not landed (2026-10-07)

Wave C lane C4 built the conservation check for the reading verbs and
shelved it: with it applied the suite shows 22 failures, each an existing
fixture whose own head counters do not balance (roster rows
capture_dominated, net_growth, goal_query_undeclared; test_items 9,
test_verbs 4, test_waves 4, test_schema 1, test_init 1). Landing it needs
those fixtures repaired first. The item carries the measurement.

The patch applies on the lane commit `2313550` (main carries that commit
as the lc-185 change). Consumer: the lane that picks up lc-203.

```diff
diff --git a/plugin/cli/lifecycle_core/cli.py b/plugin/cli/lifecycle_core/cli.py
index fc42787..8d7e10c 100644
--- a/plugin/cli/lifecycle_core/cli.py
+++ b/plugin/cli/lifecycle_core/cli.py
@@ -370,6 +370,45 @@ def cmd_item_check(args, out, err=None) -> int:
     return code
 
 
+def _carrier_extent(ctx, out, *, quiet_when_clean: bool = False) -> int:
+    """THE EXTENT OF WHAT A READING VERB READ (lc-203) — conservation, run
+    where the carrier is CONSUMED rather than in one verb.
+
+    A carrier cut before a `## <id>` heading parses perfectly: every verb
+    that reads it reports the bodies that are left, and only the identity
+    `items + done == baseline + added − compacted` knows one is missing.
+    That identity ran in `item check` alone, so `item ready` called a
+    truncated carrier's survivor schedulable at exit 0.
+
+    ONE BODY BEHIND ONE CONTRACT: this is `item check`'s own closing pair,
+    `items.conservation` rendered by `items.report_conservation`, called and
+    never restated. The row names it prints (`conservation_short`,
+    `conservation_surplus`) are therefore the registered ones.
+
+    HERE AND NOT IN `verbs._load`, which the booking named: `_load` reads ONE
+    home and the identity needs both, so the shared path that holds the
+    question is the dispatch each reading verb leaves through.
+
+    `quiet_when_clean` is for a verb that prints DATA and no population
+    (`item slots`, whose `--json` form is parsed): it runs the check and
+    speaks only when the identity is not clean, so a balanced carrier's
+    output stays the bytes its readers expect.
+    """
+    items_parsed, why = verbs._load(ctx.items_path)
+    if items_parsed is None:
+        out(f"COULD NOT VERIFY: conservation — {why}")
+        return exits.COULD_NOT_VERIFY
+    done_parsed, done_why = verbs._load(ctx.done_path)
+    lines = []
+    code = items_mod.report_conservation(
+        items_mod.conservation(items_parsed, done_parsed, done_why),
+        lines.append)
+    if code != exits.CLEAN or not quiet_when_clean:
+        for line in lines:
+            out(line)
+    return code
+
+
 def cmd_item_repair(args, out) -> int:
     """`item repair --shape` (lc-129) — the MECHANICAL half of hand damage.
 
@@ -499,10 +538,13 @@ def cmd_item_waves(args, out) -> int:
     # same one `item check` grades write-sets by. A listing that failed is
     # handed down as `None` with its reason and never as an empty tree.
     tree, tree_why = items_mod.tracked_tree(ctx.repo)
-    return exits.worst([code, items_mod.report_waves(
+    code = exits.worst([code, items_mod.report_waves(
         schedulable, out, ready_n=len(ready), live_n=len(parsed.items),
         excluded=excluded, grouped=getattr(args, "grouped", False),
         tree=tree, tree_why=tree_why)])
+    # "scanned: N live item(s)" is a population, and a plan over a carrier
+    # missing a body is a plan over a set nobody saw whole (lc-203).
+    return exits.worst([code, _carrier_extent(ctx, out)])
 
 
 class _Parser(argparse.ArgumentParser):
@@ -1458,6 +1500,10 @@ def main(argv=None) -> int:
             ctx, code = _context(args, out)
             if ctx is not None:
                 code = items_mod.cmd_item_slots(args, out, ctx.items_path)
+                # lc-203. Quiet over a balanced carrier: this verb prints
+                # one block's DATA, and its `--json` form is parsed.
+                code = exits.worst([code, _carrier_extent(
+                    ctx, out, quiet_when_clean=True)])
         elif args.item_action == "waves":
             code = cmd_item_waves(args, out)
         elif args.item_action in ("add", "amend", "promote", "ready", "park",
@@ -1680,18 +1726,32 @@ def _carrier_verb(args, out) -> int:
                 "AND a filter over many. Drop the id for the goal's listing, "
                 "or drop --goal for that one item.")
             return exits.COULD_NOT_VERIFY
+        # THE READING VERBS LEAVE THROUGH `_carrier_extent` (lc-203): each
+        # reports a population, and none of them knew whether it was the
+        # whole one. `item statusline` below is NOT among them — see the
+        # note at its branch.
         if getattr(args, "head", False) or getattr(args, "goal", None):
-            return verbs.cmd_item_head(args, out, ctx)
+            return exits.worst([verbs.cmd_item_head(args, out, ctx),
+                                _carrier_extent(ctx, out)])
         if not args.ident:
             out("COULD NOT VERIFY: `item ready` needs an item id, or `--head` "
                 "for the whole derived head. Refusing rather than picking one "
                 "for you: an id-less run that printed the head anyway would "
                 "answer a question nobody asked.")
             return exits.COULD_NOT_VERIFY
-        return verbs.cmd_item_ready(args, out, ctx)
+        return exits.worst([verbs.cmd_item_ready(args, out, ctx),
+                            _carrier_extent(ctx, out)])
     if args.item_action == "ratio":
-        return verbs.cmd_item_ratio(args, out, ctx)
+        return exits.worst([verbs.cmd_item_ratio(args, out, ctx),
+                            _carrier_extent(ctx, out)])
     if args.item_action == "statusline":
+        # NO EXTENT HERE, AND THAT IS A STATED LIMIT, NOT AN OVERSIGHT
+        # (lc-203). This verb is ONE line, rendered on every prompt in every
+        # declaring repo, and its own docstring rules out a full parse of
+        # either home at that cost. So it still prints `1R.0P` over a
+        # carrier missing a body. Its line is a syntactic approximation by
+        # its own account; `item ready --head` is the answer that now says
+        # whether the carrier was whole.
         return verbs.cmd_item_statusline(args, out, ctx)
     if args.item_action == "park":
         return verbs.cmd_item_park(args, out, ctx)
diff --git a/test/test_drain_c_c4.py b/test/test_drain_c_c4.py
index fb1c005..19a027c 100644
--- a/test/test_drain_c_c4.py
+++ b/test/test_drain_c_c4.py
@@ -299,5 +299,114 @@ class TheJoinResolvesItsPaths(Base):
         self.assertEqual((bucket, paths), (items.WAVE_PATHS, [TYPO]))
 
 
+# --- lc-203 -------------------------------------------------------------------
+
+#: A REAL two-item carrier, and the same bytes CUT IMMEDIATELY BEFORE THE
+#: SECOND HEADING — the shape `atomic.py`'s docstring warns about. The head
+#: still says two bodies were admitted; one is in the file.
+WHOLE = carrier([block("xx-1", "docs/readme.md"),
+                 block("xx-2", "test/absence-scan.test.mjs")])
+CUT = WHOLE[:WHOLE.index("## xx-2")]
+
+#: The reading verbs that print a POPULATION — a count of what they read.
+COUNTING_VERBS = (
+    ("item", "ready", "--head"),
+    ("item", "ready", "xx-1"),
+    ("item", "waves"),
+    ("item", "ratio"),
+)
+
+
+class EveryReadingVerbStatesItsExtent(Base):
+    """lc-203 — conservation was the only instrument that saw a truncated
+    carrier, and it ran in exactly one verb.
+
+    Each reading verb is run over the cut carrier and must name the missing
+    body itself; over the whole one it must say the extent it checked.
+    """
+
+    def _repo_text(self, text):
+        repo = self._repo([])
+        (repo.dir / "ITEMS.md").write_text(text, encoding="utf-8")
+        subprocess.run(["git", "commit", "-qam", "the carrier under test"],
+                       cwd=str(repo.dir), capture_output=True, text=True)
+        return repo
+
+    def test_the_fixture_is_the_truncation_the_item_names(self):
+        self.assertIn("baseline: 2", CUT)
+        self.assertIn("## xx-1", CUT)
+        self.assertNotIn("## xx-2", CUT)
+
+    def test_each_counting_verb_NAMES_the_missing_body(self):
+        for argv in COUNTING_VERBS:
+            with self.subTest(verb=" ".join(argv)):
+                with self._repo_text(CUT) as r:
+                    code, out = self._run(r, *argv)
+                    self.assertIn("FINDING [conservation_short]", out)
+                    self.assertNotEqual(code, exits.CLEAN, out)
+
+    def test_a_verb_that_was_CLEAN_over_the_cut_carrier_is_now_a_FINDING(self):
+        """`ready` answered exit 0 — schedulable — over a carrier missing a
+        body. The code is the part a scripted caller reads."""
+        for argv in (("item", "ready", "--head"), ("item", "ready", "xx-1"),
+                     ("item", "waves")):
+            with self.subTest(verb=" ".join(argv)):
+                with self._repo_text(CUT) as r:
+                    code, out = self._run(r, *argv)
+                    self.assertEqual(code, exits.FINDING, out)
+
+    def test_NO_counting_verb_prints_a_count_with_no_extent_statement(self):
+        """The assertion on what must NOT appear: a population reported
+        with nothing said about whether it is the whole population. Over the
+        WHOLE carrier, so this is the arm that catches the check DEGRADING —
+        a verb that stopped running it would still pass the cut-carrier arm
+        of nothing but its own silence."""
+        for argv in COUNTING_VERBS:
+            with self.subTest(verb=" ".join(argv)):
+                with self._repo_text(WHOLE) as r:
+                    _code, out = self._run(r, *argv)
+                    extent = [ln for ln in out.splitlines()
+                              if ln.startswith("conservation: items 2 + done 0")]
+                    self.assertEqual(len(extent), 1, out)
+                    self.assertIn("conservation: CLEAN", out)
+
+    def test_the_whole_carrier_keeps_the_code_each_verb_gave(self):
+        """MUST-NOT-MOVE: a balanced carrier changes no verb's answer."""
+        for argv, want in ((("item", "ready", "--head"), exits.CLEAN),
+                           (("item", "ready", "xx-1"), exits.CLEAN),
+                           (("item", "waves"), exits.CLEAN)):
+            with self.subTest(verb=" ".join(argv)):
+                with self._repo_text(WHOLE) as r:
+                    code, out = self._run(r, *argv)
+                    self.assertEqual(code, want, out)
+
+    def test_slots_names_the_missing_body_too(self):
+        with self._repo_text(CUT) as r:
+            code, out = self._run(r, "item", "slots", "xx-1")
+            self.assertIn("FINDING [conservation_short]", out)
+            self.assertEqual(code, exits.FINDING, out)
+
+    def test_slots_over_a_whole_carrier_is_the_DATA_and_nothing_else(self):
+        """`item slots` is the pickup instrument and its `--json` form is
+        parsed. It prints no population, so over a balanced carrier it adds
+        no line — a second line there would break every reader of it."""
+        import json
+        with self._repo_text(WHOLE) as r:
+            code, out = self._run(r, "item", "slots", "xx-1", "--json")
+            self.assertEqual(code, exits.CLEAN, out)
+            self.assertEqual(json.loads(out)["ident"], "xx-1")
+            code, out = self._run(r, "item", "slots", "xx-1")
+            self.assertNotIn("conservation", out)
+            self.assertEqual(out.splitlines()[0], "grade: READY")
+
+    def test_a_head_that_cannot_be_computed_is_COULD_NOT_VERIFY(self):
+        """The third answer travels with the check: no baseline, no
+        identity, and `ready` must not call that carrier clean."""
+        with self._repo_text(WHOLE.replace("baseline: 2\n", "", 1)) as r:
+            code, out = self._run(r, "item", "ready", "xx-1")
+            self.assertIn("COULD NOT VERIFY: conservation", out)
+            self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
+
+
 if __name__ == "__main__":
     unittest.main()
```
