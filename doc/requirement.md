This project works on Python project based on
`uv` tool, which includes two main files:
`pyproject.toml` and `uv.lock`,
and with the project structure as follows:

```
.
├── README.md
├── .python-version
├── pyproject.toml
├── uv.lock
├── src
│   └── package
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       └── xxx.py
└── tests
    ├── __init__.py
    └── test_xxx.py
```

If there is any script defined in `pyproject.toml`,
which seems like:

```toml
[project.scripts]
build-pyckage = "build_pyckage.cli:main"
```

should add `if __name__ == '__main__'` to `src/build_pyckage/cli.py`.
