# Virtual Scientist Runtime Gate

Date: 2026-06-04
Status: `not_ready`
Checkout: `/Users/hgh54913/research/Virtual-Scientists`
Simulation specs: 30
Data root: `/Users/hgh54913/research/Virtual-Scientists/data`
Ollama URL: `http://localhost:11434`

Virtual Scientist is a VirSci team-simulation platform, not a drop-in runner for the recovered EvoScientist natural-language queries. This gate verifies whether a replacement rerun can start from generated per-query simulation specs.

## Blocking Items

- missing pinned Virtual-Scientists checkout
- sci_platform/run.py is not present
- sci_platform/sci_platform.py is not present
- AMiner-derived Virtual Scientist data package is not installed at the requested data root
- Python faiss module is not importable
- Ollama CLI is not installed
- required Ollama models are missing: llama3.1, llama3.1:70b, mxbai-embed-large

## Commands

| Command | Available | Version/Path |
| --- | --- | --- |
| python3 | True | `Python 3.9.6` |
| git | True | `git version 2.50.1 (Apple Git-155)` |
| ollama | False | `` |

## Data And Models

- FAISS importable: False
- Data name hits: none
- Required Ollama models: llama3.1, llama3.1:70b, mxbai-embed-large
- Installed Ollama models: none detected
