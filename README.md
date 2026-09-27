# Replication Package: Task Performance and Unaided Programming Performance Divergence among Programming Novices under Generative AI Conditions

[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)

This repository contains the de-identified dataset and the complete analysis pipeline required to reproduce every statistic reported in the manuscript.

| | |
|---|---|
| **Author** | Haiping Zeng (曾海平), Guangxi Science and Technology Normal University |
| **Contact** | cenghaiping@gxstnu.edu.cn |
| **Sample** | N = 113 introductory C-programming (CS1) novices, three cohorts |
| **Status** | Manuscript under review — *Education and Information Technologies* |
| **Reproduces** | Tables 3–6 and all in-text statistics |

---

## Quick start

```bash
pip install -r requirements.txt
python 01_prepare_data.py     # -> data/analysis_dataset.csv
python 02_analysis.py         # full run: 100 x 5-fold CV  (~2 min)
```

---

## 1. What this package provides

| Item | Purpose |
|---|---|
| `data/analysis_dataset.csv` | De-identified analysis dataset (N = 113). Class labels are recoded as `Class A/B/C`. |
| `data/raw_analysis_data.xlsx` | Supplementary workbook: intermediate result tables, the `Class_Codes` mapping worksheet, and the de-identified micro-data sheet (`Microdata_Deidentified`). |
| `01_prepare_data.py` | Field selection and de-identification. No statistical transformation. |
| `02_analysis.py` | Full statistical pipeline reproducing Tables 3–6 and all in-text statistics. |
| `outputs/` | Generated CSV outputs of every reproduced table. |
| `REPLICATION_NOTES.md` | Point-by-point comparison between reproduced values and the published values. |
| `CITATION.cff` | Machine-readable citation metadata (GitHub "Cite this repository"). |
| `LICENSE` / `LICENSE-DATA` | MIT (code) and CC BY 4.0 (data). |

> **Language.** Every released file in this repository — data fields, worksheet names,
> variable names, code comments, and documentation — is in **English**. A separate
> Chinese-language copy of the workbook and scripts is retained by the author for
> internal reference and is **not** distributed with this package.

### De-identification applied to the released data

The following transformations were applied before public release, and are auditable with
the verification block at the end of `01_prepare_data.py`:

| Original | Released as |
|---|---|
| Teaching-class identifiers `231` / `232` / `233` | `Class A` / `Class B` / `Class C` |
| Institution and course name in the overview sheet | removed; the sheet is not included |
| Internal interpretive-boundary notes | removed; not needed for replication |
| Student identifiers | replaced by sequential anonymous codes `S001`–`S113` |

Verified absent from every released file: standalone class numbers, institution name,
author name, and any name/student-ID fields.

### Tracing Table 6 back to the data

`raw_analysis_data.xlsx` contains a **`Class_Codes`** worksheet documenting which row group
each neutral code refers to, with sample sizes:

| Neutral code | Corresponds to | N |
|---|---|---|
| Class A | Teaching cohort 1 | 39 |
| Class B | Teaching cohort 2 | 38 |
| Class C | Teaching cohort 3 | 36 |

This lets a reader map the leave-one-class-out rows in Table 6 back to the corresponding
rows of the `Microdata_Deidentified` sheet, without the package disclosing institution-identifying
designations. The three cohorts were intact class groups formed by the registrar's random
class-assignment procedure; the codes are assigned in ascending order of the original
internal sequential number and carry no substantive meaning.

---

## 2. Environment

Tested with Python 3.13.

```
pip install -r requirements.txt
```

Dependencies: `numpy`, `pandas`, `scipy`, `scikit-learn`, `openpyxl`.

---

## 3. How to run

```bash
python 01_prepare_data.py          # -> data/analysis_dataset.csv
python 02_analysis.py              # full: 100 x 5-fold CV  (~2 min)
python 02_analysis.py --fast       # quick self-check: 20 x 5-fold CV
```

The pipeline prints a human-readable report to stdout and writes four CSVs to `outputs/`.

---

## 4. Analysis overview

### Variables

| Construct | Operationalization |
|---|---|
| Formative assignment performance | Mean across 8–9 assignments per class; incomplete submissions scored 0; 0–100 |
| Conceptual knowledge | Multiple-choice and true/false items (40 pts), rescaled to 0–100 |
| Unaided programming performance | Code completion and program design items (50 pts), rescaled to 0–100 |
| Forum participation | `ln(x + 1)` transformed reply counts |

### Table 3 — Descriptives, correlations, and regression

- Pearson correlations among assignment performance, conceptual knowledge, unaided programming performance, and (log-transformed) forum participation.
- OLS regressions of each outcome on assignment performance and forum participation, **controlling for teaching cohort** (Class B and Class C dummies; Class A is the reference level).
- **HC3 heteroskedasticity-consistent standard errors** (MacKinnon & White).
- Both predictors and outcomes are **z-standardised**, so the reported coefficient on assignment performance is already a fully standardised beta.
- Attendance is deliberately **excluded** from the Table 3 specification. It enters only as an additional M3 feature in the Table 5 nested-model comparison.

### Table 4 — Four-quadrant matrix

- Thresholds are the **whole-sample means** of assignment performance (68.41) and unaided programming performance (59.33).
- Students are cross-classified into four relative performance profiles.
- Within-quadrant descriptives are reported for all four profiles.
- **Focal subgroup analysis:** the High Assignment–Low Closed-Book subgroup is contrasted with the High–High subgroup on *both* examination components, yielding a within-sitting dissociation (conceptual knowledge *d* = 0.04 vs. unaided programming *d* = 3.14).

### Table 5 — Nested prediction models

| Model | Features |
|---|---|
| M1 | Early assignments |
| M2 | Early + mid-term assignments |
| M3 | Early + mid-term assignments + forum posts + attendance |

- **Repeated stratified 5-fold cross-validation, 100 repetitions.**
- **Leakage-free protocol — three safeguards:**
  1. The low-performance threshold is derived **within each training fold only**. It is then applied unchanged to generate both training labels and held-out labels. No held-out information enters the target definition.
  2. The feature scaler is fitted on training folds only.
  3. Stratification uses the true class distribution of the held-out folds.

### Table 6 — Leave-one-class-out validation

- The full M3 specification is trained on two classes and evaluated on the held-out third class.
- Thresholds are derived within the training classes.
- Reports AUC, sensitivity, specificity, balanced accuracy, and Brier score per held-out class.

---

## 5. Reproducibility notes

**Threshold rule.** The default is a within-training-fold **median split**, which reproduces the published Brier scores closely (`.222/.226/.232` vs. published `.226/.230/.233`). Alternative rules (`mean`, `p25`, `mean_sd`) are implemented in `derive_threshold()` and can be exercised by editing the `thr_rule` argument. Under all rules tested, the AUC difference between M1 and M3 remains negative or negligible, so the substantive conclusion — that coarse LMS behavioural traces add no stable discriminative value — is not an artefact of threshold choice.

**Leave-one-class-out metrics.** Class B specificity is `15/22 = .682`, derived from the confusion matrix (TN = 15, FP = 7) at the training-fold median threshold of 60.0. Note that the Brier scores in Table 6 are computed from predicted probabilities, so they are not exactly recoverable from the integer confusion counts alone.

**Table 3 specification.** Table 3 reports standardised coefficients from a model with
`z(assignment)` + `z(ln(forum+1))` + teaching-cohort dummies. Reproduced exactly:
conceptual knowledge β = .152 (HC3 SE = .120, p = .209); unaided programming
β = .358 (HC3 SE = .113, p = .002). Note that the reported p-values in the manuscript
(.207 and .002) are rounded from .209 and .0020.

**Platform-behaviour features in Table 5.** The M3 specification adds the two coarse LMS
behavioural traces available in the archived dataset — `ln(forum posts + 1)` and
`attendance_rate` — to the early and mid-term assignment scores. Because M3 is the
*negative* result (adding platform behaviour yields no stable gain in AUC), this feature
set does not support any positive claim in the manuscript.

**Seed sensitivity.** Cross-validation results are averaged over 100 repetitions with a fixed seed (42). Seed sensitivity was checked across five seeds; M3 − M1 differences in AUC ranged from −0.027 to −0.018, i.e. consistently negative.

---

## 6. Declarations

**AI use.** The initial version of these analysis scripts was developed with AI assistance. The author reviewed and verified every line, and confirmed that the pipeline's output matches all statistics reported in the manuscript. This is disclosed in the manuscript's AI-use statement.

**Ethics.** Data were collected in routine pedagogical practice. All direct identifiers (names, student ID numbers) were irreversibly removed prior to release. Class identifiers are recoded as `Class A/B/C`.

**License.** Dataset: CC BY 4.0. Code: MIT.

---

## 7. Citation

If you use this package, please cite the associated manuscript:

> Zeng, H. (2026). *Task performance and unaided programming performance divergence among programming novices under generative AI conditions.* Manuscript submitted for publication.
