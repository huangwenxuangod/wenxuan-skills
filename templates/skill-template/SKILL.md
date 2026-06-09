---
name: your-skill-name
description: Describe the task this skill solves, when it should trigger, and what specialized workflow or judgment it provides.
---

# Overview

Use this skill when the request matches the description above and a repeatable workflow is more reliable than ad hoc reasoning.

## Trigger

- The user is asking for:
- The workspace shows:
- The likely repeated problem is:

## Workflow

1. Gather the smallest set of files, logs, or diffs needed to understand the issue.
2. Identify the failure mode, constraint, or repeated pattern.
3. Apply the standard fix or decision framework for this problem type.
4. Validate with the narrowest useful verification step.
5. Report only the result, key risk, and any remaining unknowns.

## Use bundled resources

- Read `references/` only when domain details are needed.
- Use `scripts/` when the same fix, analysis, or generation step is repeated.

## Do not use this skill when

- The request is unrelated to this problem type.
- The problem is novel enough that a fixed workflow would be misleading.
