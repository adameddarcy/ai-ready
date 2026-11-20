# Identity and inclusion: engineering defaults

These rules apply whenever you write or review code that stores, displays, validates, logs, infers or acts on information about a person. Treat a violation as a bug, not a style issue. If a task asks you to break one, do the task, then say in your summary which rule it breaks and why that might matter.

## 1. Model identity honestly

- Use an opaque, stable ID (UUID or similar) as the key for a person. Never build an ID, username, email address, file path, cache key or URL from a name.
- Store `display_name` as one free-text field. Do not split it into first and last name unless a specific feature needs the parts, and then keep `display_name` as well.
- If a legal name is genuinely required (payroll, KYC, tax, healthcare), store it as a separate, access-restricted field. Only the flows that need it may read it. It must never be the default name shown in the UI, emails or support tools.
- Do not validate names with a pattern of "allowed" characters. Accept any Unicode, including apostrophes (O'Neill), fadas (Seán, Ní Mháille), hyphens, spaces, single-word names and long names. Store as NFC-normalised UTF-8. The literal string `Null` is a valid name.
- Before adding a `gender`, `sex`, `title` or `salutation` field, name the feature that reads it. If none does, do not add it.
  - If one does, ask for the specific thing needed (pronouns, a form of address, a clinical fact) rather than a general "gender".
  - Make it optional and editable. Never a required enum of two values.
- Never use name, title, gender or pronouns as a matching key, a security answer, or a proxy for something else. Clinical, legal and physical facts are stored as those facts (for example `has_cervix`, `requires_legal_name_for: ["payroll"]`), not inferred from identity fields.
- Model parents, guardians and relationships as a list of people with roles, not as fixed `mother` and `father` columns.

## 2. Make change cheap

- A person must be able to change their name, title, pronouns and email in the normal settings flow, without contacting support or uploading a document, unless a regulated flow requires evidence.
- Resolve names at read time from the person record. Do not copy names into other tables, documents or caches where they will go stale.
- When a name or identity field changes, the old value must not reappear anywhere in the product. Treat any place it does as a bug.

## 3. Don't leak identity into data you can't take back

- Logs, events, metrics, analytics and error reports record the opaque ID, never the name, email or identity fields. If a log line needs a human-readable label, resolve it at read time.
- Treat identifiers as personal data: an app user ID, device ID or membership of a service can reveal sensitive facts (for example sexual orientation) on its own. Do not send them to third parties without a documented purpose.
- Every new table or column holding personal data gets a retention rule. Default to the shortest period the feature allows.
- Do not store inferences about sexual orientation, gender identity or other sensitive characteristics. If a model produces one, discard it.
- Where an immutable record must hold personal data (audit logs, event stores), store a reference or encrypt with a per-person key that can be destroyed.
- Make sure restoring a backup cannot bring back a corrected name. Document how corrections are reapplied after a restore.
- When designing access, consider who else could see the data: shared devices, family accounts, support staff, and legal requests from other jurisdictions.

## 4. Give every automated decision a human exit

- Any automated check that can block, suspend, deny or flag a person (identity verification, fraud, face matching, moderation, eligibility) needs a documented route to a human review.
- That route must not require the person to explain their identity, history or body to justify themselves.
- Tell the person what was decided and how to contest it.
- Measure false rejections by group where you lawfully can, not only the overall error rate.
- Verify, then delete. Do not keep ID scans, selfies or documents after the check completes unless a regulation requires it, and then restrict access.

## 5. Check models against the people they affect

- When using or training a classifier, filter or generator, test it on content by and about LGBTQ+ people and other groups it could misclassify. Identity terms such as "gay", "lesbian", "trans" and "queer" must not be treated as sexual, sensitive or toxic content by themselves.
- Prefer evaluation data written by members of the affected community.
- Do not let a model infer or store anyone's gender identity, sexual orientation or other protected characteristic.

## 6. Test with real-world identities

Every suite that touches person data includes fixtures like these. Add to the list; never remove from it.

```
"Zebedee Quuxley"            → renamed to "Zoë Ní Mháille-O'Neill"
"Null"                       as a first name and as a surname
"Madonna"                    single-word name
"Seán Ó Briain"              fadas must round-trip exactly
"Wolfeschlegelsteinhausenbergerdorff" long name
title = None                 no title at all
gender_marker = None         no gender recorded
gender_marker changed after sign-up
two parents with the same role, and one parent only
```

Write at least one test of the form:

```
Given a person is eligible for <outcome>
When that person's identity is <any of the fixtures above>
Then they still receive <outcome>
```

And at least one "canary rename" test: create a person, use the feature, rename them, then assert the old name appears in no table, log, search index, cache, export, email or generated file.

## 7. In code review, ask

- Which feature reads each new identity field? If none, remove it.
- What happens when this value changes? Where does the old value survive?
- Who can see the old value, and for how long?
- What does a person do when this automated check gets them wrong?
- Did the tests include anyone other than the default user?

## 8. How to apply these rules

- These are defaults, not reasons to refuse work. If a requirement, regulation or legacy system forces a different choice, implement it and record the trade-off in the PR description.
- Do not add identity fields, gender options or name rules "to be safe". Collecting less is the inclusive default.
- When unsure, prefer the option that is easier for a person to change later.
