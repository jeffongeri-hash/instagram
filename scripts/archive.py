#!/usr/bin/env python3
"""Copy what's worth keeping from a saved-reels-to-skill run folder into vault/.

Keeps the plan, your profile, notes, clusters, captions and transcripts.
Videos, stills, the sandbox and the Chrome profile stay behind.

Then rewrites vault/log.md: one row per reel that has a note, with a link to
the reel, a link to the creator who made it, the verdict and the technique.
A reel keeps the date it was first logged on every later run.

    python3 scripts/archive.py                  # from ~/reel-vault
    python3 scripts/archive.py "/path/to/run"   # from another run folder
"""
import csv
import re
import shutil
import sys
from datetime import date
from pathlib import Path

KEEP = [
    "plan.md",
    "profile.md",
    "notes/*.md",
    "clusters/*.md",
    "raw/sources.csv",
    "raw/skip.txt",
    "raw/items/*/caption.txt",
    "raw/items/*/transcript.txt",
    "raw/items/*/frames.txt",
    "raw/items/*/flags.txt",
]

GUIDE = "https://www.murphmaxxing.com/vault/saved-reels-to-claude-skill"
FIELD = re.compile(r"^(\w+): *(.*)$")
BY = re.compile(r"^By @([\w.]+)", re.M)
LOGGED = re.compile(r"^\| (\d{4}-\d{2}-\d{2}) \|.*\]\(notes/([^)]+)\.md\) \|$", re.M)


def note_fields(text):
    """The `key: value` lines at the top of a note, up to the first blank line."""
    fields = {}
    for line in text.splitlines():
        m = FIELD.match(line)
        if not m:
            break
        fields[m.group(1)] = m.group(2).strip()
    return fields


def cell(text):
    """Text that can't break out of a table cell or a link."""
    return " ".join(text.split()).replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def write_log(vault):
    log = vault / "log.md"
    logged = {}
    if log.exists():
        logged = {rid: day for day, rid in LOGGED.findall(log.read_text(encoding="utf-8"))}
    sources = {}
    if (vault / "raw" / "sources.csv").exists():
        with open(vault / "raw" / "sources.csv", encoding="utf-8", newline="") as f:
            sources = {r["id"]: r for r in csv.DictReader(f) if r.get("id")}

    today = date.today().isoformat()
    rows = []
    for note in sorted((vault / "notes").glob("*.md")):
        rid = note.stem
        text = note.read_text(encoding="utf-8")
        fields = note_fields(text)
        src = sources.get(rid, {})
        by = BY.search(text)
        owner = (src.get("owner") or (by.group(1) if by else "")).lstrip("@").rstrip(".")
        url = src.get("url") or (f"https://www.instagram.com/p/{rid[3:]}/" if rid.startswith("ig-") else "")
        creator = f"[@{owner}](https://www.instagram.com/{owner}/)" if owner else "unknown"
        reel = f"[{cell(url.split('://', 1)[-1].removeprefix('www.'))}]({url})" if url else rid
        technique = cell(fields.get("technique") or "no technique noted")
        day = logged.get(rid, today)
        rows.append((day, f"| {day} | {creator} | {reel} | {fields.get('verdict', '')} "
                          f"| [{technique}](notes/{rid}.md) |"))
    rows.sort(key=lambda r: r[0], reverse=True)

    log.write_text(
        "# Saved reels log\n\n"
        "Every saved reel and post that's been watched and read, newest first, with a\n"
        "link to the reel and to the creator who made it. The technique links to the\n"
        "full note.\n\n"
        f"Made with the saved-reels-to-skill workflow from {GUIDE}.\n"
        "`scripts/archive.py` rewrites this file after each run, so edit the notes, not\n"
        "this table.\n\n"
        "| Logged | Creator | Reel | Verdict | Technique |\n"
        "|---|---|---|---|---|\n"
        + "".join(line + "\n" for _, line in rows),
        encoding="utf-8",
    )
    return len(rows)


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "reel-vault").expanduser()
    dest = Path(__file__).resolve().parent.parent / "vault"
    if not src.is_dir():
        sys.exit(f"No run folder at {src}")
    copied = 0
    for pattern in KEEP:
        for f in src.glob(pattern):
            target = dest / f.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
            copied += 1
    print(f"Archived {copied} files from {src} to {dest}")
    print(f"Logged {write_log(dest)} reels in {dest / 'log.md'}")


if __name__ == "__main__":
    main()
