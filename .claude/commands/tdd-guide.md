# TDD Guide — Python / Pytest

## TDD Workflow (Red-Green-Refactor)

1. **Red**: Write a failing test first
2. **Green**: Write the minimum code to make it pass
3. **Refactor**: Improve code while keeping tests green
4. **Repeat**: Small iterations, frequent commits

## Test Generation

- **From requirements**: Convert user stories and API specs into test cases before writing implementation
- **Test behavior, not implementation**: Focus on what code does, not how
- **One assertion focus**: Each test should verify one specific behavior
- **Descriptive names**: Test names should read like specifications

## Suggesting Missing Scenarios

When reviewing tests, identify untested:
- Edge cases and boundary values
- Error conditions and exception paths
- Empty/null/zero inputs
- Permission and validation failures

## Test Quality Standards

- **Independent**: Each test runs in isolation
- **Fast**: Unit tests under 100ms each
- **Deterministic**: Always produce the same result
- **Clear failures**: Assertion messages explain what went wrong
- **No test smells**: No logic in tests, no shared mutable state, no order dependence

## Coverage Goals

- **80%+ line coverage** as a baseline
- **100% on critical paths**: Authentication, payments, data validation
- **Branch coverage matters**: Line coverage alone is insufficient
- **Don't game metrics**: Meaningful tests over coverage numbers

## Pytest Specifics

- **Frameworks**: Pytest (preferred), unittest
- **Coverage**: pytest-cov / coverage.py
- **Fixtures**: Use `@pytest.fixture` for setup; prefer function scope
- **Parametrize**: Use `@pytest.mark.parametrize` for data-driven tests
- **Markers**: Use markers to categorise tests (slow, integration, etc.)

## Prioritisation

When recommending test improvements, rank by:
- **P0 (critical)**: Untested failure modes that could cause data loss or security issues
- **P1 (important)**: Missing happy-path coverage, unhandled edge cases
- **P2 (nice-to-have)**: Naming improvements, fixture cleanup, minor refactors
