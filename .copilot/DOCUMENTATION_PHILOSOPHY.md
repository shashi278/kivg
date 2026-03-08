# Documentation Philosophy

**Purpose**: Guidelines for maintaining `.copilot/` documentation

## Core Principles

### 1. Keep Top-Level Docs Generic

**Files that should be generic**:
- `.copilot/README.md` - Agent system overview
- `.copilot/ORGANIZATION_SUMMARY.md` - How system works
- `.copilot/repository_guide.md` - Repository architecture

**Why**: These files explain the *system*, not specific work. They should remain useful regardless of which plans are active or completed.

**Bad**: ❌
```markdown
## Current Status
- Phase 1: 40% complete
- Files modified: 5
- Next: Add type hints to mesh_handler.py
```

**Good**: ✅
```markdown
## Checking Status
To see current work:
- Check .copilot/plans/[plan-name]/status.md
- Each plan tracks its own progress
```

### 2. Keep Plan Details in Plans

**Plan-specific information goes in**:
- `.copilot/plans/[plan-name]/status.md` - Current progress
- `.copilot/plans/[plan-name]/progress.md` - Detailed changes
- `.copilot/plans/[plan-name]/plan.md` - Implementation details

**Why**: Plans come and go. Specific details belong with their plan, not in global docs.

**What belongs in plan files**:
- Completion percentages
- Files modified
- Specific tasks remaining
- Metrics and statistics
- Next immediate steps

### 3. Date-Based Plan Naming

**Format**: `YYYY-MM-DD_feature_name/`

**Examples**:
- `2026-03-08_phase1_code_quality/`
- `2026-03-15_add_async_support/`
- `2026-04-01_performance_improvements/`

**Why**: 
- Clear chronological order
- Easy to find latest work
- Historical context preserved
- No naming conflicts

### 4. Each Plan is Self-Contained

**Required files in each plan**:
```
plans/YYYY-MM-DD_feature_name/
├── plan.md        # Detailed implementation plan
├── status.md      # Current progress (updated frequently)
├── progress.md    # Summary of completed work
└── testing.md     # Testing procedures (if applicable)
```

**Why**: Anyone (human or AI) can understand a plan's scope and status by reading just that plan's directory.

## Agent Guidelines

### When Creating New Plans

```bash
# Create plan directory
mkdir -p .copilot/plans/$(date +%Y-%m-%d)_feature_name

# Create required files
cd .copilot/plans/$(date +%Y-%m-%d)_feature_name
touch plan.md status.md progress.md testing.md
```

### When Updating Documentation

**Update Plan Files** (frequently):
- `status.md` - Every major milestone
- `progress.md` - When work is complete
- `testing.md` - When tests are added/changed

**Update Global Files** (rarely):
- Only when the *system* changes
- New agent types added
- New documentation patterns
- Directory structure changes

### When Plans Complete

**Don't delete completed plans**. They serve as:
- Historical reference
- Learning resource for future work
- Audit trail of changes

Plans naturally become inactive when their status shows 100% complete.

## Anti-Patterns to Avoid

### ❌ Don't: Put specific metrics in global docs
```markdown
# .copilot/README.md
Current coverage: 85%
Files remaining: 5
```

### ✅ Do: Reference the plan instead
```markdown
# .copilot/README.md
To see metrics, check the active plan's status.md file
```

### ❌ Don't: Duplicate plan details
Having the same information in both global docs and plan files.

### ✅ Do: Single source of truth
Plan details live in plan files only. Global docs explain how to find them.

### ❌ Don't: Name plans vaguely
```
plans/improvements/
plans/fixes/
plans/new_feature/
```

### ✅ Do: Use dates and clear names
```
plans/2026-03-08_phase1_code_quality/
plans/2026-03-15_fix_animation_bug/
plans/2026-04-01_add_caching_layer/
```

## Maintenance

### Monthly Review

Check if global documentation needs updates:
- Are agent roles still accurate?
- Is the directory structure still correct?
- Are guidelines still relevant?

### Quarterly Cleanup

Review old plans:
- Are completed plans still relevant?
- Can very old plans be archived?
- Is there learnings to extract?

### Before New Plans

Check existing structure:
- Follow naming convention
- Include all required files
- Link to relevant docs

## Benefits

✅ **Scalability**: System handles 10 or 100 plans equally well  
✅ **Clarity**: Global docs stay focused and useful  
✅ **Maintainability**: Changes are localized  
✅ **Discoverability**: Easy to find current work  
✅ **Historical Context**: Past work is preserved  

---

**Document Purpose**: Guidelines for documentation maintainers  
**Last Updated**: 2026-03-08  
**Applies To**: All `.copilot/` documentation
