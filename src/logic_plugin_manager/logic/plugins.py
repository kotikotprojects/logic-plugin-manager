from collections import defaultdict
from dataclasses import dataclass

from ..components import AudioComponent, AudioUnitType


@dataclass
class SearchResult:
    plugin: AudioComponent
    score: float
    match_field: str


class Plugins:
    def __init__(self):
        self._plugins: set[AudioComponent] = set()

        self._by_full_name: dict[str, AudioComponent] = {}
        self._by_manufacturer: dict[str, set[AudioComponent]] = defaultdict(set)
        self._by_name: dict[str, AudioComponent] = {}
        self._by_manufacturer_code: dict[str, set[AudioComponent]] = defaultdict(set)
        self._by_factory_function: dict[str, set[AudioComponent]] = defaultdict(set)
        self._by_type_code: dict[str, set[AudioComponent]] = defaultdict(set)
        self._by_subtype_code: dict[str, set[AudioComponent]] = defaultdict(set)
        self._by_tags_id: dict[str, AudioComponent] = {}
        self._by_category: dict[str | None, set[AudioComponent]] = defaultdict(set)

    def add(self, plugin: AudioComponent, *, lazy: bool = False) -> "Plugins":
        self._plugins.add(plugin)
        if not lazy:
            self._index_plugin(plugin)
        return self

    def _index_plugin(self, plugin: AudioComponent):
        if plugin.lazy:
            plugin.load()
            plugin.tagset.load()

        self._by_full_name[plugin.full_name.lower()] = plugin
        self._by_manufacturer[plugin.manufacturer.lower()].add(plugin)
        self._by_name[plugin.name.lower()] = plugin
        self._by_manufacturer_code[plugin.manufacturer_code.lower()].add(plugin)
        self._by_factory_function[plugin.factory_function.lower()].add(plugin)
        self._by_type_code[plugin.type_code.lower()].add(plugin)
        self._by_subtype_code[plugin.subtype_code.lower()].add(plugin)
        self._by_tags_id[plugin.tags_id.lower()] = plugin
        for tag in plugin.tagset.tags.keys():
            self._by_category[tag.lower()].add(plugin)
        if not plugin.tagset.tags.keys():
            self._by_category[None].add(plugin)

    def reindex_all(self):
        self._by_full_name.clear()
        self._by_manufacturer.clear()
        self._by_name.clear()
        self._by_manufacturer_code.clear()
        self._by_factory_function.clear()
        self._by_type_code.clear()
        self._by_subtype_code.clear()
        self._by_tags_id.clear()
        self._by_category.clear()

        for plugin in self._plugins:
            self._index_plugin(plugin)

    def all(self):
        return self._plugins.copy()

    def get_by_full_name(self, full_name: str) -> AudioComponent | None:
        return self._by_full_name.get(full_name.lower())

    def get_by_manufacturer(self, manufacturer: str) -> set[AudioComponent]:
        return self._by_manufacturer.get(manufacturer.lower(), set())

    def get_by_name(self, name: str) -> AudioComponent | None:
        return self._by_name.get(name.lower())

    def get_by_manufacturer_code(self, manufacturer_code: str) -> set[AudioComponent]:
        return self._by_manufacturer_code.get(manufacturer_code.lower(), set())

    def get_by_factory_function(self, factory_function: str) -> set[AudioComponent]:
        return self._by_factory_function.get(factory_function.lower(), set())

    def get_by_type_code(self, type_code: str) -> set[AudioComponent]:
        return self._by_type_code.get(type_code.lower(), set())

    def get_by_subtype_code(self, subtype_code: str) -> set[AudioComponent]:
        return self._by_subtype_code.get(subtype_code.lower(), set())

    def get_by_tags_id(self, tags_id: str) -> AudioComponent | None:
        return self._by_tags_id.get(tags_id.lower())

    def get_by_category(self, category: str | None) -> set[AudioComponent]:
        return self._by_category.get(category.lower(), set())

    def search_simple(self, query: str) -> set[AudioComponent]:
        return {
            plugin
            for plugin in self._plugins
            if query.lower() in plugin.full_name.lower()
        }

    def search(
        self,
        query: str,
        *,
        use_fuzzy: bool = True,
        fuzzy_threshold: int = 80,
        max_results: int | None = None,
    ) -> list[SearchResult]:
        if not query or not query.strip():
            return []

        query = query.strip()
        query_lower = query.lower()

        if use_fuzzy:
            try:
                from rapidfuzz import fuzz
            except ImportError:
                raise ImportError(
                    "Search requires rapidfuzz as additional dependency. "
                    "Please install extra -> logic-plugin-manager[search]"
                )
        else:
            fuzz = None

        results: dict[AudioComponent, SearchResult] = {}

        def add_result(plugin_: AudioComponent, score_: float, field: str):
            if plugin_ in results:
                if score > results[plugin_].score:
                    results[plugin_] = SearchResult(plugin_, score_, field)
            else:
                results[plugin_] = SearchResult(plugin, score_, field)

        exact_match = self._by_tags_id.get(query_lower)
        if exact_match:
            add_result(exact_match, 1000.0, "tags_id")

        for plugin in self._plugins:
            name_lower = plugin.name.lower()
            full_name_lower = plugin.full_name.lower()

            if query_lower in name_lower:
                score = 900.0 if name_lower.startswith(query_lower) else 850.0
                add_result(plugin, score, "name")
            elif query_lower in full_name_lower:
                score = 800.0 if full_name_lower.startswith(query_lower) else 750.0
                add_result(plugin, score, "full_name")
            elif use_fuzzy and len(query) >= 3:
                ratio_name = fuzz.token_set_ratio(query_lower, name_lower)
                ratio_full = fuzz.token_set_ratio(query_lower, full_name_lower)

                best_ratio = max(ratio_name, ratio_full)

                if best_ratio >= fuzzy_threshold:
                    query_tokens = set(query_lower.split())
                    name_tokens = set(full_name_lower.split())
                    all_tokens_present = query_tokens.issubset(name_tokens)

                    base_score = 700.0 if all_tokens_present else 650.0
                    score = base_score + (best_ratio / 100.0 * 50)
                    add_result(plugin, score, "name")

        for plugin in self._plugins:
            manufacturer_lower = plugin.manufacturer.lower()

            if query_lower in manufacturer_lower:
                score = 650.0 if manufacturer_lower.startswith(query_lower) else 620.0
                add_result(plugin, score, "manufacturer")
            elif use_fuzzy and len(query) >= 3:
                ratio = fuzz.token_set_ratio(query_lower, manufacturer_lower)
                if ratio >= fuzzy_threshold:
                    score = 580.0 + (ratio / 100.0 * 40)
                    add_result(plugin, score, "manufacturer")

        for plugin in self._plugins:
            if plugin.tagset and plugin.tagset.tags:
                for tag in plugin.tagset.tags.keys():
                    tag_lower = tag.lower()

                    if query_lower in tag_lower:
                        score = 550.0 if tag_lower.startswith(query_lower) else 520.0
                        add_result(plugin, score, "category")
                        break
                    elif use_fuzzy and len(query) >= 3:
                        ratio = fuzz.ratio(query_lower, tag_lower)
                        if ratio >= fuzzy_threshold:
                            score = 480.0 + (ratio / 100.0 * 40)  # 480-520
                            add_result(plugin, score, "category")
                            break

        type_plugins = self._by_type_code.get(query_lower, set())
        for plugin in type_plugins:
            add_result(plugin, 450.0, "type_code")

        matching_types = AudioUnitType.search(query)
        for audio_type in matching_types:
            type_plugins = self._by_type_code.get(audio_type.code, set())
            for plugin in type_plugins:
                if query_lower == audio_type.display_name.lower():
                    score = 440.0
                else:
                    score = 420.0
                add_result(plugin, score, "type_name")

        if use_fuzzy and len(query) == 4:
            for type_code, plugins in self._by_type_code.items():
                ratio = fuzz.ratio(query_lower, type_code)
                if ratio >= fuzzy_threshold:
                    for plugin in plugins:
                        score = 380.0 + (ratio / 100.0 * 30)  # 380-410
                        add_result(plugin, score, "type_code")

        for plugin in self._plugins:
            subtype_lower = plugin.subtype_code.lower()

            if query_lower in subtype_lower:
                score = 350.0 if subtype_lower.startswith(query_lower) else 330.0
                add_result(plugin, score, "subtype_code")
            elif use_fuzzy and len(query) >= 3 and len(subtype_lower) >= 3:
                ratio = fuzz.ratio(query_lower, subtype_lower)
                if ratio >= fuzzy_threshold:
                    score = 290.0 + (ratio / 100.0 * 30)  # 290-320
                    add_result(plugin, score, "subtype_code")

        for plugin in self._plugins:
            mfr_code_lower = plugin.manufacturer_code.lower()

            if query_lower in mfr_code_lower:
                score = 250.0 if mfr_code_lower.startswith(query_lower) else 230.0
                add_result(plugin, score, "manufacturer_code")
            elif use_fuzzy and len(query) >= 3 and len(mfr_code_lower) >= 3:
                ratio = fuzz.ratio(query_lower, mfr_code_lower)
                if ratio >= fuzzy_threshold:
                    score = 190.0 + (ratio / 100.0 * 30)  # 190-220
                    add_result(plugin, score, "manufacturer_code")

        sorted_results = sorted(results.values(), key=lambda r: r.score, reverse=True)

        if max_results:
            sorted_results = sorted_results[:max_results]

        return sorted_results


__all__ = ["Plugins", "SearchResult"]
