# The Boy Scout Rule

> "Always leave the campground cleaner than you found it."
> — Robert Baden-Powell

> "Always check a module in cleaner than when you checked it out."
> — Robert C. Martin, *Clean Code*

## The Philosophy

You don't have to make every module perfect. You simply have to make it **a little bit better** than when you found it.

If we all followed this simple rule:
- Our systems would gradually get better as they evolved
- Teams would care for the system as a whole
- The relentless deterioration of software would end

## When Working on Code

Every time you touch code, look for **at least one small improvement**:

### Quick Wins (Do These Immediately)
- Rename a poorly named variable
- Delete a redundant comment
- Remove dead code or unused imports
- Replace a magic number with a named constant
- Extract a deeply nested block into a well-named function

### Deeper Improvements (When Time Allows)
- Split a function that does multiple things
- Remove duplication (DRY)
- Add missing boundary checks
- Improve test coverage

## The Rule in Practice

```python
# You're asked to fix a bug in this function:
def proc(d, x, flag=False):
    # process data
    for i in d:
        if i > 0:
            if flag:
                x.append(i * 1.0825)  # tax
            else:
                x.append(i)
    return x

# Don't just fix the bug and leave.
# Leave it cleaner:
TAX_RATE = 0.0825

def process_positive_values(
    values: list[float],
    apply_tax: bool = False
) -> list[float]:
    """Filter positive values, optionally applying tax."""
    rate = 1 + TAX_RATE if apply_tax else 1
    return [v * rate for v in values if v > 0]
```

## The Mindset

**Don't:**
- Leave code worse than you found it
- Say "that's not my code"
- Wait for a dedicated refactoring sprint
- Make massive changes unrelated to your task

**Do:**
- Make one small improvement with every commit
- Fix what you see, even if you didn't break it
- Keep changes proportional to your task
- Leave a trail of quality improvements

## AI Behaviour

When working on code:
1. Complete the requested task first
2. Identify at least one small cleanup opportunity
3. Note the improvement made (e.g., "Also cleaned up: renamed `x` to `results` for clarity")

When reviewing code:
1. Flag violations by rule number
2. Suggest incremental improvements, not complete rewrites

Every piece of code you touch gets a little better. Not perfect—just better.

Over time, better compounds into excellent.
