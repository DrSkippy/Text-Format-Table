"""Custom exceptions raised by text_format_table."""


class TextFormatTableError(Exception):
    """Base class for every error raised by this package."""


class InvalidSignificantFiguresError(TextFormatTableError, ValueError):
    """A numeric value was given a non-positive or unparsable significant figure count."""


class ColumnCountMismatchError(TextFormatTableError, ValueError):
    """A row has more columns than the per-column significant figure list covers."""


class ColumnWidthError(TextFormatTableError, ValueError):
    """A value does not fit the requested column width or decimal offset."""


class EmptyTableError(TextFormatTableError, ValueError):
    """A table was created without any rows."""


class ConfigError(TextFormatTableError, ValueError):
    """A configuration file or value is invalid."""
