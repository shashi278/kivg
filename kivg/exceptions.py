"""
Custom exceptions for the Kivg library.

This module defines all custom exception classes used throughout
the Kivg library to provide clear error messages and better
exception handling.
"""


class KivgError(Exception):
    """Base exception for all Kivg-related errors."""

    pass


class SVGParseError(KivgError):
    """
    Raised when an SVG file cannot be parsed.

    This typically occurs when:
    - The file is not valid XML
    - The file is not a valid SVG
    - Required SVG elements are missing
    """

    pass


class SVGValidationError(KivgError):
    """
    Raised when SVG structure is invalid.

    This occurs when:
    - ViewBox attribute is missing or invalid
    - Path data is malformed
    - Required attributes are missing
    """

    pass


class AnimationConfigError(KivgError):
    """
    Raised when animation configuration is invalid.

    This occurs when:
    - Required configuration keys are missing
    - Configuration values are invalid
    - Shape ID references don't exist
    """

    pass


class CoordinateTransformError(KivgError):
    """
    Raised when coordinate transformation fails.

    This occurs when:
    - SVG dimensions are invalid (zero or negative)
    - Widget dimensions are invalid
    - Coordinate values are out of range
    """

    pass


class WidgetError(KivgError):
    """
    Raised when widget is invalid or incompatible.

    This occurs when:
    - Widget doesn't have required attributes
    - Widget is not a Kivy widget
    - Widget canvas is not accessible
    """

    pass


class SVGFileNotFoundError(KivgError):
    """
    Raised when SVG file is not found.

    This occurs when:
    - File path doesn't exist
    - File path is inaccessible
    """

    pass
