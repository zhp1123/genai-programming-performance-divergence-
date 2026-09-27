# Zenodo DOI 申请操作指南（手把手版）

> **这个 DOI 有什么用？**
> GitHub 链接会变（你可以改仓库名、可以删仓库），但 DOI 是永久的。
> 期刊的 Data Availability 声明如果只写 GitHub 链接，审稿人会认为"可复现性保障不足"；
> 有 DOI 就等于给你的数据和代码上了一个**永久身份编号**，任何人引用它都不会失效。
>
> 你的论文里已经写了 "The repository is archived with a persistent DOI via Zenodo"，
> 所以**这一步要完成**，否则声明不实。

---

## 总览：一共 5 步，约 10 分钟

```
① 先把仓库整理好并打 Release (v1.0.0)
        ↓
② 用 GitHub 账号登录 Zenodo
        ↓
③ 在 Zenodo 里"打开"你的仓库开关
        ↓
④ 回 GitHub 再打一个新 Release (v1.0.1)   ← 关键，Zenodo 只抓开关打开之后的
        ↓
⑤ 等 1-2 分钟，拿到 DOI，发给我
```

**最容易出错的地方是第 ③④ 步的顺序。** 很多人先打了 Release 再去 Zenodo 开开关，
结果 Zenodo 什么都没抓到，以为坏了。**开关必须先打开，Release 必须后打。**

---

## 第 ① 步：给仓库打 Release

1. 打开你的仓库：`https://github.com/zhp1123/genai-programming-performance-divergence-`
2. 在页面**右侧栏**找到 **Releases**，点进去
   （或者直接在地址栏访问 `你的仓库地址/releases`）
3. 点绿色按钮 **Create a new release**
4. 按下表填写：

| 字段 | 填什么 |
|---|---|
| **Choose a tag** | 输入 `v1.0.0`，然后点下方弹出的 **+ Create new tag: v1.0.0 on publish** |
| **Target** | 保持 `main` |
| **Release title** | `v1.0.0 - Submission version (EAIT)` |
| **Describe this release** | 复制下面这段 |

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

5. 点 **Publish release**

> **这一步的目的是什么？** 先把仓库状态"钉"住一个版本。以后你改了代码，
> v1.0.0 仍然指向今天这份，审稿人复现出来的结果和你论文里写的一致。

---

## 第 ② 步：登录 Zenodo

1. 打开 **https://zenodo.org**
2. 点右上角 **Sign up**（如果没账号）或 **Sign in**
3. **关键：选择 "Sign in with GitHub"**（那个章鱼猫图标）
   - ⚠️ **不要**用邮箱单独注册。必须用 GitHub 授权登录，
     否则 Zenodo 没办法看到你的仓库，后面第 ③ 步会找不到。
4. 授权时如果问权限，同意即可

---

## 第 ③ 步：在 Zenodo 打开仓库开关

1. 登录后，点右上角**你的头像** → **Settings**
2. 左侧菜单找到 **GitHub**（有时写作 "Linked accounts" → GitHub）
3. 会看到一个列表，列出你 GitHub 账号下的所有仓库
4. 找到 **`genai-programming-performance-divergence-`**
   - 如果列表很长，页面有搜索框，输入 `genai` 就能筛出来
5. 把它右边的开关**从 OFF 拨到 ON**
   - 有些版本需要先点 **Sync now** 刷新仓库列表才能看到新仓库

> **此时 Zenodo 还没有 DOI。** 开关打开只是"订阅"，等第 ④ 步有新 Release 才触发。

---

## 第 ④ 步：回 GitHub 再打一个 Release

**这一步不能省**，因为 Zenodo 的抓取机制是「监测到新 Release 事件」，
不会回溯抓你开关打开**之前**已经存在的 v1.0.0。

1. 回到 GitHub 仓库的 Releases 页面
2. 再点 **Create a new release**
3. 这次填：

| 字段 | 填什么 |
|---|---|
| **Choose a tag** | `v1.0.1` |
| **Release title** | `v1.0.1 - Zenodo archive` |
| **Describe** | `Zenodo-archived version. Same content as v1.0.0.` |

4. 点 **Publish release**

> **为什么用 v1.0.1 而不是重新发 v1.0.0？**
> 因为 v1.0.1 这个号在 Zenodo 那边是新的，一定能触发抓取。内容两者完全一样，
> 所以 DOI 指向哪个版本都无所谓，但这样最稳妥。

---

## 第 ⑤ 步：拿到 DOI

1. 等 **1–2 分钟**（有时要 5 分钟，Zenodo 用队列处理）
2. 刷新 Zenodo 的 GitHub 页面（Settings → GitHub）
3. 你的仓库名旁边会出现一个**蓝色 DOI 徽章**，形如：

```
10.5281/zenodo.1234567
```

4. **点一下那个徽章**，会进入 Zenodo 的归档页面，能看到：
   - 一个 **DOI**（这是你要的）
   - 一个 **Concept DOI**（形如 `10.5281/zenodo.1234566`，指向"这个项目所有版本"，**推荐用这个**）
   - 引用格式（BibTeX 等）

> **该用哪个 DOI？** 用 **Concept DOI**（版本号较小、不带 `.1234567` 后缀那个）。
> 它的含义是"这个仓库的整体"，以后你更新 v1.1.0 也不会失效。
> 如果你分不清，**两个都发给我**，我来判断。

5. 把 DOI 发给我（格式如 `10.5281/zenodo.1234567`）

---

## 我拿到 DOI 后会做什么

一次性更新这些位置：

| 文件 | 改动 |
|---|---|
| `EAIT英文版_投稿修复版.docx` · Data Availability | 把 "archived with a persistent DOI via Zenodo" 换成具体 DOI 和链接 |
| `EAIT英文版_投稿修复版.docx` · Code Availability | 补上 DOI |
| `reproducibility/README.md` | 顶部加 DOI 徽章 |
| `reproducibility/CITATION.cff` | 加 `doi:` 字段 |

---

## 常见问题

**Q：我在 Zenodo 的仓库列表里找不到我的仓库？**
两个可能：
1. 你注册时不是用 GitHub 登录的 → 退出，改用 **Sign in with GitHub**
2. 仓库是新建的，Zenodo 缓存没刷新 → 在 Zenodo 的 GitHub 页面点 **Sync now**

**Q：开关打开了，但打了 Release 还是没 DOI？**
检查这几点：
- Release 是**在开关打开之后**发布的吗？（顺序错了就再打一个 `v1.0.2`）
- 仓库是 **Public** 吗？（Private 仓库 Zenodo 抓不到）
- Release 是"已发布"状态，不是 Draft 吧？

**Q：DOI 要花钱吗？**
不要。Zenodo 是 CERN 运营的免费开放科学基础设施，科研用途完全免费。

**Q：DOI 能改吗？**
不能改，但你可以为将来更新的版本发新的 DOI，那时 Zenodo 会自动把它们归到同一个 Concept DOI 下。

**Q：我可以不用 Zenodo，直接写 GitHub 链接吗？**
可以，但**不推荐**。期刊（尤其 Springer）现在普遍把"有无持久标识符"作为数据开放程度的判断依据。
而且你论文里已经承诺了 Zenodo DOI。要放弃的话告诉我，我把那句话删掉。

---

## 如果你嫌麻烦

**最少要做的两步**是：② 用 GitHub 登录 Zenodo → ③ 打开开关 → ④ 再打一个 Release。
其他步骤（v1.0.0、Release 描述文案）都是锦上添花，不做也不影响拿 DOI。

如果中间卡住了，**把卡住的那个页面截图发我**，我直接告诉你点哪里。
