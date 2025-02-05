import re
import zipfile
from pathlib import Path
from typing import Optional

from .config import Config


def prepare_embedded_python(version: str, config: Config) -> Optional[zipfile.ZipFile]:
    glob_res = config.embed_python_path.glob(f"python-{version}*-embed-amd64.zip")
    glob_res = list(glob_res)

    if len(glob_res) == 0:
        print("not found embedded python. download first.")
        return None

    def get_semver(path: Path) -> tuple[int, int, int]:
        sr = re.search(r"python-(\d+)\.(\d+)\.(\d+)-embed-amd64.zip", path.name)
        if sr is None:
            return (0, 0, 0)
        return (int(sr.group(1)), int(sr.group(2)), int(sr.group(3)))

    latest_path = max(glob_res, key=get_semver)
    return zipfile.ZipFile(latest_path, "r")
