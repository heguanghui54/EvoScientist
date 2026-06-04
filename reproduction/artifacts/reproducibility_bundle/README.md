# EvoScientist Reproducibility Bundle

Date: 2026-06-04
Status: `incomplete`
Paper-exact: `false`
Branch: `codex/reproduction-assets`

portable verification bundle for the current EvoScientist replacement/proxy reproduction state

## Component Summary

- full_trajectories: 30/30 complete
- table1: 420/420 replacement/proxy judge records
- table2: 120 inputs, 1440 LLM-surrogate labels, human label packet ready, formal human labels missing
- table3: 30-query replacement ablation rerun
- figure2: 240-record replacement code-execution probe

## Line Count Checks

- `artifacts/judge_inputs/results.jsonl`: 420
- `artifacts/judge_outputs/results.jsonl`: 420
- `artifacts/human_evaluation/inputs.jsonl`: 120
- `artifacts/human_evaluation/surrogate_labels.jsonl`: 1440
- `artifacts/human_evaluation/label_packet/label_sheet_template.csv`: 1441

## Blocking Items

- incomplete: table2_human_idea_generation

## Files

| Path | Bytes | SHA256 |
| --- | ---: | --- |
| `final_reproduction_dossier.md` | 2787 | `43e8e23ddff4b387c117f3a4159c0789255f575ee6c228aaf152755b040cc053` |
| `final_reproduction_dossier.json` | 24322 | `006c5a020e49984a94ba4f9ecfb24d0a0badb794573200285c6fa07fd6239fb5` |
| `artifacts/audit/paper_level_completion_latest.md` | 1115 | `64eec8a7ca83d1c9b24c09487aa7b4a5a391cc0eed43fbd66655467964b2b74c` |
| `artifacts/audit/paper_level_completion_latest.json` | 15611 | `c07db6a75b98aba9675d91f4733df5e1f10a6f7d42295b60914f27a7b9115105` |
| `artifacts/audit/paper_artifact_schema_latest.json` | 7748 | `7b6e492c04fad6a915772f59c9cfff1dfbf88761b91a44abda913f39d8fadad0` |
| `table1_replacement_all_baselines_monica_report.md` | 1679 | `0eecc6b4804e8cd7cd6497024a7332d481d22e3032c73fe2744312abc827916f` |
| `table1_replacement_all_baselines_monica_report.json` | 12079 | `0b5f48315091e24fb028e04fc437a8359eef61eecdfe99b2dfc5171152c80164` |
| `artifacts/judge_inputs/results.jsonl` | 4772022 | `facef9e49eb24dde1f426ec61a020bd70ccbce57d49f7e69fa40c1c9d2e90d8d` |
| `artifacts/judge_outputs/results.jsonl` | 806560 | `91b9343a063541df645d388b6da3ae49adcf645b5bffcdfa24d455658fa9f4be` |
| `artifacts/tables/idea_generation_win_tie_lose.csv` | 1586 | `d97005c3e2bf55c21f851daf3ac5573d7adc2abe82e594565daad6b6f02c475b` |
| `artifacts/tables/idea_generation_win_tie_lose.json` | 8897 | `cd983c9416b4f4e690c27b65d53ae750ddacaa1cde343a63c426ce35680de4bf` |
| `table2_surrogate_monica_report.md` | 1452 | `626152dc5575a11437b974a3e092da179e5e0ea1262000b85d6b3aabdcb7b19b` |
| `table2_surrogate_monica_report.json` | 6852 | `525864ca26137f5521715c57150b76d59707bd9e103f1bb70668d40807176b9c` |
| `artifacts/human_evaluation/inputs.jsonl` | 61568 | `ff3927bad2b424b4d5c01ce5cf07f75b265d4e99ce9192a3bbdf95668e0659ca` |
| `artifacts/human_evaluation/surrogate_labels.jsonl` | 683460 | `dffcd0793c15396e829b6562b3e1d1ab228059b680773d50064402d17172426c` |
| `artifacts/human_evaluation/surrogate_aggregate.csv` | 931 | `4bc3ad2c58493058d599a98e5b7a598a09ea60b2deac6999b47dbf67fcc7d42b` |
| `artifacts/human_evaluation/surrogate_aggregate.json` | 5257 | `9b548ad68d59a6f349cc96feccee350b44a92ba8b04da54f5b793e3e7ef11fea` |
| `artifacts/human_evaluation/label_packet/annotation_guide.md` | 1117 | `4d8f6b02131f4461eb5f680c34d90089e3f82e046d2590d7b76fee7fde269925` |
| `artifacts/human_evaluation/label_packet/manifest.json` | 867 | `cbae9c6c30d9606640547171d41dc0959aa3a0d93b93ad60108f14a6105eb5b1` |
| `artifacts/human_evaluation/label_packet/review_tasks.jsonl` | 1347238 | `98465e8b2817ec257e7812a6fbc367e8cb7b2f9670489f50bd514936b290bf9c` |
| `artifacts/human_evaluation/label_packet/task_index.csv` | 98481 | `5de4c9bb80b694a5b96d869292a7d87c26d2b92fe9d48042f30e3a98528cb16a` |
| `artifacts/human_evaluation/label_packet/label_sheet_template.csv` | 73505 | `6b9cc83f5115117f68ee5def9d9996975a48ac80468d1bb8805690b257adac54` |
| `ablation_queries01_30_monica_gemini_report.md` | 3174 | `23bbddaed59f9b0d4c95332b68a8565baefc9c896d58e16b390df58f92bf2883` |
| `ablation_queries01_30_monica_gemini_report.json` | 4305 | `edc9f11aa0d98cc52c037c289de0f5e873445d462a8a5700f4dc953e63aec083` |
| `artifacts/ablations/combined_aggregate.csv` | 1067 | `45af61ff1fe2b41858d9781f12e2364ec77f745bbefbf41394233e27d3874c51` |
| `artifacts/ablations/combined_aggregate.json` | 10220 | `93121f7be08ff5b6a00dfca9a8fdc62685bcb462a718745196750ab43269f7bf` |
| `figure2_code_execution_replacement_report.md` | 2183 | `041fc787df43211cbdb27a363ed456cf9ab4e49908efb13621a5825ff9c05e98` |
| `figure2_code_execution_replacement_report.json` | 2070 | `246355bc677f58cb1c29bb8a1e9c6bd3b8e2389f9b3069eaffa31c2a8f67022e` |
| `artifacts/code_execution/summary.csv` | 404 | `d0d145489a9bb51291f85f9449c70eba0d317f86472f475d39a3d085b1ec52be` |
| `artifacts/code_execution/summary.json` | 1889 | `ef72cd6d6977f6efd8988ec0a317d44b2a80a06d93b9e2c08d8abacf7ebd9c83` |
| `artifacts/paper_previews/evoscientist_query01_final_report.pdf` | 402343 | `56fe67b159fb887aaf67f1865f9e9bd23e1bf84b000a7a3973cc7398cfb12d9c` |
| `artifacts/paper_previews/ai_scientist_v2_query01_idea.pdf` | 124434 | `44f5e22e1caef2e83325384aa86016b11cf067b78d6e629e3b82af26ea1bc052` |
| `artifacts/paper_previews/rendered/evoscientist_query01_final_report_page1.png` | 198293 | `310ceb850396c2b68842429491f2a679f1bbf07a32106395fe80c174278d34e3` |
| `artifacts/paper_previews/rendered/ai_scientist_v2_query01_idea_page1.png` | 252591 | `9bb14ae9b0623219c24cec27e07330d6caafaf38e7906685406ca8a39cf80ae0` |
| `paper_reproduction_action_plan.md` | 2271 | `020f1929b1cd9b81e60d993847e9f8175f3d9a0edab66a40e8cecdfb152715b9` |
| `paper_reproduction_action_plan.json` | 2446 | `fb9e3484b2504eb45e029de1f362b2097c2b4dab46e13c4cb9f5f33cc095edaa` |

## Verification

```bash
.venv/bin/python reproduction/verify_reproduction_assets.py
bash reproduction/run_preflight.sh
.venv/bin/python reproduction/audit_paper_level_completion.py --strict
```
