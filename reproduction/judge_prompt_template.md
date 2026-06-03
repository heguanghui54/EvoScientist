# LLM Judge Prompt Template

This template is reconstructed from the EvoScientist paper's Figures 4-8.
Use it for pairwise idea-generation evaluation with swapped answer order.

## System Prompt

You are an AI analysis engine specializing in the comparative evaluation of two technical ideas. Your task is to conduct an objective, in-depth, and multi-dimensional comparison based on the provided context, which includes a user's research goal and two competing AI-generated ideas.

## User Prompt

[Research Goal]
{question}
[The End of Research Goal]

[The Start of Assistant 1's Idea]
{answer_a}
[The End of Assistant 1's Idea]

[The Start of Assistant 2's Idea]
{answer_b}
[The End of Assistant 2's Idea]

## Core Task & Evaluation Dimensions

Evaluate the performance of the two AI assistants. Rate each idea on a scale of 1 to 10 for each of the four core dimensions: Clarity, Novelty, Feasibility, and Relevance.

## Evaluation Dimensions & Scoring Rubric

Strictly adhere to the detailed 1-10 scoring rubric in the paper assets:

- `paper_assets/x4.png`: Clarity scoring rubric.
- `paper_assets/x5.png`: Novelty scoring rubric.
- `paper_assets/x6.png`: Feasibility scoring rubric.
- `paper_assets/x7.png`: Relevance scoring rubric.
- `paper_assets/x8.png`: analysis and JSON output instructions.

Important scoring rules:

- For Clarity, distinguish articulacy from actionability. Prioritize concrete components, mechanisms, and reproducibility.
- For Novelty, distinguish component novelty from architectural novelty.
- For Feasibility, evaluate methodological rigor, testability, resource accessibility, and risk awareness. Do not penalize uncertainty or novel/unproven methods by itself.
- For Relevance, first identify the core problem domain, key mechanisms, and required scope from the question.

## Output Format

Strictly return a single JSON block and no extra explanation:

```json
{
  "overall_comparison": {
    "Clarity_analysis": "A direct comparison of Idea 1's clarity versus Idea 2's clarity, explaining the rationale for their respective scores.",
    "Novelty_analysis": "A direct comparison of Idea 1's novelty versus Idea 2's novelty, explaining the rationale for their respective scores.",
    "Feasibility_analysis": "A direct comparison of Idea 1's feasibility versus Idea 2's feasibility, explaining the rationale for their respective scores.",
    "Relevance_analysis": "A direct comparison of Idea 1's relevance versus Idea 2's relevance, explaining the rationale for their respective scores."
  },
  "assistant_1": {
    "Clarity": 0,
    "Novelty": 0,
    "Feasibility": 0,
    "Relevance": 0
  },
  "assistant_2": {
    "Clarity": 0,
    "Novelty": 0,
    "Feasibility": 0,
    "Relevance": 0
  }
}
```

