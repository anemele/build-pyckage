from build_pyckage.parser import Package, _parse_packages


def test_parse_packages():
    s = """\
build-pyckage v0.1.0
├── requests v2.32.3
│   ├── certifi v2024.12.14
│   ├── charset-normalizer v3.4.1
│   ├── idna v3.10
│   └── urllib3 v2.3.0
└── returns v0.24.0
    └── typing-extensions v4.12.2
"""
    packages = list(_parse_packages(s))
    assert len(packages) == 8
    assert packages == [
        Package(name="build-pyckage", version="0.1.0"),
        Package(name="requests", version="2.32.3"),
        Package(name="certifi", version="2024.12.14"),
        Package(name="charset-normalizer", version="3.4.1"),
        Package(name="idna", version="3.10"),
        Package(name="urllib3", version="2.3.0"),
        Package(name="returns", version="0.24.0"),
        Package(name="typing-extensions", version="4.12.2"),
    ]
