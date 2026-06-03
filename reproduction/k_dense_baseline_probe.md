# K-Dense Baseline Probe

Date: 2026-06-04
Organization: https://github.com/K-Dense-AI
Hosted platform: https://k-dense.ai/
BYOK repository: https://github.com/K-Dense-AI/k-dense-byok
Checked BYOK HEAD: `593c49b8e79c704c5979ec81c49f1791b5114083`

Drop-in status: `local_web_api_adapter_candidate`
Paper-exact status: `not_paper_exact`

## Finding

K-Dense has a hosted platform and a public BYOK local app. The BYOK app exposes an ADK `/run_sse` chat endpoint that can be adapted to submit each recovered EvoScientist query, but it is not a paper-exact artifact and the repository does not provide the paper's raw K-Dense Table 1 outputs. A reproducible rerun needs a pinned local project, model selection, keys, and an HTTP/SSE output-capture adapter.

## Signals

- hosted_platform_available: True
- byok_repo_available: True
- local_web_app_available: True
- adk_run_sse_endpoint_available: True
- project_scoped_api: True
- requires_python_3_13: True
- openrouter_key_required: True
- expert_path_uses_gemini_cli: True
- no_documented_batch_cli: True
- raw_table1_outputs_found: False

## Entrypoints

- hosted: `https://app.k-dense.ai`
- local_app: `git clone https://github.com/K-Dense-AI/k-dense-byok && cd k-dense-byok && ./start.sh`
- local_http_adapter: `POST /apps/kady_agent/users/user/sessions, then POST /run_sse with appName=kady_agent, userId=user, sessionId, and newMessage.parts[0].text`

## Required Environment

- `OPENROUTER_API_KEY`
- `optional Exa or Parallel search key`
- `optional Paperclip key`
- `Gemini CLI path configured by the K-Dense BYOK startup flow`

## Next Actions

- Start k-dense-byok with a pinned commit, Python 3.13, and OpenRouter/Gemini CLI configuration.
- Create one fresh session per recovered EvoScientist query through the ADK session endpoint.
- Submit each query through `/run_sse` and capture the final assistant text plus turn manifest.
- Import captured answers with import_baseline_outputs.py under system name K-Dense.
- Judge imported outputs through the existing swapped pairwise judge pipeline.
