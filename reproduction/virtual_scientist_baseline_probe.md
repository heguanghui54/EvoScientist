# Virtual Scientist Baseline Probe

Date: 2026-06-04
Repository: https://github.com/open-sciencelab/Virtual-Scientists
Website: https://renqichen.github.io/Virtual-Scientists/
arXiv: https://arxiv.org/abs/2410.09403

Drop-in status: `open_source_platform_not_drop_in`
Paper-exact status: `not_paper_exact`

## Finding

Virtual Scientist maps to the public VirSci/Virtual-Scientists repository. It is a runnable open-source scientific-collaboration platform, but it is not a drop-in runner for EvoScientist's 30 recovered natural-language Table 1 queries: the public entrypoint is a team-simulation run script that depends on AMiner-derived paper/author/embedding data, FAISS, Ollama models, and patched local paths. The repository does not provide the paper's raw Virtual Scientist Table 1 outputs.

## Signals

- repo_available: True
- arxiv_2410_09403_linked: True
- run_py_available: True
- data_required: True
- ollama_models_required: True
- faiss_required: True
- hardcoded_data_paths_present: True
- query_cli_available: False
- dialogue_json_output_available: True
- raw_table1_outputs_found: False

## GitHub Tree Note

HTTPError: HTTP Error 403: rate limit exceeded


## Entrypoints

- setup: `pip install -r requirements.txt; cd agentscope-main && pip install -e .`
- data: `Download AMiner-derived Papers, Embeddings, Authors, and adjacency.txt from the repository's Google Drive link and patch sci_platform/sci_platform.py paths.`
- models: `ollama serve; ollama pull llama3.1; ollama pull llama3.1:70b; ollama pull mxbai-embed-large`
- run: `cd sci_platform && python run.py --runs ... --team_limit ... --max_discuss_iteration ... --max_team_member ... --epochs ...`

## Required Environment

- AMiner-derived paper/author/embedding data package
- FAISS index files and preferably GPU FAISS
- Ollama llama3.1 8B/70B and mxbai-embed-large
- Adapter design if mapping the 30 recovered EvoScientist natural-language queries into VirSci's team/ecosystem simulation

## Next Actions

- For a replacement rerun, first decide a principled adapter from each recovered query to a VirSci simulation seed/topic.
- Install the AMiner-derived data package and patch all local paths in sci_platform/sci_platform.py.
- Run VirSci under a pinned team/epoch/model protocol and extract generated idea/abstract fields from dialogue JSON outputs.
- Import extracted answers with import_baseline_outputs.py under system name Virtual Scientist.
- Do not treat this as paper-exact unless the original 30-query raw outputs are obtained from the EvoScientist authors.
