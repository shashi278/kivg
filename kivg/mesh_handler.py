"""
Mesh generation and handling for SVG shapes.

This module provides mesh tesselation and rendering capabilities
for filling SVG shapes with colors using Kivy's mesh system.
"""

from typing import List, Tuple, Any

from kivy.graphics import Mesh as KivyMesh, Color
from kivy.graphics.tesselator import Tesselator, WINDING_ODD, TYPE_POLYGONS

from .constants import TESSELATION_WINDING, TESSELATION_TYPE


class MeshHandler:
    """
    Handler for mesh generation and rendering of SVG paths.

    This class handles the tesselation of SVG paths into triangular meshes
    that can be rendered with colors/fills in Kivy. Uses Kivy's tesselator
    to convert path contours into renderable triangle meshes.
    """

    @staticmethod
    def create_tesselator(shapes: List[List[float]]) -> Tesselator:
        """
        Create a tesselator for the given shapes.

        Args:
            shapes: List of shapes where each shape is a list of point coordinates
                   [x1, y1, x2, y2, ...]. Minimum 3 points (6 coordinates) required.

        Returns:
            Tesselator object with added contours ready for tesselation

        Example:
            >>> shapes = [[0, 0, 100, 0, 100, 100, 0, 100]]  # Square
            >>> tess = MeshHandler.create_tesselator(shapes)
        """
        tess = Tesselator()
        for shape in shapes:
            if len(shape) >= 6:  # Minimum 3 points (6 coordinates) required
                tess.add_contour(shape)
        return tess

    @staticmethod
    def generate_meshes(
        shapes: List[List[float]],
    ) -> List[Tuple[List[float], List[int]]]:
        """
        Generate triangle meshes from the given shapes using tesselation.

        Args:
            shapes: List of shapes where each shape is a list of point coordinates

        Returns:
            List of (vertices, indices) tuples where:
            - vertices: List of vertex coordinates [x1, y1, x2, y2, ...]
            - indices: List of triangle indices for rendering

        Example:
            >>> shapes = [[0, 0, 100, 0, 100, 100]]
            >>> meshes = MeshHandler.generate_meshes(shapes)
            >>> vertices, indices = meshes[0]
        """
        tess = MeshHandler.create_tesselator(shapes)
        tess.tesselate(TESSELATION_WINDING, TESSELATION_TYPE)
        return tess.meshes

    @staticmethod
    def render_mesh(
        widget: Any, shapes: List[List[float]], color: List[float], opacity_attr: str
    ) -> None:
        """
        Render filled meshes onto the widget canvas.

        Generates triangle meshes from shapes and renders them with the specified
        color and opacity. The opacity is read from a widget attribute to enable
        animation of the fill opacity.

        Args:
            widget: Kivy widget that contains the canvas to render on
            shapes: List of shapes where each shape is a list of point coordinates
            color: RGB or RGBA color values [r, g, b] or [r, g, b, a]
            opacity_attr: Name of the widget attribute containing opacity value (0.0-1.0)

        Example:
            >>> shapes = [[0, 0, 100, 0, 100, 100, 0, 100]]
            >>> color = [1.0, 0.0, 0.0]  # Red
            >>> MeshHandler.render_mesh(widget, shapes, color, "mesh_opacity")
        """
        meshes = MeshHandler.generate_meshes(shapes)
        # Get the opacity value, using 1.0 as a default if the attribute doesn't exist
        opacity = getattr(widget, opacity_attr, 1.0)

        with widget.canvas:
            Color(*color[:3], opacity)
            for vertices, indices in meshes:
                KivyMesh(vertices=vertices, indices=indices, mode="triangle_fan")
