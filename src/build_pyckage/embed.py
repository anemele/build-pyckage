import os
import re
import zipfile
from pathlib import Path
from typing import Optional

from .utils import ensure_path

EMBEDDED_PYTHON_DIR = Path(os.getenv("EMBEDDED_PYTHON_DIR", ""))
ensure_path(EMBEDDED_PYTHON_DIR, False)


def prepare_embedded_python(version: str) -> Optional[zipfile.ZipFile]:
    glob_res = EMBEDDED_PYTHON_DIR.glob(f"python-{version}*-embed-amd64.zip")
    glob_res = list(glob_res)

    if len(glob_res) == 0:
        print("not found embedded python. download first.")
        return None

    def get_semver(path: Path) -> tuple[int, int, int]:
        sr = re.search(r"python-(\d+)\.(\d+)\.(\d+)-embed-amd64.zip", path.name)
        if sr is None:
            return (0, 0, 0)
        major, minor, patch = map(int, sr.group())
        return (major, minor, patch)

    latest_path = max(glob_res, key=get_semver)
    return zipfile.ZipFile(latest_path, "r")
