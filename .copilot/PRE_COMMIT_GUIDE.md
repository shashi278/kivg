# Pre-commit Setup Guide

## What is Pre-commit?

Pre-commit hooks automatically format and check your code before each commit. This ensures code quality and consistency without manual effort.

## Installation

### First Time Setup

1. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

2. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

That's it! The hooks are now active.

## How It Works

### Automatic Formatting on Commit

When you run `git commit`, pre-commit will:

1. **Black** - Format your Python code
2. **isort** - Organize your imports
3. **Flake8** - Check for style issues

If any tool makes changes:
- The commit is stopped
- Changes are automatically applied to your files
- You need to stage the changes and commit again

### Example Workflow

```bash
# Make code changes
vim kivg/parser/svg_parser.py

# Stage your changes
git add kivg/parser/svg_parser.py

# Commit (pre-commit runs automatically)
git commit -m "Add new parser feature"

# If pre-commit made changes:
# - Review the changes
# - Stage them: git add kivg/parser/svg_parser.py
# - Commit again: git commit -m "Add new parser feature"
```

## Manual Usage

### Run on All Files

To manually format/check all files:
```bash
pre-commit run --all-files
```

### Run on Specific Files

To run on specific files:
```bash
pre-commit run --files kivg/parser/svg_parser.py
```

### Skip Hooks (Not Recommended)

To bypass pre-commit hooks:
```bash
git commit --no-verify -m "message"
```

**Warning**: Only use `--no-verify` in emergencies. It bypasses code quality checks.

## Configured Tools

### Black
- **Purpose**: Python code formatter
- **Line length**: 88 characters
- **Style**: PEP 8 compliant

### isort
- **Purpose**: Import organizer
- **Profile**: black-compatible
- **Groups**: stdlib, third-party, first-party

### Flake8
- **Purpose**: Linter (style checker)
- **Max line length**: 88
- **Ignores**: E203 (whitespace before ':')

## Troubleshooting

### Hooks Not Running

If hooks don't run on commit:
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### Pre-commit Command Not Found

If `pre-commit` command is not found:
```bash
# Install in virtual environment
source .venv/bin/activate
pip install pre-commit
```

### Hooks Taking Too Long

First run downloads hook environments (can take 1-2 minutes). Subsequent runs are fast (seconds).

### Conflicts with Editor

If your editor auto-formats differently:
- Configure editor to use Black
- Configure editor to use isort with black profile
- Or disable editor auto-format

## Best Practices

1. **Commit often**: Let pre-commit catch issues early
2. **Review changes**: Check what pre-commit modified
3. **Don't skip**: Avoid `--no-verify` unless absolutely necessary
4. **Update hooks**: Run `pre-commit autoupdate` periodically
5. **Clean commits**: Let tools format so you can focus on logic

## Benefits

✅ **Consistent formatting** across all contributors
✅ **Catches issues early** before code review
✅ **Saves review time** - no formatting debates
✅ **Automatic** - no manual formatting needed
✅ **Fast feedback** - catch issues locally, not in CI

## Related Files

- `.pre-commit-config.yaml` - Hook configuration
- `requirements.txt` - Dependencies including pre-commit
- `.github/workflows/test.yml` - CI runs same checks

## More Information

- Pre-commit documentation: https://pre-commit.com/
- Black documentation: https://black.readthedocs.io/
- isort documentation: https://pycqa.github.io/isort/
- Flake8 documentation: https://flake8.pycqa.org/
