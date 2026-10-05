# Gap sweep, 2026-10-05 — what was found and deliberately NOT built

**Lifecycle desk, for the scorecard of the wan2gp desk's gap-sweep handoff.**
Each entry is state that changes without an act, or an exposure, that no
unprompted surface reports. Each was read as a NEW MECHANISM under the
2026-09-24 freeze by the driving desk (wan2gp-e3, 2026-10-05) and is
recorded here with its evidence instead of being built. What WAS built is in
the commits `41a8968`, `b97eb32`, `3a7a9e7`.

"Unprompted" means the five verbs the session-start hook runs (`item check`,
`kind list --digest`, `kind list --structure`, `item ready --head`, `item
ratio`) and `item statusline`.

| # | the gap | evidence | grade |
|---|---|---|---|
| 1 | A FIRED lane is named by nothing unprompted, under either `trigger-policy`. An arc deadline that has arrived is seen only by whoever runs `lane list`. | Observed on a scratch repo: `arc open` + `arc deadline` with a past date; none of the six unprompted surfaces names the arc or the lane. No site in `lifecycle_core` branches on `trigger-policy` (it is validated, printed, recorded), and no hook under dotfiles `claude/hooks` mentions `trigger-policy`, `advise` or `lane list` (zero hits; control: the same search finds the `ready` call). | observed |
| 2 | An item whose `evidence:` pointer names a file that does not exist is named by no surface, prompted or not. | Observed on scratch: `evidence: docs/gone.md:3-9`; all six unprompted surfaces and `audit`, `lane list`, `arc status`, `ledger check`, `kind moments` silent. The items kind declares exactly this as its staleness; `audit` prints "staleness check: NOT RUN". | observed |
| 3 | The ledger accepts two different answers to one question; the per-item verdict takes the LAST. | Observed on scratch: two `ledger add decision` lines, same question, answers "left" then "right" (second with `--join new`); `ledger check` CLEAN, no surface names it. LIVE INSTANCE the same day: lc-36's question has LEDGER:70, :185 and :190 bearing on it, and the head showed only :70's answer because only its question text equals the blocker. | observed |
| 4 | The session-start hook's timeout message names no cause. | From the hook's source (dotfiles `session-scan.py`): a verb exceeding `LIFECYCLE_TIMEOUT_S` (0.5 s) yields "did not run". Dotfiles' write boundary, not this repo's. The lifecycle side — the head pass can no longer exceed the budget because of a predicate — is `3a7a9e7`. | derived from source |
| 5 | `item close` (DONE) over a live `evidence`, `external` or `decision` blocker goes through with exit 0; only a live item-id blocker is refused. Dropping a target another live item is blocked on goes through silently at the drop; the dependent appears as `dangling_reference` at the next `item check`. | Observed: ten door runs on scratch. Reported, NOT graded a defect: a close ends the wait by design, and the drop's consequence is named one pass later. | observed |
| 6 | The real fire log holds lines for scratch repos that no longer exist. | 320 lines from another session on 2026-10-04 and 592 from this desk on 2026-10-05 (one harness run started without `XDG_STATE_HOME`; the harness now refuses before its first verb). Derived, not run: the audit and retire walks read exit events keyed on the repo path, so these enter no real repo's count; they add bulk to a 165 MB log. Left in place by the driving desk's ruling. | observed count, derived effect |

Not on this list because it is surfaced: a kind's moments going stale (the
`kind list --structure` line prints "STALE, N day(s)" unprompted).
