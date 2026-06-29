# Failure Modes

Define failure modes as invariants. Test the invariants before writing the happy path.
A system that only works when everything goes right doesn't work.

---

## When to activate

Run this whenever a feature involves:
- External calls (APIs, databases, queues, file systems, network)
- State mutations (writes, updates, deletes, transitions)
- Concurrent or async operations
- User-facing flows where partial failure is possible
- Anything where "what if this fails halfway through?" has a non-trivial answer

**Skip for**: pure functions with no side effects, read-only display logic,
single-expression transforms.

---

## Step 1 — Enumerate failure modes

For the feature being built, list the concrete ways it can fail. Not theoretical
categories — actual scenarios tied to real operations in the code.

For each failure mode, answer:
- **What breaks?** (the specific operation — a network call, a write, a parse)
- **When?** (before, during, or after the critical state change)
- **What state is left behind?** (partial write, orphaned resource, stale cache,
  inconsistent references)

Focus on the failures that are **likely**, not exotic. The common ones:
- External service is unreachable or slow
- Input is technically valid but semantically wrong
- Operation succeeds but the confirmation/follow-up fails
- Same operation runs twice (retry, race, duplicate message)
- Operation interleaves with another operation on the same state

---

## Step 2 — Define invariants

Convert each failure mode into an invariant — a property that **must hold regardless
of whether the operation succeeds or fails**.

Good invariants are:
- **Testable**: You can write an assertion for them
- **Unconditional**: They hold in success AND failure paths
- **Specific**: They name actual data, state, or behaviour

Write them in this form:

```
INVARIANT: [plain-language statement of what must always be true]
FAILURE MODE: [the scenario that would violate this if unhandled]
EVIDENCE: [how a test can observe that the invariant holds or is broken]
```

Examples:

```
INVARIANT: A user's balance is never negative after a withdrawal
FAILURE MODE: Concurrent withdrawals pass validation independently, both succeed
EVIDENCE: Assert balance >= 0 after concurrent withdrawal attempts

INVARIANT: If payment capture fails, the order stays in PENDING, not CONFIRMED
FAILURE MODE: Order status updates before payment confirmation returns
EVIDENCE: Simulate payment timeout, assert order.status == PENDING

INVARIANT: Partial batch failures don't leave the successful items unrecoverable
FAILURE MODE: Batch insert fails at item 5 of 10, items 1-4 are committed but
             not recorded in the job status
EVIDENCE: Simulate mid-batch failure, assert all committed items appear in job result
```

---

## Step 3 — Write invariant tests (TDD red phase)

Each invariant becomes a test **before any implementation**. This is where the skill
integrates with the TDD flow:

1. Write the invariant test — it should fail (red) because the handling doesn't exist yet
2. Implement the minimum handling to make it pass (green)
3. Then write the happy-path tests and implementation as normal
4. Refactor with both happy-path and failure-mode tests as your safety net

Invariant tests go **first**, not after. The happy path is easy to get right by accident.
The failure path is easy to get wrong by omission.

### Test structure

Invariant tests should:
- **Simulate the failure** — don't just test that error handling code exists; trigger
  the actual failure condition (mock the timeout, inject the duplicate, force the
  partial write)
- **Assert the invariant, not the mechanism** — test that the balance is non-negative,
  not that a specific lock was acquired. The invariant survives refactors; the
  mechanism doesn't.
- **Name the invariant in the test name** — `test_balance_never_negative_on_concurrent_withdrawal`,
  not `test_withdrawal_error_handling`

### Parametrize where it fits

If multiple failure modes threaten the same invariant, parametrize:

```python
@pytest.mark.parametrize("failure", [
    "timeout",
    "connection_refused",
    "malformed_response",
])
def test_order_stays_pending_when_payment_capture_fails(failure):
    ...
```

---

## Step 4 — Invariant summary

After defining invariants and before writing any implementation, produce a summary:

```
INVARIANTS DEFINED: [count]
FAILURE TESTS WRITTEN: [count]
HIGHEST RISK: [the invariant most likely to be violated in production]
INTEGRATION NOTE: [how these invariants interact with existing tests, if any]
```

---

## Integration with other skills

- **tdd-guide**: This skill extends the TDD red phase. Invariant tests are written
  first, then happy-path tests. The TDD cycle runs as normal — failure-mode red,
  failure-mode green, happy-path red, happy-path green, refactor.
- **socratic-preflight**: If preflight Q5 (how does this fail?) already ran, use its
  output as the starting point for Step 1. Don't repeat the analysis — sharpen it
  into testable invariants.
- **threat-check**: Security-related failure modes from the STRIDE pass should become
  invariants here. A threat without a test is a hope, not a mitigation.

---

## Anti-patterns

- **Testing the mock, not the invariant**: If your test only proves that the mock
  was configured correctly, it's not testing a failure mode. The test should break
  if someone removes the error handling.
- **Invariants that are just happy-path rephrased**: "The function returns the correct
  result" is not a failure-mode invariant. An invariant describes what holds *when
  things go wrong*.
- **Exhaustive enumeration**: You don't need an invariant for every conceivable failure.
  Cover the likely ones and the catastrophic ones. Three good invariants beat twelve
  performative ones.
- **Testing after the fact**: Writing invariant tests after the implementation defeats
  the purpose. The test should force you to think about the failure *before* you
  write the code that handles it.
