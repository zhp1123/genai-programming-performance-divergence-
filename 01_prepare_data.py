#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_prepare_data.py — Data preparation and de-identification
===========================================================
Input : data/raw_analysis_data.xlsx   (English release workbook; sheet Microdata_Deidentified)
Output: data/analysis_dataset.csv     (analysis dataset, class labels as Class A/B/C)

This script performs field selection and de-identification only. No statistical
transformation is applied here; every transformation is written out explicitly in
02_analysis.py so that it can be reviewed line by line.

The released workbook is already in English and already carries Class A/B/C codes.
For convenience, this script also accepts the original Chinese-language workbook with
numeric class codes (231/232/233), so that a researcher holding the untranslated
source data can still run it unchanged.

Declaration: the initial version of this script was developed with AI assistance.
The author reviewed it line by line and verified that its output matches every
statistic reported in the manuscript.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent          # reproducibility/
RAW = ROOT / 'data' / 'raw_analysis_data.xlsx'
OUT = ROOT / 'data' / 'analysis_dataset.csv'

# Chinese workbook uses Chinese sheet/column names; the English release uses English
# ones. Accept either so the script is robust to whichever file is present.
SHEET_CANDIDATES = ['Microdata_Deidentified', '匿名分析明细']

# Map from either language to the canonical English column name
COLUMN_MAP = {
    # English release
    'student_id': 'student_id', 'class_label': 'class_label',
    'assignment_mean': 'assignment_mean', 'submission_rate': 'submission_rate',
    'assignment_early': 'assignment_early', 'assignment_mid': 'assignment_mid',
    'assignment_late': 'assignment_late', 'assignment_slope': 'assignment_slope',
    'assignment_sd': 'assignment_sd', 'zero_score_count': 'zero_score_count',
    'conceptual_knowledge': 'conceptual_knowledge',
    'unaided_programming': 'unaided_programming',
    'ai_assisted_problem_solving': 'ai_assisted_problem_solving',
    'forum_posts_raw': 'forum_posts_raw', 'attendance_rate': 'attendance_rate',
    'conversion_residual_z': 'conversion_residual_z',
    'theoretical_type': 'theoretical_type',
    'cluster_k3': 'cluster_k3', 'cluster_k4': 'cluster_k4',
    # Original Chinese workbook
    '匿名编号': 'student_id', '教学班': 'class_label',
    '任务成绩': 'assignment_mean', '提交率': 'submission_rate',
    '前期作业': 'assignment_early', '中期作业': 'assignment_mid',
    '后期作业': 'assignment_late', '作业斜率': 'assignment_slope',
    '作业波动': 'assignment_sd', '零分次数': 'zero_score_count',
    '知识理解': 'conceptual_knowledge', '编程应用': 'unaided_programming',
    'AI辅助问题求解': 'ai_assisted_problem_solving',
    '讨论数': 'forum_posts_raw', '签到率': 'attendance_rate',
    '转化残差Z': 'conversion_residual_z', '理论分型': 'theoretical_type',
    '3类聚类': 'cluster_k3', '4类聚类': 'cluster_k4',
}

# Class-label de-identification.
# The released workbook already uses Class A/B/C. The numeric codes are retained
# here so that a researcher holding the un-de-identified source data can run this
# script unchanged and obtain the same output.
CLASS_MAP = {
    231: 'Class A', 232: 'Class B', 233: 'Class C',
    '231': 'Class A', '232': 'Class B', '233': 'Class C',
    'Class A': 'Class A', 'Class B': 'Class B', 'Class C': 'Class C',
}

# theoretical_type values are Chinese in the source workbook; normalise to English
TYPE_MAP = {
    '任务—能力脱节型': 'Discrepant',
    '低投入潜能型': 'Low-engagement potential',
    '双重困难型': 'Double-low',
    '稳定获得型': 'Stable-acquisition',
}


def pick_sheet(path):
    names = pd.ExcelFile(path).sheet_names
    for cand in SHEET_CANDIDATES:
        if cand in names:
            return cand
    raise ValueError(f'None of {SHEET_CANDIDATES} found in {path.name}; sheets = {names}')


def main():
    sheet = pick_sheet(RAW)
    df = pd.read_excel(RAW, sheet_name=sheet)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns=COLUMN_MAP)

    # Class-label de-identification (accepts numeric codes, string codes, or
    # already-de-identified labels)
    df['class_label'] = df['class_label'].map(CLASS_MAP)
    if df['class_label'].isna().any():
        bad = sorted(set(pd.read_excel(RAW, sheet_name=sheet).iloc[:, 1]))
        raise ValueError(f'Unmapped class labels {bad}; check CLASS_MAP')

    # Normalise the typology labels if the Chinese source was used
    if 'theoretical_type' in df.columns:
        df['theoretical_type'] = df['theoretical_type'].map(
            lambda v: TYPE_MAP.get(str(v).strip(), v))

    # student_id is already of the form S001; kept so rows remain traceable
    df = df.sort_values('student_id').reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding='utf-8-sig')

    print(f'[OK] wrote {OUT}')
    print(f'     N = {len(df)}')
    print(f'     class distribution = {df["class_label"].value_counts().sort_index().to_dict()}')
    print(f'     columns = {df.shape[1]}')

    verify_deidentification()


def verify_deidentification():
    """Audit the released workbook: no class numbers, institution, or person names.

    Included so that any reader can independently confirm the released data are
    de-identified, rather than having to take the authors' word for it.
    """
    import re
    import openpyxl

    print()
    print('=' * 64)
    print('De-identification audit / 去标识化核验')
    print('=' * 64)

    wb = openpyxl.load_workbook(RAW, data_only=True)

    # Standalone class numbers only -- avoids false positives such as the "232"
    # inside 0.232
    class_re = re.compile(r'(?<![0-9.])23[123](?![0-9])')
    other_re = re.compile(r'智能制造|广西科技|曾海平|学号|姓名')
    cjk_re = re.compile(r'[\u4e00-\u9fff]')

    class_hits, other_hits, cjk_hits = [], [], []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                v = cell.value
                if v is None:
                    continue
                if isinstance(v, int) and not isinstance(v, bool) and v in (231, 232, 233):
                    class_hits.append(f'{ws.title}!{cell.coordinate}')
                elif isinstance(v, str):
                    if class_re.search(v):
                        class_hits.append(f'{ws.title}!{cell.coordinate}={v[:30]}')
                    if other_re.search(v):
                        other_hits.append(f'{ws.title}!{cell.coordinate}={v[:30]}')
                    if cjk_re.search(v):
                        cjk_hits.append(f'{ws.title}!{cell.coordinate}')

    ok = not class_hits and not other_hits and not cjk_hits
    print(f'  class-number residue : {len(class_hits):>3}  '
          f'{"PASS" if not class_hits else "FAIL " + str(class_hits[:5])}')
    print(f'  name / institution   : {len(other_hits):>3}  '
          f'{"PASS" if not other_hits else "FAIL " + str(other_hits[:5])}')
    print(f'  untranslated CJK     : {len(cjk_hits):>3}  '
          f'{"PASS" if not cjk_hits else "FAIL " + str(cjk_hits[:5])}')
    print(f'  verdict              : '
          f'{"data are adequately de-identified" if ok else "*** identifiable content remains -- do not publish ***"}')
    return ok


if __name__ == '__main__':
    main()
