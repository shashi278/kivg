# Testing Guide for Phase 1 Changes

This guide helps you verify that Phase 1 improvements work correctly and don't break existing functionality.

## Quick Syntax Check

```bash
# Compile all modified files
python3 -m py_compile kivg/constants.py
python3 -m py_compile kivg/exceptions.py
python3 -m py_compile kivg/svg_parser.py
python3 -m py_compile kivg/path_utils.py
python3 -m py_compile kivg/main.py

# Or all at once
python3 -m py_compile kivg/*.py kivg/**/*.py
```

## Manual Testing

### Test 1: Import New Modules
```python
# Test constants
from kivg.constants import (
    DEFAULT_LINE_WIDTH,
    AnimationType,
    AnimationDirection
)
print(f"Line width: {DEFAULT_LINE_WIDTH}")
print(f"Sequential type: {AnimationType.SEQUENTIAL.value}")
```

### Test 2: Import Exceptions
```python
from kivg.exceptions import KivgError, SVGParseError
try:
    raise SVGParseError("Test error")
except KivgError as e:
    print(f"Caught: {e}")
```

### Test 3: Test Enhanced svg_parser
```python
from kivg.svg_parser import parse_svg

# Test with valid file
try:
    dimensions, paths = parse_svg("demo/icons/github.svg")
    print(f"SVG dimensions: {dimensions}")
    print(f"Number of paths: {len(paths)}")
except Exception as e:
    print(f"Error: {e}")

# Test with invalid file (should raise helpful error)
try:
    parse_svg("nonexistent.svg")
except Exception as e:
    print(f"Expected error: {e}")
```

### Test 4: Test Widget Validation
```python
from kivy.uix.widget import Widget
from kivg import Kivg

# Valid widget
widget = Widget()
widget.size = (256, 256)
kivg = Kivg(widget)
print("✓ Valid widget accepted")

# Invalid widget (should raise WidgetError)
try:
    kivg = Kivg("not a widget")
except Exception as e:
    print(f"✓ Invalid widget rejected: {e}")
```

### Test 5: Test draw() with File Validation
```python
from kivy.uix.widget import Widget
from kivg import Kivg

widget = Widget()
widget.size = (256, 256)
kivg = Kivg(widget)

# Test with valid file
try:
    kivg.draw("demo/icons/github.svg")
    print("✓ Valid SVG loaded")
except Exception as e:
    print(f"Error: {e}")

# Test with missing file (should raise FileNotFoundError)
try:
    kivg.draw("missing.svg")
except Exception as e:
    print(f"✓ Missing file caught: {type(e).__name__}")
```

### Test 6: Test Animation Config Validation
```python
from kivy.uix.widget import Widget
from kivg import Kivg

widget = Widget()
widget.size = (256, 256)
kivg = Kivg(widget)

# Valid config
config = [
    {"id_": "shape1", "from_": "left", "d": 0.4}
]
try:
    kivg.shape_animate("demo/icons/text.svg", config)
    print("✓ Valid config accepted")
except Exception as e:
    print(f"Error: {e}")

# Invalid config (missing id_)
bad_config = [
    {"from_": "left", "d": 0.4}  # Missing id_
]
try:
    kivg.shape_animate("demo/icons/text.svg", bad_config)
except Exception as e:
    print(f"✓ Invalid config rejected: {type(e).__name__}")
```

## Run Demo App

The most comprehensive test is running the existing demo:

```bash
cd demo
python3 main.py
```

**What to verify:**
- [ ] App starts without errors
- [ ] Icons display in button grid
- [ ] Clicking buttons triggers animations
- [ ] Sequential animation works (default)
- [ ] Shape animations work (for specific icons)
- [ ] No console errors or warnings

## Expected Behavior

### What Should Work the Same:
- ✅ All existing demos and examples
- ✅ Static SVG rendering
- ✅ Animated path drawing
- ✅ Shape animations with configs
- ✅ Fill and stroke options
- ✅ All animation transitions

### What's Better:
- ✅ Better error messages when files not found
- ✅ Clear error when widget is invalid
- ✅ Validation catches config errors early
- ✅ SVG validation catches malformed files
- ✅ IDE autocomplete works better with type hints

### What Might Fail (Known Issues):
- Missing Kivy installation will prevent imports
- Missing demo SVG files will cause FileNotFoundError
- Invalid SVG structure will raise clear errors (this is good!)

## Type Checking (Optional)

If you have mypy installed:

```bash
pip install mypy
mypy kivg/constants.py
mypy kivg/exceptions.py
mypy kivg/svg_parser.py
mypy kivg/path_utils.py
mypy kivg/main.py
```

Expected: No errors (some warnings about Kivy types are OK)

## Visual Inspection

### Check Constants File
```bash
cat kivg/constants.py
```
Verify:
- [ ] All enums defined correctly
- [ ] Default values match original code
- [ ] Comments are clear

### Check Exceptions File
```bash
cat kivg/exceptions.py
```
Verify:
- [ ] All exceptions inherit from KivgError
- [ ] Docstrings explain when they're raised

### Check Updated Files
```bash
git diff kivg/svg_parser.py
git diff kivg/path_utils.py
git diff kivg/main.py
```
Verify:
- [ ] Only intended changes present
- [ ] No accidental modifications
- [ ] Imports added correctly

## Rollback Instructions

If something breaks:

```bash
# Undo all changes
git checkout kivg/svg_parser.py
git checkout kivg/path_utils.py
git checkout kivg/main.py

# Remove new files
rm kivg/constants.py
rm kivg/exceptions.py
```

## Success Criteria

Phase 1 is successful if:

- [x] All files compile without syntax errors
- [x] No circular import dependencies
- [ ] Demo app runs without errors
- [ ] All existing functionality works
- [ ] Error messages are more helpful
- [ ] Code is more maintainable

## Troubleshooting

### Issue: Import errors
**Solution**: Make sure you're in the repository root directory

### Issue: Kivy not found
**Solution**: Install Kivy: `pip install kivy`

### Issue: Demo app won't run
**Solution**: Check that demo/icons/ directory exists with SVG files

### Issue: Type errors with mypy
**Solution**: Install type stubs: `pip install types-all`

## Next Steps After Testing

Once testing is complete:

1. ✅ Commit changes with clear message
2. ✅ Push to feature branch
3. ✅ Create pull request
4. ✅ Request code review
5. ✅ Continue with remaining Phase 1 tasks

## Test Checklist

Basic Tests:
- [ ] Files compile
- [ ] Imports work
- [ ] Constants accessible
- [ ] Exceptions can be raised

Functional Tests:
- [ ] Demo app runs
- [ ] SVG parsing works
- [ ] Animations work
- [ ] Error handling works

Validation Tests:
- [ ] Invalid file rejected
- [ ] Invalid widget rejected
- [ ] Invalid config rejected
- [ ] Malformed SVG rejected

Quality Tests:
- [ ] Type hints correct
- [ ] Docstrings comprehensive
- [ ] Error messages helpful
- [ ] Code more readable

---

**Status**: Ready for testing  
**Estimated Testing Time**: 10-15 minutes  
**Required**: Python 3.6+, Kivy 2.0+
