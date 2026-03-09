"""
SVG parsing utilities for Kivg.
Handles parsing SVG files and extracting path data.
"""

import os
from typing import Tuple, List
from xml.dom import minidom

from kivy.utils import get_color_from_hex

from .constants import DEFAULT_FILL_COLOR
from .exceptions import SVGParseError, SVGValidationError


def parse_svg(svg_file: str) -> Tuple[List[float], List[Tuple[str, str, List[float]]]]:
    """
    Parse an SVG file and extract relevant information.

    Extracts viewBox dimensions and path elements with their IDs and fill colors.

    Args:
        svg_file: Path to the SVG file

    Returns:
        Tuple containing (svg_dimensions, path_data)
            - svg_dimensions: [width, height] from viewBox
            - path_data: List of tuples (path_string, element_id, color)

    Raises:
        SVGParseError: If file cannot be parsed or is invalid XML
        SVGValidationError: If SVG structure is invalid

    Example:
        >>> dimensions, paths = parse_svg("icon.svg")
        >>> print(dimensions)
        [100.0, 100.0]
        >>> print(paths[0])
        ('M 10,10 L 90,90', 'path1', [1.0, 0.0, 0.0, 1.0])
    """
    # Validate file exists
    if not os.path.exists(svg_file):
        raise SVGParseError(f"SVG file not found: {svg_file}")

    # Parse XML
    try:
        doc = minidom.parse(svg_file)
    except Exception as e:
        raise SVGParseError(f"Failed to parse SVG file '{svg_file}': {e}") from e

    # Extract viewBox
    svg_elements = doc.getElementsByTagName("svg")
    if not svg_elements:
        doc.unlink()
        raise SVGValidationError(f"No <svg> element found in '{svg_file}'")

    svg_element = svg_elements[0]
    viewbox_string = svg_element.getAttribute("viewBox")

    if not viewbox_string:
        doc.unlink()
        raise SVGValidationError(f"SVG missing 'viewBox' attribute in '{svg_file}'")

    # Parse viewBox dimensions
    try:
        if "," in viewbox_string:
            sw_size = list(map(float, viewbox_string.split(",")[2:]))
        else:
            sw_size = list(map(float, viewbox_string.split(" ")[2:]))

        if len(sw_size) != 2 or sw_size[0] <= 0 or sw_size[1] <= 0:
            raise ValueError("Invalid dimensions")
    except (ValueError, IndexError) as e:
        doc.unlink()
        raise SVGValidationError(
            f"Invalid viewBox format in '{svg_file}': {viewbox_string}"
        )

    # Extract path data
    path_count = 0
    path_strings: List[Tuple[str, str, List[float]]] = []

    for path in doc.getElementsByTagName("path"):
        id_ = path.getAttribute("id") or f"path_{path_count}"
        d = path.getAttribute("d")

        if not d:
            # Skip empty paths
            continue

        # Parse fill color
        try:
            fill_attr = path.getAttribute("fill")
            clr = (
                get_color_from_hex(fill_attr) if fill_attr else list(DEFAULT_FILL_COLOR)
            )
        except ValueError:
            # Default if color format is unsupported (e.g., gradients)
            clr = list(DEFAULT_FILL_COLOR)

        path_strings.append((d, id_, clr))
        path_count += 1

    doc.unlink()
    return sw_size, path_strings
