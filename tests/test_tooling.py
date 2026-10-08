import shutil

import whisper


def test_cli_tools_on_path():
    for tool in ("ffmpeg", "yt-dlp", "whisper"):
        assert shutil.which(tool), f"{tool} not found on PATH"


def test_whisper_models_listed():
    assert "base" in whisper.available_models()


def test_browser_renders(page):
    page.set_content("<h1>ok</h1>")
    assert page.inner_text("h1") == "ok"
