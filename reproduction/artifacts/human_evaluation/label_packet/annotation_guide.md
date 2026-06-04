# Table 2 Human Label Packet

Date: 2026-06-04
Paper-exact target: `true`

This packet is for real human annotation. It should not be filled with
LLM-surrogate labels if the goal is paper-level Table 2 completion.

## Files

- Review tasks with full answer text: `artifacts/human_evaluation/label_packet/review_tasks.jsonl`
- Task index CSV: `artifacts/human_evaluation/label_packet/task_index.csv`
- Fillable label sheet: `artifacts/human_evaluation/label_packet/label_sheet_template.csv`

## Winner Values

- `assistant_1`: EvoScientist is better for the dimension.
- `assistant_2`: the baseline answer is better for the dimension.
- `tie`: no clear winner.

## Import

After replacing every blank `winner` cell in the label sheet, run:

```bash
.venv/bin/python reproduction/import_table2_human_label_sheet.py --sheet reproduction/artifacts/human_evaluation/label_packet/label_sheet_template.csv --output-labels reproduction/artifacts/human_evaluation/labels.jsonl --output-csv reproduction/artifacts/human_evaluation/aggregate.csv --output-json reproduction/artifacts/human_evaluation/aggregate.json --strict
```
