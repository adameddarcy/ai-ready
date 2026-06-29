# Socratic Preflight

A structured inner dialogue Claude runs **before writing any code** on non-trivial tasks.
The goal is to slow down the first instinct, surface hidden assumptions, and commit to a
reasoned approach rather than the nearest plausible one.

---

## When to activate

Activate on any task involving:
- Designing or scaffolding a new component, module, service, or API
- Choosing between implementation approaches
- Refactoring or restructuring existing code
- Anything touching persistence, external dependencies, or shared state
- Any request phrased as "how should I...", "what's the best way to...", "design me a..."
- Anything the user flags as important, complex, or long-lived

**Skip only for**: fixing typos, renaming symbols, running shell commands, trivial
one-liner fixes where the solution space is genuinely closed.

When in doubt, run the preflight. The cost of a brief dialogue is always lower than the
cost of building the wrong thing confidently.

---

## The Five Questions

Work through these in order. Answer each one honestly before moving to the next.
Be concise — 2–4 sentences per answer is the target.

### Q1 — What problem am I actually solving?

Restate the goal in your own words, without referencing the proposed solution.
Ask: *Is the stated task the real task? Is there a simpler problem hiding inside a complex one?*

Watch for:
- XY problems (user asks for X to solve Y; X may not be the right path)
- Scope creep embedded in the request
- Conflation of the immediate need with a speculative future need

### Q2 — What am I assuming that I haven't verified?

List the top 2–3 implicit assumptions baked into your first instinct.
Ask: *What would have to be true for my default approach to be correct?*

Common unexamined assumptions:
- The data shape / schema is stable
- The caller controls the full execution context
- Performance is or isn't a constraint
- The existing code can be trusted / is worth building on
- The user wants a general solution, not a specific one

### Q3 — What are the real alternatives?

Name at least two meaningfully different approaches — not variations on the same theme.
Ask: *What would a developer with a different background reach for here?*

Think across dimensions:
- Build vs. use existing (library, stdlib, framework feature)
- Stateful vs. stateless
- Synchronous vs. event-driven
- Composition vs. inheritance
- More abstraction vs. less abstraction
- Inline vs. extracted

For each alternative, note its primary tradeoff in one sentence.

### Q4 — What is most likely to change?

Identify the volatility axis: *what part of this is most likely to evolve?*
Ask: *Am I coupling stable things to volatile things?*

Apply volatility thinking (per Juval Löwy / righting-software principles where applicable):
- Separate what changes often from what changes rarely
- Don't let a volatile detail (a provider, a config shape, a UI concern) infect a stable core
- Prefer interfaces at volatility boundaries

If this skill is being used alongside `righting-software`, cross-reference its
decomposition output here.

### Q5 — How does this fail?

Name the most likely failure mode under realistic conditions — not worst-case catastrophe,
but the thing that will actually bite you in three months.
Ask: *What does the on-call engineer curse about at 2am?*

Consider:
- Partial failure (what if the external call times out?)
- State corruption (what if this runs twice?)
- Observability (can you tell when it's broken?)
- Coupling failure (what breaks if a dependency changes?)

---

## Commit Block

After the five questions, write a short **Commit Block** before touching any code:

```
APPROACH: [One sentence describing the chosen implementation]
RATIONALE: [Why this over the alternatives — one or two sentences]
TRADEOFF ACCEPTED: [What you're giving up and why that's acceptable]
VOLATILITY BOUNDARY: [Where you're drawing the abstraction line, if applicable]
```

This is the contract between reasoning and implementation. The code that follows
should be consistent with this commit.

---

## Output format

Structure responses as follows:

1. **Preflight** — Run the five questions visibly, with brief answers
2. **Commit Block** — State the chosen approach
3. **Implementation** — Write the code

The preflight should feel like a senior engineer thinking out loud, not a bureaucratic
checklist. Keep it tight. If a question has an obvious, uninteresting answer, say so
briefly and move on. The value is in the questions that *don't* have obvious answers.

---

## Calibration by task scope

| Task scope | Preflight depth |
|---|---|
| Small (single function, <50 LOC) | Q1 + Q3 + Commit Block minimum |
| Medium (new module, interface design) | All five questions |
| Large (new service, system design, cross-cutting refactor) | All five + reference `righting-software` volatility decomposition if available |

---

## Integration with other skills

- **righting-software**: Q4 (volatility) should explicitly reference volatility
  decomposition output if that skill is active in the same session
- **tdd-guide**: Commit Block should note expected test surface before code is written
- **clean-code / boyscout**: Q5 failure mode should inform naming, error paths, and
  observable state in the implementation

---

## Anti-patterns to avoid

- **Performing the checklist**: Going through motions without genuine uncertainty.
  If you find yourself writing "assumption: none", question harder.
- **Analysis paralysis**: The goal is a 60-second dialogue, not a dissertation.
  Timebox it mentally and commit.
- **Retrofitting**: Don't write the code first and fill in the preflight afterward.
  The whole value is in doing it before.
- **Skipping Q3**: "There's really only one way to do this" is almost never true.
  Name the alternative even if you immediately dismiss it.
