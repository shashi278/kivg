# Code Quality Improvement Plan

**Repository**: Kivg (svg-anim-kivy)  
**Date**: 2026-03-08  
**Status**: Analysis Complete - Ready for Implementation

---

## Executive Summary

This document outlines a comprehensive plan to improve code quality across the Kivg codebase while maintaining backward compatibility and existing functionality. The improvements are categorized into phases to allow incremental, safe implementation.

---

## Current State Analysis

### File Size Analysis
```
kivg/animation/kivy_animation.py    800 lines (Modified Kivy code - handle carefully)
kivg/animation/animation_shapes.py  262 lines
kivg/main.py                        240 lines
kivg/drawing/manager.py             224 lines
kivg/path_utils.py                  173 lines
kivg/animation/handler.py           152 lines
kivg/svg_renderer.py                118 lines
kivg/mesh_handler.py                 64 lines
kivg/svg_parser.py                   52 lines
kivg/data_classes.py                 12 lines
```

### Identified Issues

#### 1. **Type Hints Missing or Incomplete**
- Inconsistent type annotations across modules
- Return types often missing
- Complex types not properly annotated
- No use of `Optional`, `Union`, `List`, `Dict` consistently

#### 2. **Class Organization Issues**
- Static method classes (`ShapeAnimator`, `SvgRenderer`, `MeshHandler`, etc.) should be proper utility classes or modules
- No clear separation of concerns in some areas
- Missing abstract base classes where appropriate

#### 3. **Error Handling**
- Minimal exception handling
- No custom exception classes
- Silent failures in some areas
- Missing validation

#### 4. **Code Duplication**
- Repeated property setting patterns
- Similar transformation logic in multiple places
- Duplicate animation setup code

#### 5. **Documentation Issues**
- Inconsistent docstring formats
- Missing parameter descriptions
- No examples in docstrings
- Return values not always documented

#### 6. **Magic Strings and Numbers**
- Hard-coded attribute name patterns
- Magic numbers (40 segments, 0.02 duration, etc.)
- No constants file

#### 7. **Testing**
- No visible test files in repository
- No test coverage metrics
- Demo app exists but no unit tests

#### 8. **Configuration**
- No configuration file support
- Hard-coded values throughout
- No global settings management

---

## Improvement Phases

### Phase 1: Foundation (Non-Breaking Changes)

#### 1.1 Add Type Hints Throughout
**Priority**: HIGH  
**Risk**: LOW  
**Effort**: MEDIUM

**Action Items**:
- [ ] Add complete type hints to all function signatures
- [ ] Add return type annotations
- [ ] Use `typing` module types consistently (`Optional`, `List`, `Dict`, `Tuple`, etc.)
- [ ] Add type hints to instance variables
- [ ] Run `mypy` for type checking

**Example Changes**:
```python
# Before
def transform_x(x_pos, widget_x, widget_width, svg_width, svg_file):
    return widget_x + widget_width * x_pos / svg_width

# After
def transform_x(
    x_pos: float, 
    widget_x: float, 
    widget_width: float, 
    svg_width: float, 
    svg_file: str
) -> float:
    """Transform X coordinate from SVG to Kivy space."""
    return widget_x + widget_width * x_pos / svg_width
```

#### 1.2 Create Constants Module
**Priority**: HIGH  
**Risk**: LOW  
**Effort**: LOW

**Action Items**:
- [ ] Create `kivg/constants.py`
- [ ] Move all magic numbers and strings to constants
- [ ] Group constants by category
- [ ] Use Enum where appropriate

**File Structure**:
```python
# kivg/constants.py
from enum import Enum

class AnimationType(Enum):
    SEQUENTIAL = "seq"
    PARALLEL = "par"

class AnimationDirection(Enum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    CENTER_X = "center_x"
    CENTER_Y = "center_y"

# Default values
DEFAULT_LINE_WIDTH: int = 2
DEFAULT_LINE_COLOR: List[float] = [0, 0, 0, 1]
DEFAULT_ANIMATION_DURATION: float = 0.02
DEFAULT_BEZIER_SEGMENTS: int = 40
DEFAULT_SHAPE_ANIM_DURATION: float = 0.3
DEFAULT_SHAPE_ANIM_TRANSITION: str = "out_sine"

# Tesselation constants
TESSELATION_WINDING: int = WINDING_ODD
TESSELATION_TYPE: int = TYPE_POLYGONS
```

#### 1.3 Improve Docstrings
**Priority**: MEDIUM  
**Risk**: NONE  
**Effort**: MEDIUM

**Action Items**:
- [ ] Use consistent docstring format (Google or NumPy style)
- [ ] Add parameter descriptions
- [ ] Add return value descriptions
- [ ] Add usage examples
- [ ] Document exceptions raised

**Example**:
```python
def bezier_points(
    bezier: CubicBezier, 
    widget_size: Tuple[float, float], 
    widget_pos: Tuple[float, float], 
    svg_size: Tuple[float, float], 
    svg_file: str
) -> List[float]:
    """
    Convert a CubicBezier to Kivy-compatible bezier points.
    
    Transforms SVG coordinate space to Kivy coordinate space, accounting
    for different origin positions and Y-axis directions.
    
    Args:
        bezier: CubicBezier object from svg.path
        widget_size: (width, height) of target widget
        widget_pos: (x, y) position of target widget
        svg_size: (width, height) of original SVG
        svg_file: Path to SVG file (used for special icon handling)
        
    Returns:
        List of 8 floats: [x1, y1, cx1, cy1, cx2, cy2, x2, y2]
        representing start point, control points, and end point
        
    Example:
        >>> bezier = CubicBezier(...)
        >>> points = bezier_points(bezier, (256, 256), (0, 0), (100, 100), "icon.svg")
        >>> print(points)
        [0.0, 0.0, 85.3, 170.6, 170.6, 85.3, 256.0, 256.0]
    """
    return [
        *transform_point(bezier.start, widget_size, widget_pos, svg_size, svg_file),
        *transform_point(bezier.control1, widget_size, widget_pos, svg_size, svg_file),
        *transform_point(bezier.control2, widget_size, widget_pos, svg_size, svg_file),
        *transform_point(bezier.end, widget_size, widget_pos, svg_size, svg_file),
    ]
```

#### 1.4 Add Input Validation
**Priority**: HIGH  
**Risk**: LOW  
**Effort**: MEDIUM

**Action Items**:
- [ ] Validate file paths exist
- [ ] Validate SVG structure
- [ ] Validate animation config
- [ ] Validate widget is valid Kivy widget
- [ ] Add helpful error messages

**Example**:
```python
def draw(self, svg_file: str, animate: bool = False, **kwargs) -> None:
    # Validate inputs
    if not os.path.exists(svg_file):
        raise FileNotFoundError(f"SVG file not found: {svg_file}")
    
    if not svg_file.lower().endswith('.svg'):
        raise ValueError(f"File must be SVG format: {svg_file}")
    
    if not hasattr(self.widget, 'canvas'):
        raise TypeError("Widget must be a Kivy widget with canvas")
    
    # ... rest of implementation
```

#### 1.5 Create Custom Exceptions
**Priority**: MEDIUM  
**Risk**: LOW  
**Effort**: LOW

**Action Items**:
- [ ] Create `kivg/exceptions.py`
- [ ] Define custom exception classes
- [ ] Use throughout codebase

**File Structure**:
```python
# kivg/exceptions.py
class KivgError(Exception):
    """Base exception for Kivg library."""
    pass

class SVGParseError(KivgError):
    """Raised when SVG file cannot be parsed."""
    pass

class SVGValidationError(KivgError):
    """Raised when SVG structure is invalid."""
    pass

class AnimationConfigError(KivgError):
    """Raised when animation configuration is invalid."""
    pass

class CoordinateTransformError(KivgError):
    """Raised when coordinate transformation fails."""
    pass
```

---

### Phase 2: Structural Improvements (Minimal Breaking Changes)

#### 2.1 Refactor Static Method Classes
**Priority**: MEDIUM  
**Risk**: MEDIUM  
**Effort**: MEDIUM

**Action Items**:
- [ ] Consider converting utility classes to modules
- [ ] Or add `__init__` with configuration
- [ ] Make intent clearer (utility vs service class)

**Options**:

**Option A: Keep as static classes (current approach)**
```python
class PathUtils:
    """Utility functions for path transformations."""
    
    @staticmethod
    def transform_x(...) -> float:
        ...
```

**Option B: Convert to module functions**
```python
# kivg/path_utils.py
def transform_x(...) -> float:
    """Transform X coordinate."""
    ...
```

**Option C: Make configurable service class**
```python
class PathTransformer:
    """Handles coordinate transformations."""
    
    def __init__(self, svg_size: Tuple[float, float], widget_size: Tuple[float, float]):
        self.svg_size = svg_size
        self.widget_size = widget_size
    
    def transform_x(self, x_pos: float) -> float:
        ...
```

**Recommendation**: Keep Option A (static classes) for backward compatibility, but improve documentation.

#### 2.2 Improve Property Management
**Priority**: MEDIUM  
**Risk**: MEDIUM  
**Effort**: MEDIUM

**Action Items**:
- [ ] Create `PropertyManager` class to handle widget property setting
- [ ] Centralize property naming logic
- [ ] Reduce code duplication

**Example**:
```python
class WidgetPropertyManager:
    """Manages dynamic widget properties for animation."""
    
    def __init__(self, widget: Any):
        self.widget = widget
    
    def set_line_property(
        self, 
        index: int, 
        prop_type: str, 
        value: float,
        prefix: str = ""
    ) -> None:
        """Set a line property on the widget."""
        prop_name = f"{prefix}line{index}_{prop_type}"
        setattr(self.widget, prop_name, value)
    
    def get_line_property(
        self, 
        index: int, 
        prop_type: str,
        prefix: str = ""
    ) -> float:
        """Get a line property from the widget."""
        prop_name = f"{prefix}line{index}_{prop_type}"
        return getattr(self.widget, prop_name)
```

#### 2.3 Separate Configuration from Logic
**Priority**: MEDIUM  
**Risk**: LOW  
**Effort**: MEDIUM

**Action Items**:
- [ ] Create `KivgConfig` dataclass
- [ ] Allow global and per-instance configuration
- [ ] Support config file loading

**Example**:
```python
@dataclass
class KivgConfig:
    """Configuration for Kivg rendering."""
    line_width: int = DEFAULT_LINE_WIDTH
    line_color: List[float] = field(default_factory=lambda: DEFAULT_LINE_COLOR)
    animation_duration: float = DEFAULT_ANIMATION_DURATION
    bezier_segments: int = DEFAULT_BEZIER_SEGMENTS
    cache_svg_parsing: bool = True
    validate_inputs: bool = True
    
    @classmethod
    def from_file(cls, path: str) -> 'KivgConfig':
        """Load configuration from JSON file."""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

# Usage
class Kivg:
    def __init__(self, widget: Any, config: Optional[KivgConfig] = None):
        self.widget = widget
        self.config = config or KivgConfig()
```

#### 2.4 Add Builder Pattern for Complex Objects
**Priority**: LOW  
**Risk**: LOW  
**Effort**: MEDIUM

**Action Items**:
- [ ] Create builder for animation configurations
- [ ] Make API more fluent and discoverable

**Example**:
```python
class AnimationConfigBuilder:
    """Builder for animation configurations."""
    
    def __init__(self, shape_id: str):
        self._config = {"id_": shape_id}
    
    def from_direction(self, direction: str) -> 'AnimationConfigBuilder':
        self._config["from_"] = direction
        return self
    
    def with_transition(self, transition: str) -> 'AnimationConfigBuilder':
        self._config["t"] = transition
        return self
    
    def with_duration(self, duration: float) -> 'AnimationConfigBuilder':
        self._config["d"] = duration
        return self
    
    def build(self) -> Dict[str, Any]:
        return self._config

# Usage
config = (
    AnimationConfigBuilder("shape1")
    .from_direction("left")
    .with_transition("out_back")
    .with_duration(0.4)
    .build()
)
```

---

### Phase 3: Testing Infrastructure

#### 3.1 Add Unit Tests
**Priority**: HIGH  
**Risk**: NONE  
**Effort**: HIGH

**Action Items**:
- [ ] Create `tests/` directory
- [ ] Add tests for each module
- [ ] Use pytest fixtures for common setup
- [ ] Mock Kivy widgets for testing
- [ ] Aim for >80% code coverage

**Structure**:
```
tests/
├── __init__.py
├── conftest.py                # Pytest configuration and fixtures
├── test_svg_parser.py
├── test_path_utils.py
├── test_drawing_manager.py
├── test_animation_handler.py
├── test_animation_shapes.py
├── test_svg_renderer.py
├── test_mesh_handler.py
├── test_main.py
└── fixtures/
    ├── simple.svg
    ├── complex.svg
    └── animated.svg
```

**Example Test**:
```python
# tests/test_path_utils.py
import pytest
from kivg.path_utils import transform_x, transform_y

class TestCoordinateTransformation:
    """Test coordinate transformation functions."""
    
    def test_transform_x_basic(self):
        """Test basic X coordinate transformation."""
        result = transform_x(
            x_pos=50.0,
            widget_x=0.0,
            widget_width=256.0,
            svg_width=100.0,
            svg_file="test.svg"
        )
        assert result == 128.0
    
    def test_transform_x_with_offset(self):
        """Test X transformation with widget offset."""
        result = transform_x(
            x_pos=50.0,
            widget_x=100.0,
            widget_width=256.0,
            svg_width=100.0,
            svg_file="test.svg"
        )
        assert result == 228.0
    
    def test_transform_y_flips_coordinate(self):
        """Test that Y coordinate is flipped."""
        result = transform_y(
            y_pos=25.0,
            widget_y=0.0,
            widget_height=100.0,
            svg_height=100.0,
            svg_file="test.svg"
        )
        assert result == 75.0  # Flipped
```

#### 3.2 Add Integration Tests
**Priority**: MEDIUM  
**Risk**: NONE  
**Effort**: MEDIUM

**Action Items**:
- [ ] Test full rendering pipeline
- [ ] Test animation sequences
- [ ] Test with real SVG files
- [ ] Test error scenarios

#### 3.3 Add Performance Tests
**Priority**: LOW  
**Risk**: NONE  
**Effort**: MEDIUM

**Action Items**:
- [ ] Benchmark SVG parsing
- [ ] Benchmark animation performance
- [ ] Test with large SVG files
- [ ] Profile memory usage

---

### Phase 4: Advanced Improvements (Optional)

#### 4.1 Add Logging
**Priority**: MEDIUM  
**Risk**: LOW  
**Effort**: LOW

**Action Items**:
- [ ] Use Python's `logging` module
- [ ] Add debug logs for troubleshooting
- [ ] Configurable log levels
- [ ] Don't use `print()` statements

**Example**:
```python
import logging

logger = logging.getLogger(__name__)

class Kivg:
    def draw(self, svg_file: str, **kwargs):
        logger.debug(f"Drawing SVG: {svg_file}")
        logger.debug(f"Animation settings: {kwargs}")
        
        try:
            # ... implementation
            logger.info(f"Successfully rendered {svg_file}")
        except Exception as e:
            logger.error(f"Failed to render {svg_file}: {e}")
            raise
```

#### 4.2 Add Caching Layer
**Priority**: LOW  
**Risk**: LOW  
**Effort**: MEDIUM

**Action Items**:
- [ ] Use `functools.lru_cache` for expensive operations
- [ ] Cache SVG parsing results
- [ ] Cache coordinate transformations
- [ ] Make cache configurable

**Example**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def parse_svg_cached(svg_file: str) -> Tuple[List[float], List[Tuple]]:
    """Parse SVG with caching."""
    return parse_svg(svg_file)
```

#### 4.3 Add Context Manager Support
**Priority**: LOW  
**Risk**: LOW  
**Effort**: LOW

**Action Items**:
- [ ] Make Kivg usable as context manager
- [ ] Clean up resources automatically

**Example**:
```python
class Kivg:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup
        if hasattr(self, 'widget'):
            Animation.cancel_all(self.widget)
        return False

# Usage
with Kivg(widget) as kivg:
    kivg.draw("icon.svg", animate=True)
```

#### 4.4 Add Async Support
**Priority**: LOW  
**Risk**: HIGH  
**Effort**: HIGH

**Action Items**:
- [ ] Add async versions of methods
- [ ] Support concurrent animations
- [ ] Use asyncio for I/O operations

---

## Implementation Guidelines

### Order of Implementation

1. **Start with Phase 1** - These are safe, non-breaking changes
2. **Create constants module first** - Other changes depend on it
3. **Add type hints incrementally** - Module by module
4. **Add tests as you go** - Test each improvement
5. **Update documentation** - Keep docs in sync

### Testing Strategy

**Before Each Change**:
1. Run existing demo app
2. Verify all features work
3. Document current behavior

**After Each Change**:
1. Run demo app again
2. Verify behavior unchanged
3. Run new tests
4. Check type hints with mypy

### Git Workflow

**Branch Naming**:
- `improve/type-hints`
- `improve/add-constants`
- `improve/add-validation`
- `refactor/property-management`
- `test/add-unit-tests`

**Commit Messages**:
```
improve: Add type hints to path_utils module

- Add complete type hints to all functions
- Add return type annotations
- Update docstrings with parameter types
- No functional changes
```

### Code Review Checklist

- [ ] Backward compatible (no breaking changes)
- [ ] Tests pass (or new tests added)
- [ ] Type hints added
- [ ] Docstrings updated
- [ ] No new dependencies added
- [ ] Demo app still works
- [ ] Code formatted with black
- [ ] No print statements (use logging)

---

## Priority Matrix

| Priority | Risk | Effort | Items |
|----------|------|--------|-------|
| HIGH | LOW | LOW | Create constants module |
| HIGH | LOW | MEDIUM | Add type hints |
| HIGH | LOW | MEDIUM | Add input validation |
| HIGH | NONE | HIGH | Add unit tests |
| MEDIUM | LOW | LOW | Add custom exceptions |
| MEDIUM | LOW | MEDIUM | Improve docstrings |
| MEDIUM | MEDIUM | MEDIUM | Refactor property management |
| LOW | LOW | MEDIUM | Add builder pattern |
| LOW | LOW | MEDIUM | Add caching layer |

---

## Success Metrics

- [ ] Type coverage: 100%
- [ ] Test coverage: >80%
- [ ] All tests passing
- [ ] Demo app works unchanged
- [ ] mypy passes with no errors
- [ ] Documentation updated
- [ ] No breaking API changes
- [ ] Performance maintained or improved

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Create GitHub issues** for each phase
3. **Set up CI/CD** for automated testing
4. **Start with constants module** (easiest win)
5. **Add type hints module by module**
6. **Write tests for each module**
7. **Refactor incrementally**

---

## Notes

- Maintain backward compatibility throughout
- Focus on improvements that add value
- Don't over-engineer
- Keep it simple and Pythonic
- Test thoroughly before merging
- Document all changes

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-08  
**Status**: Ready for Implementation
