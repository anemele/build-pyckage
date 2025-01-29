import re
import subprocess
from dataclasses import dataclass, field
from itertools import starmap
from pathlib import Path
from typing import Iterator, Optional, Self

from mashumaro.mixins.toml import DataClassTOMLMixin as _DataClassTOMLMixin


class DataClassTOMLMixin(_DataClassTOMLMixin):
    @classmethod
    def _toml_file(cls) -> str: ...

    @classmethod
    def from_file(cls, root: Path) -> Optional[Self]:
        """
        `root` is where the .toml file is located.
        """
        py_toml = root / cls._toml_file()
        if not py_toml.exists():
            return None

        return cls.from_toml(py_toml.read_text())


@dataclass
class Project:
    name: str
    version: str
    # description: str
    # authors: list
    # requires_python: str = field(metadata=field_options(alias="requires-python"))
    dependencies: list = field(default_factory=list)
    scripts: dict[str, str] = field(default_factory=dict)


@dataclass
class PyProject(DataClassTOMLMixin):
    project: Project

    @classmethod
    def _toml_file(cls):
        return "pyproject.toml"


@dataclass
class Package:
    name: str
    version: str

    def to_snake_case(self):
        self.name = self.name.replace("-", "_")

    def dist_info(self) -> str:
        return f"{self.name}-{self.version}.dist-info"


def get_project(root: Path) -> Optional[Project]:
    pyproject = PyProject.from_file(root)
    if pyproject is None:
        return None
    project = pyproject.project
    project.dependencies = list(parse_dependencies(root))
    return project


PATTERN = re.compile(r"(?:[└├]──\s)?([a-zA-Z0-9_-]+)\sv([0-9.]+)$", re.MULTILINE)


def parse_packages(s: str) -> Iterator[Package]:
    tmp = PATTERN.findall(s)
    return starmap(Package, tmp)


def parse_dependencies(root: Path) -> Iterator[Package]:
    """Run at the root of the project to get all dependencies"""
    res = subprocess.run(
        "uv tree --no-dev", capture_output=True, cwd=root
    ).stdout.decode()
    return parse_packages(res)
