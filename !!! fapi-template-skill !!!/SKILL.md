---
name: fapi-template-skill
description: >-
  Template for drafting FAPI MCP workflow skills. Use only when creating or
  reviewing a new FAPI skill template, not for live FAPI account operations.
  Replace all bracketed placeholders before using a copied skill in production.
---
--------------------------------------------------------------------

# [Skill title]

## Purpose

[One or two sentences describing the specific capability this skill adds.]

## Scope

Use this skill for:

* [Supported task]
* [Supported task]
* [Supported task]

Do not use this skill for:

* [Near-miss task handled by another skill]
* [Unsupported operation]

## Domain model

Define only concepts required for this workflow.

### [Concept or entity]

* [Meaning in FAPI]
* [Relevant states or properties]
* [Relationship to another entity]

### [State or lifecycle]

```text
[state] -> [state] -> [state]
              |
              -> [alternative state]
```

Important distinctions:

* `[term A]` means [definition].
* `[term B]` means [definition].
* Do not treat `[term A]` and `[term B]` as interchangeable.

## Procedure

### 1. Identify [entity or situation]

Determine:

* [Task-specific fact]
* [Task-specific fact]
* [Task-specific classification]

### 2. Retrieve [required domain data]

Use `[tool or reference]` to obtain:

* [Field or entity]
* [Field or entity]
* [Field or entity]

Read `references/[file].md` when [specific condition].

### 3. Evaluate [domain conditions]

Apply these rules in order:

1. If [condition], then [action or conclusion].
2. If [condition], then [action or conclusion].
3. If neither applies, [fallback procedure].

### 4. Perform [task-specific operation]

1. [Concrete operation]
2. [Concrete operation]
3. [Concrete validation]
4. [Task-specific follow-up]

### 5. Verify the result

Verify:

* [Expected state or returned value]
* [Required downstream effect]
* [Task-specific consistency condition]

Do not consider the task complete when only [insufficient signal] is available.

## Decision table

| Condition     | Interpretation | Action   |
| ------------- | -------------- | -------- |
| [Condition A] | [Meaning]      | [Action] |
| [Condition B] | [Meaning]      | [Action] |
| [Condition C] | [Meaning]      | [Action] |

## Domain-specific rules

* [Concrete FAPI rule]
* [Concrete dependency]
* [State transition restriction]
* [Permission or configuration requirement]
* [Non-obvious tool behavior]

## Known failure modes

### [Failure or symptom]

Likely causes, in diagnostic order:

1. [Most likely cause]
2. [Second cause]
3. [Less common cause]

Check:

* [Evidence or field]
* [Evidence or field]

Resolution:

1. [Corrective step]
2. [Verification step]

### [Another failure or symptom]

[Repeat only when this failure is common enough to justify permanent skill context.]

## Gotchas

* [UI terminology differs from API terminology in this way.]
* [A successful tool response does not prove this downstream effect.]
* [This state can look valid while this dependency is missing.]
* [This operation affects another FAPI entity unexpectedly.]
* [This value is inherited, cached, delayed, or computed.]

## Output

For this workflow, return:

```markdown
## [Task-specific result heading]

[Required result]

## [Task-specific evidence or configuration]

[Relevant details]

## [Task-specific next step]

[Only when needed]
```

Omit sections that are not relevant to the actual result.

## Examples

### Example: [Common request]

**Request**

> [Realistic user request]

**Procedure**

1. [Relevant procedure step]
2. [Relevant procedure step]
3. [Relevant procedure step]

**Expected result**

[What a correct answer or completed operation must establish.]

### Example: [Ambiguous or indirect request]

**Request**

> [Realistic indirect phrasing]

**Interpretation**

[How the request maps to this skill.]

**Procedure**

1. [Relevant procedure]
2. [Relevant procedure]

## Resources

Load resources only under the stated conditions:

* `references/[file].md` — Read when [condition].
* `references/[file].md` — Read when [condition].
* `scripts/[script]` — Run when [condition].
* `assets/[template]` — Use when [condition].
