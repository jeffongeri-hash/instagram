# instagram

Where my saved Instagram reels end up once they've been watched, transcribed
and sorted by the `saved-reels-to-skill` Claude Code skill. `vault/` holds the
ranked plan, a note per reel, one file per technique, and each reel's caption
and transcript. Videos and stills are never committed.

## Setup on a Mac (one time)

```bash
git clone https://github.com/jeffongeri-hash/instagram.git ~/instagram
cd ~/instagram
./scripts/setup.sh
```

`setup.sh` installs ffmpeg with Homebrew, then puts openai-whisper, yt-dlp and
Playwright into `./.venv`. The skill plays reels in Google Chrome, so install
it if you don't have it: `brew install --cask google-chrome`.

If `/saved-reels-to-skill` isn't already in Claude Code, install the skill:

```bash
mkdir -p ~/.claude/skills
unzip ~/Downloads/saved-reels-to-skill.skill -d ~/.claude/skills
```

## Each run

```bash
cd ~/instagram
source .venv/bin/activate
claude
```

Then send:

```
/saved-reels-to-skill My Instagram username is jefneyongeri. Make the plan for this repo, and tell me what fits my other projects too. Skip my own posts, start the board so I can watch, and show me the ranked plan before you change anything.
```

- The board is at http://localhost:4321.
- Log in to Instagram yourself in the Chrome window it opens. Instagram's
  terms don't allow automated access; it runs at normal viewing speed.
- The skill works in `~/reel-vault`. Nothing in your projects changes until
  you approve items from the plan.

When the plan is done, copy the keepers into this repo and commit:

```bash
python3 scripts/archive.py
git add vault && git commit -m "Archive saved reels run"
```

The next run only watches new saves; earlier notes carry over in `~/reel-vault`.

## Cloud sessions

`.claude/hooks/session-start.sh` runs `scripts/setup.sh` at the start of every
Claude Code cloud session. `python3 -m pytest tests` checks the tools and the
archive script.
