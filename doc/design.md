# design

This project is based on tool `uv`.

Running command `uv tree --no-dev` will generate the production
dependency tree of the project, from which we get the dependency
list and zip into a single file, named it `foo.zip`.

The Python official would contain an embedded version of Python
in every release for Windows, which is named like `python-3.8.10-embed-amd64.zip`.
Unzipping this embedded Python and the `foo.zip` into the same directory
will make the project runnable without any installation.

Beside the dependencies, the `foo.zip` contains entry points of
the main program `bar.bat`:

```bat
@call %~dp0lib\python.exe -c "import sys;sys.argv[0]="%~n0";from xxx.yyy import main;sys.exit(main())" %*
@exit /b %errorlevel%
```
