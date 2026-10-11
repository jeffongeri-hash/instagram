import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_archive_keeps_text_and_leaves_media(tmp_path):
    run = tmp_path / "run"
    for rel in [
        "plan.md", "profile.md", "guard.json", "now.txt", "raw/sources.csv",
        "raw/items/ig-A/caption.txt", "raw/items/ig-A/transcript.txt",
        "raw/items/ig-A/video.mp4", "raw/items/ig-A/frames/01.jpg",
        "notes/ig-A.md", "clusters/hook.md", "sandbox/x/f", ".chrome/c",
    ]:
        (run / rel).parent.mkdir(parents=True, exist_ok=True)
        (run / rel).write_text("x")
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy(REPO / "scripts" / "archive.py", repo / "scripts")

    subprocess.run([sys.executable, repo / "scripts" / "archive.py", run], check=True)

    got = sorted(str(p.relative_to(repo / "vault")) for p in (repo / "vault").rglob("*") if p.is_file())
    assert got == [
        "clusters/hook.md", "notes/ig-A.md", "plan.md", "profile.md",
        "raw/items/ig-A/caption.txt", "raw/items/ig-A/transcript.txt", "raw/sources.csv",
    ]
