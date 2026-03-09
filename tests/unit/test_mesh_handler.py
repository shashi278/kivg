"""
Tests for mesh_handler.py - Mesh generation and tesselation.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from kivy.graphics.tesselator import Tesselator, WINDING_ODD, TYPE_POLYGONS

from kivg.mesh_handler import MeshHandler


class TestCreateTesselator:
    """Test MeshHandler.create_tesselator() method."""

    def test_basic_single_shape(self):
        """Test creating tesselator with a single valid shape."""
        shapes = [[0, 0, 100, 0, 100, 100, 0, 100]]  # Square
        tess = MeshHandler.create_tesselator(shapes)

        assert isinstance(tess, Tesselator)
        # Tesselator is created but not yet tesselated
        assert isinstance(tess, Tesselator)

    def test_multiple_shapes(self):
        """Test creating tesselator with multiple shapes."""
        shapes = [
            [0, 0, 100, 0, 100, 100, 0, 100],  # Square
            [200, 200, 300, 200, 250, 300],  # Triangle
        ]
        tess = MeshHandler.create_tesselator(shapes)

        assert isinstance(tess, Tesselator)

    def test_minimum_valid_shape(self):
        """Test with minimum valid shape (3 points = 6 coordinates)."""
        shapes = [[0, 0, 100, 0, 50, 100]]  # Triangle
        tess = MeshHandler.create_tesselator(shapes)

        assert isinstance(tess, Tesselator)

    def test_shape_with_too_few_points(self):
        """Test that shapes with less than 3 points are skipped."""
        shapes = [
            [0, 0, 100, 0],  # Only 2 points - should be skipped
            [0, 0, 100, 0, 100, 100],  # 3 points - should be added
        ]
        tess = MeshHandler.create_tesselator(shapes)

        # Should only contain the valid shape
        assert isinstance(tess, Tesselator)

    def test_empty_shapes_list(self):
        """Test with empty shapes list."""
        shapes = []
        tess = MeshHandler.create_tesselator(shapes)

        assert isinstance(tess, Tesselator)
        # Empty list means no vertices added before tesselate
        assert tess.vertex_count == 0

    def test_all_invalid_shapes(self):
        """Test when all shapes have too few points."""
        shapes = [[0, 0], [0, 0, 100, 0]]  # 1 point  # 2 points
        tess = MeshHandler.create_tesselator(shapes)

        # No valid shapes added
        assert tess.vertex_count == 0

    def test_complex_polygon(self):
        """Test with a complex polygon (many points)."""
        # Hexagon
        shapes = [[50, 0, 100, 25, 100, 75, 50, 100, 0, 75, 0, 25]]
        tess = MeshHandler.create_tesselator(shapes)

        assert isinstance(tess, Tesselator)

    def test_negative_coordinates(self):
        """Test shapes with negative coordinates."""
        shapes = [[-100, -100, 0, -100, -50, 0]]
        tess = MeshHandler.create_tesselator(shapes)

        assert isinstance(tess, Tesselator)

    def test_decimal_coordinates(self):
        """Test shapes with decimal coordinates."""
        shapes = [[0.5, 0.5, 100.7, 0.3, 50.2, 100.9]]
        tess = MeshHandler.create_tesselator(shapes)

        assert isinstance(tess, Tesselator)


class TestGenerateMeshes:
    """Test MeshHandler.generate_meshes() method."""

    def test_basic_triangle_mesh(self):
        """Test generating mesh from a simple triangle."""
        shapes = [[0, 0, 100, 0, 50, 100]]
        meshes = MeshHandler.generate_meshes(shapes)

        assert isinstance(meshes, list)
        assert len(meshes) > 0

        # Each mesh should be a tuple of (vertices, indices)
        vertices, indices = meshes[0]
        # Vertices can be MemoryView or list-like
        assert hasattr(vertices, "__len__")
        assert hasattr(indices, "__len__")
        assert len(vertices) >= 6  # At least 3 points (x,y pairs)
        assert len(indices) >= 3  # At least 1 triangle

    def test_square_mesh(self):
        """Test generating mesh from a square."""
        shapes = [[0, 0, 100, 0, 100, 100, 0, 100]]
        meshes = MeshHandler.generate_meshes(shapes)

        assert len(meshes) > 0
        vertices, indices = meshes[0]
        assert len(vertices) >= 8  # At least 4 points (square corners)

    def test_multiple_shapes_meshes(self):
        """Test generating meshes from multiple shapes."""
        shapes = [
            [0, 0, 100, 0, 100, 100, 0, 100],  # Square
            [200, 200, 300, 200, 250, 300],  # Triangle
        ]
        meshes = MeshHandler.generate_meshes(shapes)

        assert isinstance(meshes, list)
        # Should have at least one mesh (might combine or separate)
        assert len(meshes) >= 1

    def test_empty_shapes(self):
        """Test with empty shapes list."""
        shapes = []
        meshes = MeshHandler.generate_meshes(shapes)

        assert isinstance(meshes, list)
        # Empty input should result in no meshes
        assert len(meshes) == 0

    def test_invalid_shapes_filtered(self):
        """Test that invalid shapes don't produce meshes."""
        shapes = [
            [0, 0, 100, 0],  # Too few points
        ]
        meshes = MeshHandler.generate_meshes(shapes)

        assert len(meshes) == 0

    def test_mesh_vertices_format(self):
        """Test that mesh vertices are in correct format."""
        shapes = [[0, 0, 100, 0, 50, 100]]
        meshes = MeshHandler.generate_meshes(shapes)

        vertices, indices = meshes[0]
        # Vertices should be iterable with even number of values (x,y pairs)
        assert len(vertices) % 2 == 0
        # All vertices should be numbers (can be MemoryView)
        vertex_list = list(vertices)
        assert all(isinstance(v, (int, float)) for v in vertex_list)

    def test_mesh_indices_format(self):
        """Test that mesh indices are in correct format."""
        shapes = [[0, 0, 100, 0, 50, 100]]
        meshes = MeshHandler.generate_meshes(shapes)

        vertices, indices = meshes[0]
        # Indices can be range or list-like
        indices_list = list(indices)
        # Indices should be integers
        assert all(isinstance(i, int) for i in indices_list)
        # Indices should reference valid vertex positions
        max_index = len(vertices) // 2 - 1
        assert all(0 <= i <= max_index for i in indices_list)

    def test_complex_polygon_mesh(self):
        """Test mesh generation for complex polygon."""
        # Pentagon
        shapes = [[50, 0, 100, 35, 80, 100, 20, 100, 0, 35]]
        meshes = MeshHandler.generate_meshes(shapes)

        assert len(meshes) > 0
        vertices, indices = meshes[0]
        assert len(vertices) >= 10  # At least 5 points

    @patch("kivg.mesh_handler.MeshHandler.create_tesselator")
    def test_uses_create_tesselator(self, mock_create_tess):
        """Test that generate_meshes uses create_tesselator."""
        mock_tess = Mock()
        mock_tess.meshes = [([0, 0, 1, 1, 2, 2], [0, 1, 2])]
        mock_create_tess.return_value = mock_tess

        shapes = [[0, 0, 100, 0, 50, 100]]
        meshes = MeshHandler.generate_meshes(shapes)

        mock_create_tess.assert_called_once_with(shapes)
        mock_tess.tesselate.assert_called_once()

    @patch("kivg.mesh_handler.MeshHandler.create_tesselator")
    def test_tesselation_parameters(self, mock_create_tess):
        """Test that correct tesselation parameters are used."""
        mock_tess = Mock()
        mock_tess.meshes = []
        mock_create_tess.return_value = mock_tess

        shapes = [[0, 0, 100, 0, 50, 100]]
        MeshHandler.generate_meshes(shapes)

        # Should use TESSELATION_WINDING and TESSELATION_TYPE constants
        mock_tess.tesselate.assert_called_once()
        args = mock_tess.tesselate.call_args[0]
        # Verify constants are used (they should match Kivy's constants)
        assert len(args) == 2


class TestRenderMesh:
    """Test MeshHandler.render_mesh() method."""

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.Color")
    def test_basic_render(self, mock_color, mock_mesh):
        """Test basic mesh rendering."""
        widget = Mock()
        widget.canvas = MagicMock()
        widget.mesh_opacity = 1.0

        shapes = [[0, 0, 100, 0, 50, 100]]
        color = [1.0, 0.0, 0.0]  # Red

        MeshHandler.render_mesh(widget, shapes, color, "mesh_opacity")

        # Should have entered canvas context
        widget.canvas.__enter__.assert_called()
        # Should have created Color
        mock_color.assert_called()

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.Color")
    def test_opacity_from_widget_attribute(self, mock_color, mock_mesh):
        """Test that opacity is read from widget attribute."""
        widget = Mock()
        widget.canvas = MagicMock()
        widget.custom_opacity = 0.5

        shapes = [[0, 0, 100, 0, 50, 100]]
        color = [1.0, 0.0, 0.0]

        MeshHandler.render_mesh(widget, shapes, color, "custom_opacity")

        # Color should be called with RGB values and opacity
        mock_color.assert_called()
        call_args = mock_color.call_args[0]
        assert call_args[3] == 0.5  # Opacity should be 0.5

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.Color")
    def test_default_opacity_when_attribute_missing(self, mock_color, mock_mesh):
        """Test that default opacity 1.0 is used when attribute doesn't exist."""
        widget = Mock(spec=[])  # Empty spec means no attributes
        widget.canvas = MagicMock()

        shapes = [[0, 0, 100, 0, 50, 100]]
        color = [1.0, 0.0, 0.0]

        MeshHandler.render_mesh(widget, shapes, color, "some_opacity")

        call_args = mock_color.call_args[0]
        assert call_args[3] == 1.0  # Should use default opacity

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.Color")
    def test_rgb_color_format(self, mock_color, mock_mesh):
        """Test rendering with RGB color (3 values)."""
        widget = Mock()
        widget.canvas = MagicMock()
        widget.opacity = 0.8

        shapes = [[0, 0, 100, 0, 50, 100]]
        color = [0.5, 0.7, 0.3]  # RGB

        MeshHandler.render_mesh(widget, shapes, color, "opacity")

        # Should use first 3 color values
        call_args = mock_color.call_args[0]
        assert call_args[0] == 0.5
        assert call_args[1] == 0.7
        assert call_args[2] == 0.3

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.Color")
    def test_rgba_color_format(self, mock_color, mock_mesh):
        """Test rendering with RGBA color (4 values, alpha ignored)."""
        widget = Mock()
        widget.canvas = MagicMock()
        widget.opacity = 0.6

        shapes = [[0, 0, 100, 0, 50, 100]]
        color = [0.5, 0.7, 0.3, 0.9]  # RGBA (alpha should be ignored)

        MeshHandler.render_mesh(widget, shapes, color, "opacity")

        # Should use only first 3 values, alpha from widget attribute
        call_args = mock_color.call_args[0]
        assert call_args[0] == 0.5
        assert call_args[1] == 0.7
        assert call_args[2] == 0.3
        assert call_args[3] == 0.6  # From widget attribute, not color[3]

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.MeshHandler.generate_meshes")
    @patch("kivg.mesh_handler.Color")
    def test_creates_mesh_objects(self, mock_color, mock_gen_meshes, mock_kivy_mesh):
        """Test that Kivy Mesh objects are created for each mesh."""
        widget = Mock()
        widget.canvas = MagicMock()
        widget.opacity = 1.0

        # Mock multiple meshes
        mock_gen_meshes.return_value = [
            ([0, 0, 1, 1, 2, 2], [0, 1, 2]),
            ([10, 10, 11, 11, 12, 12], [0, 1, 2]),
        ]

        shapes = [[0, 0, 100, 0, 50, 100]]
        color = [1.0, 0.0, 0.0]

        MeshHandler.render_mesh(widget, shapes, color, "opacity")

        # Should create two Mesh objects
        assert mock_kivy_mesh.call_count == 2

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.MeshHandler.generate_meshes")
    @patch("kivg.mesh_handler.Color")
    def test_mesh_parameters(self, mock_color, mock_gen_meshes, mock_kivy_mesh):
        """Test that meshes are created with correct parameters."""
        widget = Mock()
        widget.canvas = MagicMock()
        widget.opacity = 1.0

        vertices = [0, 0, 100, 0, 50, 100]
        indices = [0, 1, 2]
        mock_gen_meshes.return_value = [(vertices, indices)]

        shapes = [[0, 0, 100, 0, 50, 100]]
        color = [1.0, 0.0, 0.0]

        MeshHandler.render_mesh(widget, shapes, color, "opacity")

        # Check Mesh was called with correct parameters
        mock_kivy_mesh.assert_called_once_with(
            vertices=vertices, indices=indices, mode="triangle_fan"
        )

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.Color")
    def test_empty_shapes(self, mock_color, mock_mesh):
        """Test rendering with empty shapes."""
        widget = Mock()
        widget.canvas = MagicMock()
        widget.opacity = 1.0

        shapes = []
        color = [1.0, 0.0, 0.0]

        # Should not raise an error
        MeshHandler.render_mesh(widget, shapes, color, "opacity")

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.Color")
    def test_zero_opacity(self, mock_color, mock_mesh):
        """Test rendering with zero opacity."""
        widget = Mock()
        widget.canvas = MagicMock()
        widget.opacity = 0.0

        shapes = [[0, 0, 100, 0, 50, 100]]
        color = [1.0, 0.0, 0.0]

        MeshHandler.render_mesh(widget, shapes, color, "opacity")

        call_args = mock_color.call_args[0]
        assert call_args[3] == 0.0

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.Color")
    def test_full_opacity(self, mock_color, mock_mesh):
        """Test rendering with full opacity."""
        widget = Mock()
        widget.canvas = MagicMock()
        widget.opacity = 1.0

        shapes = [[0, 0, 100, 0, 50, 100]]
        color = [1.0, 0.0, 0.0]

        MeshHandler.render_mesh(widget, shapes, color, "opacity")

        call_args = mock_color.call_args[0]
        assert call_args[3] == 1.0

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.MeshHandler.generate_meshes")
    @patch("kivg.mesh_handler.Color")
    def test_calls_generate_meshes(self, mock_color, mock_gen_meshes, mock_mesh):
        """Test that render_mesh calls generate_meshes."""
        widget = Mock()
        widget.canvas = MagicMock()
        widget.opacity = 1.0

        mock_gen_meshes.return_value = []

        shapes = [[0, 0, 100, 0, 50, 100]]
        color = [1.0, 0.0, 0.0]

        MeshHandler.render_mesh(widget, shapes, color, "opacity")

        mock_gen_meshes.assert_called_once_with(shapes)


class TestIntegration:
    """Integration tests for mesh handling workflow."""

    def test_complete_mesh_pipeline(self):
        """Test the complete pipeline: shapes -> tesselator -> meshes."""
        shapes = [[0, 0, 100, 0, 100, 100, 0, 100]]

        # Step 1: Create tesselator
        tess = MeshHandler.create_tesselator(shapes)
        assert isinstance(tess, Tesselator)

        # Step 2: Generate meshes
        meshes = MeshHandler.generate_meshes(shapes)
        assert len(meshes) > 0

        vertices, indices = meshes[0]
        assert len(vertices) >= 8
        assert len(indices) >= 3

    def test_multiple_shapes_integration(self):
        """Test handling multiple shapes through the pipeline."""
        shapes = [
            [0, 0, 50, 0, 50, 50, 0, 50],  # Small square
            [100, 100, 200, 100, 150, 200],  # Triangle
        ]

        tess = MeshHandler.create_tesselator(shapes)
        assert isinstance(tess, Tesselator)

        meshes = MeshHandler.generate_meshes(shapes)
        assert len(meshes) >= 1

    @patch("kivg.mesh_handler.KivyMesh")
    @patch("kivg.mesh_handler.Color")
    def test_full_render_pipeline(self, mock_color, mock_mesh):
        """Test the complete render pipeline."""
        widget = Mock()
        widget.canvas = MagicMock()
        widget.opacity = 0.7

        shapes = [[0, 0, 100, 0, 50, 100]]
        color = [1.0, 0.5, 0.0]

        MeshHandler.render_mesh(widget, shapes, color, "opacity")

        # Verify Color was set
        mock_color.assert_called_once()
        call_args = mock_color.call_args[0]
        assert call_args[0:3] == (1.0, 0.5, 0.0)
        assert call_args[3] == 0.7

        # Verify Mesh was created
        assert mock_mesh.call_count >= 1
