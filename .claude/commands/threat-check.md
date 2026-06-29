# Threat Check

A quick threat model pass for large features or significant changes. Not a full security
audit — a focused check that the change doesn't introduce or ignore obvious attack surface.

---

## When to activate

Run this on any change that:
- Introduces or modifies authentication, authorization, or session handling
- Adds or changes an API endpoint, webhook, or external-facing interface
- Touches persistence (database, file system, cache, queue)
- Handles user input, file uploads, or external data
- Introduces a new dependency or external service integration
- Changes trust boundaries (what talks to what, who can call whom)
- Moves or exposes secrets, tokens, or credentials
- Is flagged by the user as large, security-sensitive, or long-lived

**Skip for**: pure UI cosmetics, internal refactors with no boundary changes, documentation,
test-only changes.

---

## Step 1 — Check for an existing threat model

Before doing anything else:
- Look for threat model documents in the repo (`THREAT_MODEL.md`, `docs/security/`,
  `docs/threat*`, or similar)
- If one exists, read it. Check whether the current change:
  - Violates any stated assumptions
  - Introduces a component or flow not covered by the model
  - Changes a trust boundary the model relies on
- If the change conflicts with the existing model, flag it explicitly and note whether
  the model or the code needs updating

If no threat model exists, say so and proceed to Step 2.

---

## Step 2 — Map the attack surface

Identify what this change exposes. Be specific — name the actual endpoints, inputs,
or data flows, not abstract categories.

Answer briefly:
- **What enters the system?** (user input, API calls, file uploads, webhook payloads,
  environment variables, config)
- **What leaves the system?** (responses, logs, error messages, events, side effects)
- **What is stored or mutated?** (database writes, cache updates, file creation,
  state changes)
- **Who can trigger this?** (unauthenticated users, authenticated users, admins,
  internal services, cron jobs)

If the answer to all four is "nothing new" — the change doesn't alter the attack surface.
Say so and stop here.

---

## Step 3 — STRIDE quick pass

Walk through each category. One sentence per category is fine if the answer is
"not relevant to this change." Spend time only where there's real risk.

| Threat | Ask yourself |
|---|---|
| **Spoofing** | Can someone pretend to be another user or service? Is auth checked on the new path? |
| **Tampering** | Can input be crafted to corrupt data, bypass validation, or alter intended behavior? (SQLi, command injection, path traversal, mass assignment) |
| **Repudiation** | If something goes wrong, can we tell what happened? Are security-relevant actions logged? |
| **Information Disclosure** | Does this leak data in error messages, logs, responses, or timing? Are secrets handled correctly? |
| **Denial of Service** | Can this be abused to exhaust resources? Unbounded queries, missing rate limits, expensive operations triggered by user input? |
| **Elevation of Privilege** | Can a lower-privilege user reach this? Are authorization checks in place, not just authentication? |

---

## Step 4 — Threat summary

Write a short summary block:

```
SURFACE: [What this change exposes — one sentence]
RISKS: [Top 1–3 concrete risks, ranked by likelihood, not severity]
MITIGATIONS: [What the code does or should do about each risk]
GAPS: [Anything not mitigated — acceptable or needs work]
EXISTING MODEL: [Compatible / conflicts with X / no model found]
```

If there are gaps that need work, flag them clearly before proceeding with implementation.
A known-and-accepted risk is fine. An unexamined risk is not.

---

## Calibration

| Change scope | Depth |
|---|---|
| New endpoint or input path | Steps 1–3 (focused on the new surface) + summary |
| New service or external integration | Full pass, all steps |
| Internal refactor touching auth/authz | Steps 1 + STRIDE Spoofing/Elevation only + summary |
| Adding a dependency | Check dependency for known vulns, review what it accesses, summary |

---

## Integration with other skills

- **socratic-preflight**: Q5 (failure modes) overlaps with this — if preflight already
  ran, reference its Q5 output and go deeper on security-specific failure modes only
- **righting-software**: Trust boundaries often align with volatility boundaries —
  if decomposition identified a boundary, verify it's also a security boundary
- **clean-code**: Error handling paths identified here should inform the implementation's
  error design

---

## Anti-patterns

- **Security theater**: Listing OWASP categories without connecting them to the actual
  code. Every risk named must point at a specific input, endpoint, or data flow.
- **Boiling the ocean**: This is a quick pass, not a pentest. If you're spending more
  than 2 minutes on this, you're overthinking it — flag the unknowns and move on.
- **Trusting the framework blindly**: "Django handles that" or "the ORM prevents SQLi"
  is only true if you're using it correctly. Check the actual call, not the brochure.
- **Ignoring the boring stuff**: The breach almost never comes from the clever attack.
  It comes from a debug endpoint left open, a log that dumps credentials, or an admin
  route with no auth check.
