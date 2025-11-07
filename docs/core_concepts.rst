Core Concepts
=============

This page explains the key concepts and architecture of Logic Plugin Manager.

Architecture Overview
---------------------

Logic Plugin Manager is structured around three main areas:

1. **Components**: Audio Unit plugin bundles and their metadata
2. **Logic Management**: High-level interface for plugin discovery and organization
3. **Tags & Categories**: Logic Pro's categorization system

The Library's Structure
~~~~~~~~~~~~~~~~~~~~~~~~

::

    logic_plugin_manager/
    ├── components/          # Audio Unit components
    │   ├── AudioComponent   # Individual plugin representation
    │   ├── Component        # .component bundle parser
    │   └── AudioUnitType    # Audio Unit type enumeration
    ├── logic/               # Main management interface
    │   ├── Logic            # Primary entry point
    │   ├── Plugins          # Plugin collection with search
    │   └── SearchResult     # Search result with scoring
    └── tags/                # Category and tag management
        ├── Category         # Plugin category management
        ├── MusicApps        # Database interface
        ├── Tagpool          # Plugin count tracking
        ├── Properties       # Category sorting
        └── Tagset           # Plugin tag files

Understanding Audio Components
------------------------------

Audio Component Bundle Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

macOS Audio Unit plugins are distributed as ``.component`` bundles:

::

    PluginName.component/
    └── Contents/
        ├── Info.plist       # Metadata and component definitions
        ├── MacOS/
        │   └── PluginName   # Executable binary
        └── Resources/       # UI resources, presets, etc.

The ``Info.plist`` file contains an ``AudioComponents`` array defining one or more Audio Units within the bundle.

AudioComponent Class
~~~~~~~~~~~~~~~~~~~~

Each Audio Unit is represented by an ``AudioComponent`` instance with:

- **Identification**: Type, subtype, and manufacturer codes
- **Metadata**: Name, description, version
- **Categories**: Tags assigned in Logic Pro
- **Tags ID**: Unique identifier derived from codes

.. code-block:: python

   from logic_plugin_manager import Logic

   logic = Logic()
   plugin = logic.plugins.get_by_name("Pro-Q 3")

   # Access component information
   print(f"Full Name: {plugin.full_name}")
   print(f"Manufacturer: {plugin.manufacturer}")
   print(f"Type Code: {plugin.type_code}")
   print(f"Subtype Code: {plugin.subtype_code}")
   print(f"Manufacturer Code: {plugin.manufacturer_code}")
   print(f"Tags ID: {plugin.tags_id}")

Audio Unit Types
~~~~~~~~~~~~~~~~

Logic Plugin Manager recognizes five Audio Unit types:

.. list-table::
   :header-rows: 1
   :widths: 15 25 20 40

   * - Code
     - Display Name
     - Alternative Name
     - Description
   * - ``aufx``
     - Audio FX
     - Effect
     - Audio effect processors
   * - ``aumu``
     - Instrument
     - Music Device
     - Software instruments and synthesizers
   * - ``aumf``
     - MIDI-controlled Effects
     - Music Effect
     - Effects controlled by MIDI input
   * - ``aumi``
     - MIDI FX
     - MIDI Generator
     - MIDI processors and generators
   * - ``augn``
     - Generator
     - Generator
     - Audio generators

.. code-block:: python

   from logic_plugin_manager import AudioUnitType

   # Get type by code
   instrument_type = AudioUnitType.from_code("aumu")
   print(instrument_type.display_name)  # "Instrument"

   # Search for types
   effect_types = AudioUnitType.search("effect")

The Logic Class
---------------

The ``Logic`` class is the main entry point for plugin management.

Initialization Process
~~~~~~~~~~~~~~~~~~~~~~

When you create a ``Logic`` instance (with ``lazy=False``, the default):

1. Loads MusicApps database (tagpool and properties files)
2. Scans ``/Library/Audio/Plug-Ins/Components`` directory
3. Parses each ``.component`` bundle's ``Info.plist``
4. Creates ``AudioComponent`` instances
5. Loads tagsets and categories for each plugin
6. Indexes plugins for fast lookups

.. code-block:: python

   from logic_plugin_manager import Logic

   # Full initialization
   logic = Logic()  # Discovers everything

   # Lazy initialization (manual control)
   logic = Logic(lazy=True)
   logic.discover_plugins()      # When ready to load plugins
   logic.discover_categories()   # When ready to load categories

Logic Instance Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   logic = Logic()

   # Access discovered data
   logic.plugins           # Plugins collection
   logic.components        # Set of Component bundles
   logic.categories        # Dict of category_name -> Category
   logic.musicapps         # MusicApps database interface

   # Configuration paths
   logic.components_path   # Path to Components directory
   logic.tags_path         # Path to tags database

Plugin Collection & Search
---------------------------

The Plugins Class
~~~~~~~~~~~~~~~~~

The ``Plugins`` class provides a searchable collection with multiple indexes:

- **By full name**: Exact manufacturer + plugin name match
- **By manufacturer**: All plugins from a vendor
- **By name**: Plugin name only
- **By codes**: Type, subtype, manufacturer codes
- **By category**: All plugins in a category
- **By tags_id**: Unique component identifier

.. code-block:: python

   logic = Logic()

   # Exact lookups (fast)
   plugin = logic.plugins.get_by_full_name("fabfilter: pro-q 3")
   plugin = logic.plugins.get_by_tags_id("61756678-65517033-46466")

   # Set lookups
   fabfilter = logic.plugins.get_by_manufacturer("fabfilter")
   effects = logic.plugins.get_by_type_code("aufx")
   eq_plugins = logic.plugins.get_by_category("Effects:EQ")

Search Algorithm
~~~~~~~~~~~~~~~~

The ``search()`` method implements a sophisticated scoring system:

**Priority Levels** (highest to lowest):

1. **Tags ID exact match** (score: 1000)
2. **Name substring match** (850-900)
3. **Full name substring match** (750-800)
4. **Fuzzy name match** (650-700, requires rapidfuzz)
5. **Manufacturer match** (580-650)
6. **Category match** (480-550)
7. **Type code match** (380-450)
8. **Subtype code match** (290-350)
9. **Manufacturer code match** (190-250)

.. code-block:: python

   logic = Logic()

   # Fuzzy search with scoring
   results = logic.plugins.search(
       "serum",
       use_fuzzy=True,
       fuzzy_threshold=80,
       max_results=10
   )

   for result in results:
       print(f"{result.plugin.full_name}")
       print(f"  Score: {result.score}")
       print(f"  Matched: {result.match_field}")

Categories & Tags
-----------------

Hierarchical Structure
~~~~~~~~~~~~~~~~~~~~~~

Categories in Logic Pro use colon-separated hierarchies:

::

    Effects
    Effects:Dynamics
    Effects:Dynamics:Compressor
    Effects:EQ
    Instruments
    Instruments:Synth

.. code-block:: python

   logic = Logic()

   # Navigate hierarchy
   dynamics = logic.categories["Effects:Dynamics"]
   parent = dynamics.parent  # "Effects" category
   child = parent.child("EQ")  # "Effects:EQ" category

   # Check properties
   print(dynamics.plugin_amount)
   print(dynamics.is_root)

Category Operations
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   logic = Logic()

   # Create new category
   my_cat = logic.introduce_category("Studio Essentials")

   # Manage plugins
   plugin = logic.plugins.get_by_name("Pro-Q 3")
   plugin.add_to_category(my_cat)
   plugin.remove_from_category(my_cat)
   plugin.move_to_category(my_cat)  # Removes from all others

   # Bulk operations
   plugins_set = {plugin1, plugin2, plugin3}
   logic.add_plugins_to_category(my_cat, plugins_set)

   # Update plugin count
   logic.sync_category_plugin_amount(my_cat)

Category Sorting
~~~~~~~~~~~~~~~~

Categories have a sort order managed by the ``Properties`` database:

.. code-block:: python

   category = logic.categories["Effects:EQ"]

   # Check position
   print(category.index)
   print(category.is_first)
   print(category.is_last)
   prev, next = category.neighbors

   # Reorder
   category.move_up(steps=2)
   category.move_down()
   category.move_to_top()
   category.move_to_bottom()
   category.move_before(other_category)
   category.move_after(other_category)
   category.swap(other_category)

Tagsets
-------

What are Tagsets?
~~~~~~~~~~~~~~~~~

Each ``AudioComponent`` has an associated ``.tagset`` file stored at:

``~/Music/Audio Music Apps/Databases/Tags/<tags_id>.tagset``

These XML plist files store:

- **nickname**: Custom display name
- **shortname**: Abbreviated name for UI
- **tags**: Dictionary of category assignments

.. code-block:: python

   logic = Logic()
   plugin = logic.plugins.get_by_name("Pro-Q 3")

   # Access tagset
   print(plugin.tagset.nickname)
   print(plugin.tagset.shortname)
   print(plugin.tagset.tags)  # {"Effects:EQ": "user"}

   # Modify tagset
   plugin.set_nickname("My Favorite EQ")
   plugin.set_shortname("PQ3")

Tag Values
~~~~~~~~~~

Category tags typically have the value ``"user"`` indicating user assignment, but can have other values from Logic Pro's internal management.

MusicApps Database
------------------

Database Files
~~~~~~~~~~~~~~

Logic Pro stores category information in two files:

**MusicApps.tagpool**
  Maps category names to plugin counts:
  
  .. code-block:: python

     {
         "Effects": 245,
         "Effects:EQ": 18,
         "Instruments": 89,
         ...
     }

**MusicApps.properties**
  Stores category sort order and preferences:
  
  .. code-block:: python

     {
         "sorting": ["Effects", "Effects:Dynamics", ...],
         "user_sorted": "property"  # or absent for alphabetical
     }

Accessing the Database
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   logic = Logic()
   musicapps = logic.musicapps

   # Access tagpool
   print(musicapps.tagpool.categories)

   # Access properties
   print(musicapps.properties.sorting)
   print(musicapps.properties.user_sorted)

   # Modify database
   musicapps.introduce_category("New Category")
   musicapps.remove_category("Old Category")

Thread Safety
-------------

Logic Plugin Manager is **not thread-safe**. The library performs file I/O operations on Logic Pro's database files without locking mechanisms.

**Recommendations:**

- Use a single ``Logic`` instance per process
- Avoid concurrent writes to categories or tagsets
- Reload data after external changes (e.g., Logic Pro modifying categories)

Performance Considerations
--------------------------

Initial Discovery
~~~~~~~~~~~~~~~~~

Loading all plugins can take several seconds depending on the number of installed components. Use ``lazy=True`` for faster startup when you don't need immediate access.

Indexing
~~~~~~~~

The ``Plugins`` collection maintains multiple indexes. Reindexing is required if you:

- Modify plugin properties externally
- Add plugins after initialization

.. code-block:: python

   logic = Logic(lazy=True)
   logic.discover_plugins()
   # ... modify plugins externally ...
   logic.plugins.reindex_all()

Search Performance
~~~~~~~~~~~~~~~~~~

- Exact lookups by indexes are O(1)
- Fuzzy search with ``rapidfuzz`` is O(n) but optimized
- Use ``max_results`` to limit computation for large result sets

Best Practices
--------------

1. **Single Instance**: Create one ``Logic`` instance and reuse it
2. **Error Handling**: Wrap operations in try-except blocks for specific exceptions
3. **Lazy Loading**: Use for CLI tools or services that don't need immediate access
4. **Reloading**: Call ``load()`` methods after external modifications to databases

.. code-block:: python

   from logic_plugin_manager import (
       Logic,
       CategoryValidationError,
       PluginLoadError
   )

   try:
       logic = Logic()
   except PluginLoadError as e:
       print(f"Failed to load plugins: {e}")
       # Handle gracefully

   # Batch operation example
   favorites = {
       logic.plugins.get_by_name(name)
       for name in ["Pro-Q 3", "Serum", "Valhalla VintageVerb"]
       if logic.plugins.get_by_name(name)
   }

   if favorites:
       fav_category = logic.introduce_category("Favorites")
       logic.add_plugins_to_category(fav_category, favorites)
       logic.sync_category_plugin_amount(fav_category)
