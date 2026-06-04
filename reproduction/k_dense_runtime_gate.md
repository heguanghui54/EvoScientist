# K-Dense Runtime Gate

Date: 2026-06-04
Status: `not_ready`
Checkout: `/Users/hgh54913/research/k-dense-byok`
Backend URL: `http://localhost:8000`

K-Dense BYOK is a local web/API adapter candidate, not a paper-exact raw Table 1 artifact. This gate verifies whether a replacement rerun can start from the pinned public checkout.

## Blocking Items

- python3.13 is not installed
- uv is not installed
- Gemini CLI is not installed
- neither OPENROUTER_API_KEY nor a reachable Ollama server is available
- K-Dense backend is not running at the requested backend URL

## Commands

| Command | Available | Version/Path |
| --- | --- | --- |
| python3.13 | False | `` |
| uv | False | `` |
| node | True | `v26.0.0` |
| npm | True | `11.12.1` |
| gemini | False | `` |
| ollama | False | `` |

## Environment Keys

| Key | Present |
| --- | --- |
| OPENROUTER_API_KEY | False |
| GEMINI_API_KEY | False |
| GOOGLE_GEMINI_BASE_URL | False |
| OLLAMA_BASE_URL | False |
| EXA_API_KEY | False |
| PARALLEL_API_KEY | False |
| PAPERCLIP_API_KEY | False |
