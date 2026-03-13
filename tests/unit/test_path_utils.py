"""Unit tests for path_utils module."""

from svg.path.path import CubicBezier, Line

from kivg.path_utils import (
    bezier_points,
    find_center,
    get_all_points,
    line_points,
    transform_point,
    transform_x,
    transform_y,
)


class TestTransformX:
    """Tests for transform_x function."""

    def test_basic_transform(self):
        """Test basic X coordinate transformation."""
        result = transform_x(50.0, 0.0, 256.0, 100.0, "test.svg")
        assert result == 128.0

    def test_at_origin(self):
        """Test transformation at origin (x=0)."""
        result = transform_x(0.0, 0.0, 256.0, 100.0, "test.svg")
        assert result == 0.0

    def test_at_maximum(self):
        """Test transformation at maximum SVG width."""
        result = transform_x(100.0, 0.0, 256.0, 100.0, "test.svg")
        assert result == 256.0

    def test_with_widget_offset(self):
        """Test transformation with widget position offset."""
        result = transform_x(50.0, 100.0, 256.0, 100.0, "test.svg")
        assert result == 228.0  # 100 + 128

    def test_kivy_icon_special_handling(self):
        """Test special handling for Kivy SVG icons."""
        result = transform_x(50.0, 0.0, 256.0, 100.0, "kivy-icon.svg")
        # For kivy files: widget_x + (widget_width * (x_pos / 10) / svg_width)
        expected = 0.0 + (256.0 * (50.0 / 10) / 100.0)
        assert result == expected
        assert result == 12.8

    def test_kivy_in_path(self):
        """Test that 'kivy' anywhere in path triggers special handling."""
        result1 = transform_x(50.0, 0.0, 256.0, 100.0, "path/to/kivy/icon.svg")
        result2 = transform_x(50.0, 0.0, 256.0, 100.0, "my-kivy-file.svg")

        expected = 0.0 + (256.0 * (50.0 / 10) / 100.0)
        assert result1 == expected
        assert result2 == expected

    def test_with_decimal_values(self):
        """Test with decimal coordinate values."""
        result = transform_x(33.33, 0.0, 300.0, 100.0, "test.svg")
        assert abs(result - 99.99) < 0.01

    def test_negative_svg_coordinate(self):
        """Test with negative SVG coordinate."""
        result = transform_x(-10.0, 0.0, 256.0, 100.0, "test.svg")
        assert result == -25.6

    def test_different_svg_widths(self):
        """Test with various SVG widths."""
        # Smaller SVG
        result1 = transform_x(25.0, 0.0, 256.0, 50.0, "test.svg")
        assert result1 == 128.0

        # Larger SVG
        result2 = transform_x(100.0, 0.0, 256.0, 200.0, "test.svg")
        assert result2 == 128.0


class TestTransformY:
    """Tests for transform_y function."""

    def test_basic_transform(self):
        """Test basic Y coordinate transformation."""
        # Y is inverted in Kivy: svg_height - y_pos
        result = transform_y(50.0, 0.0, 256.0, 100.0, "test.svg")
        expected = 0.0 + 256.0 * (100.0 - 50.0) / 100.0
        assert result == expected
        assert result == 128.0

    def test_at_top(self):
        """Test transformation at SVG top (y=0)."""
        result = transform_y(0.0, 0.0, 256.0, 100.0, "test.svg")
        # At top of SVG (y=0), should map to bottom of widget
        assert result == 256.0

    def test_at_bottom(self):
        """Test transformation at SVG bottom (y=max)."""
        result = transform_y(100.0, 0.0, 256.0, 100.0, "test.svg")
        # At bottom of SVG (y=100), should map to top of widget
        assert result == 0.0

    def test_with_widget_offset(self):
        """Test transformation with widget position offset."""
        result = transform_y(50.0, 100.0, 256.0, 100.0, "test.svg")
        assert result == 228.0  # 100 + 128

    def test_kivy_icon_special_handling(self):
        """Test special handling for Kivy SVG icons."""
        result = transform_y(50.0, 0.0, 256.0, 100.0, "kivy-icon.svg")
        # For kivy files: widget_y + (widget_height * (y_pos / 10) / svg_height)
        expected = 0.0 + (256.0 * (50.0 / 10) / 100.0)
        assert result == expected
        assert result == 12.8

    def test_y_inversion(self):
        """Test that Y coordinates are properly inverted."""
        # SVG has origin at top-left, Kivy at bottom-left
        y_top = transform_y(0.0, 0.0, 256.0, 100.0, "test.svg")
        y_bottom = transform_y(100.0, 0.0, 256.0, 100.0, "test.svg")

        assert y_top > y_bottom  # Top of SVG = higher in Kivy
        assert y_top == 256.0
        assert y_bottom == 0.0

    def test_with_decimal_values(self):
        """Test with decimal coordinate values."""
        result = transform_y(25.5, 0.0, 300.0, 100.0, "test.svg")
        expected = 0.0 + 300.0 * (100.0 - 25.5) / 100.0
        assert abs(result - expected) < 0.01


class TestTransformPoint:
    """Tests for transform_point function."""

    def test_basic_point_transform(self):
        """Test transforming a complex point to list."""
        point = complex(50.0, 50.0)
        result = transform_point(
            point,
            (256.0, 256.0),  # widget_size
            (0.0, 0.0),  # widget_pos
            (100.0, 100.0),  # svg_size
            "test.svg",
        )

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == 128.0  # X at center
        assert result[1] == 128.0  # Y at center

    def test_origin_point(self):
        """Test transforming origin point (0, 0)."""
        point = complex(0.0, 0.0)
        result = transform_point(
            point, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        assert result[0] == 0.0
        assert result[1] == 256.0  # Y inverted

    def test_max_point(self):
        """Test transforming maximum point."""
        point = complex(100.0, 100.0)
        result = transform_point(
            point, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        assert result[0] == 256.0
        assert result[1] == 0.0  # Y inverted

    def test_with_widget_offset(self):
        """Test point transformation with widget offset."""
        point = complex(0.0, 0.0)
        result = transform_point(
            point, (256.0, 256.0), (100.0, 50.0), (100.0, 100.0), "test.svg"
        )

        assert result[0] == 100.0
        assert result[1] == 306.0  # 50 + 256

    def test_negative_coordinates(self):
        """Test with negative coordinates."""
        point = complex(-10.0, -10.0)
        result = transform_point(
            point, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        assert result[0] == -25.6
        assert result[1] == 281.6


class TestLinePoints:
    """Tests for line_points function."""

    def test_basic_line(self):
        """Test converting a basic line."""
        line = Line(start=complex(0, 0), end=complex(100, 100))
        result = line_points(
            line, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        assert isinstance(result, list)
        assert len(result) == 4  # [x1, y1, x2, y2]
        assert result[0] == 0.0
        assert result[1] == 256.0  # Y inverted
        assert result[2] == 256.0
        assert result[3] == 0.0  # Y inverted

    def test_horizontal_line(self):
        """Test horizontal line transformation."""
        line = Line(start=complex(0, 50), end=complex(100, 50))
        result = line_points(
            line, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        # Y should be same for both points (horizontal line)
        assert result[1] == result[3]
        assert result[0] == 0.0
        assert result[2] == 256.0

    def test_vertical_line(self):
        """Test vertical line transformation."""
        line = Line(start=complex(50, 0), end=complex(50, 100))
        result = line_points(
            line, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        # X should be same for both points (vertical line)
        assert result[0] == result[2]
        assert result[0] == 128.0

    def test_short_line(self):
        """Test very short line."""
        line = Line(start=complex(50, 50), end=complex(51, 51))
        result = line_points(
            line, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        assert len(result) == 4
        # Points should be close but not identical
        assert abs(result[0] - result[2]) < 5
        assert abs(result[1] - result[3]) < 5


class TestBezierPoints:
    """Tests for bezier_points function."""

    def test_basic_bezier(self):
        """Test converting a basic cubic bezier."""
        bezier = CubicBezier(
            start=complex(0, 0),
            control1=complex(25, 50),
            control2=complex(75, 50),
            end=complex(100, 0),
        )
        result = bezier_points(
            bezier, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        assert isinstance(result, list)
        assert len(result) == 8  # [x1, y1, cx1, cy1, cx2, cy2, x2, y2]

    def test_bezier_point_order(self):
        """Test that bezier points are in correct order."""
        bezier = CubicBezier(
            start=complex(0, 0),
            control1=complex(33, 33),
            control2=complex(66, 66),
            end=complex(100, 100),
        )
        result = bezier_points(
            bezier, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        # Start point
        assert result[0] == 0.0
        assert result[1] == 256.0

        # Control points should be between start and end
        assert 0.0 < result[2] < 256.0
        assert 0.0 < result[4] < 256.0

        # End point
        assert result[6] == 256.0
        assert result[7] == 0.0

    def test_straight_line_bezier(self):
        """Test bezier that forms a straight line."""
        # All points collinear
        bezier = CubicBezier(
            start=complex(0, 0),
            control1=complex(33, 33),
            control2=complex(66, 66),
            end=complex(100, 100),
        )
        result = bezier_points(
            bezier, (100.0, 100.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        assert len(result) == 8


class TestGetAllPoints:
    """Tests for get_all_points function (Bezier discretization)."""

    def test_basic_bezier_discretization(self):
        """Test generating points along bezier curve."""
        result = get_all_points(
            start=(0.0, 0.0),
            control1=(25.0, 50.0),
            control2=(75.0, 50.0),
            end=(100.0, 0.0),
            segments=40,
        )

        assert isinstance(result, list)
        # 40 segments means 41 points (including t=0), but loop uses <=
        # So it generates 40 points * 2 coords = 80 values
        assert len(result) == 80

    def test_straight_line_segments(self):
        """Test bezier for a straight line."""
        result = get_all_points(
            start=(0.0, 0.0),
            control1=(33.0, 33.0),
            control2=(66.0, 66.0),
            end=(100.0, 100.0),
            segments=10,
        )

        # Should generate points along diagonal
        assert len(result) >= 20  # At least 10 points * 2 coords

    def test_few_segments(self):
        """Test with minimal segments."""
        result = get_all_points(
            start=(0.0, 0.0),
            control1=(50.0, 50.0),
            control2=(50.0, 50.0),
            end=(100.0, 100.0),
            segments=2,
        )

        assert isinstance(result, list)
        assert len(result) >= 4  # At least 2 points

    def test_many_segments(self):
        """Test with many segments for smooth curve."""
        result = get_all_points(
            start=(0.0, 0.0),
            control1=(25.0, 75.0),
            control2=(75.0, 75.0),
            end=(100.0, 0.0),
            segments=100,
        )

        # Should generate 100 points * 2 coords = 200 values
        assert len(result) == 200

    def test_default_segments(self):
        """Test with default segment count."""
        result = get_all_points(
            start=(0.0, 0.0),
            control1=(50.0, 50.0),
            control2=(50.0, 50.0),
            end=(100.0, 100.0),
            # segments defaults to 40
        )

        # Default 40 segments, generates 40 points * 2 coords = 80 values
        assert len(result) == 80

    def test_start_and_end_points_included(self):
        """Test that start and end points are in result."""
        result = get_all_points(
            start=(10.0, 20.0),
            control1=(30.0, 40.0),
            control2=(50.0, 60.0),
            end=(70.0, 80.0),
            segments=10,
        )

        # First point should be start
        assert result[0] == 10.0
        assert result[1] == 20.0

        # Last point should be close to end (t=1)
        assert abs(result[-2] - 70.0) < 1.0
        assert abs(result[-1] - 80.0) < 1.0

    def test_symmetrical_curve(self):
        """Test with symmetrical control points."""
        result = get_all_points(
            start=(0.0, 0.0),
            control1=(25.0, 50.0),
            control2=(75.0, 50.0),
            end=(100.0, 0.0),
            segments=20,
        )

        # 20 segments = 20 points * 2 coords = 40 values
        assert len(result) == 40


class TestFindCenter:
    """Tests for find_center function."""

    def test_odd_length_list(self):
        """Test finding center of odd-length list."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = find_center(values)
        assert result == 3.0

    def test_even_length_list(self):
        """Test finding center of even-length list."""
        values = [1.0, 2.0, 3.0, 4.0]
        result = find_center(values)
        assert result == 2.5  # Average of 2 and 3

    def test_single_element(self):
        """Test with single element list."""
        values = [42.0]
        result = find_center(values)
        assert result == 42.0

    def test_two_elements(self):
        """Test with two element list."""
        values = [10.0, 20.0]
        result = find_center(values)
        assert result == 15.0

    def test_large_list(self):
        """Test with large list."""
        values = list(range(1, 101))  # 1 to 100
        result = find_center(values)
        assert result == 50.5  # Average of 50 and 51

    def test_negative_values(self):
        """Test with negative values."""
        values = [-5.0, -3.0, -1.0, 1.0, 3.0]
        result = find_center(values)
        assert result == -1.0

    def test_decimal_values(self):
        """Test with decimal values."""
        values = [1.5, 2.5, 3.5, 4.5, 5.5]
        result = find_center(values)
        assert result == 3.5

    def test_unsorted_list_assumption(self):
        """Test that function expects pre-sorted list."""
        # Function assumes sorted list, just verify it works
        values = [1.0, 2.0, 3.0]
        result = find_center(values)
        assert result == 2.0


class TestIntegration:
    """Integration tests for path_utils functions working together."""

    def test_transform_point_uses_transform_x_y(self):
        """Test that transform_point correctly uses transform_x and transform_y."""
        point = complex(50.0, 50.0)
        widget_size = (256.0, 256.0)
        widget_pos = (0.0, 0.0)
        svg_size = (100.0, 100.0)
        svg_file = "test.svg"

        result = transform_point(point, widget_size, widget_pos, svg_size, svg_file)

        expected_x = transform_x(50.0, 0.0, 256.0, 100.0, svg_file)
        expected_y = transform_y(50.0, 0.0, 256.0, 100.0, svg_file)

        assert result[0] == expected_x
        assert result[1] == expected_y

    def test_line_points_uses_transform_point(self):
        """Test that line_points uses transform_point correctly."""
        line = Line(start=complex(0, 0), end=complex(100, 100))
        result = line_points(
            line, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        # Should match individual transform_point calls
        start_point = transform_point(
            line.start, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )
        end_point = transform_point(
            line.end, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        assert result[0:2] == start_point
        assert result[2:4] == end_point

    def test_bezier_points_uses_transform_point(self):
        """Test that bezier_points uses transform_point correctly."""
        bezier = CubicBezier(
            start=complex(0, 0),
            control1=complex(25, 50),
            control2=complex(75, 50),
            end=complex(100, 0),
        )
        result = bezier_points(
            bezier, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        # Verify it uses transform_point for all 4 points
        assert len(result) == 8

        # First two should be transformed start point
        start_transformed = transform_point(
            bezier.start, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )
        assert result[0:2] == start_transformed

    def test_consistency_across_functions(self):
        """Test that all transform functions are consistent."""
        x_pos, y_pos = 50.0, 50.0
        point = complex(x_pos, y_pos)

        # Direct transform
        x_result = transform_x(x_pos, 0.0, 256.0, 100.0, "test.svg")
        y_result = transform_y(y_pos, 0.0, 256.0, 100.0, "test.svg")

        # Via transform_point
        point_result = transform_point(
            point, (256.0, 256.0), (0.0, 0.0), (100.0, 100.0), "test.svg"
        )

        assert point_result[0] == x_result
        assert point_result[1] == y_result
