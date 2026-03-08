"""
SVG rendering functionality for Kivg.

This module handles rendering of SVG path elements (lines, bezier curves)
to Kivy canvas using dynamically set widget properties.
"""
from typing import List, Any, Union

from kivy.graphics import Line as KivyLine, Color
from svg.path.path import Line, CubicBezier, Close, Move

from .path_utils import get_all_points

class SvgRenderer:
    """
    Handles rendering of SVG paths to Kivy canvas.
    
    This class converts SVG path elements (Line, CubicBezier) into Kivy
    drawing instructions by reading coordinate and style properties from
    the target widget that were set during animation setup.
    """
    
    @staticmethod
    def update_canvas(widget: Any, path_elements: List[Union[Line, CubicBezier]], 
                     line_color: List[float]) -> None:
        """
        Update the canvas with the current path elements.
        
        Reads current animation property values from the widget and draws
        lines and bezier curves accordingly. Clears canvas before drawing.
        
        Args:
            widget: Kivy widget to draw on (must have canvas attribute)
            path_elements: List of SVG path elements (Line or CubicBezier objects)
            line_color: RGBA color to use for drawing lines [r, g, b, a]
            
        Example:
            >>> from svg.path import Line
            >>> elements = [Line(0+0j, 100+100j)]
            >>> color = [0, 0, 0, 1]  # Black
            >>> SvgRenderer.update_canvas(widget, elements, color)
        """
        widget.canvas.clear()
        
        with widget.canvas:
            Color(*line_color)
            
            line_count = 0
            bezier_count = 0
            
            # Draw each path element
            for element in path_elements:
                if isinstance(element, Line):
                    SvgRenderer._draw_line(widget, line_count)
                    line_count += 1
                    
                elif isinstance(element, CubicBezier):
                    SvgRenderer._draw_bezier(widget, bezier_count)
                    bezier_count += 1
    
    @staticmethod
    def _draw_line(widget: Any, line_index: int) -> None:
        """
        Draw a line element on the canvas.
        
        Reads line coordinates and width from widget properties that were
        set during animation setup (e.g., line0_start_x, line0_end_y).
        
        Args:
            widget: Kivy widget containing line properties
            line_index: Index of the line (0-based)
        """
        KivyLine(
            points=[
                getattr(widget, f"line{line_index}_start_x"),
                getattr(widget, f"line{line_index}_start_y"),
                getattr(widget, f"line{line_index}_end_x"),
                getattr(widget, f"line{line_index}_end_y"),
            ],
            width=getattr(widget, f"line{line_index}_width"),
        )
    
    @staticmethod
    def _draw_bezier(widget: Any, bezier_index: int) -> None:
        """
        Draw a cubic bezier curve element on the canvas.
        
        Reads bezier control points and width from widget properties that were
        set during animation setup (e.g., bezier0_start_x, bezier0_control1_x).
        
        Args:
            widget: Kivy widget containing bezier properties
            bezier_index: Index of the bezier curve (0-based)
        """
        KivyLine(
            bezier=[
                getattr(widget, f"bezier{bezier_index}_start_x"),
                getattr(widget, f"bezier{bezier_index}_start_y"),
                getattr(widget, f"bezier{bezier_index}_control1_x"),
                getattr(widget, f"bezier{bezier_index}_control1_y"),
                getattr(widget, f"bezier{bezier_index}_control2_x"),
                getattr(widget, f"bezier{bezier_index}_control2_y"),
                getattr(widget, f"bezier{bezier_index}_end_x"),
                getattr(widget, f"bezier{bezier_index}_end_y"),
            ],
            width=getattr(widget, f"bezier{bezier_index}_width"),
        )
    
    @staticmethod
    def collect_shape_points(tmp_elements_lists: List[List[Any]], widget: Any, 
                           shape_id: str) -> List[float]:
        """
        Collect all current points for a shape during animation.
        
        Used during shape_animate to gather all current coordinate values
        for mesh generation. Reads animated property values from the widget.
        
        Args:
            tmp_elements_lists: Nested list of path elements from shape_animate
                              [[element1, element2], [element3, element4], ...]
            widget: Kivy widget containing animated properties
            shape_id: ID of the shape being animated (used as property prefix)
            
        Returns:
            Flat list of all current point coordinates [x1, y1, x2, y2, ...]
            
        Example:
            >>> elements = [[(0, 100), (100, 100)]]  # One line
            >>> points = SvgRenderer.collect_shape_points(elements, widget, "shape1")
            >>> # Returns: [x1, y1, x2, y2] from widget.shape1_mesh_line0_*
        """
        shape_list = []
        line_count = 0
        bezier_count = 0

        for path_elements in tmp_elements_lists:
            for element in path_elements:
                # Collect line points
                if len(element) == 2:  # Line (start, end)
                    shape_list.extend([
                        getattr(widget, f"{shape_id}_mesh_line{line_count}_start_x"),
                        getattr(widget, f"{shape_id}_mesh_line{line_count}_start_y"),
                        getattr(widget, f"{shape_id}_mesh_line{line_count}_end_x"),
                        getattr(widget, f"{shape_id}_mesh_line{line_count}_end_y")
                    ])
                    line_count += 1
                
                # Collect bezier points
                if len(element) == 4:  # Bezier (start, control1, control2, end)
                    shape_list.extend(
                        get_all_points(
                            (getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_start_x"),
                             getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_start_y")),
                            (getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_control1_x"),
                             getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_control1_y")),
                            (getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_control2_x"),
                             getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_control2_y")),
                            (getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_end_x"),
                             getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_end_y"))
                        )
                    )
                    bezier_count += 1
        return shape_list
