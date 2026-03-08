"""
Shape-specific animation functionality for Kivg.
"""
from kivg.animation.kivy_animation import Animation
from typing import Dict, List, Tuple

from kivg.data_classes import AnimationContext
from ..path_utils import find_center, line_points, bezier_points
from svg.path.path import Line, CubicBezier

class ShapeAnimator:
    """
    Handles creation and management of shape-specific animations.
    
    Provides functionality to animate individual shapes from different directions
    (left, right, top, bottom, center) with customizable transitions and durations.
    """
    
    @staticmethod
    def setup_animation(caller: Any, context: AnimationContext) -> Optional[List[Animation]]:
        """
        Set up the animation for a given shape.
        
        Creates animations for all path elements (lines and beziers) within a shape,
        animating them from a base point determined by the direction parameter.
        
        Args:
            caller: The widget or Kivg instance calling the animation
            context: AnimationContext containing:
                    - widget: Widget to animate
                    - shape_id: ID of the shape to animate
                    - direction: Animation direction (left/right/top/bottom/center_x/center_y/None)
                    - transition: Transition type (e.g., "out_sine", "out_back")
                    - duration: Duration in seconds
                    - closed_shapes: SVG path data
                    - sw_size: SVG dimensions
                    - svg_file: SVG file path
                    
        Returns:
            List of Animation objects for each path element, or None if shape not found
            
        Example:
            >>> context = AnimationContext(
            ...     widget=widget, shape_id="icon", direction="left",
            ...     transition="out_back", duration=0.5, ...
            ... )
            >>> anims = ShapeAnimator.setup_animation(kivg, context)
        """

        if context.shape_id not in context.closed_shapes:
            return None
        
        caller.prev_shapes = []
        caller.curr_shape = []

        line_count = 0
        bezier_count = 0
        anim_list = []

        # Extract path data and transform to animation format
        path_data = ShapeAnimator._extract_path_data(
            context.widget, context.shape_id, context.closed_shapes, 
            context.sw_size, context.svg_file
        )
        
        if not path_data:
            return None
        
        # Calculate base point for animation, can be None if direct reveal
        base_point = ShapeAnimator._calculate_base_point(path_data, context.direction)
        
        # Set up animation properties for each path element
        for i, path_elements in enumerate(path_data):
            for j, element in enumerate(path_elements):
                if len(element) == 2:  # Line
                    new_anims = ShapeAnimator._setup_line_animation(
                        context.widget, context.shape_id, line_count, element, base_point, 
                        context.direction, context.transition, context.duration
                    )
                    anim_list.append(new_anims)
                    line_count += 1
                    
                elif len(element) == 4:  # Bezier
                    new_anims = ShapeAnimator._setup_bezier_animation(
                        context.widget, context.shape_id, bezier_count, element, base_point, 
                        context.direction, context.transition, context.duration
                    )
                    anim_list.append(new_anims)
                    bezier_count += 1

        # Store the extracted path data for later use
        setattr(caller, f"{context.shape_id}_tmp", path_data)
        return anim_list
    
    @staticmethod
    def _extract_path_data(widget: Any, shape_id: str, closed_shapes: Dict, 
                          sw_size: Tuple[float, float], sf: str) -> List[List[Tuple[float, float]]]:
        """
        Extract and transform path data for animation.
        
        Converts SVG path elements into coordinate tuples suitable for animation setup.
        
        Args:
            widget: Widget containing size and position
            shape_id: ID of the shape to extract
            closed_shapes: OrderedDict of all shapes from SVG
            sw_size: SVG dimensions (width, height)
            sf: SVG file path
            
        Returns:
            Nested list of path elements as coordinate tuples:
            Lines: [[start, end], ...]
            Beziers: [[start, control1, control2, end], ...]
        """
        result = []
        
        for path in closed_shapes[shape_id][shape_id + "paths"]:
            path_elements = []
            
            for element in path:
                if isinstance(element, Line):
                    lp = line_points(
                        element, [*widget.size], [*widget.pos], 
                        [*sw_size], sf
                    )
                    path_elements.append([
                        (lp[0], lp[1]),
                        (lp[2], lp[3])
                    ])
                    
                elif isinstance(element, CubicBezier):
                    bp = bezier_points(
                        element, [*widget.size], [*widget.pos], 
                        [*sw_size], sf
                    )
                    path_elements.append([
                        (bp[0], bp[1]),
                        (bp[2], bp[3]),
                        (bp[4], bp[5]),
                        (bp[6], bp[7])
                    ])
            
            result.append(path_elements)
            
        return result
    
    @staticmethod
    def _calculate_base_point(path_data: List[List[Tuple[float, float]]], 
                             direction: Optional[str]) -> Optional[float]:
        """
        Calculate the starting point for an animation based on direction.
        
        Determines the base coordinate from which all path elements should
        animate. For example, "left" means all elements start from the leftmost
        point and animate to their final positions.
        
        Args:
            path_data: Nested list of path elements with coordinate tuples
            direction: Animation direction - one of:
                      "left", "right", "top", "bottom", "center_x", "center_y", None
            
        Returns:
            Base coordinate value (x or y depending on direction), or None if no direction
            
        Example:
            >>> path_data = [[[( 10, 20), (50, 60)]]]  # One line
            >>> base = ShapeAnimator._calculate_base_point(path_data, "left")
            >>> # Returns 10 (leftmost x coordinate)
        """
        if not direction:
            return None
            
        coordinates = []
        
        # Extract relevant coordinates based on direction
        for path in path_data:
            for element in path:
                for point in element:
                    if direction in ("left", "right", "center_x"):
                        coordinates.append(point[0])  # X coordinates
                    else:
                        coordinates.append(point[1])  # Y coordinates

        # Determine base point based on direction
        if direction in ("top", "right"):
            return max(coordinates)  # Start from rightmost/topmost point
        elif direction in ("left", "bottom"):
            return min(coordinates)  # Start from leftmost/bottommost point
        elif direction in ("center_x", "center_y"):
            return find_center(sorted(coordinates))
        return
    
    @staticmethod
    def _setup_line_animation(widget: Any, shape_id: str, line_count: int, 
                              line_points: List[Tuple[float, float]], 
                              base_point: Optional[float], direction: Optional[str], 
                              transition: str, duration: float) -> Animation:
        """
        Set up animation for a line element.
        
        Creates initial widget properties and Animation object for a line
        that will animate from base_point to its final position.
        
        Args:
            widget: Widget to set properties on
            shape_id: ID of the shape (used as property prefix)
            line_count: Index of this line within the shape
            line_points: [(start_x, start_y), (end_x, end_y)]
            base_point: Starting coordinate for animation (x or y value)
            direction: Animation direction (determines which coordinate to animate)
            transition: Kivy transition type (e.g., "out_sine", "out_back")
            duration: Animation duration in seconds
            
        Returns:
            Animation object for this line
        """
        is_horizontal = direction in ("left", "right", "center_x") if direction else False
        is_vertical = direction in ("top", "bottom", "center_y") if direction else False
        start_point, end_point = line_points
        
        # Set initial property values
        setattr(
            widget, 
            f"{shape_id}_mesh_line{line_count}_start_x",
            base_point if is_horizontal else start_point[0]
        )
        setattr(
            widget, 
            f"{shape_id}_mesh_line{line_count}_start_y",
            base_point if is_vertical else start_point[1]
        )
        setattr(
            widget, 
            f"{shape_id}_mesh_line{line_count}_end_x",
            base_point if is_horizontal else end_point[0]
        )
        setattr(
            widget, 
            f"{shape_id}_mesh_line{line_count}_end_y",
            base_point if is_vertical else end_point[1]
        )

        # Create animation properties
        anim_props = {}
        if is_horizontal:
            anim_props = {
                f"{shape_id}_mesh_line{line_count}_start_x": start_point[0],
                f"{shape_id}_mesh_line{line_count}_end_x": end_point[0]
            }
        else:
            anim_props = {
                f"{shape_id}_mesh_line{line_count}_start_y": start_point[1],
                f"{shape_id}_mesh_line{line_count}_end_y": end_point[1]
            }
        return Animation(d=duration, t=transition, **anim_props)
    
    @staticmethod
    def _setup_bezier_animation(widget, shape_id: str, bezier_count: int, 
                                bezier_points: List[Tuple[float, float]],
                                base_point: float, direction: str, 
                                transition: str, duration: float):
        """Set up animation for a bezier curve element."""
        is_horizontal = direction in ("left", "right", "center_x")
        is_vertical = direction in ("top", "bottom", "center_y")
        start, ctrl1, ctrl2, end = bezier_points
        
        # Set initial properties
        ShapeAnimator._set_bezier_properties(
            widget, shape_id, bezier_count, start, ctrl1, ctrl2, end,
            base_point, is_horizontal, is_vertical
        )
        
        # Create animation properties
        anim_props = {}
        if is_horizontal:
            anim_props = {
                f"{shape_id}_mesh_bezier{bezier_count}_start_x": start[0],
                f"{shape_id}_mesh_bezier{bezier_count}_control1_x": ctrl1[0],
                f"{shape_id}_mesh_bezier{bezier_count}_control2_x": ctrl2[0],
                f"{shape_id}_mesh_bezier{bezier_count}_end_x": end[0]
            }
        else:
            anim_props = {
                f"{shape_id}_mesh_bezier{bezier_count}_start_y": start[1],
                f"{shape_id}_mesh_bezier{bezier_count}_control1_y": ctrl1[1],
                f"{shape_id}_mesh_bezier{bezier_count}_control2_y": ctrl2[1],
                f"{shape_id}_mesh_bezier{bezier_count}_end_y": end[1]
            }
        
        return Animation(d=duration, t=transition, **anim_props)
    
    @staticmethod
    def _set_bezier_properties(widget, shape_id: str, index: int, start: Tuple[float, float], 
                              ctrl1: Tuple[float, float], ctrl2: Tuple[float, float], 
                              end: Tuple[float, float], base_point: float, 
                              is_horizontal: bool, is_vertical: bool) -> None:
        """Set initial bezier curve properties."""
        # Start point
        setattr(
            widget, 
            f"{shape_id}_mesh_bezier{index}_start_x",
            base_point if is_horizontal else start[0]
        )
        setattr(
            widget, 
            f"{shape_id}_mesh_bezier{index}_start_y",
            base_point if is_vertical else start[1]
        )
        
        # Control point 1
        setattr(
            widget, 
            f"{shape_id}_mesh_bezier{index}_control1_x",
            base_point if is_horizontal else ctrl1[0]
        )
        setattr(
            widget, 
            f"{shape_id}_mesh_bezier{index}_control1_y",
            base_point if is_vertical else ctrl1[1]
        )
        
        # Control point 2
        setattr(
            widget, 
            f"{shape_id}_mesh_bezier{index}_control2_x",
            base_point if is_horizontal else ctrl2[0]
        )
        setattr(
            widget, 
            f"{shape_id}_mesh_bezier{index}_control2_y",
            base_point if is_vertical else ctrl2[1]
        )
        
        # End point
        setattr(
            widget, 
            f"{shape_id}_mesh_bezier{index}_end_x",
            base_point if is_horizontal else end[0]
        )
        setattr(
            widget, 
            f"{shape_id}_mesh_bezier{index}_end_y",
            base_point if is_vertical else end[1]
        )
