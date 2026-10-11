import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def archive(tmp_path, run):
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO / "scripts" / "archive.py", repo / "scripts")
    subprocess.run([sys.executable, repo / "scripts" / "archive.py", run], check=True)
    return repo / "vault"


def make_run(run, files):
    for rel, text in files.items():
        (run / rel).parent.mkdir(parents=True, exist_ok=True)
        (run / rel).write_text(text)


def test_archive_keeps_text_and_leaves_media(tmp_path):
    run = tmp_path / "run"
    make_run(run, {rel: "x" for rel in [
        "plan.md", "profile.md", "guard.json", "now.txt", "raw/sources.csv",
        "raw/items/ig-A/caption.txt", "raw/items/ig-A/transcript.txt",
        "raw/items/ig-A/video.mp4", "raw/items/ig-A/frames/01.jpg",
        "notes/ig-A.md", "clusters/hook.md", "sandbox/x/f", ".chrome/c",
    ]})

    vault = archive(tmp_path, run)

    got = sorted(str(p.relative_to(vault)) for p in vault.rglob("*") if p.is_file())
    assert got == [
        "clusters/hook.md", "log.md", "notes/ig-A.md", "plan.md", "profile.md",
        "raw/items/ig-A/caption.txt", "raw/items/ig-A/transcript.txt", "raw/sources.csv",
    ]


def test_log_links_each_reel_and_its_creator(tmp_path):
    run = tmp_path / "run"
    make_run(run, {
        "raw/sources.csv": (
            "id,kind,url,origin,thread,owner,caption_chars,sponsored,file\n"
            "ig-C8xYz,reel,https://www.instagram.com/reel/C8xYz/,saved,,dev_jane,40,,links.txt\n"
        ),
        "notes/ig-C8xYz.md": (
            "verdict: keep\ntechnique: Run the tests | after every edit\ncluster: hook\n\nBy @dev_jane.\n"
        ),
        # Not in sources.csv: the creator comes from the note, the link from the id.
        "notes/ig-DaB12.md": "verdict: teaser\ntechnique: A/B test a page\n\nBy @growth.gal.\n",
    })

    log = (archive(tmp_path, run) / "log.md").read_text()

    assert "https://www.murphmaxxing.com/vault/saved-reels-to-claude-skill" in log
    assert ("| [@dev_jane](https://www.instagram.com/dev_jane/) "
            "| [instagram.com/reel/C8xYz/](https://www.instagram.com/reel/C8xYz/) | keep "
            "| [Run the tests \\| after every edit](notes/ig-C8xYz.md) |") in log
    assert ("| [@growth.gal](https://www.instagram.com/growth.gal/) "
            "| [instagram.com/p/DaB12/](https://www.instagram.com/p/DaB12/) | teaser "
            "| [A/B test a page](notes/ig-DaB12.md) |") in log


def test_log_keeps_the_first_logged_date(tmp_path):
    run = tmp_path / "run"
    make_run(run, {"notes/ig-A.md": "verdict: fluff\n\nBy @x.\n"})
    vault = archive(tmp_path, run)
    log = vault / "log.md"
    log.write_text(re.sub(r"^\| \d{4}-\d{2}-\d{2} \|", "| 2025-01-01 |", log.read_text(), flags=re.M))

    make_run(run, {"notes/ig-B.md": "verdict: keep\ntechnique: New one\n\nBy @y.\n"})
    rows = [line for line in (archive(tmp_path, run) / "log.md").read_text().splitlines()
            if "](notes/" in line]

    assert len(rows) == 2
    assert "notes/ig-B.md" in rows[0] and not rows[0].startswith("| 2025-01-01 |")
    assert rows[1].startswith("| 2025-01-01 |") and "notes/ig-A.md" in rows[1]
