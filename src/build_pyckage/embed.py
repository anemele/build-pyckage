import os
import os.path as osp
import zipfile

import requests
from semver import Version as SemVer

EMBEDDED_PYTHON_DIR = os.getenv("EMBEDDED_PYTHON_DIR", "")
if not osp.exists(EMBEDDED_PYTHON_DIR):
    os.mkdir(EMBEDDED_PYTHON_DIR)


def get_embedded_python(version: SemVer) -> str:
    filepath = osp.join(EMBEDDED_PYTHON_DIR, f"python-{version}-embed-amd64.zip")
    return filepath


def get_embedded_python_url(version: SemVer) -> str:
    return (
        "https://www.python.org/ftp/python/"
        + f"{version}/python-{version}-embed-amd64.zip"
    )


def prepare_embedded_python(version: SemVer) -> zipfile.ZipFile:
    filepath = get_embedded_python(version)

    if osp.exists(filepath):
        return zipfile.ZipFile(filepath)

    url = get_embedded_python_url(version)
    res = requests.get(url, stream=True)
    res.raise_for_status()
    with open(filepath, "rwb") as f:
        for chunk in res.iter_content(chunk_size=8192):
            f.write(chunk)
        f.seek(0)
        return zipfile.ZipFile(f)
