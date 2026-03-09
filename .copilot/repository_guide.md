# AI Agent Repository Guide: Kivg (svg-anim-kivy)

**Last Updated**: 2026-03-08  
**Version**: 1.2  
**Repository**: https://github.com/shashi278/svg-anim-kivy

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Key Features](#key-features)
5. [Code Organization](#code-organization)
6. [Technical Implementation Details](#technical-implementation-details)
7. [Dependencies](#dependencies)
8. [Usage Patterns](#usage-patterns)
9. [Testing & Development](#testing--development)
10. [Common Workflows](#common-workflows)
11. [Important Notes](#important-notes)

---

## Overview

### What is Kivg?
**Kivg** (Kivy Vector Graphics) is a Python library that brings SVG path drawing and animation capabilities to Kivy applications. It allows developers to render SVG files in Kivy with support for both static rendering and sophisticated animations.

### Purpose
- **Primary Goal**: Enable SVG rendering in Kivy applications with animation support
- **Use Cases**: 
  - Icon animations in mobile/desktop apps
  - Interactive UI elements
  - Vector graphics rendering
  - Logo animations
  - Shape morphing effects

### Key Capabilities
1. **Path Drawing**: Render SVG paths with line strokes
2. **Path Filling**: Fill SVG shapes with colors
3. **Sequential Animation**: Animate SVG paths drawing sequentially
4. **Parallel Animation**: Animate multiple paths simultaneously
5. **Shape Animation**: Individual shape-level animations with directional effects
6. **Color Support**: Parse and apply hex colors from SVG files

### Project Statistics
- **Total Lines of Code**: ~2,111 lines
- **Primary Language**: Python 3.6+
- **License**: MIT License
- **Author**: Shashi Ranjan (shashiranjankv@gmail.com)
- **Package Name**: Kivg (on PyPI)

---

## Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────┐
│                    User Code                        │
│            (Kivy App with Kivg)                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                 Kivg Main API                       │
│              (kivg/main.py)                         │
│   • draw() - Path drawing & animation               │
│   • shape_animate() - Shape-level animation         │
└──────────────────┬──────────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      ▼            ▼             ▼
┌──────────┐ ┌──────────┐ ┌──────────────┐
│   SVG    │ │ Drawing  │ │  Animation   │
│  Parser  │ │ Manager  │ │   Handler    │
└──────────┘ └──────────┘ └──────────────┘
      │            │             │
      ▼            ▼             ▼
┌─────────────────────────────────────────┐
│          Rendering Layer                │
│  • SvgRenderer - Canvas updates         │
│  • MeshHandler - Shape filling          │
│  • PathUtils - Coordinate transforms    │
└─────────────────────────────────────────┘
```

### Data Flow

#### Path Drawing Flow
```
SVG File → parse_svg() → Path Elements → DrawingManager
  ↓
Calculate coordinates & properties
  ↓
Set widget attributes (line/bezier properties)
  ↓
Create Animation objects (if animated)
  ↓
SvgRenderer → Update Canvas → Display
  ↓
MeshHandler → Fill shapes (if fill=True)
```

#### Shape Animation Flow
```
SVG File + Animation Config → Kivg.shape_animate()
  ↓
Parse SVG & extract shapes by ID
  ↓
AnimationHandler.prepare_shape_animations()
  ↓
ShapeAnimator.setup_animation() for each shape
  ↓
Calculate base points based on direction
  ↓
Create property animations (slide from direction)
  ↓
Bind progress tracking → track_progress()
  ↓
Update canvas on progress → Render current state
  ↓
Chain animations sequentially
  ↓
Call on_complete callback when finished
```

---

## Core Components

### 1. `kivg/main.py` - Main API Class
**Purpose**: Primary interface for users

**Key Class: `Kivg`**
- **Initialization**: `Kivg(widget)` - Takes a Kivy widget as target
- **Main Methods**:
  - `draw(svg_file, animate=False, anim_type="seq", **kwargs)` - Draw SVG with optional animation
  - `shape_animate(svg_file, anim_config_list, on_complete)` - Animate individual shapes
  - `fill_up(shapes, color)` - Fill shapes with color using meshes
  - `fill_up_shapes()` - Fill all shapes in current SVG
  - `update_canvas()` - Update canvas with current drawing state
  
**State Management**:
- `closed_shapes`: OrderedDict of parsed SVG shapes by ID
- `svg_size`: SVG dimensions
- `path`: List of path elements
- `current_svg_file`: Currently loaded SVG
- `_previous_svg_file`: Cache for performance

### 2. `kivg/svg_parser.py` - SVG Parsing
**Purpose**: Parse SVG files and extract path data

**Key Function: `parse_svg(svg_file)`**
- Uses `xml.dom.minidom` for XML parsing
- Extracts viewBox dimensions
- Parses all `<path>` elements
- Extracts attributes: `d` (path data), `id`, `fill` color
- Returns: `(svg_dimensions, path_data_list)`

**Color Handling**:
- Supports hex colors via `kivy.utils.get_color_from_hex()`
- Defaults to transparent `[1,1,1,0]` if color parsing fails
- Gradients not supported (fallback to white)

### 3. `kivg/drawing/manager.py` - Drawing Manager
**Purpose**: Process SVG paths and prepare rendering data

**Key Methods**:
- `process_path_data(svg_file)` - Parse SVG and organize paths by shape ID
- `calculate_paths()` - Transform SVG coordinates to Kivy coordinates, set widget properties
- `_setup_line_properties()` - Set line animation properties on widget
- `_setup_bezier_properties()` - Set bezier curve animation properties

**Path Organization**:
- Groups paths by shape ID
- Separates closed shapes for filling
- Stores both path data and mesh data

### 4. `kivg/animation/handler.py` - Animation Handler
**Purpose**: Centralized animation management

**Key Static Methods**:
- `create_animation_sequence(animations, sequential)` - Combine animations
- `add_fill_animation(anim, widget, callback)` - Add fade-in for fills
- `prepare_and_start_animation()` - Bind callbacks and start animation
- `prepare_shape_animations()` - Create shape-level animations from config
- `setup_shape_animations()` - Delegate to ShapeAnimator

**Animation Chaining**:
- Sequential: `anim1 + anim2` (runs one after another)
- Parallel: `anim1 & anim2` (runs simultaneously)

### 5. `kivg/animation/animation_shapes.py` - Shape Animator
**Purpose**: Handle shape-specific animations

**Key Class: `ShapeAnimator`**

**Key Methods**:
- `setup_animation(caller, context)` - Main entry point for shape animation
- `_extract_path_data()` - Transform path elements to animation format
- `_calculate_base_point(path_data, direction)` - Determine animation start point
- `_setup_line_animation()` - Create line slide animation
- `_setup_bezier_animation()` - Create bezier curve slide animation

**Direction Handling**:
- `left`, `right`: Slide horizontally
- `top`, `bottom`: Slide vertically  
- `center_x`, `center_y`: Grow from center
- `None`: Reveal without animation (uses duration as delay)

### 6. `kivg/svg_renderer.py` - SVG Renderer
**Purpose**: Render paths to Kivy canvas

**Key Methods**:
- `update_canvas(widget, path_elements, line_color)` - Clear and redraw canvas
- `_draw_line(widget, line_index)` - Draw a line element
- `_draw_bezier(widget, bezier_index)` - Draw a bezier curve element
- `collect_shape_points()` - Collect points during animation

**Rendering Approach**:
- Clears canvas before each frame
- Uses Kivy's `Line` graphics instruction
- Reads properties from widget attributes
- Supports both straight lines and bezier curves

### 7. `kivg/mesh_handler.py` - Mesh Handler
**Purpose**: Generate and render filled shapes

**Key Methods**:
- `create_tesselator(shapes)` - Create tesselator for shapes
- `generate_meshes(shapes)` - Tesselate shapes into triangles
- `render_mesh()` - Render triangulated mesh on canvas

**Tesselation**:
- Uses Kivy's `Tesselator` class
- `WINDING_ODD` rule for path filling
- `TYPE_POLYGONS` for polygon generation
- Converts complex shapes to triangle fans

### 8. `kivg/path_utils.py` - Path Utilities
**Purpose**: Coordinate transformation and path calculations

**Key Functions**:
- `transform_x()`, `transform_y()` - SVG to Kivy coordinate conversion
- `transform_point()` - Transform complex points
- `bezier_points()` - Extract bezier curve points
- `line_points()` - Extract line points
- `get_all_points()` - Discretize bezier curves into line segments
- `find_center()` - Find center of sorted list

**Coordinate System**:
- SVG: Origin at top-left, Y increases downward
- Kivy: Origin at bottom-left, Y increases upward
- Special handling for "kivy" icon files (different scale)

### 9. `kivg/data_classes.py` - Data Classes
**Purpose**: Type-safe data structures

**`AnimationContext` Dataclass**:
```python
@dataclass
class AnimationContext:
    widget: object          # Target widget
    shape_id: str          # Shape identifier
    direction: str         # Animation direction
    transition: str        # Animation transition type
    duration: float        # Animation duration
    closed_shapes: dict    # SVG shape data
    sw_size: tuple        # SVG dimensions
    svg_file: str         # SVG file path
```

### 10. `kivg/animation/kivy_animation.py` - Modified Kivy Animation
**Purpose**: Custom animation implementation

**Note**: This is a modified version of Kivy's Animation class with customizations for Kivg's needs. Not all Kivy animation features may be available.

---

## Key Features

### Feature 1: Path Drawing with Animation
**Location**: `Kivg.draw()`

**Parameters**:
- `svg_file`: Path to SVG file
- `animate`: Whether to animate drawing (default: False)
- `anim_type`: "seq" (sequential) or "par" (parallel)
- `fill`: Fill shape after drawing (default: True)
- `line_width`: Stroke width (default: 2)
- `line_color`: Stroke color RGBA (default: [0,0,0,1])
- `dur`: Duration per animation step (default: 0.02)

**How It Works**:
1. Parse SVG and extract paths
2. Transform coordinates to Kivy space
3. Set initial properties on widget
4. Create animation sequence
5. Animate drawing (if enabled)
6. Fill shapes (if enabled)

**Example**:
```python
from kivg import Kivg
s = Kivg(my_widget)
s.draw("icon.svg", animate=True, anim_type="seq", fill=True)
```

### Feature 2: Shape-Level Animation
**Location**: `Kivg.shape_animate()`

**Parameters**:
- `svg_file`: Path to SVG file
- `anim_config_list`: List of animation configurations
- `on_complete`: Callback when all animations finish

**Animation Config Structure**:
```python
{
    "id_": "shape_id",        # Required: SVG path id
    "from_": "left",          # Optional: direction
    "t": "out_bounce",        # Optional: transition
    "d": 0.5                  # Optional: duration
}
```

**Supported Directions**:
- `"left"`, `"right"` - Horizontal slide
- `"top"`, `"bottom"` - Vertical slide
- `"center_x"`, `"center_y"` - Grow from center
- `None` - No animation (delay only)

**Supported Transitions**: All Kivy animation transitions
- `out_sine`, `out_bounce`, `out_elastic`, `out_back`, etc.

**Example**:
```python
config = [
    {"id_": "letter_k", "from_": "left", "t": "out_back", "d": 0.4},
    {"id_": "letter_i", "from_": "center_y", "t": "out_bounce", "d": 0.4}
]
s.shape_animate("text.svg", anim_config_list=config)
```

### Feature 3: Coordinate Transformation
**Location**: `kivg/path_utils.py`

**Challenge**: SVG and Kivy use different coordinate systems

**Solution**:
- SVG: Top-left origin, Y+ downward
- Kivy: Bottom-left origin, Y+ upward
- Transform functions handle conversion
- Special scaling for specific icons

### Feature 4: Mesh-Based Filling
**Location**: `MeshHandler.render_mesh()`

**Challenge**: Fill complex SVG shapes with color

**Solution**:
- Use Kivy's Tesselator to triangulate shapes
- Render as triangle fan meshes
- Support opacity animation for fade-in effects

---

## Code Organization

### Directory Structure
```
svg-anim-kivy/
├── kivg/                      # Main package
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Main Kivg class (API)
│   ├── svg_parser.py         # SVG parsing logic
│   ├── svg_renderer.py       # Canvas rendering
│   ├── mesh_handler.py       # Shape filling with meshes
│   ├── path_utils.py         # Coordinate transformations
│   ├── data_classes.py       # Data structures
│   ├── svg_elements.py       # SVG element definitions
│   ├── version.py            # Version string
│   ├── animation/            # Animation subsystem
│   │   ├── handler.py        # Animation coordination
│   │   ├── animation_shapes.py  # Shape animations
│   │   ├── kivy_animation.py    # Modified Kivy Animation
│   │   └── path_tracker.py   # Path tracking utilities
│   └── drawing/              # Drawing subsystem
│       └── manager.py        # Drawing coordination
├── demo/                      # Demo application
│   ├── main.py               # Demo app code
│   ├── icons/                # Sample SVG files
│   ├── svg_demo.gif          # Demo animation
│   └── adv_svg_anim.gif      # Advanced demo
├── build/                     # Build artifacts
├── Kivg.egg-info/            # Package metadata
├── .github/                   # GitHub configuration
│   └── workflows/
│       └── python-publish.yml  # PyPI publishing workflow
├── setup.py                   # Package setup configuration
├── requirements.txt           # Dependencies
├── README.md                  # User documentation
├── LICENSE                    # MIT License
├── .gitignore                # Git ignore patterns
└── .travis.yml               # Travis CI config (legacy)
```

### Module Dependencies
```
main.py
  ├── svg_parser.py
  ├── drawing/manager.py
  │   ├── svg_parser.py
  │   ├── path_utils.py
  │   └── animation/kivy_animation.py
  ├── animation/handler.py
  │   ├── animation/kivy_animation.py
  │   ├── animation/animation_shapes.py
  │   └── data_classes.py
  ├── svg_renderer.py
  │   └── path_utils.py
  └── mesh_handler.py

animation/animation_shapes.py
  ├── path_utils.py
  ├── data_classes.py
  └── animation/kivy_animation.py
```

---

## Technical Implementation Details

### How Widget Properties Are Used

**Property Naming Convention**:
```python
# For path drawing animation
f"line{index}_start_x"
f"line{index}_start_y"
f"line{index}_end_x"
f"line{index}_end_y"
f"line{index}_width"

f"bezier{index}_start_x"
f"bezier{index}_start_y"
f"bezier{index}_control1_x"
f"bezier{index}_control1_y"
f"bezier{index}_control2_x"
f"bezier{index}_control2_y"
f"bezier{index}_end_x"
f"bezier{index}_end_y"
f"bezier{index}_width"

# For shape animation
f"{shape_id}_mesh_line{index}_start_x"
f"{shape_id}_mesh_line{index}_start_y"
f"{shape_id}_mesh_line{index}_end_x"
f"{shape_id}_mesh_line{index}_end_y"

f"{shape_id}_mesh_bezier{index}_start_x"
# ... etc for bezier control points

# For opacity animation
"mesh_opacity"
```

**How Animation Works**:
1. Set initial property values on widget (e.g., line start point)
2. Create Animation object targeting final values
3. Kivy Animation interpolates property values over time
4. `on_progress` callback triggers canvas redraw
5. Renderer reads current property values from widget
6. Draws paths with interpolated values

### Path Element Storage

**`closed_shapes` Structure**:
```python
{
    "shape_id": {
        "shape_id" + "paths": [
            [Line(...), CubicBezier(...)],  # Path 1
            [Line(...), Line(...)],          # Path 2
        ],
        "shape_id" + "shapes": [
            [x1, y1, x2, y2, ...],  # Points for mesh 1
            [x1, y1, x2, y2, ...],  # Points for mesh 2
        ],
        "color": [r, g, b, a]
    }
}
```

### SVG Path Types Supported

**Supported**:
- `Line` - Straight line segments
- `CubicBezier` - Cubic bezier curves
- `Move` - Move to position (path start)
- `Close` - Close path

**Not Supported** (will need conversion):
- `Arc` - Elliptical arcs (use converter tool)
- `QuadraticBezier` - Quadratic curves (convert to cubic)
- Relative commands (convert to absolute)

### Animation Chaining Mechanism

**Sequential Animations**:
```python
anim1 = Animation(d=0.5, x=100)
anim2 = Animation(d=0.3, y=200)
combined = anim1 + anim2  # anim2 starts after anim1
```

**Parallel Animations**:
```python
anim1 = Animation(d=0.5, x=100)
anim2 = Animation(d=0.5, y=200)
combined = anim1 & anim2  # Both start simultaneously
```

**Shape Animation Chaining**:
```python
# Each shape animates sequentially
# Progress callback redraws canvas
# On complete callback triggers next shape
# Final shape can trigger on_complete callback for looping
```

### Bezier Curve Discretization

**Purpose**: Convert bezier curves to line segments for mesh filling

**Algorithm**: Uses Bernstein polynomials
```python
# For parameter t from 0 to 1
B0(t) = (1-t)³
B1(t) = 3t(1-t)²
B2(t) = 3t²(1-t)
B3(t) = t³

# Point at t
P(t) = B0(t)*P0 + B1(t)*P1 + B2(t)*P2 + B3(t)*P3
```

**Segments**: Default 40 segments per curve (adjustable)

---

## Dependencies

### Core Dependencies
```
kivy>=2.0.0           # UI framework
svg.path==4.1         # SVG path parsing
```

### Development Dependencies
```
typing-extensions>=4.0.0  # Type hints
pytest>=7.0.0            # Testing
black>=23.0.0            # Code formatting
```

### Python Version
- **Required**: Python 3.6+
- **Recommended**: Python 3.8+ for better type hint support

### Platform Support
- **Android**: Yes (main target)
- **Windows**: Yes
- **Linux**: Yes (via Kivy)
- **macOS**: Yes (via Kivy)
- **iOS**: Likely (via Kivy, untested)

---

## Usage Patterns

### Pattern 1: Simple Static Icon Display
```python
from kivy.app import App
from kivy.uix.widget import Widget
from kivg import Kivg

class MyWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (256, 256)
        s = Kivg(self)
        s.draw("icon.svg")  # Static, filled

class MyApp(App):
    def build(self):
        return MyWidget()
```

### Pattern 2: Animated Path Drawing
```python
s = Kivg(widget)
s.draw(
    "logo.svg",
    animate=True,
    anim_type="seq",
    fill=False,
    line_width=2,
    line_color=[1, 0, 0, 1],  # Red
    dur=0.05
)
```

### Pattern 3: Shape Animation with Callback
```python
def animation_complete(*args):
    print("Animation finished!")
    # Could trigger next animation or loop

config = [
    {"id_": "shape1", "from_": "left", "t": "out_back", "d": 0.4},
    {"id_": "shape2", "from_": "top", "t": "out_bounce", "d": 0.3}
]

s = Kivg(widget)
s.shape_animate("shapes.svg", anim_config_list=config, on_complete=animation_complete)
```

### Pattern 4: Looping Animation
```python
from kivy.clock import Clock

class MyApp(App):
    def animate_logo(self, *args):
        self.kivg.shape_animate(
            "logo.svg",
            anim_config_list=self.config,
            on_complete=lambda *args: Clock.schedule_once(self.animate_logo, 0.5)
        )
    
    def on_start(self):
        self.animate_logo()
```

### Pattern 5: Multiple Instances
```python
# Multiple widgets with different SVGs
widget1 = Widget()
widget2 = Widget()

s1 = Kivg(widget1)
s2 = Kivg(widget2)

s1.draw("icon1.svg")
s2.draw("icon2.svg", animate=True)
```

---

## Testing & Development

### Test Structure
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_data_classes.py    # ✅ 8 tests (100% coverage)
│   ├── test_path_utils.py      # ✅ 47 tests (100% coverage)
│   └── (more tests in progress)
├── integration/             # Integration tests
│   └── __init__.py
└── fixtures/                # Test data
    └── sample_data/
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=kivg tests/

# Run specific test file
pytest tests/unit/test_path_utils.py

# Run with verbose output
pytest -v tests/
```

### Test Progress
| Module | Tests | Status | Coverage |
|--------|-------|--------|----------|
| data_classes.py | 8 | ✅ Complete | 100% |
| path_utils.py | 47 | ✅ Complete | 100% |
| svg_parser.py | - | 📋 Planned | - |
| mesh_handler.py | - | 📋 Planned | - |
| svg_renderer.py | - | 📋 Planned | - |
| main.py | - | 📋 Planned | - |

**Current Total**: 55 tests  
**Overall Coverage**: ~15% (target: >80%)

See `.copilot/plans/2026-03-08_testing_infrastructure/progress.md` for detailed testing roadmap.

### Code Formatting
```bash
black kivg/
```

### Building Package
```bash
python -m pip install build
python -m build
```

### Installing Locally for Testing
```bash
pip install -e .
```

### Running Demo
```bash
cd demo
python main.py
```

---

## Common Workflows

### Adding a New Feature

1. **Identify Component**: Determine which module needs changes
   - SVG parsing → `svg_parser.py`
   - Animation → `animation/handler.py` or `animation/animation_shapes.py`
   - Rendering → `svg_renderer.py` or `mesh_handler.py`
   - Coordinates → `path_utils.py`

2. **Update Implementation**: Make changes to target module

3. **Update API** (if needed): Modify `main.py` to expose feature

4. **Test**: Run demo app and verify

5. **Document**: Update README.md with examples

### Debugging an Animation Issue

1. **Check SVG File**: Ensure paths have correct `id` attributes

2. **Verify Config**: Check animation config dictionary structure

3. **Print Debug Info**:
   ```python
   print(f"Closed shapes: {s.closed_shapes.keys()}")
   print(f"Animation list: {s.all_anim}")
   ```

4. **Check Widget Properties**: Verify properties are being set
   ```python
   print(getattr(widget, f"{shape_id}_mesh_line0_start_x"))
   ```

5. **Test Without Animation**: Try static rendering first
   ```python
   s.draw("test.svg", animate=False)
   ```

### Adding Support for New SVG Element

1. **Update Parser**: Modify `svg_parser.py` to extract element

2. **Add Transform Function**: Create coordinate transform in `path_utils.py`

3. **Update Drawing Manager**: Add element handling in `drawing/manager.py`

4. **Update Renderer**: Add rendering logic in `svg_renderer.py`

5. **Add Animation Support**: Update animation system if needed

### Optimizing Performance

**Performance Considerations**:
- SVG parsing is cached by file name
- Avoid calling `draw()` repeatedly with same file
- Use `animate=False` for static icons
- Reduce `segments` in `get_all_points()` for simpler curves
- Minimize number of paths in SVG files
- Consider pre-processing SVGs (optimize, simplify)

**Profiling**:
```python
import cProfile
cProfile.run('s.draw("complex.svg", animate=True)')
```

---

## Important Notes

### SVG File Requirements

1. **Path IDs**: Each `<path>` element should have a unique `id` for shape animation
   ```xml
   <path id="shape1" d="M 10,10 L 100,100" fill="#FF0000"/>
   ```

2. **Fill Colors**: Must be in hex format inside `<path>` tag
   ```xml
   <path fill="#FF0000" d="..."/>  ✓ Supported
   <path style="fill:#FF0000" d="..."/>  ✗ Not parsed
   ```

3. **ViewBox**: SVG must have `viewBox` attribute
   ```xml
   <svg viewBox="0 0 100 100">...</svg>
   ```

4. **Absolute Paths**: Relative path commands should be converted to absolute
   - Use tool: https://codepen.io/thednp/pen/EgVqLw

5. **No Arcs**: Convert Arc commands to cubic bezier curves
   - Use tool: https://itchylabs.com/tools/path-to-bezier/

6. **Closed Paths**: Ensure paths end with `Z` command

### Known Limitations

1. **Gradient Fills**: Not supported (defaults to white)
2. **Text Elements**: Not supported (convert to paths)
3. **Clipping Paths**: Not supported
4. **Masks**: Not supported
5. **Filters**: Not supported
6. **Transform Attributes**: Not parsed (bake transforms into paths)
7. **Relative Commands**: May cause issues (convert to absolute)
8. **Arc Commands**: Not supported (convert to bezier)
9. **Quadratic Bezier**: Not directly supported (convert to cubic)

### Best Practices

1. **Optimize SVGs**: Use SVGOMG (https://jakearchibald.github.io/svgomg/)
2. **Test Separately**: Test drawing and animation separately
3. **Use IDs**: Always add IDs for shape animation
4. **Keep It Simple**: Fewer paths = better performance
5. **Cache Instances**: Reuse Kivg instances when possible
6. **Preprocess**: Convert problematic SVG features before runtime

### Troubleshooting

**Problem**: SVG doesn't display
- **Check**: ViewBox attribute exists
- **Check**: Path data is valid
- **Check**: Widget size is non-zero
- **Check**: SVG file path is correct

**Problem**: Animation doesn't work
- **Check**: `animate=True` is set
- **Check**: Widget properties are being set
- **Check**: Animation callbacks are binding

**Problem**: Colors don't appear
- **Check**: Fill attribute is in hex format
- **Check**: Fill is in `<path>` tag, not style
- **Check**: Colors are not gradients

**Problem**: Shape animation fails
- **Check**: Path has `id` attribute
- **Check**: `id_` in config matches SVG
- **Check**: Shape is in `closed_shapes` dict

### Version History

**v1.2** (Current)
- Refactored code structure
- Improved code quality
- Updated documentation

**v1.1**
- Fixed crashing when SVG size is not int

**v1.0**
- Shape animation feature added
- Added `anim_type` parameter

**Earlier**
- Initial release with basic drawing and filling

---

## CI/CD Pipeline

### GitHub Actions Workflow
**File**: `.github/workflows/python-publish.yml`

**Triggers**: On release published

**Jobs**:
1. **release-build**: Build distribution packages
   - Setup Python 3.x
   - Install `build` package
   - Run `python -m build`
   - Upload artifacts

2. **pypi-publish**: Publish to PyPI
   - Download build artifacts
   - Publish using trusted publishing (OIDC)
   - Update PyPI project page

**Publishing Process**:
1. Create GitHub release with version tag
2. Workflow automatically builds and publishes to PyPI
3. Package available at https://pypi.org/project/Kivg/

---

## Quick Reference

### Main API Methods
```python
# Initialize
kivg = Kivg(widget)

# Draw static
kivg.draw("file.svg")

# Draw animated
kivg.draw("file.svg", animate=True, anim_type="seq")

# Shape animation
kivg.shape_animate("file.svg", anim_config_list=[...])
```

### Animation Config Keys
- `id_`: Shape ID (required)
- `from_`: Direction (optional)
- `t`: Transition (optional, default: "out_sine")
- `d`: Duration (optional, default: 0.3)

### Coordinate Transform Functions
- `transform_x()`, `transform_y()` - Single coordinate
- `transform_point()` - Complex point
- `bezier_points()` - Full bezier
- `line_points()` - Full line

### Useful External Tools
- **SVGOMG**: https://jakearchibald.github.io/svgomg/
- **Path to Bezier**: https://itchylabs.com/tools/path-to-bezier/
- **Relative to Absolute**: https://codepen.io/thednp/pen/EgVqLw

---

## Contact & Support

- **Author**: Shashi Ranjan
- **Email**: shashiranjankv@gmail.com
- **GitHub**: https://github.com/shashi278/svg-anim-kivy
- **PyPI**: https://pypi.org/project/Kivg/
- **Issues**: https://github.com/shashi278/svg-anim-kivy/issues

---

**End of AI Agent Documentation**
