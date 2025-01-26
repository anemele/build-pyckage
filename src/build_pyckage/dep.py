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


def parse_dependencies() -> Iterator[Package]:
    """Run at the root of the project to get all dependencies"""
    res = subprocess.run("uv tree --no-dev", capture_output=True).stdout.decode()
    return parse_packages(res)


@dataclass
class PackageInfo:
    pre: Path
    rel: str

    def join(self):
        return str(self.pre / self.rel)


SITE_PACKAGES = Path(".venv/Lib/site-packages")


def read_record(package: Package) -> Iterable[PackageInfo]:
    pkg_path = SITE_PACKAGES / str(package)
    if not pkg_path.exists():
        pkg_path = SITE_PACKAGES / package.toggle().info()

    lines = (pkg_path / "RECORD").read_text().splitlines()
    for line in lines:
        path, *_ = line.split(",", 1)
        if path.endswith(".py") and not path.startswith("../../Scripts/"):
            yield PackageInfo(SITE_PACKAGES, path)


def get_files(packages: Iterable[Package]) -> Iterable[PackageInfo]:
    for package in packages:
        yield from read_record(package)


def prepare_files() -> tuple[Package, Iterable[PackageInfo]]:
    deps = parse_dependencies()
    this_package = next(deps)

    def get_this_files():
        root = Path("src")
        for path in (root / this_package.toggle().name).glob("**/*.py"):
            yield PackageInfo(root, str(path.relative_to(root)))

    return this_package, chain(get_this_files(), get_files(deps))
