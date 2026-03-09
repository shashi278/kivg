"""
DrawingManager handles SVG path processing and rendering preparation.

This module processes SVG files, extracts path data, and prepares it for
rendering by setting up widget properties for lines and bezier curves.
"""

from collections import OrderedDict
from typing import List, Tuple, Dict, Any, Optional

from svg.path import parse_path
from svg.path.path import Line, CubicBezier, Close, Move

from ..animation.kivy_animation import Animation
from ..path_utils import get_all_points, bezier_points, line_points
from ..svg_parser import parse_svg
from ..constants import DEFAULT_LINE_WIDTH, DEFAULT_ANIMATION_DURATION


class DrawingManager:
    """
    Handles the drawing and rendering of SVG paths.

    This class processes SVG files, extracts path data, and sets up
    widget properties for animated or static rendering of SVG elements.
    """

    @staticmethod
    def process_path_data(svg_file: str) -> Tuple[List[float], OrderedDict, List[Any]]:
        """
        Process SVG file and extract path data.

        Parses the SVG file and organizes paths by shape ID, tracking
        closed paths for mesh generation and individual elements for drawing.

        Args:
            svg_file: Path to the SVG file

        Returns:
            Tuple containing:
            - svg_dimensions: [width, height] from SVG viewBox
            - closed_shapes: OrderedDict mapping shape IDs to their paths and metadata
            - path_elements: Flat list of all path elements (Line, CubicBezier, etc.)

        Raises:
            SVGParseError: If SVG file cannot be parsed

        Example:
            >>> dims, shapes, elements = DrawingManager.process_path_data("icon.svg")
            >>> print(f"SVG size: {dims}, Shapes: {len(shapes)}")
        """
        sw_size, path_strings = parse_svg(svg_file)

        path = []
        closed_shapes = OrderedDict()

        for path_string, id_, clr in path_strings:
            move_found = False
            tmp = []
            closed_shapes[id_] = dict()
            closed_shapes[id_][id_ + "paths"] = []
            closed_shapes[id_][id_ + "shapes"] = []  # for drawing meshes
            closed_shapes[id_]["color"] = clr

            _path = parse_path(path_string)
            for e in _path:
                path.append(e)

                if isinstance(e, Close) or (isinstance(e, Move) and move_found):
                    closed_shapes[id_][id_ + "paths"].append(tmp)
                    move_found = False

                if isinstance(e, Move):  # shape started
                    tmp = []
                    move_found = True

                if not isinstance(e, Move) and move_found:
                    tmp.append(e)

        return sw_size, closed_shapes, path

    @staticmethod
    def calculate_paths(
        widget: Any,
        closed_shapes: OrderedDict,
        svg_size: List[float],
        svg_file: str,
        animate: bool = False,
        line_width: int = DEFAULT_LINE_WIDTH,
        duration: float = DEFAULT_ANIMATION_DURATION,
    ) -> List[Animation]:
        """
        Calculate and set up path properties for rendering.

        Processes all paths and sets widget properties for each line and bezier
        curve. If animating, creates Animation objects for each element.

        Args:
            widget: Kivy widget to draw on (properties will be set on this widget)
            closed_shapes: OrderedDict of path data organized by shape ID
            svg_size: SVG dimensions [width, height] from viewBox
            svg_file: Path to the SVG file
            animate: If True, creates animations for drawing; if False, sets final values
            line_width: Width of the drawn lines in pixels (default: 2)
            duration: Duration for each animation step in seconds (default: 0.02)

        Returns:
            List of Animation objects if animate=True, empty list otherwise

        Example:
            >>> anims = DrawingManager.calculate_paths(
            ...     widget, shapes, [100, 100], "icon.svg",
            ...     animate=True, line_width=2, duration=0.02
            ... )
            >>> print(f"Created {len(anims)} animations")
        """
        line_count = 0
        bezier_count = 0
        anim_list = []

        for id_, closed_paths in closed_shapes.items():
            for s in closed_paths[id_ + "paths"]:
                tmp = []
                for e in s:
                    if isinstance(e, Line):
                        lp = line_points(
                            e, [*widget.size], [*widget.pos], [*svg_size], svg_file
                        )
                        DrawingManager._setup_line_properties(
                            widget, line_count, lp, animate, line_width
                        )

                        if animate:
                            anim_list.append(
                                Animation(
                                    d=duration,
                                    **{
                                        f"line{line_count}_end_x": lp[2],
                                        f"line{line_count}_end_y": lp[3],
                                        f"line{line_count}_width": line_width,
                                    },
                                )
                            )
                        line_count += 1
                        tmp.extend(lp)

                    elif isinstance(e, CubicBezier):
                        bp = bezier_points(
                            e, [*widget.size], [*widget.pos], [*svg_size], svg_file
                        )
                        DrawingManager._setup_bezier_properties(
                            widget, bezier_count, bp, animate, line_width
                        )

                        if animate:
                            anim_list.append(
                                Animation(
                                    d=duration,
                                    **{
                                        f"bezier{bezier_count}_control1_x": bp[2],
                                        f"bezier{bezier_count}_control1_y": bp[3],
                                        f"bezier{bezier_count}_control2_x": bp[4],
                                        f"bezier{bezier_count}_control2_y": bp[5],
                                        f"bezier{bezier_count}_end_x": bp[6],
                                        f"bezier{bezier_count}_end_y": bp[7],
                                        f"bezier{bezier_count}_width": line_width,
                                    },
                                )
                            )
                        bezier_count += 1

                        tmp.extend(
                            get_all_points(
                                (bp[0], bp[1]),
                                (bp[2], bp[3]),
                                (bp[4], bp[5]),
                                (bp[6], bp[7]),
                            )
                        )

                if tmp not in closed_paths[id_ + "shapes"]:
                    closed_paths[id_ + "shapes"].append(tmp)

        return anim_list

    @staticmethod
    def _setup_line_properties(
        widget: Any,
        line_index: int,
        line_points: List[float],
        animate: bool,
        line_width: int,
    ) -> None:
        """
        Set up line properties on the widget for rendering.

        Sets widget attributes like line0_start_x, line0_end_y, etc.
        If animating, starts from start point; if not, sets final values.

        Args:
            widget: Widget to set properties on
            line_index: Index of the line (0-based)
            line_points: Line coordinates [x1, y1, x2, y2]
            animate: If True, set initial animation state; if False, set final state
            line_width: Width of the line in pixels
        """
        setattr(widget, f"line{line_index}_start_x", line_points[0])
        setattr(widget, f"line{line_index}_start_y", line_points[1])
        setattr(
            widget,
            f"line{line_index}_end_x",
            line_points[0] if animate else line_points[2],
        )
        setattr(
            widget,
            f"line{line_index}_end_y",
            line_points[1] if animate else line_points[3],
        )
        setattr(
            widget,
            f"line{line_index}_width",
            1 if animate else line_width,
        )

    @staticmethod
    def _setup_bezier_properties(
        widget: Any,
        bezier_index: int,
        bezier_points: List[float],
        animate: bool,
        line_width: int,
    ) -> None:
        """
        Set up bezier curve properties on the widget for rendering.

        Sets widget attributes like bezier0_start_x, bezier0_control1_x, etc.
        If animating, starts from start point; if not, sets final values.

        Args:
            widget: Widget to set properties on
            bezier_index: Index of the bezier curve (0-based)
            bezier_points: Bezier coordinates [x1, y1, cx1, cy1, cx2, cy2, x2, y2]
            animate: If True, set initial animation state; if False, set final state
            line_width: Width of the curve in pixels
        """
        # Start point
        setattr(widget, f"bezier{bezier_index}_start_x", bezier_points[0])
        setattr(widget, f"bezier{bezier_index}_start_y", bezier_points[1])

        # Control points
        setattr(
            widget,
            f"bezier{bezier_index}_control1_x",
            bezier_points[0] if animate else bezier_points[2],
        )
        setattr(
            widget,
            f"bezier{bezier_index}_control1_y",
            bezier_points[1] if animate else bezier_points[3],
        )
        setattr(
            widget,
            f"bezier{bezier_index}_control2_x",
            bezier_points[0] if animate else bezier_points[4],
        )
        setattr(
            widget,
            f"bezier{bezier_index}_control2_y",
            bezier_points[1] if animate else bezier_points[5],
        )

        # End point
        setattr(
            widget,
            f"bezier{bezier_index}_end_x",
            bezier_points[0] if animate else bezier_points[6],
        )
        setattr(
            widget,
            f"bezier{bezier_index}_end_y",
            bezier_points[1] if animate else bezier_points[7],
        )

        # Width
        setattr(
            widget,
            f"bezier{bezier_index}_width",
            1 if animate else line_width,
        )
