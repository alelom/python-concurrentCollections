# Release Process

Update the version in `pyproject.toml`.

Then build as below.

Requirement: `pip install build`

## Build from Windows

If using UV:

```cmd
del dist\*.* /Q && uv run python -m build
```
or without UV:

```cmd
del dist\*.* /Q && python -m build
```

## Build on Linux
If using UV:

```bash
rm dist/*.* | uv run python3 -m build
```
or without UV:

```bash
rm dist/*.* | python3 -m build
```

## Release on PyPI

First, if needed: `pip install twine`
   
Upload to PyPi: 

```cmd/bash
python -m twine upload dist/*
```

Upload to PyPiTest: 

```cmd/bash
python -m twine upload --repository testpypi dist/*
```
