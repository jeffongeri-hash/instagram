#!/usr/bin/env python3
"""Copy what's worth keeping from a saved-reels-to-skill run folder into vault/.

Keeps the plan, your profile, notes, clusters, captions and transcripts.
Videos, stills, the sandbox and the Chrome profile stay behind.

    python3 scripts/archive.py                  # from ~/reel-vault
    python3 scripts/archive.py "/path/to/run"   # from another run folder
"""
import shutil
import sys
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


if __name__ == "__main__":
    main()
