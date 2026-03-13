# Kivy Testing Research & Recommendations

## Overview
This document outlines testing strategies and tools for the Kivg library, which is a Kivy-based SVG animation library.

## Current Testing Status
- **Unit Tests**: Comprehensive test coverage for core modules (✅ Complete)
  - `data_classes.py` - 100% coverage
  - `path_utils.py` - 100% coverage  
  - `svg_parser.py` - 28 tests, comprehensive coverage
- **Integration Tests**: Not yet implemented
- **UI/Widget Tests**: Not yet implemented

## Kivy Testing Options

### 1. **GraphUnitTest (Built-in Kivy Testing)**
**Status**: Official Kivy testing framework

**Pros**:
- Official Kivy testing framework
- Integrated with unittest
- Can render widgets and simulate touch events
- Good for widget-level testing
- Well-documented in Kivy docs

**Cons**:
- Requires graphical environment (can run headless with Xvfb on CI)
- Tests run slower than pure unit tests
- More complex setup

**Use Case**: Best for testing Kivy widget behavior and visual components

**Setup**:
```python
from kivy.tests.common import GraphicUnitTest

class TestKivgWidget(GraphicUnitTest):
    def test_kivg_drawing(self):
        from kivg import Kivg
        # Test widget behavior
```

### 2. **pytest-kivy** (Community Plugin)
**Status**: Third-party plugin, less maintained

**Repository**: Not actively maintained as of 2024

**Decision**: ❌ Not recommended due to maintenance concerns

### 3. **Mock-based Testing** (Current Approach)
**Status**: ✅ Currently used in the project

**Pros**:
- Fast execution
- No GUI required
- Easy to run in CI/CD
- Excellent for logic testing

**Cons**:
- Cannot test actual rendering or visual behavior
- Requires mocking Kivy components

**Use Case**: Perfect for testing business logic, parsers, utilities (what we currently do)

### 4. **Integration Testing with Headless Mode**
**Status**: Recommended for CI/CD

**Approach**: Use Xvfb (virtual framebuffer) for headless testing

**Setup for CI**:
```yaml
- name: Setup Xvfb
  run: |
    sudo apt-get install -y xvfb
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    echo "DISPLAY=:99" >> $GITHUB_ENV
```

## Recommended Testing Strategy for Kivg

### Phase 1: Unit Tests (✅ COMPLETED)
- Test all non-UI logic
- Mock Kivy components
- Focus on: parsers, utilities, data classes, animation logic
- **Coverage Target**: 90%+ for non-UI code

### Phase 2: Widget-Level Tests (NEXT)
**Scope**: Test Kivg widget behavior without full app

**Approach**:
```python
from kivy.tests.common import GraphicUnitTest
from kivg import Kivg
from kivy.uix.widget import Widget

class TestKivgWidget(GraphicUnitTest):
    def test_kivg_initialization(self):
        """Test Kivg can be instantiated"""
        parent = Widget()
        kivg = Kivg(parent)
        self.assertIsNotNone(kivg)
    
    def test_draw_svg(self):
        """Test drawing an SVG file"""
        parent = Widget()
        kivg = Kivg(parent)
        # Test with a simple SVG
        kivg.draw("tests/fixtures/simple.svg")
        # Assert instructions were added
        self.assertTrue(len(parent.canvas.children) > 0)
```

### Phase 3: Integration Tests (FUTURE)
**Scope**: Test complete demo app functionality

**Approach**: Run demo app in headless mode and verify:
- App launches without errors
- SVG files load correctly
- Animations execute
- No crashes

### Phase 4: Visual Regression Testing (OPTIONAL)
**Tools**: 
- Kivy's screenshot capabilities
- Image comparison libraries (Pillow, OpenCV)

**Use Case**: Ensure visual output remains consistent across changes

## Recommendation for This Project

### ✅ **Keep Current Approach + Add Selective Widget Tests**

**Rationale**:
1. **Current unit tests are excellent** - Fast, comprehensive, CI-friendly
2. **Add GraphicUnitTest only for critical widget behavior**:
   - Kivg initialization
   - SVG drawing creates canvas instructions
   - Animation callbacks work correctly
3. **Don't over-test UI** - The library's core value is in parsing/animation logic, not visual appearance

### Proposed Test Structure
```
tests/
├── unit/                          # ✅ Current - Fast, no GUI
│   ├── test_data_classes.py
│   ├── test_path_utils.py
│   ├── test_svg_parser.py
│   └── test_animation_logic.py    # TODO: Add animation logic tests
├── widget/                        # 🆕 New - GraphicUnitTest
│   ├── test_kivg_widget.py       # Basic widget functionality
│   └── test_animation_widget.py  # Animation execution
├── integration/                   # 🔮 Future - Full app tests
│   └── test_demo_app.py
└── fixtures/                      # Test data
    ├── simple.svg
    ├── animated.svg
    └── complex.svg
```

### Implementation Priority

**NOW (Before Next PR)**:
1. ✅ Unit tests for remaining modules (animation logic)
2. Create test fixtures (simple SVG files)
3. Add 2-3 GraphicUnitTest cases for core Kivg widget

**LATER**:
1. Integration test for demo app
2. CI/CD configuration for headless testing (if widget tests added)

### Running Tests Locally

**Unit tests** (fast, always run):
```bash
pytest tests/unit -v --cov=kivg --cov-report=term-missing
```

**Widget tests** (slower, optional locally):
```bash
pytest tests/widget -v
```

**All tests**:
```bash
pytest -v --cov=kivg
```

## CI/CD Considerations

### Current Setup (GitHub Actions)
- ✅ Runs unit tests on every PR
- ✅ Fast execution (~30s)
- ✅ No special setup needed

### If Adding Widget Tests
Would need to add to workflow:
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y libgl1-mesa-dev xvfb
    
- name: Run tests with Xvfb
  run: |
    xvfb-run -a pytest tests/ -v --cov=kivg
```

## Demo App Testing

### Manual Testing (Current Approach)
The demo app (`demo/main.py`) can be run manually to verify:
- SVG icons load and display correctly
- Path animations work (drawing effect)
- Shape animations work with custom configs
- No crashes or errors

**To run demo**:
```bash
cd demo
python3 main.py
```

**What to test**:
1. App launches and shows icon grid
2. Click icons to see animations
3. Test different animation types:
   - Path drawing: github, python, kivy, etc.
   - Shape animations: pie_chart, so (Stack Overflow), text

### Automated Demo Testing (Future)
Could use Kivy's screenshot and automation features:
```python
from kivy.tests.async_common import UnitTestTouch

class TestDemoApp(GraphicUnitTest):
    def test_app_launches(self):
        from demo.main import KivgDemo
        app = KivgDemo()
        # Simulate app lifecycle
        # Verify no crashes
```

## Resources

- **Kivy Testing Docs**: https://kivy.org/doc/stable/guide/unittests.html
- **GraphicUnitTest**: https://kivy.org/doc/stable/api-kivy.tests.common.html
- **pytest-cov**: https://pytest-cov.readthedocs.io/

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-09 | Keep mock-based unit tests as primary strategy | Fast, reliable, CI-friendly |
| 2026-03-09 | Add selective GraphicUnitTest for critical widget behavior | Ensure core widget functionality works |
| 2026-03-09 | Skip pytest-kivy | Maintenance concerns |
| 2026-03-09 | Defer full integration tests | Not critical for library stability |
| 2026-03-09 | Recommend manual demo testing | Most practical for visual verification |

## Conclusion

**Recommended approach**: 
- ✅ **Continue with comprehensive unit tests** (current approach is excellent)
- ✅ **Manual demo app testing** for visual verification (practical and effective)
- 🆕 **Add 2-3 GraphicUnitTest cases** for critical Kivg widget behavior (optional, for future)
- ⏳ **Defer integration testing** until library is more mature

This provides a good balance between test coverage, execution speed, and maintenance burden.
