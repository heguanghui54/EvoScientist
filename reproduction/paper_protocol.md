# Paper-Level Reproduction Protocol

This file turns the public experimental details from the EvoScientist paper
into an actionable reproduction checklist. It should be read together with
`queries.json`, `paper_assets/`, and `README.md`.

## Paper Sources Captured

- Paper: `https://arxiv.org/abs/2603.08127`
- HTML: `https://arxiv.org/html/2603.08127`
- Public code: `https://github.com/heguanghui54/EvoScientist`
- Local fork checkout: `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist`

Downloaded image assets from the arXiv HTML version:

- `paper_assets/x3.png`: 30 research queries.
- `paper_assets/x4.png` to `paper_assets/x8.png`: LLM judge prompt parts.
- `paper_assets/x9.png`: human evaluation instructions.
- `paper_assets/x10.png`: idea direction evolution prompt.
- `paper_assets/x11.png`: idea validation evolution prompt.
- `paper_assets/x12.png`: experiment strategy evolution prompt.

## Publicly Recoverable Experimental Setup

The paper defines four research questions:

- RQ1: idea quality in novelty, feasibility, relevance, and clarity.
- RQ2: code-generation reliability via execution success rate.
- RQ3: end-to-end scientific discovery, from idea generation to papers.
- RQ4: contribution of the multi-agent evolution mechanism.

Dataset/task levels:

- Idea generation: 30 research queries in `queries.json`.
- Code generation: each generated proposal becomes the input for experiment implementation and execution.
- End-to-end discovery: 6 selected research ideas are developed into full manuscripts and submitted to ICAIS 2025 AI Scientist Track.

Baselines:

- Open-source: Virtual Scientist, AI-Researcher, InternAgent, AI Scientist-v2.
- Commercial: Hypogenic, Novix, K-Dense.

Implementation settings reported by the paper:

- Literature review retrieval: Semantic Scholar API.
- Idea generation model: Gemini-2.5-Pro.
- Code generation model: Claude-4.5-Haiku.
- End-to-end manuscript authoring model: Gemini-2.5-Pro.
- Memory indexing/retrieval embedding model: `mxbai-embed-large` via Ollama.
- Ideation retrieval top-k: `k_I = 2`.
- Maximum idea-tree candidates: `N_I = 21`.
- Idea tree search parallel workers: 3.
- Experimentation retrieval top-k: `k_E = 1`.
- Experiment execution parallel workers: 4.
- Stage attempt budgets: `N_E1 = 20`, `N_E2 = 12`, `N_E3 = 12`, `N_E4 = 18`.

## LLM Evaluation Protocol

The paper evaluates idea generation with pairwise comparisons. Each idea pair is
judged twice with swapped answer order to reduce positional bias. The judge is
reported as `gemini-3-flash`. It scores:

- Clarity
- Novelty
- Feasibility
- Relevance

The prompt text was recovered from the PDF extraction and corresponding images
are saved in `paper_assets/x4.png` to `paper_assets/x8.png`.

Important judge logic:

- Clarity must prioritize actionability and reproducibility over academic eloquence.
- Novelty should distinguish component novelty from architectural novelty.
- Feasibility should evaluate research-design rigor, not whether the method is conservative.
- Relevance should identify the core problem domain, key mechanisms, and required scope before comparing ideas.
- Output must be a JSON block with per-dimension analyses and numeric scores for `assistant_1` and `assistant_2`.

Human evaluation instructions are saved visually in `paper_assets/x9.png`. The
paper reports 3 PhD-level annotators, internet access for claim checking, and
win/tie/lose decisions over the same four dimensions.

## Evolution Prompts

The paper exposes three memory/evolution prompts:

- `IDE(.)`: idea direction evolution, captured in `paper_assets/x10.png`.
- `IVE(.)`: idea validation evolution, captured in `paper_assets/x11.png`.
- `ESE(.)`: experiment strategy evolution, captured in `paper_assets/x12.png`.

The extracted text indicates:

- IDE distills reusable promising research directions from top-ranked ideas.
- IVE records failed directions and reusable failure signals from execution reports.
- ESE summarizes winning data-processing and model-training strategies from trajectories and final code.

## Full Reproduction Requirements Still Missing

These items are required to reproduce the paper's tables rather than only the
publicly recoverable protocol:

- API/model access matching the paper: Gemini-2.5-Pro, Claude-4.5-Haiku, Gemini-3-flash, Semantic Scholar, Ollama `mxbai-embed-large`.
- EvoScientist outputs for all 30 queries using the reported search budgets.
- Outputs from seven baseline systems under comparable settings.
- Code-generation trajectories and execution logs for each proposal.
- Human evaluation labels for the reported PhD-annotator results.
- The exact six selected research ideas/manuscripts and submission artifacts for ICAIS 2025.

## Practical Reproduction Stages

1. Run `bash reproduction/run_preflight.sh`.
2. Validate the offline evaluation pipeline shape:

   ```bash
   .venv/bin/python reproduction/run_offline_smoke.py --limit 3
   ```

   The output is synthetic and validates plumbing only, not paper scores.

3. Configure provider credentials and Ollama embedding model.
4. Run `bash reproduction/run_preflight.sh --with-agent`.
5. Generate one proposal per query in `queries.json`:

   ```bash
   .venv/bin/python reproduction/run_idea_generation.py --limit 1
   .venv/bin/python reproduction/run_idea_generation.py
   ```

   To verify the planned prompts without spending API budget:

   ```bash
   .venv/bin/python reproduction/run_idea_generation.py --dry-run
   ```

6. Run the same generation budget for baseline systems, or import their outputs.
7. Evaluate all pairwise comparisons with the LLM judge prompt and swapped answer order.

   ```bash
   .venv/bin/python reproduction/run_llm_judge.py \
     --provider google \
     --model gemini-3-flash \
     --input reproduction/artifacts/judge_inputs/results.jsonl \
     --output reproduction/artifacts/judge_outputs/results.jsonl \
     --resume
   ```

8. Aggregate win/tie/lose rates per dimension:

   ```bash
   .venv/bin/python reproduction/aggregate_judge_results.py \
     --input reproduction/artifacts/judge_outputs/results.jsonl \
     --output-csv reproduction/artifacts/tables/idea_generation_win_tie_lose.csv \
     --output-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json
   ```

9. Compare reproduced aggregate values against the paper-reported target table:

   ```bash
   .venv/bin/python reproduction/compare_reproduction_to_paper.py \
     --actual-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json \
     --section table1_llm_idea_generation \
     --require-all
   ```

10. Audit artifact coverage before treating a run as paper-level reproduction:

   ```bash
   .venv/bin/python reproduction/audit_reproduction_artifacts.py --strict
   ```

   For Table 1, the full paper setup requires 30 queries, 7 baselines, and
   swapped-order judging, i.e. 420 pairwise judge records.

11. For code generation, feed each generated proposal into the engineer flow and record execution success.
12. For ablations, rerun with `-IDE`, `-IVE`, and `-all` variants if the code exposes toggles or patch equivalent prompt/memory removal.
