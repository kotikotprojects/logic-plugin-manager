# Logic Plugin Manager

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE.md)
[![Commercial License](https://img.shields.io/badge/License-Commercial-green.svg)](LICENSE-COMMERCIAL.md)
[![PyPI version](https://badge.fury.io/py/logic-plugin-manager.svg)](https://pypi.org/project/logic-plugin-manager/)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

Programmatic management of Logic Pro audio plugins on macOS.

## Overview

Logic Plugin Manager is a Python library that provides programmatic access to Logic Pro's plugin management system. It enables automated discovery, categorization, and organization of macOS Audio Unit plugins through Logic's internal tag database.

**Key Capabilities:**
- Automated plugin discovery and indexing
- Hierarchical category management
- Advanced search with fuzzy matching
- Bulk operations on plugin collections
- Programmatic metadata manipulation

## Requirements

- **Python**: 3.13 or higher
- **Operating System**: macOS
- **Dependencies**: None (core functionality), `rapidfuzz>=3.14.3` (optional, for fuzzy search)

## Installation

```bash
pip install logic-plugin-manager
```

For fuzzy search functionality:
```bash
pip install logic-plugin-manager[search]
```

## Usage

```python
from logic_plugin_manager import Logic

# Initialize and discover plugins
logic = Logic()

# Access plugin collection
for plugin in logic.plugins.all():
    print(f"{plugin.full_name} - {plugin.type_name.display_name}")

# Search with scoring
results = logic.plugins.search("reverb", use_fuzzy=True, max_results=10)

# Category management
category = logic.introduce_category("Production Tools")
plugin = logic.plugins.get_by_full_name("fabfilter: pro-q 3")
plugin.add_to_category(category)
```

## Architecture

The library is organized into three primary modules:

- **`components`**: Audio Unit component and bundle parsing
- **`logic`**: High-level plugin management interface
- **`tags`**: Category system and tag database operations

## Documentation

Full documentation available at: https://logic-plugin-manager.readthedocs.io

## License

This project is dual-licensed:

**Open Source (AGPL-3.0)**: Free for open source projects. See [LICENSE.md](LICENSE.md).

**Commercial License**: Required for closed-source or commercial applications. See [LICENSE-COMMERCIAL.md](LICENSE-COMMERCIAL.md).

Contact: h@kotikot.com

## Links

- **Repository**: https://github.com/kotikotprojects/logic-plugin-manager
- **PyPI**: https://pypi.org/project/logic-plugin-manager/
- **Documentation**: https://logic-plugin-manager.readthedocs.io
