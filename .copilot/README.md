# Copilot Agent Configuration

This directory contains AI agent definitions and plans for the Kivg repository.

## Directory Structure

See `repository_guide.md` for the complete repository structure and architecture.

**This directory contains**:
- `agents/` - Agent definitions (roles, capabilities, guidelines)
- `plans/` - Implementation plans (organized by date)
- `repository_guide.md` - Complete repository documentation

## Agent Usage

### Code Implementer Agent
**Purpose**: Implement code changes according to plan  
**Skills**: Python, Kivy, code refactoring, type hints  
**Usage**: `@code_implementer Implement Phase 1.2 constants module`

### Test Writer Agent
**Purpose**: Write comprehensive unit and integration tests  
**Skills**: pytest, mocking, test design  
**Usage**: `@test_writer Create tests for svg_parser module`  
**Progress**: 55 tests completed (data_classes: 8, path_utils: 47)

### Test Runner Agent
**Purpose**: Run tests and validate implementations  
**Skills**: pytest execution, result interpretation  
**Usage**: `@test_runner Validate Phase 1 changes`

### Git Manager Agent
**Purpose**: Handle git operations (commit, push, PR)  
**Skills**: git, GitHub API, PR creation  
**Usage**: `@git_manager Create PR for Phase 1 improvements`

## Plan Naming Convention

Plans are organized by date and feature:
- Format: `YYYY-MM-DD_feature_name/`
- Example: `2026-03-08_phase1_code_quality/`

Each plan contains:
- `plan.md` - Original detailed plan
- `progress.md` - Current progress and completion status
- `testing.md` - Testing procedures and validation

## Agent Guidelines

1. **Always read `repository_guide.md` first** for context
2. **Check the relevant plan** before starting work
3. **Update progress.md** after completing tasks
4. **Follow existing code style** and patterns
5. **Maintain backward compatibility** unless explicitly stated
6. **Test thoroughly** before committing

## Quick Start for Agents

```bash
# 1. Read repository guide
cat .copilot/repository_guide.md

# 2. Check active plans
ls -la .copilot/plans/

# 3. Read specific plan
cat .copilot/plans/2026-03-08_phase1_code_quality/plan.md

# 4. Check progress
cat .copilot/plans/2026-03-08_phase1_code_quality/progress.md
```

## Finding Active Plans

To see what work is currently being done:

```bash
# List all plans
ls -la .copilot/plans/

# Check latest plan (sort by date)
ls -t .copilot/plans/ | head -1

# Read status of a specific plan
cat .copilot/plans/[plan-name]/status.md
```

---

**Last Updated**: 2026-03-08  
**Maintained By**: AI Agents
