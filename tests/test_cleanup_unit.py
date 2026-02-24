from pathlib import Path
from app.core.cleanup import safe_cleanup


def test_safe_cleanup_deletes_file(tmp_path):
    file_path = tmp_path / "temp.txt"
    file_path.write_text("data")

    assert file_path.exists()

    safe_cleanup(files=[file_path])

    assert not file_path.exists()


def test_safe_cleanup_runs_callback():
    called = {"flag": False}

    def callback():
        called["flag"] = True

    safe_cleanup(callbacks=[callback])

    assert called["flag"] is True