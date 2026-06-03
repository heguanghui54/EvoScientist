# Public Artifact Gap Report

Date: 2026-06-03

This report checks whether public EvoScientist sources provide the raw artifacts
needed for exact paper-level reproduction of arXiv:2603.08127.

## Checked Sources

1. Official repository:
   `https://github.com/EvoScientist/EvoScientist`

   A fresh shallow clone of upstream `main` was checked at commit
   `0198e50e7f5d3148dc9c5a499fef6f2afd8d3888`. The latest tree contains source
   code, docs, tests, and examples. It does not contain an `experiments/`
   directory, a `reproduction/` directory, or raw paper baseline/judge/human-label
   artifacts.

2. Official repository README:
   `https://github.com/EvoScientist/EvoScientist`

   The README links the technical report and lists a benchmark suite as future
   roadmap work. It does not publish the paper's Table 1, Table 2, Table 3, or
   Figure 2 raw artifacts.

3. Paper:
   `https://arxiv.org/abs/2603.08127`

   The paper reports the 30-query idea-generation evaluation, seven baselines,
   Gemini-3-flash judge, human evaluation, code execution success, and ablations.
   The paper text and figures expose enough information to reconstruct the query
   list, judge prompt images, protocol notes, and reported aggregate numbers, but
   not the raw system outputs, judge JSON, human labels, or execution logs.

4. Web search:

   Queries checked on 2026-06-03:

   - `EvoScientist EvoScientist baseline outputs judge outputs github`
   - `EvoScientist arXiv 2603.08127 baseline outputs`
   - `EvoScientist AI-Researcher InternAgent Hypogenic Novix K-Dense outputs`

   Search results surfaced the paper, the official repository, summary pages,
   release notes, and baseline project pages, but no public artifact package with
   the missing raw experiment outputs.

## Missing For Exact Reproduction

Exact Table 1 automatic idea-generation reproduction still requires:

- baseline outputs for `Virtual Scientist`, `AI-Researcher`, `InternAgent`,
  `AI Scientist-v2`, `Hypogenic`, `Novix`, and `K-Dense`;
- 420 pairwise judge input records: 30 queries x 7 baselines x 2 swapped orders;
- Gemini-3-flash judge outputs for those 420 records;
- paper-matched full EvoScientist trajectories, not only proposal-only outputs.

Exact Table 2 human evaluation reproduction still requires:

- anonymized pairwise human-evaluation inputs;
- labels from the three PhD-level annotators;
- agreement or adjudication traces if any were used.

Exact Table 3 and Figure 2 reproduction still requires:

- ablation outputs for IDE/IVE/all-removed variants;
- generated code trajectories and execution success/failure logs;
- experiment-memory before/after evolution state or equivalent trace evidence.

## Current Reproducible Substitute

The current harness does reproduce a stated replacement comparison:

- EvoScientist proposal-only outputs cover 30/30 recovered paper queries.
- `Direct-DeepSeek` direct-LLM baseline outputs cover 30/30 queries.
- DeepSeek judge covers 60/60 swapped pairwise records.
- The replacement-baseline audit is complete.

This substitute is useful for validating the evaluation pipeline and for a
limited comparison, but it is not the paper's exact seven-baseline,
Gemini-judge, human-evaluation, full-agent reproduction.

## Conclusion

As of 2026-06-03, exact paper-level numeric reproduction is not possible from
public artifacts alone. The public materials support software reproduction,
query/protocol reconstruction, and replacement-baseline evaluation, while the
paper's raw baseline outputs, judge outputs, human labels, code-execution logs,
and ablation traces remain unavailable.
