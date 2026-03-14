"""
Constants and default values for Kivg library.

This module centralizes all magic numbers and strings used throughout
the codebase to improve maintainability and consistency.
"""

from enum import Enum
from typing import Tuple

from kivy.graphics.tesselator import TYPE_POLYGONS, WINDING_ODD


class AnimationType(Enum):
    """Animation sequence types."""

    SEQUENTIAL = "seq"
    PARALLEL = "par"


class AnimationDirection(Enum):
    """Directions for shape animations."""

    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    CENTER_X = "center_x"
    CENTER_Y = "center_y"
    NONE = None


class AnimationTransition(Enum):
    """Common animation transition types."""

    OUT_SINE = "out_sine"
    OUT_BOUNCE = "out_bounce"
    OUT_ELASTIC = "out_elastic"
    OUT_BACK = "out_back"
    OUT_CUBIC = "out_cubic"
    OUT_QUINT = "out_quint"
    OUT_CIRC = "out_circ"


# Default rendering values
DEFAULT_LINE_WIDTH: int = 2
DEFAULT_LINE_COLOR: Tuple[float, float, float, float] = (0, 0, 0, 1)
DEFAULT_FILL_COLOR: Tuple[float, float, float, float] = (
    1,
    1,
    1,
    0,
)  # Transparent white
DEFAULT_ANIMATION_DURATION: float = 0.02
DEFAULT_FILL_ANIMATION_DURATION: float = 0.4

# Default shape animation values
DEFAULT_SHAPE_ANIM_DURATION: float = 0.3
DEFAULT_SHAPE_ANIM_TRANSITION: str = "out_sine"

# Path calculation constants
DEFAULT_BEZIER_SEGMENTS: int = 40

# Tesselation constants
TESSELATION_WINDING: int = WINDING_ODD
TESSELATION_TYPE: int = TYPE_POLYGONS
TESSELATION_MODE: str = "triangle_fan"

# SVG coordinate system
SVG_ORIGIN_TOP_LEFT: bool = True
KIVY_ORIGIN_BOTTOM_LEFT: bool = True

# Special handling
SPECIAL_ICON_KEYWORD: str = "kivy"
SPECIAL_ICON_SCALE_FACTOR: float = 10.0

# Property naming patterns
LINE_PROPERTY_PREFIX: str = "line"
BEZIER_PROPERTY_PREFIX: str = "bezier"
MESH_LINE_PROPERTY_PREFIX: str = "mesh_line"
MESH_BEZIER_PROPERTY_PREFIX: str = "mesh_bezier"
MESH_OPACITY_PROPERTY: str = "mesh_opacity"

# Property suffixes
PROPERTY_START_X: str = "start_x"
PROPERTY_START_Y: str = "start_y"
PROPERTY_END_X: str = "end_x"
PROPERTY_END_Y: str = "end_y"
PROPERTY_CONTROL1_X: str = "control1_x"
PROPERTY_CONTROL1_Y: str = "control1_y"
PROPERTY_CONTROL2_X: str = "control2_x"
PROPERTY_CONTROL2_Y: str = "control2_y"
PROPERTY_WIDTH: str = "width"

# Path data suffixes
PATH_SUFFIX: str = "paths"
SHAPE_SUFFIX: str = "shapes"
COLOR_KEY: str = "color"
