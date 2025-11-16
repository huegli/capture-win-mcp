# Distribution Guide

This guide explains how to package and distribute `capture-win-mcp`.

## Prerequisites

- Python 3.12+
- `uv` or `build` package

## Building the Package

### Using uv (Recommended)

```bash
# Build both wheel and source distribution
uv build

# Output files will be in dist/:
# - capture_win_mcp-0.1.0-py3-none-any.whl (wheel)
# - capture_win_mcp-0.1.0.tar.gz (source)
```

### Using build

```bash
# Install build tool
pip install build

# Build distributions
python -m build

# Clean build
python -m build --clean
```

## Testing the Package Locally

### Test installation from wheel

```bash
# Create a test virtual environment
python3 -m venv test_env
source test_env/bin/activate

# Install from wheel
pip install dist/capture_win_mcp-0.1.0-py3-none-any.whl

# Test the command
capture-win-mcp --help

# Cleanup
deactivate
rm -rf test_env
```

### Test installation from source

```bash
pip install dist/capture_win_mcp-0.1.0.tar.gz
```

## Distribution Methods

### 1. GitHub Release

1. Create a new release on GitHub:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. Upload the distribution files to GitHub Releases:
   - `dist/capture_win_mcp-0.1.0-py3-none-any.whl`
   - `dist/capture_win_mcp-0.1.0.tar.gz`

3. Users can install directly from GitHub:
   ```bash
   pip install git+https://github.com/yourusername/capture-win-mcp.git

   # Or from a specific release
   pip install git+https://github.com/yourusername/capture-win-mcp.git@v0.1.0
   ```

### 2. PyPI (Python Package Index)

1. Create accounts on:
   - PyPI: https://pypi.org/account/register/
   - TestPyPI (optional, for testing): https://test.pypi.org/account/register/

2. Configure PyPI credentials:
   ```bash
   # Install twine
   pip install twine

   # Configure ~/.pypirc (optional)
   ```

3. Upload to TestPyPI (optional, for testing):
   ```bash
   twine upload --repository testpypi dist/*

   # Test install from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ capture-win-mcp
   ```

4. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

5. Users can then install:
   ```bash
   pip install capture-win-mcp
   ```

### 3. Direct Distribution

Share the wheel or tarball file directly:

```bash
# Users can install from a local file
pip install capture_win_mcp-0.1.0-py3-none-any.whl

# Or from a URL
pip install https://example.com/path/to/capture_win_mcp-0.1.0-py3-none-any.whl
```

## Version Management

Update version in `pyproject.toml`:

```toml
[project]
version = "0.2.0"  # Update this
```

Then rebuild:

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build new version
uv build
```

## Pre-release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `README.md` with new features/changes
- [ ] Update `CLAUDE.md` if architecture changed
- [ ] Test installation in clean environment
- [ ] Run manual tests with `python main.py`
- [ ] Test MCP server with Claude Desktop
- [ ] Update changelog/release notes
- [ ] Create git tag for version
- [ ] Build distributions: `uv build`
- [ ] Test distributions locally
- [ ] Upload to PyPI/GitHub

## Updating the Package

After making code changes:

```bash
# 1. Update version in pyproject.toml
# 2. Clean old builds
rm -rf dist/ build/ *.egg-info

# 3. Rebuild
uv build

# 4. Test locally
pip install --force-reinstall dist/capture_win_mcp-*.whl

# 5. Tag and release
git tag v0.2.0
git push origin v0.2.0
```

## Common Issues

### "Package already exists" on PyPI

Increment the version number - you cannot re-upload the same version.

### Import errors after installation

Make sure the package structure is correct:
```
capture_win_mcp/
├── __init__.py
├── tracker.py
└── server.py
```

### Missing files in distribution

Update `MANIFEST.in` to include additional files.

### Wrong Python version

Ensure `requires-python = ">=3.12"` matches your actual requirements.
