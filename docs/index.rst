Logic Plugin Manager
====================

**Programmatic management of Logic Pro audio plugins**

Logic Plugin Manager is a Python library for discovering, organizing, and managing macOS Audio Unit plugins used by Logic Pro. It provides programmatic access to Logic's internal tag database, enabling automated plugin organization, bulk categorization, and advanced search capabilities.

----

Features
--------

- **Plugin Discovery**: Automatically scan and index all installed Audio Unit plugins
- **Category Management**: Create, modify, and organize plugin categories programmatically
- **Advanced Search**: Fuzzy search with scoring across multiple attributes
- **Bulk Operations**: Efficiently manage large plugin collections
- **Metadata Control**: Set custom nicknames, short names, and categories
- **Type-Safe**: Fully typed Python API with comprehensive documentation

Quick Example
-------------

.. code-block:: python

   from logic_plugin_manager import Logic

   # Initialize and discover all plugins
   logic = Logic()

   # Search for plugins
   results = logic.plugins.search("reverb", use_fuzzy=True)
   for result in results[:5]:
       print(f"{result.plugin.full_name} (score: {result.score})")

   # Organize into categories
   favorites = logic.introduce_category("Favorites")
   plugin = logic.plugins.get_by_full_name("fabfilter: pro-q 3")
   plugin.add_to_category(favorites)

Installation
------------

.. code-block:: bash

   pip install logic-plugin-manager

   # With search functionality
   pip install logic-plugin-manager[search]

**Requirements**: Python 3.13+, macOS, Logic Pro

----

Documentation
=============

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting_started
   core_concepts
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   logic_plugin_manager

----

Indices
=======

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

----

License
=======

This project is dual-licensed:

- **Open Source (AGPL-3.0)**: Free for open source projects
- **Commercial License**: Available for closed-source/commercial use

Contact: h@kotikot.com

