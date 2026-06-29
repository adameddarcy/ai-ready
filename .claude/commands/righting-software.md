# Righting Software — Volatility-Based Decomposition

Apply Juval Löwy's core methodology from *Righting Software*: decompose systems along **axes of volatility**, not along functional or domain lines.

Annotate decomposition observations and recommendations with **"Lowy says:"** inline alongside your regular output, so the user can distinguish Löwy-informed analysis from general advice.

---

## Core Principle

> **Decompose by what changes together, not by what belongs together.**

Functional decomposition (grouping by domain, noun, or business capability) produces systems that are coupled to the business — they change whenever the business changes. Volatility-based decomposition produces systems with **stable interfaces over volatile implementations**, dramatically reducing the cost of change.

The question is never *"what does this system do?"* but *"what is likely to change, and what is likely to stay stable?"*

---

## The Four Building Blocks

Löwy's taxonomy for classifying every component:

| Type | Characteristics | Examples |
|------|----------------|---------|
| **Utility** | Stable, reusable, no business knowledge | Logger, Serialiser, Queue, Retry wrapper |
| **Engine** | Volatile implementation, stable interface; encapsulates a single volatile area | Pricing engine, Risk calculator, Recommendation engine |
| **Manager** | Orchestrates Engines and Utilities; contains workflow logic | Order manager, Checkout manager |
| **Client** | Entry point / facade; thin, no logic | REST controller, CLI handler, Event consumer |

**Key rule:** Engines must never call other Engines. Only Managers orchestrate. Clients only call Managers.

---

## Decomposition Process

### Step 1 — Enumerate Use Cases
List the system's use cases (actor + action + outcome). This is your raw material.

### Step 2 — Identify Axes of Volatility
For each use case or area, ask:
- What is most likely to change over the next 2–5 years?
- What is driven by external decisions (business rules, regulations, third parties)?
- What is stable infrastructure (retry logic, auth, transport)?

Cluster volatile areas. Each **distinct axis of volatility** is a candidate Engine.

**Common axes to probe:**
- Pricing / cost calculation logic
- Eligibility / rules / policy
- Integration with specific third-party vendors
- Notification channels (email vs SMS vs push)
- Storage backends
- ML model selection or inference strategy
- Region/locale-specific behaviour

### Step 3 — Name the Volatile Areas
Give each axis a neutral, non-functional name (not "PaymentService" — that's functional). Ask: *if we swapped the implementation entirely, would the caller care?* If no → good Engine boundary.

### Step 4 — Identify Stable Structure
What orchestrates across volatile areas? Those are your Managers. What is reused but never changes with the business? Those are Utilities.

### Step 5 — Validate the Decomposition
Run the smell-check (see below). Revise until it passes.

---

## Functional Decomposition Smells

Flag these explicitly as **anti-patterns** when spotted:

| Smell | Description | Signal |
|-------|-------------|--------|
| **Domain noun services** | Services named after business entities (OrderService, UserService, ProductService) | Likely functional decomposition |
| **Fat orchestrators** | One service that calls 8 others in sequence | Missing Engine layer; orchestrator knows too much |
| **Sibling Engine calls** | EngineA directly depends on EngineB | Violates Engine independence; introduce a Manager |
| **Leaking volatility** | Stable components import volatile ones | Dependency inversion needed |
| **God Manager** | Single Manager that orchestrates everything | Missing decomposition; find sub-volatility axes |
| **Anemic utilities** | "Utilities" that contain business rules | Misclassified; likely an Engine |
| **Chatty clients** | Client calls multiple Managers per request | Missing Manager layer or missing use-case Manager |

---

## Output Format

When analysing or designing, structure your Löwy commentary as:

```
Lowy says: [observation or recommendation]
  → Volatility axis: [what changes here]
  → Classification: [Utility / Engine / Manager / Client]
  → Smell detected: [if applicable]
  → Suggested boundary: [proposed component name and responsibility]
```

For full decomposition analyses, produce a table:

| Component | Type | Volatility Axis | Stable Interface? | Notes |
|-----------|------|----------------|-------------------|-------|
| ...       | ...  | ...            | Yes / No / ?      | ...   |

Follow the table with a dependency diagram in plain text or Mermaid showing allowed call directions (Client → Manager → Engine → Utility only).

---

## Heuristics for Edge Cases

**"Should this be one service or two?"**
Ask: do they share a volatility axis? If yes, same Engine. If they change for different reasons, separate Engines even if they look related.

**"Where does this business rule live?"**
If it changes with business decisions → Engine. If it's a stable algorithm → Utility.

**"Is this a microservice boundary?"**
Löwy is deployment-agnostic. Decompose first by volatility; deployment topology follows. Don't let infrastructure concerns drive decomposition.

**"We have an existing monolith."**
Identify volatility axes within the monolith first. Seam boundaries follow volatility, not file structure or team ownership.

**"This looks like DDD bounded contexts."**
DDD and Löwy are complementary but different. Bounded contexts are often functional; volatility axes cut across them. A single bounded context may contain multiple Engines.

---

## Quick Reference Card

```
VOLATILE?
  Yes → changes with business/external decisions → ENGINE
  No  → reused, algorithmic, infra → UTILITY

ORCHESTRATES?
  Yes → calls Engines/Utilities → MANAGER
  Entry point only → CLIENT

CALL DIRECTION (only allowed):
  Client → Manager → Engine → Utility
                    ↑
           (never Engine → Engine)
```
