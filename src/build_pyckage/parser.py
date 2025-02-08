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

    def __hash__(self) -> int:
        name = self.name.lower().replace("_", "-")
        return hash((name, self.version))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Package):
            return False
        if self.version != other.version:
            return False
        self_name = self.name.lower().replace("_", "-")
        other_name = other.name.lower().replace("_", "-")
        return self_name == other_name


def get_project(root: Path) -> Optional[Project]:
    pyproject = PyProject.from_file(root)
    if pyproject is None:
        return None
    project = pyproject.project
    project.dependencies = list(parse_dependencies(root))
    return project


UV_PTN = re.compile(r"(?:[└├]──\s)?([\w_-]+)\sv([\w\.]+)", re.MULTILINE)


def _parse_packages(s: str) -> Iterator[Package]:
    tmp = UV_PTN.findall(s)
    return starmap(Package, tmp)


def parse_dependencies(root: Path) -> Iterator[Package]:
    """Run at the root of the project to get all dependencies"""
    res = subprocess.run(
        "uv tree --no-dev", capture_output=True, cwd=root
    ).stdout.decode()
    return _parse_packages(res)
