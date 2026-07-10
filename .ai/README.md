# Khazina AI Operating System

This directory contains **AI operating instructions** for assistants working on the Khazina project (Cursor, Claude, ChatGPT, Gemini, etc.).

## What Lives Here

| Path | Purpose |
|------|---------|
| [AI_PROJECT_PROFILE.md](AI_PROJECT_PROFILE.md) | One-page project orientation — **always read first** |
| [PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md) | Pre-task mental checklist |
| [skills/](skills/) | Behavioral rules for AI assistants |
| [prompts/](prompts/) | Reusable prompt templates by task type |

## What Lives Elsewhere

Project documentation remains under [`docs/`](../docs/). That is the **single source of truth** for project knowledge.

## How It Works

1. **Read** [AI_PROJECT_PROFILE.md](AI_PROJECT_PROFILE.md) first.
2. **Classify** the task type (frontend, backend, documentation, etc.).
3. **Load** only the required skills from [skills/](skills/).
4. **Read** only the required documentation from [docs/](../docs/) — not every file on every task.
5. **Follow** [PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md) before and after implementation.

Skills define **AI behavior**. Documentation defines **project knowledge**. Do not duplicate documentation inside skills or prompts.
