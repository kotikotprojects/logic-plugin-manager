Usage Examples
==============

This page provides practical examples for common use cases.

Plugin Discovery & Inspection
------------------------------

List All Plugins
~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   print(f"Total plugins: {len(logic.plugins.all())}")

   for plugin in logic.plugins.all():
       print(f"{plugin.full_name}")
       print(f"  Type: {plugin.type_name.display_name}")
       print(f"  Version: {plugin.version}")
       print(f"  Categories: {', '.join(c.name for c in plugin.categories)}")
       print()

Filter by Type
~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Get all instruments
   instruments = logic.plugins.get_by_type_code("aumu")
   print(f"Found {len(instruments)} instruments")

   # Get all effects
   effects = logic.plugins.get_by_type_code("aufx")
   print(f"Found {len(effects)} effects")

Find Plugins by Manufacturer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # List all manufacturers
   manufacturers = set()
   for plugin in logic.plugins.all():
       manufacturers.add(plugin.manufacturer)

   for mfr in sorted(manufacturers):
       plugins = logic.plugins.get_by_manufacturer(mfr)
       print(f"{mfr}: {len(plugins)} plugins")

   # Get specific manufacturer's plugins
   fabfilter = logic.plugins.get_by_manufacturer("fabfilter")
   for plugin in fabfilter:
       print(f"  - {plugin.name}")

Inspect Plugin Details
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()
   plugin = logic.plugins.get_by_full_name("fabfilter: pro-q 3")

   if plugin:
       print(f"Full Name: {plugin.full_name}")
       print(f"Manufacturer: {plugin.manufacturer}")
       print(f"Name: {plugin.name}")
       print(f"Description: {plugin.description}")
       print(f"Type: {plugin.type_name.display_name} ({plugin.type_code})")
       print(f"Subtype: {plugin.subtype_code}")
       print(f"Manufacturer Code: {plugin.manufacturer_code}")
       print(f"Version: {plugin.version}")
       print(f"Factory Function: {plugin.factory_function}")
       print(f"Tags ID: {plugin.tags_id}")
       print(f"Tagset Path: {plugin.tagset.path}")
       
       if plugin.tagset.nickname:
           print(f"Nickname: {plugin.tagset.nickname}")
       if plugin.tagset.shortname:
           print(f"Short Name: {plugin.tagset.shortname}")
       
       print(f"Categories: {', '.join(c.name for c in plugin.categories)}")

Search & Discovery
------------------

Simple Text Search
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Simple substring search
   reverb_plugins = logic.plugins.search_simple("reverb")
   
   print(f"Found {len(reverb_plugins)} plugins with 'reverb' in name")
   for plugin in reverb_plugins:
       print(f"  - {plugin.full_name}")

Advanced Fuzzy Search
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Fuzzy search with scoring
   results = logic.plugins.search(
       query="compressor",
       use_fuzzy=True,
       fuzzy_threshold=80,
       max_results=10
   )

   for i, result in enumerate(results, 1):
       print(f"{i}. {result.plugin.full_name}")
       print(f"   Score: {result.score:.1f}")
       print(f"   Matched field: {result.match_field}")
       print()

Search by Multiple Criteria
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   def find_plugins(search_term, plugin_type=None, category=None):
       """Search plugins with optional filters."""
       results = logic.plugins.search(search_term, use_fuzzy=True)
       
       plugins = [r.plugin for r in results]
       
       # Filter by type if specified
       if plugin_type:
           plugins = [p for p in plugins if p.type_code == plugin_type]
       
       # Filter by category if specified
       if category:
           plugins = [
               p for p in plugins
               if any(c.name == category for c in p.categories)
           ]
       
       return plugins

   # Find reverb effects (not instruments)
   reverbs = find_plugins("reverb", plugin_type="aufx")
   
   # Find synthesizers in Instruments category
   synths = find_plugins("synth", plugin_type="aumu", category="Instruments")

Category Management
-------------------

List All Categories
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   print("Categories:")
   for name, category in sorted(logic.categories.items()):
       print(f"  {name} ({category.plugin_amount} plugins)")

Create Category Hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Create nested categories
   categories_to_create = [
       "My Plugins",
       "My Plugins:Favorites",
       "My Plugins:Favorites:Mixing",
       "My Plugins:Favorites:Mastering",
   ]

   for cat_name in categories_to_create:
       if cat_name not in logic.categories:
           category = logic.introduce_category(cat_name)
           print(f"Created: {cat_name}")
       else:
           print(f"Already exists: {cat_name}")

Add Plugins to Category
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Create or get category
   favorites = logic.categories.get("Favorites")
   if not favorites:
       favorites = logic.introduce_category("Favorites")

   # Add single plugin
   plugin = logic.plugins.get_by_full_name("fabfilter: pro-q 3")
   if plugin:
       plugin.add_to_category(favorites)
       print(f"Added {plugin.full_name} to {favorites.name}")

   # Update category count
   logic.sync_category_plugin_amount(favorites)

Bulk Category Assignment
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Find all FabFilter plugins
   fabfilter_plugins = logic.plugins.get_by_manufacturer("fabfilter")

   # Create category
   fabfilter_cat = logic.categories.get("FabFilter")
   if not fabfilter_cat:
       fabfilter_cat = logic.introduce_category("FabFilter")

   # Bulk add
   logic.add_plugins_to_category(fabfilter_cat, fabfilter_plugins)
   print(f"Added {len(fabfilter_plugins)} FabFilter plugins")

Move Plugins Between Categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Get plugins from one category
   dynamics_plugins = logic.plugins.get_by_category("Effects:Dynamics")

   # Filter for compressors
   compressors = {
       p for p in dynamics_plugins
       if "compress" in p.name.lower()
   }

   # Move to specific category
   comp_category = logic.categories.get("Effects:Dynamics:Compressor")
   if comp_category:
       logic.move_plugins_to_category(comp_category, compressors)
       logic.sync_category_plugin_amount(comp_category)

Organize Uncategorized Plugins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Get plugins without categories
   uncategorized = logic.plugins.get_by_category(None)

   print(f"Found {len(uncategorized)} uncategorized plugins")

   # Auto-categorize by manufacturer
   for plugin in uncategorized:
       manufacturer = plugin.manufacturer.strip()
       category_name = f"By Manufacturer:{manufacturer}"
       
       # Create category if needed
       if category_name not in logic.categories:
           logic.introduce_category(category_name)
       
       category = logic.categories[category_name]
       plugin.add_to_category(category)

   # Update all category counts
   logic.sync_all_categories_plugin_amount()

Category Sorting
~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Get category
   category = logic.categories["Effects:EQ"]

   # Check current position
   print(f"Current index: {category.index}")
   prev, next_cat = category.neighbors
   if prev:
       print(f"Previous: {prev.name}")
   if next_cat:
       print(f"Next: {next_cat.name}")

   # Move category
   category.move_to_top()
   category.move_up(steps=5)
   category.move_down()

   # Move relative to another category
   target = logic.categories["Effects:Delay"]
   category.move_before(target)

Custom Plugin Metadata
----------------------

Set Nicknames
~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Set custom nicknames for easier identification
   plugins_to_rename = {
       "fabfilter: pro-q 3": "PQ3 - Main EQ",
       "fabfilter: pro-c 2": "PC2 - Main Compressor",
       "valhalla shimmer": "Shimmer - Ambient Verb",
   }

   for full_name, nickname in plugins_to_rename.items():
       plugin = logic.plugins.get_by_full_name(full_name)
       if plugin:
           plugin.set_nickname(nickname)
           print(f"Renamed: {full_name} -> {nickname}")

Set Short Names
~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Set short names for UI display
   shortnames = {
       "fabfilter: pro-q 3": "PQ3",
       "fabfilter: pro-c 2": "PC2",
       "serum": "SRM",
   }

   for full_name, shortname in shortnames.items():
       plugin = logic.plugins.get_by_full_name(full_name)
       if plugin:
           plugin.set_shortname(shortname)

Batch Metadata Updates
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Add manufacturer prefix to all plugin nicknames
   for plugin in logic.plugins.all():
       if not plugin.tagset.nickname:
           manufacturer = plugin.manufacturer.upper()
           nickname = f"[{manufacturer}] {plugin.name}"
           plugin.set_nickname(nickname)
           print(f"Set nickname for {plugin.full_name}")

Advanced Operations
-------------------

Export Plugin Inventory
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import csv
   from logic_plugin_manager import Logic

   logic = Logic()

   # Export to CSV
   with open("plugin_inventory.csv", "w", newline="") as f:
       writer = csv.writer(f)
       writer.writerow([
           "Full Name", "Manufacturer", "Type", "Version",
           "Categories", "Subtype Code", "Tags ID"
       ])
       
       for plugin in sorted(logic.plugins.all(), key=lambda p: p.full_name):
           writer.writerow([
               plugin.full_name,
               plugin.manufacturer,
               plugin.type_name.display_name,
               plugin.version,
               "; ".join(c.name for c in plugin.categories),
               plugin.subtype_code,
               plugin.tags_id,
           ])

   print("Exported plugin inventory to plugin_inventory.csv")

Clone Category Structure
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   def clone_category(source: str, target: str, logic: Logic):
       """Clone plugins from source category to target category."""
       # Get plugins in source
       source_plugins = logic.plugins.get_by_category(source)
       
       # Create target if needed
       if target not in logic.categories:
           logic.introduce_category(target)
       
       target_category = logic.categories[target]
       
       # Add plugins to target
       logic.add_plugins_to_category(target_category, source_plugins)
       
       print(f"Cloned {len(source_plugins)} plugins from {source} to {target}")

   logic = Logic()
   clone_category("Effects:EQ", "My Plugins:EQ", logic)

Find Duplicate Plugins
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from collections import defaultdict
   from logic_plugin_manager import Logic

   logic = Logic()

   # Group by name (ignoring manufacturer)
   by_name = defaultdict(list)
   for plugin in logic.plugins.all():
       by_name[plugin.name.lower()].append(plugin)

   # Find duplicates
   duplicates = {
       name: plugins
       for name, plugins in by_name.items()
       if len(plugins) > 1
   }

   print(f"Found {len(duplicates)} plugin names with multiple versions:\n")
   for name, plugins in sorted(duplicates.items()):
       print(f"{name}:")
       for plugin in plugins:
           print(f"  - {plugin.full_name} (v{plugin.version})")
       print()

Backup and Restore Categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   from pathlib import Path
   from logic_plugin_manager import Logic

   def backup_categories(output_file: Path):
       """Backup all plugin category assignments."""
       logic = Logic()
       
       backup_data = {}
       for plugin in logic.plugins.all():
           backup_data[plugin.tags_id] = {
               "full_name": plugin.full_name,
               "categories": [c.name for c in plugin.categories],
           }
       
       with open(output_file, "w") as f:
           json.dump(backup_data, f, indent=2)
       
       print(f"Backed up {len(backup_data)} plugin assignments")

   def restore_categories(backup_file: Path):
       """Restore plugin category assignments from backup."""
       logic = Logic()
       
       with open(backup_file) as f:
           backup_data = json.load(f)
       
       restored = 0
       for tags_id, data in backup_data.items():
           plugin = logic.plugins.get_by_tags_id(tags_id)
           if plugin:
               # Restore categories
               categories = [
                   logic.categories[name]
                   for name in data["categories"]
                   if name in logic.categories
               ]
               if categories:
                   plugin.set_categories(categories)
                   restored += 1
       
       print(f"Restored {restored} plugin assignments")

   # Usage
   backup_categories(Path("categories_backup.json"))
   # restore_categories(Path("categories_backup.json"))

Generate Category Report
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   print("=" * 60)
   print("CATEGORY REPORT")
   print("=" * 60)
   print()

   # Sort categories by hierarchy
   sorted_categories = sorted(logic.categories.items())

   for name, category in sorted_categories:
       # Calculate depth based on colons
       depth = name.count(":")
       indent = "  " * depth
       
       # Get plugins in this exact category
       plugins = logic.plugins.get_by_category(name)
       
       print(f"{indent}├─ {name.split(':')[-1]}")
       print(f"{indent}│  Count: {category.plugin_amount}")
       print(f"{indent}│  Index: {category.index}")
       
       if plugins:
           print(f"{indent}│  Plugins:")
           for plugin in sorted(plugins, key=lambda p: p.full_name)[:5]:
               print(f"{indent}│    - {plugin.full_name}")
           if len(plugins) > 5:
               print(f"{indent}│    ... and {len(plugins) - 5} more")
       print()

Working with Component Bundles
-------------------------------

Inspect Component Bundles
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   print(f"Total component bundles: {len(logic.components)}\n")

   for component in logic.components:
       print(f"Bundle: {component.name}")
       print(f"  ID: {component.bundle_id}")
       print(f"  Version: {component.version} ({component.short_version})")
       print(f"  Audio Components: {len(component.audio_components)}")
       
       for audio_comp in component.audio_components:
           print(f"    - {audio_comp.full_name}")
       print()

Find Multi-Plugin Bundles
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()

   # Find bundles with multiple plugins
   multi_plugin_bundles = [
       comp for comp in logic.components
       if len(comp.audio_components) > 1
   ]

   print(f"Found {len(multi_plugin_bundles)} bundles with multiple plugins:\n")

   for component in multi_plugin_bundles:
       print(f"{component.name} - {len(component.audio_components)} plugins:")
       for plugin in component.audio_components:
           print(f"  - {plugin.name} ({plugin.type_name.display_name})")
       print()

Error Handling Examples
-----------------------

Robust Plugin Search
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import Logic, PluginLoadError

   def safe_find_plugin(plugin_name: str) -> None:
       """Safely search for a plugin with error handling."""
       try:
           logic = Logic()
       except PluginLoadError as e:
           print(f"Error loading plugins: {e}")
           return
       
       plugin = logic.plugins.get_by_full_name(plugin_name)
       
       if plugin:
           print(f"Found: {plugin.full_name}")
           print(f"Type: {plugin.type_name.display_name}")
           
           # Try to load tagset
           try:
               print(f"Categories: {', '.join(c.name for c in plugin.categories)}")
           except Exception as e:
               print(f"Could not load categories: {e}")
       else:
           print(f"Plugin '{plugin_name}' not found")
           
           # Try fuzzy search
           results = logic.plugins.search(plugin_name)
           if results:
               print(f"\nDid you mean:")
               for result in results[:3]:
                   print(f"  - {result.plugin.full_name}")

   safe_find_plugin("fabfilter: pro-q 3")

Graceful Category Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logic_plugin_manager import (
       Logic,
       CategoryValidationError,
       MusicAppsLoadError
   )

   def safe_add_to_category(plugin_name: str, category_name: str):
       """Add plugin to category with error handling."""
       try:
           logic = Logic()
       except MusicAppsLoadError as e:
           print(f"Database error: {e}")
           return
       
       # Find plugin
       plugin = logic.plugins.get_by_full_name(plugin_name)
       if not plugin:
           print(f"Plugin '{plugin_name}' not found")
           return
       
       # Get or create category
       try:
           category = logic.categories[category_name]
       except KeyError:
           try:
               category = logic.introduce_category(category_name)
               print(f"Created new category: {category_name}")
           except Exception as e:
               print(f"Could not create category: {e}")
               return
       
       # Add to category
       try:
           plugin.add_to_category(category)
           logic.sync_category_plugin_amount(category)
           print(f"Added {plugin.full_name} to {category_name}")
       except Exception as e:
           print(f"Error adding to category: {e}")

   safe_add_to_category("fabfilter: pro-q 3", "My Favorites")
