"""Shared pytest fixtures for Kivg tests."""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Tuple


@pytest.fixture
def mock_widget():
    """Create a mock Kivy widget with standard properties."""
    widget = Mock()
    widget.size = [256.0, 256.0]
    widget.pos = [0.0, 0.0]
    widget.x = 0.0
    widget.y = 0.0
    widget.width = 256.0
    widget.height = 256.0
    widget.canvas = Mock()
    return widget


@pytest.fixture
def svg_dimensions() -> Tuple[float, float]:
    """Standard SVG dimensions for testing."""
    return (100.0, 100.0)


@pytest.fixture
def widget_dimensions() -> Tuple[float, float]:
    """Standard widget dimensions for testing."""
    return (256.0, 256.0)


@pytest.fixture
def widget_position() -> Tuple[float, float]:
    """Standard widget position for testing."""
    return (0.0, 0.0)


@pytest.fixture
def svg_file_path() -> str:
    """Standard SVG file path for testing."""
    return "test.svg"


@pytest.fixture
def kivy_svg_file_path() -> str:
    """Kivy icon SVG file path for special handling."""
    return "kivy-icon.svg"


@pytest.fixture
def mock_canvas():
    """Create a mock Kivy canvas with instruction groups."""
    canvas = Mock()
    canvas.clear = Mock()
    canvas.add = Mock()
    return canvas


@pytest.fixture
def mock_color():
    """Create a mock Kivy Color instruction."""
    color = Mock()
    color.rgba = [0.0, 0.0, 0.0, 1.0]
    return color


@pytest.fixture
def mock_line():
    """Create a mock Kivy Line instruction."""
    line = Mock()
    line.points = []
    line.width = 1.0
    return line
