# Hypogenic Baseline Probe

Date: 2026-06-04
Hosted home: https://hypogenic.ai/
Hosted chat: https://hypogenic.ai/chat
Arena: https://hypogenic.ai/arena

Drop-in status: `hosted_competition_adapter_candidate`
Paper-exact status: `not_paper_exact`

## Finding

Hypogenic has a public hosted science platform with Assistant, IdeaHub, Arena, and public competition-generated repositories. The checked public materials do not provide a standalone batch runner or the raw 30-query EvoScientist Table 1 outputs. It can only be treated as a hosted replacement rerun candidate with account/session capture, not as paper-exact public evidence.

## Signals

- hosted_platform_available: True
- assistant_link_available: True
- ideahub_available: True
- arena_available: True
- sign_in_required_signal: True
- chat_requires_access_or_redirects: True
- generated_repos_available: True
- public_runner_repo_found: False
- raw_table1_outputs_found: False

## Generated Repo Examples

- `https://github.com/Hypogenic-AI/incontext-if-then-2dae-claude`
- `https://github.com/Hypogenic-AI/incontext-if-then-31c6-codex`
- `https://github.com/Hypogenic-AI/inctx-if-then-capacity-6ce0-gemini`
- `https://github.com/Hypogenic-AI/live-salmon-ai-test-19cc-claude`
- `https://github.com/Hypogenic-AI/live-salmon-ai-test-4361-gemini`
- `https://github.com/Hypogenic-AI/live-salmon-ai-test-7d56-codex`
- `https://github.com/Hypogenic-AI/lying-style-nlp-0448-claude`
- `https://github.com/Hypogenic-AI/lying-style-nlp-92c9-codex`
- `https://github.com/Hypogenic-AI/lying-style-nlp-9950-gemini`

## Required Access

- Hypogenic account/session if running the hosted Assistant
- Pinned UI/browser capture protocol for one fresh session per recovered query
- Separate interpretation if using generated competition repositories, because they are public examples rather than the paper's Table 1 baseline outputs

## Next Actions

- If Hypogenic access is available, define a pinned hosted-run protocol with account state and one fresh Assistant session per recovered query.
- Capture final answers for all 30 queries into reproduction/artifacts/idea_outputs/Hypogenic/query_XX/answer.txt.
- If access is not available, keep Hypogenic as non-reproducible from public artifacts alone and report only generated competition repositories as related examples.
- Judge any imported Hypogenic outputs through the existing swapped pairwise judge pipeline.
