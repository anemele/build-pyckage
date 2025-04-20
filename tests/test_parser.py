from build_pyckage.parser import _parse_dependencies


def test_parse_dependencies():
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
    packages = _parse_dependencies(s)
    assert len(packages) == 7
    assert packages == [
        "requests",
        "certifi",
        "charset-normalizer",
        "idna",
        "urllib3",
        "returns",
        "typing-extensions",
    ]

    s = """\
build-pyckage v0.1.5
└── mashumaro[toml] v3.15
    ├── typing-extensions v4.12.2
    └── tomli-w v1.2.0 (extra: toml)
"""
    packages = _parse_dependencies(s)
    assert len(packages) == 3
    assert packages == [
        "mashumaro",
        "typing-extensions",
        "tomli-w",
    ]
