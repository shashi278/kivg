# Testing Infrastructure Plan

**Created**: 2026-03-08  
**Branch**: test/add-comprehensive-test-suite  
**Goal**: 100% test coverage, one module at a time

## Current State
- Code: ~2,111 lines (14 files)
- Tests: None
- pytest installed, no config

## Test Structure
```
tests/
├── conftest.py
├── fixtures/ (test SVGs)
└── unit/
    ├── test_constants.py
    ├── test_path_utils.py ⭐ START
    ├── test_svg_parser.py
    ├── test_mesh_handler.py
    ├── test_svg_renderer.py
    ├── test_drawing_manager.py
    ├── test_animation_shapes.py
    └── test_main.py
```

## Order (by priority)
1. Infrastructure (pytest.ini, conftest.py)
2. test_constants.py
3. test_path_utils.py ⭐ (173 lines, 15 functions)
4. test_svg_parser.py
5. Others...

## Targets
- 150-200 tests
- 95%+ coverage
- < 60s execution
- Full mocking (Kivy, I/O)
