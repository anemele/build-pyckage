from pathlib import Path


def ensure_path(path: Path, gitignore: bool = True):
    if not path.exists():
        path.mkdir()
    if gitignore:
        if not (ignorefile := path / ".gitignore").exists():
            ignorefile.write_text("*")
