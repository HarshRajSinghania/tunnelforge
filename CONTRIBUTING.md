# Contributing to TunnelForge

Thank you for your interest in contributing! This guide covers development setup, build process, and release workflow.

## Development Setup

### Requirements

- Python 3.9+
- Rust toolchain (`cargo`) for building `tunnelforge-core`
- Git
- [Inno Setup 6](https://jrsoftware.org/isinfo.php) (for building Windows installer)

### Setup

```bash
# Clone repository
git clone https://github.com/sanghyun-io/tunnelforge.git
cd tunnelforge

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Running the Application

```bash
python main.py
```

## Project Structure

```
tunnelforge/
├── main.py                 # Entry point
├── src/
│   ├── version.py          # Version (single source of truth)
│   ├── core/               # Business logic
│   │   ├── config_manager.py   # Configuration management
│   │   ├── tunnel_engine.py    # SSH tunnel engine
│   │   ├── db_core_service.py  # Re-exports the Rust DB core client and facade
│   │   └── db_core_facade.py   # DbCoreFacade used by the UI
│   ├── exporters/          # DB Export/Import
│   │   └── rust_dump_exporter.py
│   └── ui/                 # PyQt6 UI
│       ├── main_window.py
│       ├── dialogs/
│       └── workers/
├── assets/                 # Icons and resources
├── migration_core/         # Rust tunnelforge-core DB service
├── installer/              # Inno Setup configuration
├── scripts/                # Build and release scripts
└── tests/                  # pytest suite
```

## Running Tests

```bash
# Python suite
pytest -q

# Rust core
cargo test --manifest-path migration_core/Cargo.toml
```

`tests/conftest.py` sets `QT_QPA_PLATFORM=offscreen`, so the Qt tests run without a display.

Tests that need a live MySQL or PostgreSQL server are skipped unless their environment variables are set. For example, `tests/test_explain_plan_live.py` runs only with `TF_EXPLAIN_LIVE=1`. CI starts the test servers and runs these tests as required checks (`.github/workflows/version-gate.yml`), so you do not have to run them locally.

## Building

### Build Windows Installer Locally

```bash
# Build installer
.\scripts\build-installer.ps1

# Clean build
.\scripts\build-installer.ps1 -Clean
```

**Output:**
- `dist\TunnelForge\TunnelForge.exe` - Standalone executable
- `output\TunnelForge-Setup-{version}.exe` - Windows installer

## Release Process

Contributors do not bump versions. The version lives in `src/version.py` (Semantic Versioning, `major.minor.patch`), and maintainers handle releases:

1. A maintainer adds one `version:patch`, `version:minor` or `version:major` label to the PR. The labels are created once per repository with `scripts/setup-labels.sh`.
2. `.github/workflows/version-gate.yml` pushes a version bump commit to the PR branch. The same workflow runs the required checks.
3. After the merge, a maintainer runs `.github/workflows/create-release-tag.yml` by hand to tag the merge commit as `vX.Y.Z`.
4. A maintainer then runs `.github/workflows/release.yml` for that tag. It builds the Windows installer and the macOS apps and uploads them to a draft GitHub Release, which the maintainer publishes.

**Monitor builds:** https://github.com/sanghyun-io/tunnelforge/actions

## Code Style

- Use meaningful variable and function names
- Add comments for complex logic (Korean comments are OK for UI text)
- Follow existing patterns in the codebase

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests (see [Running Tests](#running-tests))
5. Submit a pull request

## Questions?

Open an issue for questions or suggestions.
