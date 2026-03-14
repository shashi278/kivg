"""Unit tests for data_classes module."""

from unittest.mock import Mock

from kivg.data_classes import AnimationContext


class TestAnimationContext:
    """Tests for AnimationContext dataclass."""

    def test_creation_with_all_fields(self, mock_widget):
        """Test creating AnimationContext with all required fields."""
        context = AnimationContext(
            widget=mock_widget,
            shape_id="path1",
            direction="right",
            transition="out_cubic",
            duration=1.5,
            closed_shapes={"path1": True},
            sw_size=(100.0, 100.0),
            svg_file="test.svg",
        )

        assert context.widget == mock_widget
        assert context.shape_id == "path1"
        assert context.direction == "right"
        assert context.transition == "out_cubic"
        assert context.duration == 1.5
        assert context.closed_shapes == {"path1": True}
        assert context.sw_size == (100.0, 100.0)
        assert context.svg_file == "test.svg"

    def test_creation_with_different_directions(self):
        """Test AnimationContext with different direction values."""
        widget = Mock()

        for direction in ["left", "right", "top", "bottom", "center"]:
            context = AnimationContext(
                widget=widget,
                shape_id="test",
                direction=direction,
                transition="linear",
                duration=1.0,
                closed_shapes={},
                sw_size=(100.0, 100.0),
                svg_file="test.svg",
            )
            assert context.direction == direction

    def test_creation_with_empty_closed_shapes(self):
        """Test AnimationContext with empty closed_shapes dict."""
        context = AnimationContext(
            widget=Mock(),
            shape_id="test",
            direction="center",
            transition="linear",
            duration=1.0,
            closed_shapes={},
            sw_size=(100.0, 100.0),
            svg_file="test.svg",
        )

        assert context.closed_shapes == {}
        assert isinstance(context.closed_shapes, dict)

    def test_creation_with_multiple_shapes(self):
        """Test AnimationContext with multiple shapes in closed_shapes."""
        closed = {"path1": True, "path2": False, "path3": True, "circle1": False}

        context = AnimationContext(
            widget=Mock(),
            shape_id="path1",
            direction="center",
            transition="linear",
            duration=1.0,
            closed_shapes=closed,
            sw_size=(100.0, 100.0),
            svg_file="test.svg",
        )

        assert len(context.closed_shapes) == 4
        assert context.closed_shapes["path1"] is True
        assert context.closed_shapes["path2"] is False

    def test_various_svg_sizes(self):
        """Test AnimationContext with various SVG sizes."""
        sizes = [(100.0, 100.0), (200.0, 150.0), (512.0, 512.0), (50.5, 75.25)]

        for size in sizes:
            context = AnimationContext(
                widget=Mock(),
                shape_id="test",
                direction="center",
                transition="linear",
                duration=1.0,
                closed_shapes={},
                sw_size=size,
                svg_file="test.svg",
            )
            assert context.sw_size == size

    def test_various_durations(self):
        """Test AnimationContext with various duration values."""
        durations = [0.5, 1.0, 2.0, 5.0, 0.1, 10.0]

        for duration in durations:
            context = AnimationContext(
                widget=Mock(),
                shape_id="test",
                direction="center",
                transition="linear",
                duration=duration,
                closed_shapes={},
                sw_size=(100.0, 100.0),
                svg_file="test.svg",
            )
            assert context.duration == duration

    def test_various_transitions(self):
        """Test AnimationContext with various transition types."""
        transitions = [
            "linear",
            "in_cubic",
            "out_cubic",
            "in_out_cubic",
            "in_quad",
            "out_quad",
            "in_sine",
            "out_sine",
        ]

        for transition in transitions:
            context = AnimationContext(
                widget=Mock(),
                shape_id="test",
                direction="center",
                transition=transition,
                duration=1.0,
                closed_shapes={},
                sw_size=(100.0, 100.0),
                svg_file="test.svg",
            )
            assert context.transition == transition

    def test_field_access(self):
        """Test that all fields are accessible."""
        context = AnimationContext(
            widget=Mock(),
            shape_id="test_id",
            direction="left",
            transition="linear",
            duration=2.0,
            closed_shapes={"shape1": True},
            sw_size=(150.0, 150.0),
            svg_file="icon.svg",
        )

        # All fields should be accessible
        assert hasattr(context, "widget")
        assert hasattr(context, "shape_id")
        assert hasattr(context, "direction")
        assert hasattr(context, "transition")
        assert hasattr(context, "duration")
        assert hasattr(context, "closed_shapes")
        assert hasattr(context, "sw_size")
        assert hasattr(context, "svg_file")
