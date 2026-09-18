"""The ONE atomic write path for every carrier this tool owns (lc-159).

WHY THIS FILE EXISTS. Until it did, all 16 carrier writes were
`Path.write_text`, which opens with "w" — truncate, then write. An interrupt
between the truncate and the flush (a crash, a kill, a full disk, a session
ended mid-verb) leaves the carrier SHORT. That alone would be ordinary data
loss; what makes it the worst instance of the class lc-157 is about is that a
short carrier DOES NOT READ AS DAMAGED. The parse contract keys on the
`schema:` line at the head, so a file cut anywhere below it returns
`refused=False` with fewer items and NO problems, and every consumer
downstream gets a confident, clean, WRONG answer over a smaller carrier. The
tool's deliberate third answer — unknown, refuse — is routed around entirely.

MEASURED before this file was written (2026-09-18, this repo's own ITEMS.md,
223483 bytes, 71 items): truncated to 400 bytes the parse returns
`refused=False`, 1 item, 0 problems; to 2000 bytes, 2 items, 0 problems; to
20000 bytes, 8 items, 0 problems. Zero problems at every block-boundary cut.
Found from OUTSIDE this repo by a peer session that measured the downstream
consequence on another repo's capture-retention guard: full carrier ->
('cited', 'cs-42'); first 2000 bytes -> ('not-cited', None), exit 0, DELETE —
a guard whose whole purpose is protecting irreplaceable captures reporting a
clean run while destroying one.

WHAT ATOMICITY BUYS AND WHAT IT DOES NOT. `os.replace` onto a path on the
SAME filesystem is atomic: a concurrent reader sees the old file or the new
one, never a half. That closes the write path. It does NOT protect a carrier
against an editor, a partial `cp`, or a git operation that leaves it short —
for those, truncation must be made LOUD at the READ, which is lc-159's second
half and a carrier-format question, not this file's.

MODE IS CARRIED DELIBERATELY. `declaration.py`'s own comment records that
`os.replace` carries the SOURCE's mode onto the target, so a fresh temp file
would silently reset a carrier's permissions to whatever the umask gives.
Where the target exists, its mode is copied onto the temp file before the
replace, so the mode a repo chose survives its next write.
"""

import os
import stat
from pathlib import Path


def write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Replace `path`'s contents with `text`, atomically.

    The temp file is a SIBLING, never a system temp dir: `os.replace` is only
    atomic within one filesystem, and `/tmp` is routinely a different one, so
    a temp-dir implementation would silently degrade to a copy — a truncating
    write again, wearing an atomic write's name.
    """
    path = Path(path)
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    try:
        with open(tmp, "w", encoding=encoding) as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        if path.exists():
            os.chmod(tmp, stat.S_IMODE(path.stat().st_mode))
        os.replace(tmp, path)
        # Durability of the RENAME itself, not of the bytes: without this the
        # directory entry can still be lost to a power failure that the file's
        # own fsync survived. Best-effort — some filesystems refuse a
        # directory fsync, and failing the carrier write over that would trade
        # a rare durability gap for a common outage.
        try:
            dfd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except OSError:
            pass
    except BaseException:
        # BaseException, not Exception: a KeyboardInterrupt between the open
        # and the replace is exactly the interrupt this file exists for, and
        # it must not leave the sibling temp behind for the next reader to
        # find. The target is untouched either way — that is the whole point.
        try:
            tmp.unlink()
        except OSError:
            pass
        raise
