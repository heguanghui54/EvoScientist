# Hypogenic Hosted Capture Gate

Date: 2026-06-04
Status: `not_ready`
Hosted URL: https://hypogenic.ai/chat
Prompt templates: 30
Capture manifests: 30
Captured answers: 0

This gate only verifies readiness for a hosted replacement capture. It does not prove paper-exact reproduction without author-provided Table 1 raw outputs and original judge records.

## Blocking Items

- HYPOGENIC_CAPTURE_READY=1 is not set for a pinned account/browser capture
- HYPOGENIC_SESSION_NOTE is not set with account/session metadata
- 30 captured answer files are not present in the expected output directory

## Access State

- HYPOGENIC_CAPTURE_READY: False
- HYPOGENIC_SESSION_NOTE: False
- Output directory: `/Users/hgh54913/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic`
- Hosted probe available: True
- Hosted probe status: 307
