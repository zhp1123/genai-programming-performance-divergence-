# GitHub 仓库填写信息（复制粘贴用）

## 仓库名（Repository name）

```
genai-programming-performance-divergence
```

> 说明：全小写、连字符分隔、无年份无姓名，包含三个检索关键词
> （genai / programming / performance），符合学术复现包的命名惯例。

## 一句话描述（Description）— 粘贴到 About 栏

```
Replication package: de-identified dataset (N=113 CS1 novices) and full analysis pipeline for a study on task vs. unaided programming performance divergence under generative AI. Reproduces all statistics in Tables 3-6.
```

中文对照：复现包——113 名 CS1 编程初学者的去标识数据集与完整分析流水线，
用于生成式 AI 情境下任务表现与闭卷编程表现分化的研究，可复现正文表 3–6 全部统计量。

## 网址（Website）— 可留空，或填论文 DOI（录用后再补）

```
(留空，或录用后填 Springer 论文 DOI)
```

## Topics — 逐个添加，共 10 个

```
generative-ai
programming-education
cs1
assessment-validity
learning-analytics
educational-data-mining
cognitive-offloading
replication-package
open-data
python
```

## 其他勾选项

- [x] Add a README file — **不要勾**，因为我们要自己上传 README.md
- [ ] Add .gitignore — **不要勾**，仓库里已有 `.gitignore` 文件
- [ ] Choose a license — **不要勾**，仓库里已有 `LICENSE` 与 `LICENSE-DATA`
- Visibility: **Public**（公开，符合 Data Availability 声明）

## 首次发布（Releases）信息

Tag version:

```
v1.0.0
```

Release title:

```
v1.0.0 - Submission version (EAIT)
```

Release description:

```
Initial public release of the replication package accompanying the manuscript
"Task Performance and Unaided Programming Performance Divergence among
Programming Novices under Generative AI Conditions" (submitted to Education
and Information Technologies).

Contents:
- De-identified analysis dataset (N = 113)
- Data preparation and full analysis pipeline
- Generated output tables for Tables 3-6
- REPLICATION_NOTES.md with a point-by-point reproduction report
```

> Zenodo 版本号必须与 Release tag 一致才能自动抓取。先发 Release，再去 Zenodo
> 开 DOI，顺序不能反。
