# GitHub 上传操作指南（手把手版）

> 目标：把 `reproducibility` 文件夹上传为一个公开仓库，拿到一个可引用的链接，
> 再通过 Zenodo 换一个永久 DOI，写进论文的 Data Availability。
>
> 全程不需要写代码。**推荐用「浏览器拖拽」路线**（路线 A），
> 因为它最不容易出错，且不需要安装任何软件。

---

## 第 0 步：上传前先确认

你的复现包文件夹位置：

```
C:\Users\19107\Documents\教改\outputs\deep_mining\reproducibility
```

### ⚠️ 最重要：不要上传错文件夹

你的数据现在是**两份并存**的：

| 位置 | 内容 | 能不能上传 |
|---|---|---|
| `deep_mining\reproducibility\` | Class A/B/C 脱敏版 | ✅ **这个才上传** |
| `deep_mining\data_archive\` | **真实班号 231/232/233** | ❌ **绝对不要上传** |

`data_archive` 在 `reproducibility` 的**上层**，所以只要你是进到
`reproducibility` 里面去选文件，就不会误传。但**拖拽时务必看清楚路径**。

`reproducibility\.gitignore` 已加入忽略规则，用 Git 命令行推的话会自动排除；
但**浏览器拖拽上传不吃 .gitignore**，全靠你自己看准。

---

里面应该有这些文件（已为上传准备好）：

```
reproducibility/
├── 01_prepare_data.py
├── 02_analysis.py
├── README.md                    <- 仓库首页，会自动显示
├── REPLICATION_NOTES.md         <- 逐条核对报告
├── GITHUB_REPO_INFO.md          <- 本指南，上传后可删
├── CITATION.cff                 <- 让别人能"引用本仓库"
├── LICENSE                      <- 代码：MIT
├── LICENSE-DATA                 <- 数据：CC BY 4.0
├── .gitignore
├── requirements.txt
├── data/
│   ├── analysis_dataset.csv
│   └── raw_analysis_data.xlsx
└── outputs/
    ├── table3_descriptives_regression.csv
    ├── table4_quadrants.csv
    ├── table5_nested_models.csv
    └── table6_leave_one_class_out.csv
```

> **上传前请打开 `data/raw_analysis_data.xlsx` 快速扫一眼**，
> 确认 `匿名分析明细` 工作表的 **B 列**显示的是 `Class A` / `Class B` / `Class C`，
> 而不是 231/232/233。
>
> 也可以直接跑一次自检（会打印 PASS/FAIL）：
> ```bash
> python 01_prepare_data.py
> ```
> 看到这两行就说明可以放心上传：
> ```
> 班级数字码残留 : 0  PASS
> 机构/姓名残留  : 0  PASS
> ```
>
> 这一步不能省——公开仓库一旦发布，历史记录很难彻底抹除。

---

## 路线 A：浏览器拖拽上传（推荐，约 10 分钟）

### A1. 注册 / 登录 GitHub

1. 打开 https://github.com/signup
2. 用邮箱注册（建议用 `cenghaiping@gxstnu.edu.cn`，学术身份更清晰）
3. 设置用户名。**建议用 `cenghaiping`**，因为我已按此写好论文里的仓库链接：
   `https://github.com/zhp1123/genai-programming-performance-divergence-`
   - 如果这个用户名被占用，请选一个别的，**然后告诉我新用户名，我改论文里的链接**
4. 完成邮箱验证

### A2. 新建仓库

1. 登录后点右上角 **`+`** → **New repository**
2. 按下表填写：

| 字段 | 填什么 |
|---|---|
| **Repository name** | `genai-programming-performance-divergence` |
| **Description** | 见 `GITHUB_REPO_INFO.md` 里那句英文描述，复制粘贴 |
| **Public / Private** | 选 **Public** |
| **Add a README file** | **不勾** |
| **Add .gitignore** | **不勾**（仓库里已有） |
| **Choose a license** | **不勾**（仓库里已有） |

3. 点 **Create repository**

### A3. 上传文件

创建后会看到一个空仓库页面，中间有一句 *"…or upload an existing file"*。

1. 点 **uploading an existing file** 这个蓝色链接
2. 打开本地文件夹 `...\deep_mining\reproducibility`
3. **全选里面所有内容**（`Ctrl+A`），拖进浏览器上传区
   - ⚠️ 注意：**拖文件夹里的"内容"，而不是拖 `reproducibility` 文件夹本身**。
     否则仓库里会多套一层 `reproducibility/` 目录。
   - `data` 和 `outputs` 是文件夹，GitHub 网页版支持拖拽文件夹，会自动展开
4. 等进度条跑完（`raw_analysis_data.xlsx` 约 44 KB，很快）
5. 页面下方 **Commit changes** 区域填：

| 字段 | 填什么 |
|---|---|
| Commit message | `Initial release: replication package for EAIT submission` |
| Extended description | 留空即可 |

6. 点 **Commit changes**

### A4. 检查

刷新仓库首页，应该看到：

- 首页自动渲染 `README.md`（有蓝色徽章、表格、Quick start）
- 文件列表里有 `data/`、`outputs/`、`01_prepare_data.py` 等
- 右上角 About 栏显示你填的描述

**如果 About 栏是空的**：点 About 右侧的齿轮 ⚙️ →
把 Description 和 Topics 填进去（Topics 在 `GITHUB_REPO_INFO.md` 里有 10 个）→ Save changes。

### A5. 删掉这份指南（可选但建议）

`GITHUB_REPO_INFO.md` 是本地工作文件，公开仓库里留着不太合适。
在仓库里点开它 → 右上角垃圾桶图标 → Commit changes。

---

## 路线 B：Git 命令行（如果你以后会持续更新代码）

适用于：以后要反复改代码、不想每次都用网页拖。

### B1. 装 Git

下载 https://git-scm.com/download/win ，一路默认安装。

### B2. 配置身份（只做一次）

打开 Git Bash：

```bash
git config --global user.name "Haiping Zeng"
git config --global user.email "cenghaiping@gxstnu.edu.cn"
```

### B3. 初始化并推送

```bash
cd "C:/Users/19107/Documents/教改/outputs/deep_mining/reproducibility"

git init
git add .
git commit -m "Initial release: replication package for EAIT submission"

git branch -M main
git remote add origin https://github.com/zhp1123/genai-programming-performance-divergence-.git
git push -u origin main
```

推送时会弹窗要求登录。**密码栏不要填 GitHub 登录密码**（GitHub 已停用密码推送），
要填 **Personal Access Token**：

1. GitHub 头像 → Settings → Developer settings →
   Personal access tokens → **Tokens (classic)** → Generate new token (classic)
2. Note 填 `local-push`，Expiration 选 90 days
3. 勾选 **`repo`** 这一个权限即可
4. 生成后**立刻复制**那串 `ghp_...`（关掉页面就再也看不到了）
5. 回到 Git Bash，用户名填 `cenghaiping`，密码粘贴 token

---

## 第 2 步：打 Release（为了拿永久 DOI）

论文的 Data Availability 里写了"archived with a persistent DOI via Zenodo"，
所以这一步要做，否则审稿人可能会问。

### 2.1 先在 GitHub 打 Release

1. 仓库首页右侧 → **Releases** → **Create a new release**
2. 填写：

| 字段 | 填什么 |
|---|---|
| Choose a tag | 输入 `v1.0.0`，点 *Create new tag* |
| Target | `main` |
| Release title | `v1.0.0 - Submission version (EAIT)` |
| Describe this release | 复制 `GITHUB_REPO_INFO.md` 里的 Release description |

3. 点 **Publish release**

### 2.2 再用 Zenodo 抓取 DOI

1. 打开 https://zenodo.org ，用 **GitHub 账号**登录（Sign in with GitHub）
2. 右上角头像 → **Settings** → 左侧 **GitHub**
3. 找到 `genai-programming-performance-divergence`，把开关拨到 **ON**
4. 回到 GitHub，**重新发一个 Release**（Zenodo 只抓开启之后的新 Release）
   - 这次 tag 用 `v1.0.1`，其余同前
5. 等 1–2 分钟，刷新 Zenodo 的 GitHub 页面，会出现一个 **DOI 徽章**
   （形如 `10.5281/zenodo.1234567`）
6. 记下这个 DOI —— **发给我，我把它写进论文的 Data Availability**

> 如果你觉得 Zenodo 太麻烦：**也可以跳过**，但要告诉我。
> 我会把论文里"archived with a persistent DOI via Zenodo"这句删掉，
> 改成只留 GitHub 链接。不过有 DOI 对审稿印象更好，建议做。

---

## 第 3 步：告诉我结果

上传完成后，把下面三条信息发我，我一次性把论文改到位：

1. **GitHub 用户名**（如果不是 `cenghaiping`）
2. **仓库最终 URL**
3. **Zenodo DOI**（如果做了第 2 步）

我会相应更新：

- `Data Availability` 段
- `Code Availability` 段
- `CITATION.cff` 里的仓库地址

---

## 常见问题

**Q：上传后发现有错，能改吗？**
能。网页版点开文件 → 铅笔图标 → 改 → Commit changes。
如果是整个文件替换，删掉再传新的即可。Git 会保留历史，但公开页面上看到的是最新版。

**Q：能改成 Private 吗？**
能，但**不要**。论文声明了开放获取，Private 仓库会构成声明不实。
如果现在不想公开，可以先 Private，等论文录用再改 Public——但要同步改论文措辞。

**Q：学生看到自己的数据被公开会不会有问题？**
只要数据里没有可识别信息就没问题。这是为什么第 0 步要你检查一遍。
论文的 Ethics Approval 段也已经说明"全部标识信息在分析前已不可逆脱敏"。

**Q：`raw_analysis_data.xlsx` 需要传吗？**
建议传，它保留了数据溯源信息（provenance），审稿人会认可这种透明度。
如果你检查后发现它含有可识别字段，告诉我，我帮你生成一个脱敏版再传。

**Q：文件大小有限制吗？**
单个文件 100 MB、仓库 1 GB 以内免费。你的包总共不到 100 KB，完全没压力。
