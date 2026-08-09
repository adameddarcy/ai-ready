# Preflight

One lightweight pass before writing code on non-trivial tasks — approach, risk,
and volatility in a single calibrated output block, so small tasks stay small.

---

## When to run

Trigger on: a new component/module/service/API, choosing between implementation
approaches, a refactor, anything touching persistence/external deps/shared state,
a "how should I..." ask, anything the user flags as important or long-lived.

**Skip for**: typos, renames, shell one-offs, single-line fixes where there's no
real alternative.

---

## The pass

Answer inline, tight — a senior engineer thinking out loud, not a form. If a step
doesn't apply, say so in one clause and move on.

1. **Problem** — restate the actual goal in one sentence. Is the stated task the
   real task, or is a simpler problem hiding inside it?
2. **Approach + alternative** — name the approach you'll take and the one real
   alternative you're not taking, with its tradeoff. One line each. Skip the
   alternative only if there's genuinely one sane way to do this.
3. **Risk** — walk both lenses, but only the ones this change actually touches:
   - *Security*, only if this touches auth, an endpoint/webhook, persistence,
     user input, a new dependency, or a trust boundary: who can call this, what
     enters/leaves, the worst plausible misuse — name the specific input or
     endpoint, not a category.
   - *Failure*, only if this has external calls, state mutations, or
     concurrency: what breaks, when (before/during/after the state change), what
     state is left behind if it does.
   Neither applies → write "RISK: none — no new surface" and move on. Don't
   manufacture risk to fill the section.
4. **Volatility** — medium/large changes only. What's most likely to change here
   vs. stay stable? Don't couple the volatile part to the stable core. For real
   service/module decomposition, use `/righting-software` instead of guessing here.

---

## Output block

Always this shape, always this order. Omit a line only if step 3/4 said to skip it:

```
APPROACH: [one sentence]
ALTERNATIVE: [the road not taken + why]
RISK: [security and/or failure findings, or "none — no new surface"]
INVARIANTS: [what must hold even on failure — these become the first red tests]
VOLATILITY: [what's stable vs. volatile, if this is medium/large]
```

Then implement, TDD-first per `/tdd-guide`: invariant tests red, happy-path
tests red, then green.

---

## Calibration by task scope

| Task scope | Depth |
|---|---|
| Small (single function, <50 LOC) | Problem + Approach only |
| Medium (new module, interface design) | Full pass |
| Large (new service, cross-cutting refactor) | Full pass + `/righting-software` for decomposition |

---

## Anti-patterns

- **Performing the ritual**: "ASSUMPTION: none" with no real uncertainty behind
  it — question harder, or admit the step doesn't apply and skip it honestly.
- **Manufacturing risk**: naming a STRIDE category or failure mode that doesn't
  actually apply just to fill the block.
- **Retrofitting**: writing the code first, backfilling the block after. The
  value is in doing it before.
