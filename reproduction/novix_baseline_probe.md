# Novix Baseline Probe

Date: 2026-06-04
Hosted chat: https://novix.science/chat
Linked open-source system: https://github.com/HKUDS/AI-Researcher

Drop-in status: `hosted_ui_adapter_candidate`
Paper-exact status: `not_paper_exact`

## Finding

Novix is a hosted AI co-scientist product and public materials link its open-source lineage to HKUDS/AI-Researcher. The visible frontend bundle contains login, chat session, and task endpoints, but no public batch API documentation or raw EvoScientist Table 1 outputs were found. Novix can only be a replacement rerun candidate through a pinned account/browser/API-capture protocol; it is not a paper-exact public artifact.

## Signals

- hosted_chat_available: True
- product_features_available: True
- same_as_ai_researcher: True
- ai_researcher_readme_links_novix: False
- independent_public_novix_repo_found: False
- login_required_signals: True
- visible_task_api_in_frontend_bundle: True
- public_batch_api_docs_found: False
- raw_table1_outputs_found: False

## Visible Product Endpoints

- `/user/login`
- `/chat_session/create`
- `/task/create_task`
- `/task/submit_user_question`
- `/call_agent`
- `/agents`

## Required Access

- Novix account/session if running the hosted product
- Pinned UI/API capture protocol if using browser or frontend endpoints
- Alternative: use the open AI-Researcher probe/runbook rather than treating Novix as a separate open-source runner

## Next Actions

- If Novix access is available, define a pinned hosted-run protocol with account state, model defaults, and one fresh session per recovered query.
- Capture final assistant answers for all 30 queries into reproduction/artifacts/idea_outputs/Novix/query_XX/answer.txt.
- If hosted access is not available, use AI-Researcher public-runner evidence instead and report Novix as non-reproducible from public artifacts alone.
- Judge any imported Novix outputs through the existing swapped pairwise judge pipeline.
