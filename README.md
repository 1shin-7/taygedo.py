<div align="center">

[![Socialify](https://socialify.git.ci/1shin-7/taygedo.py/image?description=1&font=Inter&language=1&name=1&owner=1&pattern=Plus&theme=Dark)](https://github.com/1shin-7/taygedo.py)

<br/>

[![PyPI](https://img.shields.io/pypi/v/taygedo?style=flat-square&logo=pypi&logoColor=white&color=3B82F6)](https://pypi.org/project/taygedo/)
[![Python](https://img.shields.io/badge/python-3.13%2B-3B82F6?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/1shin-7/taygedo.py?style=flat-square&color=3B82F6)](LICENSE)
[![uv](https://img.shields.io/badge/managed%20by-uv-3B82F6?style=flat-square&logo=astral&logoColor=white)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/badge/linted%20by-ruff-3B82F6?style=flat-square)](https://github.com/astral-sh/ruff)

> **taygedo** — an unofficial Python client & CLI for the [bbs-api.tajiduo.com](https://bbs-api.tajiduo.com) platform.  
> Query game data, manage your account, and automate monthly sign-ins for Tower of Fantasy and 异环.

</div>

---

## ✨ Features

- 🔐 **Account auth** — login, session management, and credential storage
- 🗂️ **CLI config** — TOML-based configuration via `taygedo conf`
- 🗼 **Tower of Fantasy** — fetch in-game data (`tof` / `ht` commands, `gameId=1256`)
- 🌀 **异环 (NTE)** — fetch game data **and** automate monthly sign-ins (`nte` / `yh` commands, `gameId=1289`)
- 🔍 **Debug mode** — print every HTTP request/response to stderr with `--debug`
- 🧩 **Typed SDK** — `py.typed` marker included; fully type-checked with mypy strict mode
- ⚡ **Async-ready** — built on `curl-cffi` for high-performance HTTP

---

## 🚀 Getting Started

### Prerequisites

- Python **3.13+**
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`

### Installation

**With uv (recommended):**

```bash
uv tool install taygedo
```

**With pip:**

```bash
pip install taygedo
```

### Quick Usage

```bash
# Show help
taygedo --help

# Log in to your account
taygedo auth login

# Fetch Tower of Fantasy data
taygedo tof <subcommand>

# Fetch 异环 data and trigger monthly sign-in
taygedo nte sign-in

# Enable debug output
taygedo --debug tof <subcommand>
```

### CLI Reference

```
Usage: taygedo [OPTIONS] COMMAND [ARGS]...

  taygedo — bbs-api.tajiduo.com client.

Options:
  --version  Show the version and exit.
  --debug    Print every HTTP request/response to stderr.
  --help     Show this message and exit.

Commands:
  auth  Account login and management.
  conf  CLI configuration (config.toml).
  ht    Tower of Fantasy (gameId=1256) data.
  nte   异环 (gameId=1289) data + monthly sign-in.
  tof   Tower of Fantasy (gameId=1256) data.
  yh    异环 (gameId=1289) data + monthly sign-in.
```

---

## 🛠️ Development

### Setup

```bash
git clone https://github.com/1shin-7/taygedo.py.git
cd taygedo.py

# Install dependencies (including dev extras)
uv sync
```

### Running Tests

```bash
uv run pytest
```

### Linting & Type Checking

```bash
# Lint with ruff
uv run ruff check .

# Format
uv run ruff format .

# Type-check with mypy
uv run mypy src/
```

### Project Structure

```
taygedo.py/
├── src/
│   └── taygedo/
│       ├── cli/          # Click-based CLI commands
│       ├── client.py     # HTTP client (curl-cffi)
│       ├── core/         # Core logic
│       ├── crypto/       # Signing / cryptography helpers
│       ├── device/       # Device fingerprint generation
│       ├── models/       # Pydantic response models
│       ├── services/     # Game-specific service modules
│       ├── signers/      # Request signers
│       └── utils/        # Shared utilities
├── tests/
├── scripts/
└── pyproject.toml
```
