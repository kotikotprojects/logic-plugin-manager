class PluginLoadError(Exception):
    pass


class NonexistentPlistError(PluginLoadError):
    pass


class CannotParsePlistError(PluginLoadError):
    pass


class CannotParseComponentError(PluginLoadError):
    pass


class OldComponentFormatError(PluginLoadError):
    pass


class TagsetLoadError(Exception):
    pass


class NonexistentTagsetError(TagsetLoadError):
    pass


class CannotParseTagsetError(TagsetLoadError):
    pass


class TagsetWriteError(TagsetLoadError):
    pass


class MusicAppsLoadError(Exception):
    pass


class MusicAppsWriteError(Exception):
    pass


class CategoryValidationError(Exception):
    pass


class CategoryExistsError(Exception):
    pass
