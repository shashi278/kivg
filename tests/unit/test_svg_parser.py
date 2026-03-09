"""
Unit tests for kivg.svg_parser module.
"""

import os
import pytest
from unittest.mock import Mock, patch, mock_open
from xml.dom import minidom

from kivg.svg_parser import parse_svg
from kivg.exceptions import SVGParseError, SVGValidationError
from kivg.constants import DEFAULT_FILL_COLOR


class TestParseSVG:
    """Tests for parse_svg() function."""

    def test_parse_svg_basic_valid_file(self, tmp_path):
        """Test parsing a basic valid SVG file."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 200" xmlns="http://www.w3.org/2000/svg">
            <path id="test_path" d="M 10,10 L 20,20" fill="#FF0000"/>
        </svg>"""

        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert dimensions == [100.0, 200.0]
        assert len(paths) == 1
        assert paths[0][0] == "M 10,10 L 20,20"
        assert paths[0][1] == "test_path"
        assert len(paths[0][2]) == 4  # RGBA color

    def test_parse_svg_viewbox_comma_separated(self, tmp_path):
        """Test parsing viewBox with comma separators."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0,0,150,250" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert dimensions == [150.0, 250.0]

    def test_parse_svg_viewbox_space_separated(self, tmp_path):
        """Test parsing viewBox with space separators."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 300 400" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert dimensions == [300.0, 400.0]

    def test_parse_svg_multiple_paths(self, tmp_path):
        """Test parsing SVG with multiple paths."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path id="path1" d="M 0,0 L 10,10" fill="#FF0000"/>
            <path id="path2" d="M 20,20 L 30,30" fill="#00FF00"/>
            <path id="path3" d="M 40,40 L 50,50" fill="#0000FF"/>
        </svg>"""

        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert len(paths) == 3
        assert paths[0][1] == "path1"
        assert paths[1][1] == "path2"
        assert paths[2][1] == "path3"

    def test_parse_svg_path_without_id(self, tmp_path):
        """Test parsing path without id attribute - should generate default."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0 L 10,10"/>
        </svg>"""

        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert len(paths) == 1
        assert paths[0][1] == "path_0"  # Default generated ID

    def test_parse_svg_multiple_paths_without_id(self, tmp_path):
        """Test multiple paths without IDs get unique generated IDs."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
            <path d="M 10,10"/>
            <path d="M 20,20"/>
        </svg>"""

        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert len(paths) == 3
        assert paths[0][1] == "path_0"
        assert paths[1][1] == "path_1"
        assert paths[2][1] == "path_2"

    def test_parse_svg_path_without_fill(self, tmp_path):
        """Test path without fill attribute uses default color."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path id="test" d="M 0,0 L 10,10"/>
        </svg>"""

        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert len(paths) == 1
        assert paths[0][2] == list(DEFAULT_FILL_COLOR)

    def test_parse_svg_empty_path_skipped(self, tmp_path):
        """Test that paths without 'd' attribute are skipped."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path id="empty" d=""/>
            <path id="valid" d="M 0,0 L 10,10"/>
            <path id="no_d"/>
        </svg>"""

        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        # Only the valid path should be included
        assert len(paths) == 1
        assert paths[0][1] == "valid"

    def test_parse_svg_hex_color_formats(self, tmp_path):
        """Test various hex color formats are parsed correctly."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path id="p1" d="M 0,0" fill="#FF0000"/>
            <path id="p2" d="M 0,0" fill="#00FF00"/>
            <path id="p3" d="M 0,0" fill="#0000FF"/>
        </svg>"""

        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert len(paths) == 3
        # Each path should have RGBA color array
        for path in paths:
            assert len(path[2]) == 4
            assert all(0 <= c <= 1 for c in path[2])  # All values normalized 0-1

    def test_parse_svg_invalid_color_uses_default(self, tmp_path):
        """Test that invalid color formats fall back to default."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path id="gradient" d="M 0,0" fill="url(#myGradient)"/>
            <path id="invalid" d="M 0,0" fill="notacolor"/>
        </svg>"""

        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert len(paths) == 2
        # Both should use default color
        assert paths[0][2] == list(DEFAULT_FILL_COLOR)
        assert paths[1][2] == list(DEFAULT_FILL_COLOR)

    def test_parse_svg_file_not_found(self):
        """Test error raised when file doesn't exist."""
        with pytest.raises(SVGParseError, match="SVG file not found"):
            parse_svg("/nonexistent/path/file.svg")

    def test_parse_svg_invalid_xml(self, tmp_path):
        """Test error raised for invalid XML content."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100">
            <path d="M 0,0"
        </svg>"""  # Missing closing tag

        svg_file = tmp_path / "invalid.svg"
        svg_file.write_text(svg_content)

        with pytest.raises(SVGParseError, match="Failed to parse SVG file"):
            parse_svg(str(svg_file))

    def test_parse_svg_missing_svg_element(self, tmp_path):
        """Test error raised when no <svg> element found."""
        xml_content = """<?xml version="1.0"?>
        <root>
            <path d="M 0,0"/>
        </root>"""

        svg_file = tmp_path / "nosv.svg"
        svg_file.write_text(xml_content)

        with pytest.raises(SVGValidationError, match="No <svg> element found"):
            parse_svg(str(svg_file))

    def test_parse_svg_missing_viewbox(self, tmp_path):
        """Test error raised when viewBox attribute is missing."""
        svg_content = """<?xml version="1.0"?>
        <svg xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "noviewbox.svg"
        svg_file.write_text(svg_content)

        with pytest.raises(SVGValidationError, match="SVG missing 'viewBox' attribute"):
            parse_svg(str(svg_file))

    def test_parse_svg_invalid_viewbox_format(self, tmp_path):
        """Test error raised for invalid viewBox format."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="invalid format" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "badviewbox.svg"
        svg_file.write_text(svg_content)

        with pytest.raises(SVGValidationError, match="Invalid viewBox format"):
            parse_svg(str(svg_file))

    def test_parse_svg_viewbox_too_few_values(self, tmp_path):
        """Test error raised when viewBox has insufficient values."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "shortviewbox.svg"
        svg_file.write_text(svg_content)

        with pytest.raises(SVGValidationError, match="Invalid viewBox format"):
            parse_svg(str(svg_file))

    def test_parse_svg_viewbox_negative_dimensions(self, tmp_path):
        """Test error raised for negative viewBox dimensions."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 -100 200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "negdims.svg"
        svg_file.write_text(svg_content)

        with pytest.raises(SVGValidationError, match="Invalid viewBox format"):
            parse_svg(str(svg_file))

    def test_parse_svg_viewbox_zero_dimensions(self, tmp_path):
        """Test error raised for zero viewBox dimensions."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 0 100" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "zerodims.svg"
        svg_file.write_text(svg_content)

        with pytest.raises(SVGValidationError, match="Invalid viewBox format"):
            parse_svg(str(svg_file))

    def test_parse_svg_viewbox_non_numeric(self, tmp_path):
        """Test error raised for non-numeric viewBox values."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 abc def" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "nonnumeric.svg"
        svg_file.write_text(svg_content)

        with pytest.raises(SVGValidationError, match="Invalid viewBox format"):
            parse_svg(str(svg_file))

    def test_parse_svg_decimal_viewbox_dimensions(self, tmp_path):
        """Test parsing viewBox with decimal dimensions."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 123.45 678.90" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "decimal.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert dimensions == [123.45, 678.90]

    def test_parse_svg_complex_path_data(self, tmp_path):
        """Test parsing complex path data strings."""
        complex_path = "M 10,10 L 20,20 C 30,30 40,40 50,50 Q 60,60 70,70 Z"
        svg_content = f"""<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path id="complex" d="{complex_path}" fill="#123456"/>
        </svg>"""

        svg_file = tmp_path / "complex.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert len(paths) == 1
        assert paths[0][0] == complex_path
        assert paths[0][1] == "complex"

    def test_parse_svg_no_paths(self, tmp_path):
        """Test parsing SVG with no path elements."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="40"/>
        </svg>"""

        svg_file = tmp_path / "nopaths.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert dimensions == [100.0, 100.0]
        assert len(paths) == 0

    def test_parse_svg_mixed_valid_invalid_paths(self, tmp_path):
        """Test parsing with mix of valid and invalid paths."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path id="p1" d="M 0,0"/>
            <path id="p2" d=""/>
            <path id="p3"/>
            <path id="p4" d="M 10,10"/>
        </svg>"""

        svg_file = tmp_path / "mixed.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        # Only p1 and p4 should be included
        assert len(paths) == 2
        assert paths[0][1] == "p1"
        assert paths[1][1] == "p4"

    def test_parse_svg_whitespace_in_viewbox(self, tmp_path):
        """Test that viewBox with extra whitespace raises error (not handled)."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="  0   0   100   200  " xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "whitespace.svg"
        svg_file.write_text(svg_content)

        # Extra whitespace causes split to produce empty strings, leading to error
        with pytest.raises(SVGValidationError, match="Invalid viewBox format"):
            parse_svg(str(svg_file))

    def test_parse_svg_preserves_path_order(self, tmp_path):
        """Test that path order is preserved."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path id="first" d="M 0,0"/>
            <path id="second" d="M 10,10"/>
            <path id="third" d="M 20,20"/>
            <path id="fourth" d="M 30,30"/>
        </svg>"""

        svg_file = tmp_path / "order.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert len(paths) == 4
        assert paths[0][1] == "first"
        assert paths[1][1] == "second"
        assert paths[2][1] == "third"
        assert paths[3][1] == "fourth"

    def test_parse_svg_return_types(self, tmp_path):
        """Test that return types are correct."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path id="test" d="M 0,0" fill="#FF0000"/>
        </svg>"""

        svg_file = tmp_path / "types.svg"
        svg_file.write_text(svg_content)

        result = parse_svg(str(svg_file))

        # Check return is a tuple
        assert isinstance(result, tuple)
        assert len(result) == 2

        dimensions, paths = result

        # Check dimensions is a list of floats
        assert isinstance(dimensions, list)
        assert len(dimensions) == 2
        assert all(isinstance(d, float) for d in dimensions)

        # Check paths is a list of tuples
        assert isinstance(paths, list)
        assert all(isinstance(p, tuple) for p in paths)
        assert all(len(p) == 3 for p in paths)

        # Check path tuple structure: (str, str, list)
        path = paths[0]
        assert isinstance(path[0], str)  # path data
        assert isinstance(path[1], str)  # path id
        assert isinstance(path[2], list)  # color
        assert all(isinstance(c, float) for c in path[2])

    def test_parse_svg_large_viewbox_values(self, tmp_path):
        """Test parsing with large viewBox dimensions."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 10000 20000" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "large.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert dimensions == [10000.0, 20000.0]

    def test_parse_svg_small_decimal_viewbox(self, tmp_path):
        """Test parsing with small decimal viewBox dimensions."""
        svg_content = """<?xml version="1.0"?>
        <svg viewBox="0 0 0.5 1.25" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0,0"/>
        </svg>"""

        svg_file = tmp_path / "small.svg"
        svg_file.write_text(svg_content)

        dimensions, paths = parse_svg(str(svg_file))

        assert dimensions == [0.5, 1.25]
