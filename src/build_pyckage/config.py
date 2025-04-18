from dataclasses import dataclass, field
from pathlib import Path

from mashumaro.mixins.toml import DataClassTOMLMixin


@dataclass
class Config(DataClassTOMLMixin):
    embed_python_path: Path = field(default_factory=Path)
    pyckage_path: Path = field(default_factory=Path)


CONFIG_FILE = Path.home() / ".build_pyckage_config"

if not CONFIG_FILE.exists():
    print("Complete the configuration file first:")
    print(f"    {CONFIG_FILE}")
    CONFIG_FILE.write_text(Config().to_toml())
    exit(1)


def load_config():
    config = Config.from_toml(CONFIG_FILE.read_text())
    config.embed_python_path.mkdir(parents=True, exist_ok=True)
    config.pyckage_path.mkdir(parents=True, exist_ok=True)
    return config
