# AI-Researcher Runtime Gate

Date: 2026-06-04
Status: `not_ready`
Checkout: `/Users/hgh54913/research/AI-Researcher`
Benchmark templates: 30

AI-Researcher is benchmark-instance based and is not a drop-in runner for the recovered EvoScientist natural-language queries. This gate verifies whether a replacement rerun can start from generated per-query benchmark-instance templates.

## Blocking Items

- missing pinned AI-Researcher checkout
- Docker CLI is not installed or unavailable
- OPENROUTER_API_KEY is not configured
- GITHUB_AI_TOKEN is not configured

## Environment Keys

| Key | Present |
| --- | --- |
| CATEGORY | False |
| INSTANCE_ID | False |
| TASK_LEVEL | False |
| CONTAINER_NAME | False |
| WORKPLACE_NAME | False |
| CACHE_PATH | False |
| PORT | False |
| MAX_ITER_TIMES | False |
| OPENROUTER_API_KEY | False |
| GITHUB_AI_TOKEN | False |

## Commands

| Command | Available | Version/Path |
| --- | --- | --- |
| python | True | `Python 3.9.6` |
| docker | False | `` |
| git | True | `git version 2.50.1 (Apple Git-155)` |
