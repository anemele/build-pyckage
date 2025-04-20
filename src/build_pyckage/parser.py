import logging
import re
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Self, Sequence

from mashumaro.mixins.toml import DataClassTOMLMixin

__all__ = [
    "Project",
    "get_project",
]

logger = logging.getLogger(__name__)


@dataclass
class Project:
    name: str
    version: str
    # type of dependency is Package, deserialized value from pyproject.toml is str,
    # so here omit the type hint
    dependencies: Sequence = field(default_factory=list)
    scripts: Mapping[str, str] = field(default_factory=dict)


@dataclass
class PyProject(DataClassTOMLMixin):
    project: Project

    @classmethod
    def from_file(cls, root: Path) -> Optional[Self]:
        """
        `root` is where the pyproject.toml file is located.
        """
        py_toml = root / "pyproject.toml"
        if not py_toml.exists():
            return None

        return cls.from_toml(py_toml.read_text())


UV_PTN = re.compile(r"(?:[└├]──\s)([\w_-]+)", re.MULTILINE)


def _parse_dependencies(s: str) -> Sequence[str]:
    deps = UV_PTN.findall(s)
    return deps


def get_project(root: Path) -> Optional[Project]:
    pyproject = PyProject.from_file(root)
    if pyproject is None:
        return None
    """Run at the root of the project to get all dependencies"""
    res = subprocess.run(
        "uv tree --no-dev", capture_output=True, cwd=root
    ).stdout.decode()
    deps = _parse_dependencies(res)
    deps = tuple(set(deps))
    logger.debug(f"Dependencies: {deps}")
    project = pyproject.project
    project.dependencies = deps
    return project
