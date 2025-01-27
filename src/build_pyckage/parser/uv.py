from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional, Self

from mashumaro import field_options
from mashumaro.mixins.toml import DataClassTOMLMixin as _DataClassTOMLMixin

# type Item = dict[str, Any]


# @overload
# def to_snake_case(data: Item) -> Item: ...
# @overload
# def to_snake_case(data: list[Item]) -> list[Item]: ...
# def to_snake_case(data: Item | list[Item]) -> Item | list[Item]:
#     if isinstance(data, list):
#         return [to_snake_case(d) for d in data]

#     res = {}
#     for key, value in data.items():
#         if isinstance(value, dict):
#             res[key.replace("-", "_")] = to_snake_case(value)
#         elif isinstance(value, list):
#             res[key.replace("-", "_")] = [
#                 to_snake_case(v) if isinstance(v, dict) else v for v in value
#             ]
#         else:
#             res[key.replace("-", "_")] = value
#     return res


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
    # requires_python: str
    dependencies: list[str] = field(default_factory=list)
    scripts: dict[str, str] = field(default_factory=dict)


@dataclass
class PyProject(DataClassTOMLMixin):
    project: Project

    @classmethod
    def _toml_file(cls):
        return "pyproject.toml"


@dataclass
class Dependency:
    name: str


@dataclass
class Package:
    name: str
    version: str
    dependencies: list[Dependency] = field(default_factory=list)
    optional_dependencies: dict[str, list[Dependency]] = field(
        default_factory=dict, metadata=field_options(alias="optional-dependencies")
    )

    def to_snake_case(self):
        self.name = self.name.replace("-", "_")

    def dist_info(self) -> str:
        return f"{self.name}-{self.version}.dist-info"


@dataclass
class LockFile(DataClassTOMLMixin):
    package: list[Package] = field(default_factory=list)

    @classmethod
    def _toml_file(cls):
        return "uv.lock"

    def __post_init__(self):
        self.__mapping = {p.name: p for p in self.package}

    def __getitem__(self, name: str) -> Package:
        return self.__mapping[name]

    def get_deps(self, name: str) -> Iterator[Package]:
        yield self[name]

        for dep in self[name].dependencies:
            yield from self.get_deps(dep.name)

        for opt_deps in self[name].optional_dependencies.values():
            for dep in opt_deps:
                yield from self.get_deps(dep.name)
