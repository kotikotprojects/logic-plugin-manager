Getting Started
===============

This guide will help you get started with Logic Plugin Manager, a Python library for programmatically managing Logic Pro's audio plugins.

Installation
------------

Basic Installation
~~~~~~~~~~~~~~~~~~

Install the package using pip or uv:

.. code-block:: bash

   pip install logic-plugin-manager

Or with uv:

.. code-block:: bash

   uv add logic-plugin-manager

With Search Functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~

For fuzzy search capabilities, install with the ``search`` extra:

.. code-block:: bash

   pip install logic-plugin-manager[search]
   # or
   uv add logic-plugin-manager[search]

This includes the ``rapidfuzz`` dependency for advanced plugin searching.

Requirements
------------

- **Python**: 3.13 or higher
- **Operating System**: macOS only (Logic Pro specific)
- **Logic Pro**: Installed with audio plugins

The library accesses:

- Audio Components directory: ``/Library/Audio/Plug-Ins/Components``
- Tags database: ``~/Music/Audio Music Apps/Databases/Tags``

Quick Start
-----------

Basic Usage
~~~~~~~~~~~

The simplest way to start is by creating a ``Logic`` instance:

.. code-block:: python

   from logic_plugin_manager import Logic

   # Initialize and discover all plugins
   logic = Logic()

   # Access all plugins
   for plugin in logic.plugins.all():
       print(f"{plugin.full_name} - {plugin.type_name.display_name}")

   # Access categories
   for category_name, category in logic.categories.items():
       print(f"{category_name}: {category.plugin_amount} plugins")

Lazy Loading
~~~~~~~~~~~~

For faster initialization when you don't need immediate access to all plugins:

.. code-block:: python

   from logic_plugin_manager import Logic

   # Initialize without loading plugins
   logic = Logic(lazy=True)

   # Manually discover plugins when needed
   logic.discover_plugins()
   logic.discover_categories()

Searching Plugins
~~~~~~~~~~~~~~~~~

Search for plugins by name, manufacturer, or category:

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Simple substring search
   results = logic.plugins.search_simple("reverb")

   # Advanced fuzzy search with scoring
   results = logic.plugins.search("serum", use_fuzzy=True)
   for result in results[:5]:  # Top 5 results
       print(f"{result.plugin.full_name} (score: {result.score})")

Working with Categories
~~~~~~~~~~~~~~~~~~~~~~~

Organize plugins into categories:

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Get plugins in a specific category
   effects = logic.plugins.get_by_category("Effects")

   # Get or create a category
   my_category = logic.categories.get("My Favorites")
   if not my_category:
       my_category = logic.introduce_category("My Favorites")

   # Add plugin to category
   plugin = logic.plugins.get_by_full_name("fabfilter: pro-q 3")
   if plugin:
       plugin.add_to_category(my_category)

Custom Paths
~~~~~~~~~~~~

If your Logic Pro or components are in non-standard locations:

.. code-block:: python

   from pathlib import Path
   from logic_plugin_manager import Logic

   logic = Logic(
       components_path=Path("/custom/path/to/Components"),
       tags_path=Path("~/custom/path/to/Tags").expanduser()
   )

Next Steps
----------

- Learn about :doc:`core_concepts` to understand the library's architecture
- Explore :doc:`examples` for common use cases
- Check the :doc:`logic_plugin_manager` for detailed API reference

Common Patterns
---------------

Finding a Specific Plugin
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # By full name (exact match)
   plugin = logic.plugins.get_by_full_name("apple: logic eq")

   # By manufacturer
   fabfilter_plugins = logic.plugins.get_by_manufacturer("fabfilter")

   # By audio unit type
   instruments = logic.plugins.get_by_type_code("aumu")

Batch Category Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Get all synthesizer plugins
   synths = logic.plugins.search("synth", use_fuzzy=True)
   synth_plugins = {result.plugin for result in synths[:20]}

   # Move them to a custom category
   synth_category = logic.introduce_category("Synthesizers")
   logic.move_plugins_to_category(synth_category, synth_plugins)

Working with Plugin Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()
   plugin = logic.plugins.get_by_name("Pro-Q 3")

   if plugin:
       # Access metadata
       print(f"Manufacturer: {plugin.manufacturer}")
       print(f"Type: {plugin.type_name.display_name}")
       print(f"Version: {plugin.version}")
       print(f"Categories: {[c.name for c in plugin.categories]}")

       # Set custom nickname
       plugin.set_nickname("My Favorite EQ")

       # Set short name for UI display
       plugin.set_shortname("PQ3")

Error Handling
--------------

The library raises specific exceptions for different error conditions:

.. code-block:: python

   from logic_plugin_manager import (
       Logic,
       PluginLoadError,
       MusicAppsLoadError,
       CategoryValidationError
   )

   try:
       logic = Logic()
   except MusicAppsLoadError as e:
       print(f"Could not load Logic's database: {e}")
   except PluginLoadError as e:
       print(f"Error loading plugins: {e}")

   try:
       category = logic.categories["Nonexistent"]
   except KeyError:
       print("Category not found")

See :doc:`logic_plugin_manager` for all exception types.
