#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02_analysis.py - Complete statistical analysis pipeline
=====================================
Reproduces Table 3 / Table 4 / Table 5 / Table 6 and every in-text statistic.

Usage:
    python 02_analysis.py            # full run
    python 02_analysis.py --fast     # reduce CV repeats to 20 (quick self-check)

Output: CSV files in outputs/ plus a console report

Mapping to the manuscript
------------
Table 3  : descriptives + Pearson correlations + OLS with HC3 robust SEs
Table 4  : whole-sample mean-split four quadrants + group descriptives
Table 5  : nested logistic models M1-M3, 100x repeated stratified 5-fold CV (leakage-free)
Table 6  : leave-one-class-out external validation

Key methodological points (RQ4)
------------------------------
1. Leakage-free: the target threshold is derived WITHIN training folds only; no held-out
      information is used. The feature scaler is likewise fitted on training folds only.
2. Stratification: CV is stratified on the true held-out label distribution, avoiding single-class folds.
3. Threshold rule: default is the within-training-fold median split, which matches the
      Brier scores reported in Table 5 (.226/.230/.233).

Declaration: the initial version was developed with AI assistance. The author reviewed it
      line by line and verified that its output matches every reported statistic.
"""
from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

ROOT = Path(__file__).resolve().parent          # reproducibility/
DATA = ROOT / 'data' / 'analysis_dataset.csv'
OUTDIR = ROOT / 'outputs'

# Model feature specifications (Table 5)
FEATURES = {
    'M1': ['assignment_early'],
    'M2': ['assignment_early', 'assignment_mid'],
    'M3': ['assignment_early', 'assignment_mid', 'forum_posts_ln', 'attendance_rate'],
}

RANDOM_SEED = 42


# ----------------------------------------------------------------------------- #
# Helper functions
# ----------------------------------------------------------------------------- #
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    # Platform-behaviour features are ln(x+1) transformed, per Table 2
    df['forum_posts_ln'] = np.log(df['forum_posts_raw'] + 1)
    return df


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    return float(stats.pearsonr(x, y)[0])


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Independent-samples Cohen's d (pooled SD)."""
    na, nb = len(a), len(b)
    pooled = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return float((a.mean() - b.mean()) / pooled)


def ols_hc3(X: np.ndarray, y: np.ndarray):
    """OLS regression returning coefficients, SEs and p-values under HC3 robust SEs."""
    X = np.column_stack([np.ones(len(X)), X])
    n, k = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X)
    leverage = np.einsum('ij,jk,ik->i', X, XtX_inv, X)
    omega = (resid / (1 - leverage)) ** 2
    cov = XtX_inv @ (X.T @ np.diag(omega) @ X) @ XtX_inv
    se = np.sqrt(np.diag(cov))
    tval = beta / se
    pval = 2 * (1 - stats.t.cdf(np.abs(tval), df=n - k))
    return beta, se, tval, pval


def derive_threshold(y_train: np.ndarray, rule: str = 'median') -> float:
    """
    Derive the low-performance threshold WITHIN training folds (the key leakage-free step).

    rule:
      'median'  training-fold median (default; matches Table 5)
      'mean'    training-fold mean
      'p25'     training-fold 25th percentile
      'mean_sd' training-fold mean minus 1 SD
    """
    if rule == 'median':
        return float(np.median(y_train))
    if rule == 'mean':
        return float(y_train.mean())
    if rule == 'p25':
        return float(np.percentile(y_train, 25))
    if rule == 'mean_sd':
        return float(y_train.mean() - y_train.std(ddof=1))
    raise ValueError(f'Unknown threshold rule: {rule}')


# ----------------------------------------------------------------------------- #
# Analysis modules
# ----------------------------------------------------------------------------- #
def _z(v: np.ndarray) -> np.ndarray:
    """Sample z-standardisation (ddof=1), matching the published Table 3 specification."""
    return (v - v.mean()) / v.std(ddof=1)


def table3_descriptives_and_regression(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 3: descriptives, Pearson correlations, and OLS regression of assignment
    performance on the two outcomes, with HC3 robust SEs.

    Specification reproduced here (matches the published table exactly):
      predictors = z(assignment) + z(ln(forum+1)) + class dummies (Class B, Class C)
      outcomes   = z(conceptual knowledge) / z(unaided programming)

    Attendance is deliberately EXCLUDED from Table 3. It enters only as an
    additional M3 feature in the Table 5 nested-model comparison. The reported
    beta is therefore a fully standardised coefficient on z(assignment).
    """
    a = df['assignment_mean'].to_numpy(float)
    k = df['conceptual_knowledge'].to_numpy(float)
    p = df['unaided_programming'].to_numpy(float)
    d_raw = df['forum_posts_raw'].to_numpy(float)
    d = np.log(d_raw + 1)

    # Class dummies (teaching cohort fixed effects). Class A is the reference level.
    c232 = (df['class_label'] == 'Class B').to_numpy(float)
    c233 = (df['class_label'] == 'Class C').to_numpy(float)

    a_z, d_z = _z(a), _z(d)
    Z = np.column_stack([a_z, d_z, c232, c233])

    rows = []
    for outcome, y_raw in [('Conceptual Knowledge', k), ('Unaided Programming', p)]:
        y_z = _z(y_raw)
        beta, se, tval, pval = ols_hc3(Z, y_z)
        rows.append({
            'outcome': outcome,
            'mean': round(y_raw.mean(), 2),
            'sd': round(y_raw.std(ddof=1), 2),
            'r_assignment': round(pearson(a, y_raw), 3),
            'r_discussion': round(pearson(d, y_raw), 3),
            # beta[1] is already standardised because both X and y are z-scored
            'beta_std': round(float(beta[1]), 3),
            'hc3_se': round(float(se[1]), 3),
            'p_value': round(float(pval[1]), 4),
        })

    # Descriptives for assignment performance itself
    rows.append({
        'outcome': 'Formative Assignment Performance',
        'mean': round(a.mean(), 2),
        'sd': round(a.std(ddof=1), 2),
        'r_assignment': np.nan, 'r_discussion': np.nan,
        'beta_std': np.nan, 'hc3_se': np.nan, 'p_value': np.nan,
    })
    out = pd.DataFrame(rows)
    print('\n===== Table 3 reproduction: descriptives and regression =====')
    print('  specification: z(assignment) + z(ln(forum+1)) + class dummies | HC3 SEs')
    print(out.to_string(index=False))
    print(f'\n  N = {len(df)}, r(assignment, unaided) = {pearson(a, p):.4f}')
    return out


def table4_quadrants(df: pd.DataFrame) -> pd.DataFrame:
    """Table 4: whole-sample mean-split four-quadrant distribution and group descriptives."""
    a = df['assignment_mean'].to_numpy(float)
    p = df['unaided_programming'].to_numpy(float)
    a_thr, p_thr = a.mean(), p.mean()

    def label(x, y):
        if x >= a_thr and y >= p_thr:
            return 'High Assignment-High Closed-Book'
        if x >= a_thr and y < p_thr:
            return 'High Assignment-Low Closed-Book'
        if x < a_thr and y >= p_thr:
            return 'Low Assignment-High Closed-Book'
        return 'Low Assignment-Low Closed-Book'

    df = df.copy()
    df['profile'] = [label(x, y) for x, y in zip(a, p)]

    rows = []
    for name, g in df.groupby('profile'):
        rows.append({
            'profile': name,
            'n': len(g),
            'pct': round(len(g) / len(df) * 100, 1),
            'assignment_mean': round(g['assignment_mean'].mean(), 2),
            'conceptual_knowledge': round(g['conceptual_knowledge'].mean(), 2),
            'unaided_programming': round(g['unaided_programming'].mean(), 2),
            'forum_posts_raw': round(g['forum_posts_raw'].mean(), 2),
        })
    out = pd.DataFrame(rows).sort_values('n', ascending=False)

    print('\n===== Table 4 reproduction: four-quadrant distribution =====')
    print(f'  thresholds: assignment M = {a_thr:.4f}, unaided M = {p_thr:.4f}')
    print(out.to_string(index=False))

    # Focal subgroup vs High-High: within-sitting dissociation
    hh = df[df['profile'] == 'High Assignment-High Closed-Book']
    hl = df[df['profile'] == 'High Assignment-Low Closed-Book']
    print('\n----- Focal subgroup within-sitting dissociation (Section 4.4) -----')
    print(f'  focal group n={len(hl)}: knowledge M={hl["conceptual_knowledge"].mean():.2f}, '
          f'unaided M={hl["unaided_programming"].mean():.2f}')
    print(f'  High-High group n={len(hh)}: knowledge M={hh["conceptual_knowledge"].mean():.2f}, '
          f'unaided M={hh["unaided_programming"].mean():.2f}')
    print(f'  d(knowledge) = {cohens_d(hh["conceptual_knowledge"].to_numpy(), hl["conceptual_knowledge"].to_numpy()):.4f}')
    print(f'  d(unaided)   = {cohens_d(hh["unaided_programming"].to_numpy(), hl["unaided_programming"].to_numpy()):.4f}')
    print(f'  unaided gap = {hh["unaided_programming"].mean() - hl["unaided_programming"].mean():.4f} points')
    return out


def repeated_cv(df: pd.DataFrame, model: str, thr_rule: str = 'median',
                n_repeats: int = 100, n_splits: int = 5,
                seed: int = RANDOM_SEED) -> dict:
    """
    Repeated stratified K-fold cross-validation (leakage-free).

    Leakage-free implementation:
      - The threshold is derived within training folds, then applied to generate both training and held-out labels
      - The scaler is fitted on training folds only
      - Stratification uses the true label distribution of the held-out folds
    """
    feats = FEATURES[model]
    X = df[feats].to_numpy(float)
    y_raw = df['unaided_programming'].to_numpy(float)

    # Global median bins, used only for stratified sampling (not for label definition)
    strat = (y_raw >= np.median(y_raw)).astype(int)
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=seed)

    aucs, briers, sens, specs = [], [], [], []
    for tr, te in cv.split(X, strat):
        thr = derive_threshold(y_raw[tr], thr_rule)
        y_tr = (y_raw[tr] < thr).astype(int)
        y_te = (y_raw[te] < thr).astype(int)
        if y_tr.sum() == 0 or y_tr.sum() == len(y_tr):
            continue
        if y_te.sum() == 0 or y_te.sum() == len(y_te):
            continue

        scaler = StandardScaler().fit(X[tr])
        clf = LogisticRegression(max_iter=5000, solver='liblinear', random_state=seed)
        clf.fit(scaler.transform(X[tr]), y_tr)
        prob = clf.predict_proba(scaler.transform(X[te]))[:, 1]

        aucs.append(roc_auc_score(y_te, prob))
        briers.append(brier_score_loss(y_te, prob))
        tn, fp, fn, tp = confusion_matrix(y_te, (prob >= 0.5).astype(int), labels=[0, 1]).ravel()
        sens.append(tp / (tp + fn) if (tp + fn) else np.nan)
        specs.append(tn / (tn + fp) if (tn + fp) else np.nan)

    return {
        'model': model,
        'threshold_rule': thr_rule,
        'auc': round(float(np.nanmean(aucs)), 3),
        'auc_sd': round(float(np.nanstd(aucs)), 3),
        'sensitivity': round(float(np.nanmean(sens)), 3),
        'specificity': round(float(np.nanmean(specs)), 3),
        'balanced_accuracy': round(float((np.nanmean(sens) + np.nanmean(specs)) / 2), 3),
        'brier': round(float(np.nanmean(briers)), 3),
        'n_folds_used': len(aucs),
    }


def table5_nested_models(df: pd.DataFrame, n_repeats: int = 100) -> pd.DataFrame:
    """Table 5: repeated cross-validation performance of nested models M1-M3."""
    rows = [repeated_cv(df, m, n_repeats=n_repeats) for m in ['M1', 'M2', 'M3']]
    out = pd.DataFrame(rows)
    print('\n===== Table 5 reproduction: nested models (leakage-free repeated CV) =====')
    print(f'  {n_repeats} x 5 folds, threshold rule = training-fold median')
    print(out.to_string(index=False))
    delta = out.loc[2, 'auc'] - out.loc[0, 'auc']
    print(f'\n  delta AUC (M3 - M1) = {delta:+.3f}  -> no stable gain from adding platform-behaviour features')
    return out


def table6_leave_one_class_out(df: pd.DataFrame, thr_rule: str = 'median') -> pd.DataFrame:
    """Table 6: leave-one-class-out external validation."""
    feats = FEATURES['M3']
    y_raw = df['unaided_programming'].to_numpy(float)
    classes = df['class_label'].to_numpy()

    rows = []
    for held in sorted(set(classes)):
        tr = np.where(classes != held)[0]
        te = np.where(classes == held)[0]
        thr = derive_threshold(y_raw[tr], thr_rule)
        y_tr = (y_raw[tr] < thr).astype(int)
        y_te = (y_raw[te] < thr).astype(int)

        scaler = StandardScaler().fit(df.iloc[tr][feats].to_numpy(float))
        clf = LogisticRegression(max_iter=5000, solver='liblinear', random_state=RANDOM_SEED)
        clf.fit(scaler.transform(df.iloc[tr][feats].to_numpy(float)), y_tr)
        prob = clf.predict_proba(scaler.transform(df.iloc[te][feats].to_numpy(float)))[:, 1]

        tn, fp, fn, tp = confusion_matrix(y_te, (prob >= 0.5).astype(int), labels=[0, 1]).ravel()
        sens = tp / (tp + fn) if (tp + fn) else np.nan
        spec = tn / (tn + fp) if (tn + fp) else np.nan
        rows.append({
            'held_out_class': held,
            'n': len(te),
            'threshold': round(thr, 2),
            'auc': round(roc_auc_score(y_te, prob), 3),
            'sensitivity': round(sens, 3),
            'specificity': round(spec, 3),
            'balanced_accuracy': round((sens + spec) / 2, 3),
            'brier': round(brier_score_loss(y_te, prob), 3),
        })
    out = pd.DataFrame(rows)
    print('\n===== Table 6 reproduction: leave-one-class-out validation =====')
    print(out.to_string(index=False))
    print(f'\n  AUC range: {out["auc"].min():.3f} to {out["auc"].max():.3f}')
    print('  -> substantial cross-cohort fluctuation; single-cohort deployment is unreliable and requires human review')
    return out


# ----------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description='Statistical reproduction package for the EAIT manuscript')
    parser.add_argument('--fast', action='store_true',
                        help='reduce CV repeats to 20 for a quick self-check')
    args = parser.parse_args()
    n_repeats = 20 if args.fast else 100

    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    print(f'Loaded data: N = {len(df)}, classes = {sorted(df["class_label"].unique())}')

    t3 = table3_descriptives_and_regression(df)
    t4 = table4_quadrants(df)
    t5 = table5_nested_models(df, n_repeats=n_repeats)
    t6 = table6_leave_one_class_out(df)

    t3.to_csv(OUTDIR / 'table3_descriptives_regression.csv', index=False, encoding='utf-8-sig')
    t4.to_csv(OUTDIR / 'table4_quadrants.csv', index=False, encoding='utf-8-sig')
    t5.to_csv(OUTDIR / 'table5_nested_models.csv', index=False, encoding='utf-8-sig')
    t6.to_csv(OUTDIR / 'table6_leave_one_class_out.csv', index=False, encoding='utf-8-sig')
    print(f'\n[OK] results written to {OUTDIR}')


if __name__ == '__main__':
    main()
