import re
import subprocess
from dataclasses import dataclass
from itertools import chain, starmap
from pathlib import Path
from typing import Iterable, Iterator


@dataclass
class Package:
    name: str
    version: str

    def info(self):
        return f"{self.name}-{self.version}.dist-info"

    def toggle(self):
        return Package(self.name.replace("-", "_"), self.version)


PATTERN = re.compile(r"(?:[└├]──\s)?([a-zA-Z0-9_-]+)\sv([0-9.]+)$", re.MULTILINE)


def parse_packages(s: str) -> Iterator[Package]:
    tmp = PATTERN.findall(s)
    return starmap(Package, tmp)


def parse_dependencies(p: Path) -> Iterator[Package]:
    """Run at the root of the project to get all dependencies"""
    res = subprocess.run("uv tree --no-dev", capture_output=True, cwd=p).stdout.decode()
    return parse_packages(res)


@dataclass
class PackageInfo:
    pre: Path
    rel: str

    def join(self):
        return str(self.pre / self.rel)


SITE_PACKAGES = ".venv/Lib/site-packages"


def read_record(root: Path, package: Package) -> Iterable[PackageInfo]:
    root = root / SITE_PACKAGES
    pkg_path = root / package.info()
    if not pkg_path.exists():
        pkg_path = root / package.toggle().info()

    lines = (pkg_path / "RECORD").read_text().splitlines()
    for line in lines:
        path, *_ = line.split(",", 1)
        if path.startswith(".."):
            continue
        yield PackageInfo(root, path)


def get_files(root: Path, packages: Iterable[Package]) -> Iterable[PackageInfo]:
    for package in packages:
        yield from read_record(root, package)


def prepare_files(root: Path) -> tuple[Package, Iterable[PackageInfo]]:
    deps = parse_dependencies(root)
    this_package = next(deps)

    def get_this_files(root: Path):
        root = root / "src"
        for top, _, files in root.walk():
            if top.name == "__pycache__":
                continue
            for file in files:
                rel = (top / file).relative_to(root)
                yield PackageInfo(root, str(rel))

    return this_package, chain(get_this_files(root), get_files(root, deps))
