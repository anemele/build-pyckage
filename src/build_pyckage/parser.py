import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Project:
    name: str
    version: str
    # description: str
    # authors: list
    dependencies: list = field(default_factory=list)
    scripts: dict = field(default_factory=dict)


def read_pyproject_toml_file(root: Path) -> Optional[Project]:
    py_toml = root / "pyproject.toml"
    if not py_toml.exists():
        return None
    with open(py_toml, "rb") as f:
        data = tomllib.load(f)
    project_data = data.get("project")
    if project_data is None:
        return None
    return Project(
        name=project_data["name"],
        version=project_data["version"],
        # description=project_data.get("description", ""),
        # authors=project_data.get("authors"),
        dependencies=project_data.get("dependencies"),
        scripts=project_data.get("scripts"),
    )
