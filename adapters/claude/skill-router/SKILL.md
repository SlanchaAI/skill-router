---
name: skill-router
description: Use when starting a nontrivial task that may benefit from specialized instructions in the shared Agent Skills library.
---

# Skill Router

Before executing a nontrivial task, call `route_and_load` once with the full task, harness `claude`,
current working directory, and available tools and MCPs.

- Match: follow `skill_body` while completing the task.
- No match: continue without a skill.
- Never request or inject the library catalog.
- Do not route greetings, acknowledgements, or other trivial conversation.
