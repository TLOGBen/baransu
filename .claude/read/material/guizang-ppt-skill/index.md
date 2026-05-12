---
source_url: "https://github.com/op7418/guizang-ppt-skill"
title: "Guizang PPT Skill · 网页 PPT / 配图 / 封面"
captured_at: "2026-05-12T14:21:13+08:00"
conversion_tool: "markitdown 0.1.5 (direct fetch via gh api)"
slug: "guizang-ppt-skill"
platform: "WSL2"
acquire_via: "url"
---

# Guizang PPT Skill · 网页 PPT / 配图 / 封面

> 🌏 **English version: [README.en.md](./README.en.md)**

一个适配 Claude Code / Codex 等 Agent 环境的网页 PPT 技能,用于生成**单文件 HTML 横向翻页 PPT**、PPT 配图和多平台封面。

内置两套视觉系统:

- **Style A: 电子杂志 × 电子墨水**。像 *Monocle* 贴上了代码,适合叙事、观点、分享、个人风格表达。
- **Style B: 瑞士国际主义**。网格至上、单一高饱和锚点色、直角、发丝线、极致字号对比,适合事实、产品、分析、方法论表达。

> 由 [歸藏](https://x.com/op7418) 在"一人公司:被 AI 折叠的组织"、"一种新的工作方式"等线下分享中沉淀而成,踩过的每一个坑都写进了 `checklist.md`。

**旧主题 · Style A 电子杂志风**

![Style A 电子杂志风效果展示](https://github.com/user-attachments/assets/5dc316a2-401c-4e37-9123-ea081b6ae470)

**新主题 · Style B 瑞士国际主义**

![Style B 瑞士国际主义效果展示](https://github.com/user-attachments/assets/8960e78c-69bb-4b7e-aa95-6fad64b70314)

## 效果

- 🖋 **双视觉系统**:电子杂志风负责叙事,瑞士风负责事实表达
- 📐 **横向左右翻页**:键盘 ← → / 滚轮 / 触屏滑动 / 底部圆点 / ESC 索引
- 🧩 **Style A 10 种布局**:封面、章节、数据大字报、图文、图片网格、Pipeline、对比等
- 🧱 **Style B 22 种锁定版式**:Cover、Statement、KPI Tower、Loop Diagram、Duo Compare、Image Hero、Closing Manifesto 等
- 🎨 **主题色预设**:Style A 5 套电子墨水主题,Style B 4 套瑞士高饱和锚点色
- 🖼 **Codex 可选配图流程**:可用 GPT-Image 2.0 / GPT-M 2.0 生成纪实照片、信息图、流程图、系统关系图、UI 情景图,并按模板比例插入
- 📰 **多平台封面**:可用同一套视觉规则生成公众号 21:9、公众号分享卡 1:1、小红书 3:4、视频号横版等封面
- 📴 **低性能静态模式**:按 `B` 可关闭 WebGL / canvas 动画,让动态内容退回静态背景
- 📄 **单文件 HTML**:不需要构建、不需要服务器,浏览器直接打开

## 适合 / 不适合

**✅ 合适**:线下分享 / 行业内部讲话 / 私享会 / AI 产品发布 / demo day / 带强烈个人风格的演讲

**❌ 不合适**:大段表格数据 / 培训课件(信息密度不够)/ 需要多人协作编辑(静态 HTML)

## 安装

### 方式一:一行命令安装(推荐)

```bash
npx skills add https://github.com/op7418/guizang-ppt-skill --skill guizang-ppt-skill
```

### 方式二:把下面这段话直接发给 AI

> 帮我安装 `guizang-ppt-skill` 这个 Claude Code skill。请按下面步骤做:
>
> 1. 确保 `~/.claude/skills/` 目录存在(不存在就创建)
> 2. 执行 `git clone https://github.com/op7418/guizang-ppt-skill.git ~/.claude/skills/guizang-ppt-skill`
> 3. 验证:`ls ~/.claude/skills/guizang-ppt-skill/` 应该看到 `SKILL.md`、`assets/`、`references/` 三项
> 4. 告诉我安装好了,之后我说"做一份杂志风 PPT"之类的话就会触发这个 skill

把这段话复制粘贴给 Claude Code / Cursor / 任何有 shell 权限的 AI Agent,它会自动完成安装。

### 方式三:手动命令行

```bash
git clone https://github.com/op7418/guizang-ppt-skill.git ~/.claude/skills/guizang-ppt-skill
```

### 触发方式

装好后,Claude Code 会在对话里自动发现并调用这个 skill。触发关键词:

- "帮我做一份杂志风 PPT"
- "帮我做一份瑞士风 PPT"
- "生成一个 horizontal swipe deck"
- "editorial magazine style presentation"
- "electronic ink 风格演讲 slides"
- "基于这篇文章做一张公众号 21:9 封面"
- "基于这份 PPT 生成一张 1:1 分享卡"

## 使用流程

Skill 本身是结构化工作流,Agent 会逐步引导:

1. **选择风格** — Style A 电子杂志风,或 Style B 瑞士国际主义
2. **需求澄清** — 6 问清单:受众、时长、素材、图片、主题色、硬约束
3. **拷贝模板** — Style A 用 `assets/template.html`,Style B 用 `assets/template-swiss.html`
4. **填充内容** — 先做主题节奏表,再从对应 layout 骨架里挑、粘、改文案
5. **可选配图** — 在 Codex 中询问是否用 GPT-Image 2.0 / GPT-M 2.0 生成配图,再按页面比例插入
6. **自检** — 对照 `references/checklist.md`,P0 级问题必须全过；瑞士风还要运行版式校验器
7. **预览** — 浏览器直接打开
8. **迭代** — inline style 改字号/高度/间距

详细说明见 [`SKILL.md`](./SKILL.md)。

## Style B 瑞士风

瑞士风是这次新增的结构化主题。它不是"换一套 CSS",而是一套更严格的版式系统。

- **22 个具名版式**:正文页只能从 `S01` 到 `S22` 中选择,不能临时发明页面结构
- **4 套锚点色**:克莱因蓝 IKB、柠檬黄、柠檬绿、安全橙
- **网格锁定**:16 列 grid、直角色块、1px 发丝线、无阴影、无渐变、无圆角
- **中文字号收敛**:全中文大标题需要降一档,避免占掉正文和图片空间
- **图文底对齐**:左文右图 / 左图右文场景优先让正文块与图片底部对齐,同时避开页脚翻页组件
- **图片槽位绑定**:图片必须进入模板预留的 `data-image-slot`,常见主图按 21:9 或 16:10 生成
- **强校验**:用脚本拦住居中标题、实验版式、SVG 内写字、图片脱离槽位等问题

瑞士风校验命令:

```bash
node scripts/validate-swiss-deck.mjs path/to/index.html
```

## Codex 配图能力

在 Codex 环境中,完成 deck 初稿后可以主动询问用户是否需要生成配图。用户确认后,再询问图片类型或风格,常用类型包括:

- 人文纪实照片:富士 / 徕卡感的真实场景,增加人文表现力
- 信息图 / 流程图 / 对比图 / 系统关系图:用于解释无法用实拍照片说明的概念
- 截图再设计 / UI 情景图:把原始截图统一成适合 PPT 的比例和视觉密度
- 数据大字报 / 数据图表:把关键数字做成可直接插入 PPT 的视觉素材
- 多图拼贴:用于极宽图片槽位,避免把三张 16:9 图片硬塞进三列

生成图片时要遵守三个关键规则:

- 图片是 PPT 中的嵌入素材,不要自带页脚、页底、标题、角标、页码或装饰边框
- 图片语言跟随 deck 语言:中文 deck 的信息图用中文标签,英文 deck 用英文标签
- 图片比例必须先匹配落位:瑞士风主图常用 21:9,通用主图常用 16:9 / 16:10,截图再设计常用 16:10,多图网格统一高度

配图提示词见 [`references/image-prompts.md`](./references/image-prompts.md)。

## 封面生成

这个 Skill 也可以基于文章或 PPT 核心观点生成平台封面。典型规格:

- **公众号头图**:21:9,主标题优先,右侧或边缘保留视觉锚点
- **公众号分享卡**:1:1,与头图共用主题色、关键词和视觉元素
- **小红书封面 / 轮播**:3:4,大标题优先,多张时统一字号和视觉节奏
- **视频号 / 横版封面**:16:9,适合标题 + 副标题 + 单一视觉焦点

封面原则和 PPT 一样:只用少量关键词,视觉重心落在大标题上,不要把正文堆满。

## 目录结构

```
guizang-ppt-skill/
├── SKILL.md              ← Skill 主文件:工作流、原则、常见错误
├── README.md             ← 本文件
├── assets/
│   ├── template.html         ← Style A 电子杂志风模板
│   └── template-swiss.html   ← Style B 瑞士国际主义模板
├── scripts/
│   └── validate-swiss-deck.mjs ← 瑞士风版式校验器
└── references/
    ├── components.md     ← 组件手册(字体、色、网格、图标、callout、stat、pipeline)
    ├── layouts.md        ← 10 种页面布局骨架(可直接粘贴)
    ├── layouts-swiss.md  ← 22 种瑞士风锁定版式
    ├── swiss-layout-lock.md ← 瑞士风还原度和版式硬约束
    ├── themes.md         ← 5 套主题色预设(只能选不能自定义)
    ├── themes-swiss.md   ← 4 套瑞士风锚点色
    ├── image-prompts.md  ← GPT-Image 2.0 / GPT-M 2.0 配图类型、比例和基础提示词
    └── checklist.md      ← 质量检查清单(P0 / P1 / P2 / P3 分级)
```

## 主题色预设

从 `references/themes.md` 里选一套——**不允许自定义 hex 值**,保护美学比给自由更重要。

| 主题 | 适合场景 |
|------|---------|
| 🖋 墨水经典 | 通用默认、商业发布、不知道选啥 |
| 🌊 靛蓝瓷 | 科技 / 研究 / AI / 技术发布会 |
| 🌿 森林墨 | 自然 / 可持续 / 文化 / 非虚构 |
| 🍂 牛皮纸 | 怀旧 / 人文 / 文学 / 独立杂志 |
| 🌙 沙丘 | 艺术 / 设计 / 创意 / 画廊 |

切换主题只需替换 `template.html` 开头 `:root{}` 里的 6 行变量,其他 CSS 全走 `var(--...)`。

### Style B 瑞士主题

瑞士风从 `references/themes-swiss.md` 里选一套,同样**不允许自定义 hex 值**。

| 主题 | 适合场景 |
|------|---------|
| 克莱因蓝 IKB | 通用默认、商业发布、AI 产品、方法论 |
| 柠檬黄 | 年轻、运动、零售、Y2K 复古 |
| 柠檬绿 | 生态、可持续、Z 世代品牌 |
| 安全橙 | 警示、新闻、活力主题 |

如果用户说"瑞士风 PPT"但没有指定颜色,默认推荐克莱因蓝 IKB。

## 核心设计原则

1. **克制优于炫技** — WebGL 背景只在 hero 页透出
2. **结构优于装饰** — 信息靠字号 + 字体对比 + 网格留白,不用阴影和浮动卡片
3. **图片是第一公民** — 图片要对齐正文内容区,比例稳定,只裁底部,顶部和左右完整
4. **配图只做素材** — 生成图只保留核心照片 / 图表 / UI,不要把 PPT 页脚、标题和角标画进图片里
5. **节奏靠 hero 页** — hero / non-hero 交替,才不累眼睛
6. **低性能可退场** — 按 `B` 能切换到静态模式,动态效果不能成为阅读负担
7. **术语统一** — Skills 就是 Skills,不中英混译
8. **瑞士风必须守版式** — Style B 优先还原原始 22P 版式,不要为了"多样"发明不存在的页面

## 视觉参考

- [*Monocle*](https://monocle.com) 杂志的版式
- YC Garry Tan "Thin Harness, Fat Skills"
- Massimo Vignelli / Helvetica Forever / 瑞士国际主义网格系统
- 歸藏线下分享 PPT 系列

## 贡献

Bug、排版问题、新布局需求——欢迎开 Issue 或 PR。改动请优先:

- 在 `template.html` 里补类,不要让 layouts.md 使用未定义的类
- 在 `template-swiss.html` 里补类时,同步更新 `layouts-swiss.md` 和 `swiss-layout-lock.md`
- 瑞士风新增规则后,同步更新 `scripts/validate-swiss-deck.mjs`
- 把踩过的坑写到 `checklist.md` 对应的 P0 / P1 / P2 / P3 级别
- 新主题色进 `themes.md` 并给出适合的场景

## License

MIT © 2026 [op7418](https://github.com/op7418)

---
name: guizang-ppt-skill
description: 生成横向翻页网页 PPT（单 HTML 文件），含 WebGL 背景、章节幕封、数据大字报、图片网格等模板。提供两种风格：① "电子杂志 × 电子墨水"（衬线 + 流体背景 + 暖色） ② "瑞士国际主义"（无衬线 + 网格点阵 + IKB/柠檬黄/柠檬绿/安全橙高亮）。当用户需要制作分享 / 演讲 / 发布会风格的网页 PPT，或提到"杂志风 PPT"、"瑞士风 PPT"、"Swiss Style"、"horizontal swipe deck"时使用。
---

# Magazine Web Ppt

## 这个 Skill 做什么

生成一份**单文件 HTML**的横向翻页 PPT，提供两种可选的视觉基调：

### 风格 A · 电子杂志 × 电子墨水（默认）

- **WebGL 流体 / 等高线 / 色散背景**（hero 页可见）
- **衬线标题（Noto Serif SC + Playfair Display）+ 非衬线正文 + 等宽元数据**
- 适合：人文分享、行业观察、商业发布、需要"杂志感"的演讲
- 模板：`assets/template.html` · 主题色：`references/themes.md` · 布局：`references/layouts.md`
- 美学锚点：像 *Monocle* 杂志贴上了代码

### 风格 B · 瑞士国际主义（Swiss Style）

- **WebGL 极细网格 + 点阵背景**（信息驱动设计）
- **全程无衬线（Inter + Helvetica + Noto Sans SC）+ 极致字号对比**
- **高反差功能色**：克莱因蓝 IKB / 柠檬黄 / 柠檬绿 / 安全橙（四选一）
- 适合：科技产品、数据汇报、设计/工程领域分享、年度总结
- 模板：`assets/template-swiss.html` · 主题色：`references/themes-swiss.md` · 布局：`references/layouts-swiss.md`
- 美学锚点：像 Massimo Vignelli + Helvetica Forever

**两种风格共享**：横向翻页（键盘 ← →、滚轮、触屏、ESC 索引）、Lucide 图标、Motion One 入场动效（本地 + CDN 双保险）。

## 何时使用

**合适的场景**：
- 线下分享 / 行业内部讲话 / 私享会
- AI 新产品发布 / demo day
- 带有强烈个人风格的演讲
- 需要"一次做完，不用翻页工具"的网页版 slides

**不合适的场景**：
- 大段表格数据、图表叠加（用常规 PPT）
- 培训课件（信息密度不够）
- 需要多人协作编辑（这是静态 HTML）

## 工作流

### Step 1 · 需求澄清(**动手前必做**)

**如果用户已经给了完整的大纲 + 图片**,可以跳过直接进 Step 2。

**如果用户只给了主题或一个模糊想法**,用这 6 个问题逐个对齐后再动手。不要基于猜测就开始写 slide——一旦结构定错,后期翻修代价很高:

#### 运行环境适配

- **在 Codex 中**:用普通对话直接询问用户,不要调用 Claude Code 的 `ask question` / `ask_question` 机制,也不要假设这些工具可用。一次最多问 1-3 个最关键问题;如果信息缺口不影响开工,先做合理假设并在回复里说明。
- **在 Claude Code 中**:可以继续使用原有的 `ask question` 交互方式来逐项澄清。

#### 7 问澄清清单

| # | 问题 | 为什么要问 |
|---|------|-----------|
| 1 | **风格 A 还是 B?**(电子杂志风 / 瑞士国际主义风) | **必须先问**,决定用哪个 template + layouts + themes 文件 |
| 2 | **受众是谁?分享场景?**(行业内部 / 商业发布 / demo day / 私享会) | 决定语言风格和深度 |
| 3 | **分享时长?** | 15 分钟 ≈ 10 页,30 分钟 ≈ 20 页,45 分钟 ≈ 25-30 页 |
| 4 | **有没有原始素材?**(文档 / 数据 / 旧 PPT / 文章链接) | 有素材就基于素材,没有就帮他搭 |
| 5 | **有没有图片?放在哪?** | 详见下方"图片约定" |
| 6 | **想要哪套主题色?** | 杂志风 5 套(`themes.md`) / 瑞士风 4 套(`themes-swiss.md`),挑一 |
| 7 | **有没有硬约束?**(必须包含 XX 数据 / 不能出现 YY) | 避免返工 |

#### 风格选择参考(问题 1)

| 如果用户说... | 推荐风格 |
|---|---|
| "杂志感" / "人文" / "Monocle 风" / 不指定 | **A · 电子杂志风** |
| "瑞士风" / "Swiss Style" / "Helvetica" / "极简" / "网格" / "信息图" / "数据驱动" | **B · 瑞士国际主义风** |
| 内容是 AI 产品 / 技术 / 工程 / 数据汇报 | B 更合适 |
| 内容是行业观察 / 人文 / 故事 / 文化 | A 更合适 |
| 用户给了大量 KPI 数字 / 路线图 / 流程 | B 更合适(`Data Hero` 布局是瑞士风专长) |
| 用户给了大量纪实照片 / 人文图片 | A 更合适(图片网格、左文右图是杂志风专长) |
| 用户需要 GPT-M 2.0 生成截图再设计 / 信息图 / 证据墙 | B 也很合适(P23/P24 是瑞士风图片专用版式) |

#### 大纲协助(如果用户没有大纲)

用"叙事弧"模板搭骨架,再填内容:

```
钩子(Hook)       → 1 页   : 抛一个反差 / 问题 / 硬数据让人停下来
定调(Context)    → 1-2 页 : 说明背景 / 你是谁 / 为什么讲这个
主体(Core)       → 3-5 页 : 核心内容,用 Layout 4/5/6/9/10 穿插
转折(Shift)      → 1 页   : 打破预期 / 提出新观点
收束(Takeaway)   → 1-2 页 : 金句 / 悬念问题 / 行动建议
```

叙事弧 + 页数规划 + 主题节奏表(见 `layouts.md`),**三张表对齐后**再进 Step 2。

大纲建议保存为 `项目记录.md` 或 `大纲-v1.md`,便于后续迭代。

#### 图片约定(告知用户)

在动手前向用户说清:

- **文件夹位置**:`项目/XXX/ppt/images/` 下(和 `index.html` 同级)
- **命名规范**:`{页号}-{语义}.{ext}`,例如 `01-cover.jpg` / `03-figma.jpg` / `05-dashboard.png`
  - 页号补零便于排序
  - 语义用英文,短、具体、和内容对应
- **规格建议**:
  - 单张 ≥ 1600px 宽(避免大屏模糊)
  - JPG 用于照片/截图,PNG 用于透明 UI/图表
  - 总大小控制在 10MB 内(影响翻页流畅度)
- **如何替换**:保持**同名覆盖**最稳(HTML 里不用改路径);如果文件名变了,记得全局搜 `images/旧名` 改成新名
- **没图怎么办**:和用户对齐,可以先用占位色块生成结构,等图片后期补;但要告知 layout 4/5/10 等图文混排页没图就没法验证视觉效果

#### Codex 配图生成(可选)

如果当前运行环境是 **Codex**,完成 deck 初稿后,主动问用户是否需要用 GPT-M 2.0 生成配图并插入 PPT。不要默认生成。

推荐询问方式:

> 要不要为这份 PPT 生成几张配图?可以做成人文纪实照片、杂志风信息图、流程/对比/系统关系图,或把截图再设计成统一的杂志风视觉。

如果用户确认生成,再问他想要哪种图片类型或风格;如果用户没有偏好,根据页面内容自行推荐 1-3 张最值得生成的配图。

生成配图时遵守:

- 提示词保持简短,只框定主题、用途、风格和比例,不要写长篇摄影指导
- 图片风格必须贴合当前 deck 风格:风格 A 用"电子杂志 × 电子墨水";风格 B 用"瑞士国际主义 / Swiss Style"
- 信息图、图表、截图再设计里的文字语言必须跟随用户正在使用的语言;中文 deck 用中文,英文 deck 用英文
- 先看 `references/image-prompts.md` 选择图片类型和基础提示词
- 配图比例必须匹配最终落位:主视觉 16:9,左文右图 16:10 / 4:3,信息图 16:9 / 16:10,截图再设计 16:10,图文混排小图 3:2 / 3:4,网格图统一高度裁切
- 生成后的图片放到 `images/` 下,命名遵守 `{页号}-{语义}.{ext}`

### Step 2 · 拷贝模板

**根据 Step 1 选定的风格,拷贝对应的模板**到目标位置（通常是 `项目/XXX/ppt/index.html`），同时在同级建一个 `images/` 文件夹准备接图片。

```bash
mkdir -p "项目/XXX/ppt/images"

# 风格 A · 电子杂志风
cp "<SKILL_ROOT>/assets/template.html" "项目/XXX/ppt/index.html"

# 或 风格 B · 瑞士国际主义风
cp "<SKILL_ROOT>/assets/template-swiss.html" "项目/XXX/ppt/index.html"
```

两个 `template*.html` 都是**完整可运行**的文件——CSS、WebGL shader、翻页 JS、字体/图标 CDN 全已预设好,只有 `<!-- SLIDES_HERE -->` 占位符等待你填充 slide 内容。

**注意**:风格 A 和 B **不能混用**。layouts.md 里的类（如 `.h-hero` 衬线大标题、`.display-zh` 等）只在 template.html 有定义；layouts-swiss.md 里的类（如 `.kpi-hero`、`.accent-block`、`.span-N`、`.dots` 等）只在 template-swiss.html 有定义。一份 deck 只能选一套。

#### 2.1 · 必改占位符（**容易漏**）

拷贝后立刻改掉以下占位符，否则浏览器 Tab 会显示"[必填] 替换为 PPT 标题"这种尴尬文字：

| 位置 | 原始 | 需改为 |
|------|------|--------|
| `<title>` | `[必填] 替换为 PPT 标题 · Deck Title` | 实际 deck 标题(如 `一种新的工作方式 · Luke Wroblewski`) |

每次拷贝完 template.html 第一件事:grep 一下"[必填]" 确认全部替换完。

#### 2.2 · 选定主题色(5 套预设 · 不允许自定义)

本 skill **只允许从 5 套精心调配的预设里选一套**,不接受用户自定义 hex 值——颜色搭配错了画面瞬间变丑,保护美学比给自由更重要。

| # | 主题 | 适合 |
|---|------|------|
| 1 | 🖋 墨水经典 | 通用 / 商业发布 / 不知道选啥的默认 |
| 2 | 🌊 靛蓝瓷 | 科技 / 研究 / 数据 / 技术发布会 |
| 3 | 🌿 森林墨 | 自然 / 可持续 / 文化 / 非虚构 |
| 4 | 🍂 牛皮纸 | 怀旧 / 人文 / 文学 / 独立杂志 |
| 5 | 🌙 沙丘 | 艺术 / 设计 / 创意 / 画廊 |

**操作**:
1. 基于内容主题推荐一套,或直接问用户选哪一套
2. 打开 `references/themes.md`,找到对应主题的 `:root` 块
3. **整体替换** `assets/template.html`(已拷贝版本)开头 `:root{` 块里标有"主题色"注释的那几行(`--ink` / `--ink-rgb` / `--paper` / `--paper-rgb` / `--paper-tint` / `--ink-tint`)
4. 其他 CSS 都走 `var(--...)`,无需任何其他改动

**硬规则**:
- 一份 deck 只用一套主题,不要中途换色
- 不要接受用户给的任意 hex 值——委婉拒绝并展示 5 套让选
- 不要混搭(例如 ink 取墨水经典、paper 取沙丘)——会彻底违和

### Step 3 · 填充内容

#### 3.0 · 预检:类名必须在模板的 `<style>` 里有定义（**最重要**）

**这是所有生成问题的源头**。layouts 骨架使用了很多类名,如果模板的 `<style>` 里没有对应定义,浏览器会 fallback 到默认样式——大标题字体错、卡片挤成一团、pipeline 糊成一行、图片堆到页面底部。

**两种风格类名互不通用**(再次强调):
- 风格 A 模板里有 `h-hero`(衬线)、`stat-card`、`grid-2-7-5`、`frame` 等
- 风格 B 模板里有 `h-hero`(无衬线)、`kpi-hero`、`accent-block`、`span-N`、`dots`、`grid-12` 等
- 同名 class 在两个模板里**视觉表现完全不同**(例:风格 A 的 `h-hero` 是 Noto Serif SC 衬线,风格 B 的 `h-hero` 是 Inter 无衬线)

**在写任何 slide 代码之前:**

1. **先 Read 当前用的模板**(至少读到 `<style>` 块末尾):
   - 风格 A → `assets/template.html`
   - 风格 B → `assets/template-swiss.html`
2. **对照对应 layouts 文件的 Pre-flight 列表**,确认你要用的每个类都在 `<style>` 里存在
3. 如果某个类缺失:**在模板的 `<style>` 里补上**,不要在每个 slide 里 inline 重写
4. **模板是唯一的类名来源**——不要发明新类名,如需自定义用 `style="..."` inline

**风格 A 常见容易遗漏的类**:
`h-hero` / `h-xl` / `h-sub` / `h-md` / `lead` / `kicker` / `meta-row` / `stat-card` / `stat-label` / `stat-nb` / `stat-unit` / `stat-note` / `pipeline-section` / `pipeline-label` / `pipeline` / `step` / `step-nb` / `step-title` / `step-desc` / `grid-2-7-5` / `grid-2-6-6` / `grid-2-8-4` / `grid-3-3` / `grid-6` / `grid-3` / `grid-4` / `frame` / `frame-img` / `img-cap` / `callout` / `callout-src` / `chrome` / `foot`

**风格 B 常见容易遗漏的类**(2026-05 重构后):
- 画布:`canvas-card` / `chrome-min`
- 排版:`h-hero`(无衬线 7.4vw weight 200) / `h-statement`(9.6vw) / `h-xl` / `h-md` / `t-cat`(SemiBold 600 小标) / `t-meta`(mono uppercase) / `lead` / `num-mega` / `mono`
- 卡片(四类互斥):`card-ink` / `card-accent` / `card-fill` / `card-outlined`
- 网格:`grid-12` / `grid-2-9` / `grid-2-9-5` / `span-N`
- 时间线:`timeline-v` + `tl-node` + `tl-axis` + `dot` / `timeline-h` + `tl-h-node` + `tl-h-axis`
- 图表:`kpi-tower-row` + `bar-tower` / `h-bar-chart` + `bar-row` + `bar-fill` / `spec-bars` + `bar-vert`
- 装饰:`dot-mat`(SVG mask 实心点)/ `ring-mat`(描边圆)/ `cross-mat`(× 网格)/ `hr-hairline`
- 版式专属:`cover-split` / `closing-split` / `duo-compare` + `vrule` / `manifesto-top` + `ink-banner-full` / `three-forces` / `loop-diagram` / `matrix-fill` + `matrix-cell` / `brief-grid` + `brief-card` / `system-diagram` / `why-now-grid` / `four-cards` / `stacked-ledger` + `ledger-row` / `tech-spec` / `image-hero` + `hero-img-wrap` + `hero-overlay-block` + `hero-stats`
- 图片混排:`frame-img` / `fit-contain` / `r-21x9` / `r-16x9` / `r-16x10` / `h-22` / `h-26` / `swiss-img-split` / `swiss-img-grid` / `swiss-img-caption` / `swiss-keyline` / `swiss-lined`
- spacing token:`--sp-3`...`--sp-13`(8/12/16/24/32/40/48/64/80/96/160 px)

#### 3.0.5 · 规划主题节奏（**和类预检同等重要**)

**在挑布局之前**,必须先列出每一页的主题 class(`hero dark` / `hero light` / `light` / `dark`)并写到文档或草稿里对齐。详细规则看 `references/layouts.md` 开头的"主题节奏规划"一节。

**强制规则**:

- 每页 section 必须带 `light` / `dark` / `hero light` / `hero dark` 之一,不要只写 `hero`
- 连续 3 页以上同主题 = 视觉疲劳,不允许
- 8 页以上必须有 ≥1 个 `hero dark` + ≥1 个 `hero light`
- 整个 deck 不能只有 `light` 正文页,必须有 `dark` 正文页制造呼吸
- 每 3-4 页插入 1 个 hero 页(封面/幕封/问题/大引用)

**生成后自检**:`grep 'class="slide' index.html` 列出所有主题,人工确认节奏合理再交付。

#### 3.1 · 挑布局

**不要从零写 slide**。打开对应的 layouts 文件,里面有 10 种现成布局骨架,每种都是完整可粘贴的 `<section>` 代码块。

**风格 A** → `references/layouts.md`:

| Layout | 用途 |
|---|---|
| 1. 开场封面 | 第 1 页 |
| 2. 章节幕封 | 每幕开场 |
| 3. 数据大字报 | 抛硬数据 |
| 4. 左文右图(Quote + Image) | 身份反差 / 故事 |
| 5. 图片网格 | 多图对比 / 截图实证 |
| 6. 两列流水线(Pipeline) | 工作流程 |
| 7. 悬念收束 / 问题页 | 幕末 / 收尾 |
| 8. 大引用页(Big Quote) | 衬线金句 / takeaway |
| 9. 并列对比(Before / After) | 旧模式 vs 新模式 |
| 10. 图文混排(Lead Image + Side Text) | 信息密集的图文页 |

**风格 B** → 先读 `references/swiss-layout-lock.md`,再读 `references/layouts-swiss.md`。

瑞士主题默认进入 **Swiss locked mode**:

- 正文页只能使用原始参考 PPT 登记的 22 个版式 `S01-S22`;新增首页/尾页只能使用 Skill 明确提供的 `SWISS-COVER-ASCII` / `SWISS-CLOSING-ASCII`。
- 每个 `<section class="slide">` 必须写 `data-layout="Sxx"`。没有 `data-layout` 就视为未登记版式。
- 不允许临时发明 `P23/P24`、`Swiss Image Split`、`Evidence Grid` 这类原始 22P 之外的正文结构,除非用户明确要求实验版式。
- 顶部中文标题默认左对齐、处在左上内容轴。不要把小标题放左列、大标题放右列,造成视觉居中;只有原始 statement/split 版式允许强中心叙事。
- SVG 只负责几何图形。不要在 SVG 里写文字标签,所有标签改用 HTML 网格/卡片/caption。

原始 22 个正文版式如下:

| Layout | 用途 |
|---|---|
| S01 Index Cover | 原始索引封面 |
| S02 Vertical Timeline + KPI | 演化对比 / 年代变迁 |
| S03 Split Statement | 核心论点 / 左右分屏 |
| S04 Six Cells | 6 项概念定义 |
| S05 Three Layers | 三层架构 |
| S06 KPI Tower | 4 项数据视觉化高度差 |
| S07 H-Bar Chart | 5-10 项排名比较 |
| S08 Duo Compare | Before/After 对照 |
| S09 Dot Matrix Statement | 大引述 / statement |
| S10 Split Closing | 收束页 |
| S11 Horizontal Timeline | 4-7 步流程 |
| S12 Manifesto + Ink Banner | 阶段性结论 |
| S13 Three Forces | 3 个对等概念深化 |
| S14 Loop Form | 自学闭环 / 自动化 |
| S15 Matrix + Hero Stat | 8-12 项矩阵 + 总数据 |
| S16 Multi-card Brief | 6 项快讯小卡 |
| S17 System Diagram | 三层架构 / 生态地图 |
| S18 Why Now | 三论点 + 数据支撑 |
| S19 Four Cards | 4 项等权特性 |
| S20 Stacked KPI Ledger | 纵向账单数据 |
| S21 Tech Spec Sheet | 产品规格 / benchmark |
| S22 Image Hero | 21:9 顶图 + 标题块 + 三列 KPI |

选对应 layout,粘过去,改文案和图片路径即可。**务必先完成 3.0 预检**。

**风格 B 版式多样性硬规则**:
- 7-8 页 deck 至少使用 **6 个不同 S 编号版式**;10 页以上至少使用 8 个不同版式。
- 如果用户说"测试模板 / 看看效果 / 多一点版式",必须覆盖:一个封面、一个收尾、至少 1 个对比或时间线(S08/S11/S02)、至少 1 个结构图(S14/S17/S15)、至少 1 个图片版式(S22 或 S15/S16 图片格改造)。
- 不允许连续 3 页使用同一种主体结构,例如连续三页 `head + grid + card`。
- 图片页不能偷懒发明新结构。2-3 张图时,用 S15/S16 的原始网格骨架改造成图片格;单张大图用 S22。
- 开写 HTML 前先列一张 `页码 → data-layout → 选用理由 → 图片槽位` 草稿;交付前运行 `node <SKILL_ROOT>/scripts/validate-swiss-deck.mjs index.html`。

#### 3.2 · 图片比例规范

永远用**标准比例**,不要用原图奇葩比例(如 `2592/1798`):

| 场景 | 推荐比例 |
|------|---------|
| S22 顶部主图 | **21:9**;照片关键主体放中央安全区 |
| S15/S16 多图格 | 统一 21:9 或统一 16:10,不能混用 |
| 左文右图 主图(风格 A) | 16:10 或 4:3 + `max-height:56vh` |
| 图片网格(风格 A) | **固定 `height:26vh`**,不用 aspect-ratio |
| 左小图 + 右文字 | 1:1 或 3:2 |
| 全屏主视觉 | 16:9 + `max-height:64vh` |
| 图文混排小插图 | 3:2 或 3:4 |

**默认不要让图片 `align-self:end`**——会滑到页面底部,很容易碰到分页组件。用 grid 容器 + `align-items:start`(template 已预设)让图片贴顶即可;只有风格 B 的 P23 可以用 `.swiss-img-split.align-image-bottom`,因为模板已经给它内置了 `--nav-safe-bottom` 安全区。

**风格 B 瑞士风额外规则**:
- 单张大图用 S22;多图测试用 S15/S16 的原始卡片网格改造,不要用未登记的 P23/P24
- 生成图片前先写 `data-image-slot`:例如 `s22-hero-21x9` / `s15-grid-21x9` / `s16-brief-21x9`
- S22 配图默认生成 21:9,提示词必须包含 `subject centered in the safe middle area`;照片容器用 `object-position:center 35%`,不要用 `top center`
- 图片容器必须直角、无阴影、无圆角;默认背景用白色 `var(--paper)`,不要用灰底包白底信息图
- 白底 GPT 信息图/流程图/UI 图默认不要加外框描边,不要随手套 `.swiss-keyline`;需要强调时只用 `.swiss-lined` 的顶部 accent 线
- UI/信息图如果是用户原始截图或文字密集图,才用 `.fit-contain`;如果已按 S15/S16 槽位重生成,必须用 `.frame-img.r-21x9` / `.frame-img.r-16x10` 铺满容器,不要固定 `height:18vh` 后把图缩小
- 多图同组必须统一图片槽位、比例和高度,不能混用
- GPT-M 2.0 生成图使用 `image-prompts.md` 的"风格 B:瑞士国际主义配图规则"
- 任何图片、caption、timeline label、footnote 的最低处都不能进入底部分页区域;需要贴底时用 `.nav-safe-bottom` / `.nav-safe-bottom-tight`,不要手写 `bottom:2vh`

#### 3.2.1 · 中文大标题字号分档(风格 B 必做)

中文方块字视觉面积大,不能直接套英文 hero 的 6.8-7vw。写中文大标题前先分档:

| 标题形态 | 推荐字号 |
|---|---|
| 1 行,≤ 8 个中文字符 | `min(6.4vw,11.2vh)` |
| 2 行,每行≤ 8 个中文字符 | `min(5.8vw,10.2vh)` |
| 2 行,任一行 9-12 个中文字符 | `min(5.2vw,9.2vh)` |
| 3 行或更长 | 优先改写标题;不得已用 `min(4.6vw,8.2vh)` |

如果标题挤占了图片或正文区域,先压缩标题文案,再降字号;不要靠把下方内容推到底来硬塞。

组件细节(字体、颜色、网格、图标、callout、stat-card 等)在 `references/components.md`。

### Step 4 · 对照检查清单自检

生成完一定要打开 `references/checklist.md`，逐项对照。里面总结了**真实迭代过程中踩过的所有坑**，P0 级别的问题（emoji、图片撑破、标题换行、字体分工）必须全部通过。

#### 4.0 · 不只看代码:必须打开网页做视觉核对

代码只能证明类名和结构存在,不能证明版式舒服。生成后必须打开网页逐页看:

1. 同时打开原始参考 PPT、当前模板或生成页、测试 PPT;原始参考是 `/Users/guohao/Documents/op7418的仓库/项目/Thin-Harness-Fat-Skills/ppt/index.html`。
2. 截图前等入场动效稳定(约 1-2 秒),不要把动画中间态当成版式问题。
3. 先看视觉:大标题字重、标题与内容间距、图片是否与正文对齐、图片/说明是否碰到底部分页组件。
4. 再看代码:确认该页选用的版式与内容形状匹配,没有把数据专用版式拿来讲概念,也没有把可选组件堆成装饰。
5. 对照原始参考模板时,以实际页面用法为准,不要只看 CSS helper 定义;原始页面的大字实际多为 200/300,不要被 raw CSS 里的 700/800/900 带偏。
6. 如果页面别扭,先判断是版式选错、必选组件缺失、可选组件滥用,还是间距/安全区问题;不要直接靠加 margin 硬救。

#### 风格 A · 电子杂志风必查

1. **大标题必须是衬线字体**——如果显示成非衬线,99% 是 Step 3.0 预检没做,`h-hero` 类在 template.html 里缺失
2. **图片网格里只用 `height:Nvh`,不用 `aspect-ratio`**(会撑破)
3. **图片不能堆到页面底部**——不要用 `align-self:end`,用 grid + `align-items:start`(见 Step 3.2)
4. **图片只能用标准比例**(16:10 / 4:3 / 3:2 / 1:1 / 16:9),不要复制原图的奇葩比例
5. **中文大标题 ≤ 5 字且 `nowrap`**(避免 1 字 1 行)
6. **用 Lucide,不用 emoji**
7. **标题用衬线,正文用非衬线,元数据用等宽**

#### 风格 B · 瑞士国际主义必查

1. **全程无衬线**——任何衬线字体出现都是错的(检查 `font-family` 没用 `--serif` 类变量)
2. **只有一个 accent 色**——一份 deck 不能同时出现 IKB 蓝 + 柠檬黄 + 安全橙等多个高亮色
3. **不允许渐变 / 阴影 / 圆角**——所有色块直角纯色,任何 `box-shadow` / `linear-gradient` / `border-radius` > 0 都要砍掉(rule 横线除外)
4. **极致字号对比**——主标题与正文比例 ≥ 8:1
5. **大字号必须双约束限高**——`font-size:min(Xvw, Yvh)`,只用 vw 在标准 16:9 屏会溢出(吸取 P15/P20/P22 教训)
6. **大字字重 200**(ExtraLight)——字号越大越细,瑞士风灵魂;**禁止** 600/700/800 大字
7. **卡片填充类型互斥**——`card-ink` / `card-accent` / `card-fill` / `card-outlined` 四类**不能混用**(禁止"蓝底+蓝描边"、"灰底+描边"等)
8. **多卡并列时统一样式**——3-12 张卡用同一类(优先 `card-fill` 灰底);只突出一项时单独换 `card-accent`,且**只允许一张**
9. **直角到底**——任何 `border-radius` 都不允许;装饰用 8×8 直角小方块,**不要** 9px 圆形点
10. **图标用 lucide,不自己画 SVG**——`<i data-lucide="name"></i>` + `lucide.createIcons()`,选棱角风格(避免圆胖)
11. **时间线对齐**——axis 列固定 12px + dot 绝对定位,**不要**用 grid `justify-self`(会与虚线错位)
12. **章节级标题与内容间距 ≥ 9vh**——避免拥挤(吸取 P15/P16 教训)
13. **每页一个语义化动效 recipe**——不是统一 fade-up,数字 scale 弹入、bar scaleY 拉起、SVG stroke 描线、节点序列点亮等;**禁止**所有页用同一个 generic 配方
14. **playSlide 入口 reveal 容器**——`[data-anim]` 容器先强制 opacity:1,recipe 内再用 motion `{opacity:[0,1]}` 覆盖,否则有些页会"看不见"
15. **ESC 索引页可见性**——cloned slide 必须有 CSS override 让 `[data-anim]` 在缩略图里 opacity:1
16. **Helvetica/Inter 兜底中文字体**——Windows 用户没有"苹方",必须 fallback 到 `"Microsoft YaHei UI", "Noto Sans SC"`
17. **字体粗细体例**:大字 200 / 正文 300 / `t-cat` SemiBold 600 / `t-meta` mono uppercase
18. **保留低功耗快捷键**——右下角必须提示 `B 静态`;按 `B` 切换 `body.low-power`,停止 WebGL/ASCII canvas RAF 和 Motion 入场动画
19. **装饰元素严格在 grid 内**——bars 矩阵、点阵、ring-mat 不能贴边或溢出页面
20. **底部内容预留 nav 空间**——nav 在 ~97vh,内容收尾不要过 93vh(吸取 P22 KPI 大字溢底教训)
21. **图片容器直角无阴影**——`.frame-img` 不加 `border-radius` / `box-shadow`;边界只用 hairline
22. **P23/P24 图片同组一致**——同一组图片统一比例、高度、边距、线条粗细;信息图/UI 图加 `.fit-contain`
23. **组件角色要正确**——P23/P24 的 caption 是必选信息锚点;P22 的 KPI/说明是必选;数据专用版式必须有真实数据,不能靠文案硬填
24. **通用/非通用版式要分清**——P3/P8/P11/P19/P23 较通用;P6/P7/P20/P21/P22 是数据/案例专用;P14/P15/P17 是结构专用

### Step 5 · 本地预览

直接在浏览器打开 `index.html` 就行。macOS 下：

```bash
open "项目/XXX/ppt/index.html"
```

不需要本地服务器。图片走相对路径 `images/xxx.png`。

### Step 6 · 迭代

根据用户反馈修改——模板的 CSS 已经高度参数化，90% 的调整都是改 inline style（字号 `font-size:Xvw` / 高度 `height:Yvh` / 间距 `gap:Zvh`）。

---

## 资源文件导览

```
guizang-ppt-skill/
├── SKILL.md                  ← 你正在读
├── assets/
│   ├── template.html         ← 风格 A · 电子杂志风模板（种子文件）
│   ├── template-swiss.html   ← 风格 B · 瑞士国际主义风模板（种子文件）
│   └── motion.min.js         ← Motion One 本地副本（离线兜底,约 64KB,共用）
├── scripts/
│   └── validate-swiss-deck.mjs ← 风格 B 静态校验:登记版式、图片槽位、SVG 文本、标题对齐
└── references/
    ├── components.md         ← 组件手册（字体、色、网格、图标、callout、stat、pipeline、动效... 风格 A 适用）
    ├── layouts.md            ← 风格 A · 10 种页面布局骨架（可直接粘贴,含动效标记）
    ├── swiss-layout-lock.md  ← 风格 B · 原始 22P 版式锁,正文页必须按这里登记
    ├── layouts-swiss.md      ← 风格 B · 原始 22P 骨架说明 + 少量明确标注的实验区
    ├── themes.md             ← 风格 A · 5 套主题色预设（只能选不能自定义）
    ├── themes-swiss.md       ← 风格 B · 4 套瑞士风主题色预设（IKB / 柠檬黄 / 柠檬绿 / 安全橙）
    ├── image-prompts.md      ← GPT-M 2.0 配图类型、比例和基础提示词
    └── checklist.md          ← 质量检查清单（P0/P1/P2/P3 分级）
```

**加载顺序建议**：
1. 先读完 `SKILL.md`(这个文件)了解整体
2. Step 1 需求澄清**第一问**先确定风格 A 还是 B,然后:
   - 风格 A:读 `themes.md` 帮用户选一套主题色
   - 风格 B:读 `themes-swiss.md` 帮用户选一套主题色
3. **动手前 Read 对应模板的 `<style>` 块**——这是类名的唯一来源,缺类会导致整页样式崩
   - 风格 A → `assets/template.html`
   - 风格 B → `assets/template-swiss.html`
4. 读对应的 layouts 文件挑布局:
   - 风格 A → `layouts.md`(顶部有 Pre-flight 类名清单、主题节奏规划、动效 recipe 决策树)
   - 风格 B → **先读 `swiss-layout-lock.md`**,再读 `layouts-swiss.md`;正文页必须从 S01-S22 选择,每页写 `data-layout`
5. 如果在 Codex 中生成配图,读 `image-prompts.md` 挑图片类型、比例和基础提示词
6. 细节调整时读 `components.md` 查组件(含 Motion 动效系统章节,主要服务风格 A;风格 B 的组件细节在 `layouts-swiss.md` 附录)
7. 生成后先运行 `node scripts/validate-swiss-deck.mjs path/to/index.html`,再读 `checklist.md` 自检

**动效相关**:模板已把 Motion One 的加载和 recipe 逻辑内嵌到底部 module script。你不需要改 JS,只需要按 `layouts.md` / `layouts-swiss.md` 的骨架在 HTML 里加 `data-anim` / `data-animate` 即可。离线演示靠 `assets/motion.min.js`,断网时自动降级为"无动画但内容可读"。风格 B 模板必须保留 `B` 键低功耗模式:切换后停止 WebGL/ASCII canvas RAF,取消正在运行的 Web Animations,并把当前页内容直接 reveal 到静态最终态。

## 核心设计原则（哲学）

### 风格 A · 电子杂志风（5 轮迭代总结）

> 违反其中任何一条，杂志感都会垮。

1. **克制优于炫技** — WebGL 背景只在 hero 页透出，普通页几乎看不见
2. **结构优于装饰** — 不用阴影、不用浮动卡片、不用 padding box，一切信息靠**大字号 + 字体对比 + 网格留白**
3. **内容层级由字号和字体共同定义** — 最大衬线 = 主标题，中衬线 = 副标，大非衬线 = lead，小非衬线 = body，等宽 = 元数据
4. **图片是第一公民** — 图片只裁底部，保证顶部和左右完整；网格用 `height:Nvh` 固定，不要用 `aspect-ratio` 撑
5. **节奏靠 hero 页** — hero 和 non-hero 交替，才不累眼睛
6. **术语统一** — Skills 就是 Skills，不要中英混合翻译

### 风格 B · 瑞士国际主义风

> 违反其中任何一条，画面瞬间从瑞士掉到 PowerPoint。

1. **单一锚点色** — 一份 deck 只用一个 accent，不允许多色高亮拼贴
2. **极致字号对比** — 主标题与正文比例 ≥ 8:1,KPI 必须是"Data Hero"(屏幕宽度的 18-22%)
3. **无衬线只此一家** — Inter / Helvetica / Noto Sans SC,任何衬线都是错的
4. **直角纯色** — 不允许渐变 / 阴影 / 圆角(rule 横线除外)
5. **网格至上** — 所有元素吸附到 12-col grid,左对齐 + 大幅留白做非对称美学
6. **Hairline 是手术刀** — 1px 的极细分割线就够,不要加粗、不要加阴影
7. **点阵装饰只在 hero 页透出** — 正文页保持纯净底色

## 参考作品

本 skill 的两种风格分别参考了：

**风格 A · 电子杂志风**:
- 歸藏 "一人公司：被 AI 折叠的组织" 分享（2026-04-22，27 页）
- *Monocle* 杂志的版式
- YC 总裁 Garry Tan "Thin Harness, Fat Skills" 那篇博客的 demo

**风格 B · 瑞士国际主义风**:
- Massimo Vignelli 的 NYC Subway / Unimark 系统
- *Helvetica Forever* 的字体设计语言
- Josef Müller-Brockmann 的网格系统经典著作
- 当代设计:Acne Studios / Off-White / IKEA / Beck Design

可以把它们当做风格锚点。

# 质量检查清单（Checklist）

这个清单来自"一人公司"分享 PPT 的真实迭代过程。每一条都是踩过坑之后总结的，按重要性排序。

生成 PPT 前，先通读一遍；生成后，逐项自检。

---

## 🔴 P0 · 一定不能犯的错

### 0-S. Swiss locked mode:正文页必须来自原始 22P

**现象**:颜色、字体看起来像 Swiss,但标题跑到中间、图片不在网格上、页面结构和原始 22P 完全不是一套东西。

**根因**:生成时把 Swiss 当成风格包,自由组合了新的 P23/P24/自绘 SVG 页面,没有从原始参考 PPT 的 22 个登记版式里选。

**做法**:
- 先读 `references/swiss-layout-lock.md`
- 正文页只能使用 `S01-S22`;新增首页/尾页只能使用 `SWISS-COVER-ASCII` / `SWISS-CLOSING-ASCII`
- 每个 `<section class="slide">` 必须写 `data-layout="Sxx"`
- 生成后必须运行:

```bash
node <SKILL_ROOT>/scripts/validate-swiss-deck.mjs path/to/index.html
```

**校验会拦截**:
- 未登记版式 / 缺少 `data-layout`
- P23/P24 实验结构
- SVG 里写可见文字
- S22 图片未绑定 `s22-hero-21x9`
- S22 照片使用 `object-position:top center`

### 0-S-2. Swiss 顶部标题默认左上,不是居中

**现象**:最顶上的中文标题在页面中间,像一页自制海报,不再像原始 PPT。

**做法**:
- 除 `S03/S09/S10` 这类 statement/split 版式外,顶部标题必须贴原始模板的左上内容轴。
- 不要把小标题放左列、大标题放右侧大列,这会导致标题视觉居中。
- 如果需要标题 + 说明两列,必须复制原始 `S11` 或 `S17` 的骨架,不要自写 `4fr 8fr`。

### 0-A. 瑞士风画布对齐法则(每一页必查 · 最常踩)

**现象**:页眉 chrome-min 和底部 footer 都靠在 5vw 的边线上,但中间区域往内缩了一截,左右对不齐。

**根因**:`.canvas-card` 已经自带 `padding:5.6vh 5vw 4.4vh`。如果在主体区再写 `padding:5vh 5vw 4vh`,水平方向就变成 `5vw + 5vw = 10vw`,主体比 chrome-min 多内缩 5vw。

**做法**:
- 主体那层 `padding:0`,只用 grid `gap` 控垂直间距
- chrome-min 与主体之间的间距由 `.chrome-min{margin-bottom:48px}` 提供,**不要**在主体顶部叠 `margin-top` / `padding-top`
- split 模式例外:`.slide.split .canvas-card{padding:0}`,两个 `.half` 自己定 `padding:5.6vh 3.6vw 4.4vh`

```html
<!-- ❌ 错:主体多缩了 5vw,左右对不齐 -->
<div class="canvas-card">
  <div class="chrome-min">...</div>
  <div style="flex:1;padding:5vh 5vw 4vh;...">主体</div>
</div>
<!-- ✅ 对 -->
<div class="canvas-card">
  <div class="chrome-min">...</div>
  <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr auto;gap:3vh">主体</div>
</div>
```

**自检命令**:`grep "padding:.*5vw" index.html`,如果命中 `padding:Xvh 5vw Yvh` 在 canvas-card 直系子元素里,就是错的(.half / 装饰层除外)。

### 0-B. 瑞士风 head 区:kicker 必须在大标题"上方"(不要左右排)

**现象**:小标题(`.t-meta` / `.t-cat`)和大标题被挤在同一行,左侧一坨小字、右侧一坨大字,头部失去层级。

**根因**:`grid-template-columns:auto 1fr` 把两个本该上下叠的元素压成左右两列。

**做法**:
```html
<!-- ❌ 错 -->
<div data-anim="head" style="display:grid;grid-template-columns:auto 1fr;gap:3vw;align-items:end">
  <div class="t-meta">METHODOLOGY · 03</div>
  <h2 class="h-xl-zh">为什么是 N+1</h2>
</div>
<!-- ✅ 对 -->
<div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
  <div class="t-meta">METHODOLOGY · 03</div>
  <h2 class="h-xl-zh">为什么是 N+1</h2>
</div>
```

例外:head 一行同时承载"左:kicker+大标题(自己上下叠)"和"右:小注脚",外层可以用 `display:grid;grid-template-columns:1fr auto`,但**内层**仍要保持 flex column。

### 0-B-2. 瑞士风封面 / 封底默认:IKB 满屏 + ASCII 呼吸场 + 白色 weight 200(强制)

**现象**:封面用 `slide light` 白底 + 黑字 + 一个大大的"01"——同时 chrome 角标已经写了 `01 / 07`,屏幕上出现两个"01",视觉重复;白底太普通,完全没有"开场打招呼"的仪式感。

**根因**:layouts-swiss.md 旧版默认推荐左 ink + 右 paper 对开,实操中容易写成"白底 + 黑大字 + 编号大字",失去 IKB 这个标志色的开场冲击。

**做法**(瑞士风必守):
- **封面强制 `<section class="slide accent">`**(满屏 IKB),不要 `slide.light`,也不要 `slide.dark`;在 `.canvas-card` 内**第一个子元素**插入 `<canvas class="ascii-bg">`(ASCII 字符呼吸场,模板自带 IIFE 自动激活)
- **不要再写"01"等编号大字**:`.chrome-min` 已经显示 `01 / N`,封面再放一个巨大的"01"=同义重复,直接删掉
- **强调字必须用斜体**:`font-style:italic;font-weight:300`,**禁止**用 `color:var(--accent)`——IKB 蓝压 IKB 蓝,人眼看不见任何强调
- **封底强制 `slide.split`** 双半屏,左半 `.half.b-accent` + ASCII canvas(与封面色彩闭环),右半 paper 白底放 3 条 takeaway;**第 03 条**用 `var(--accent)` 上色,完成"开场全 IKB ↔ 收尾半 IKB"的色彩闭环
- ASCII canvas 在模板的 `<style>` 里已经预设 `mix-blend-mode:screen;opacity:.92`,不要去动这个值
- 封面/封底主标题字号双约束:`min(11.6vw,19vh)` ~ `min(8vw,14vh)`(遵守 Y ≥ X × 1.6 规则)

**自检命令**:
- `grep -c "ascii-bg" index.html`——封面 + 封底应至少命中 ≥ 2(各一个 canvas)
- `grep -E '"slide accent"' index.html | head -1`——封面应是 `slide accent` 而非 `slide light`
- `grep "color:var(--accent)" index.html`——若命中行同时含 `font-style:italic` 即危险信号(蓝压蓝),改为只 italic 不 accent;只有封底"03 takeaway"那一处用 `var(--accent)` 是合法的(此时背景是白色)
- 目视:打开页面看封面有没有"01"等大编号——有就删

### 0-C. 瑞士风大字号双约束:`min(Xvw, Yvh)` 中 Y ≥ X × 1.6

**现象**:在 16:9 标准屏(MacBook 13/14/16,常见显示器)打开,标题字号比预期小一截,整页内容显得空旷或缩水。

**根因**:1vw : 1vh ≈ 1.78,如果写 `min(7vw, 10vh)`,在 16:9 屏 7vw = 12.46vh,会被 10vh 上限截断到 10vh,字号缩水 20%。

**做法**:推荐数值速查
| 用途 | 推荐 |
|---|---|
| h-hero 巨字宣言 | `min(11.6vw, 19vh)` |
| h-xl 章节标题 | `min(7vw, 12vh)` ~ `min(7.4vw, 13vh)` |
| 大数字 KPI | `min(8.4vw, 14vh)` |
| 中数字 / 编号 | `min(4.6vw, 8.5vh)` ~ `min(5.6vw, 10vh)` |
| 副标 | `min(7.6vw, 13vh)` |

**自检命令**:`grep -E "font-size:min\([0-9.]+vw,\s*[0-9.]+vh\)" index.html`,把所有命中的 X/Y 看一眼,任何 Y/X < 1.6 都改大。

### 0-D. 瑞士风图片混排:直角、同高、只做证据

**现象**:图片像普通 PPT 插图,圆角、阴影、比例混乱;多张截图高度不一,或 GPT-M 2.0 生成图自带标题/页脚,和页面 chrome 重复。

**根因**:瑞士风的图片不是装饰,而是 grid 里的证据块。没有先选原始版式和图片槽位,就会把任意图片硬塞进页面。

**做法**:
- 先选版式:单张大图 + KPI 用 `S22`;多图用 `S15/S16` 的原始网格骨架改造
- S22 生成图比例固定 `21:9`,并在 `<img>` 上写 `data-image-slot="s22-hero-21x9"`
- 照片默认 `object-position:center 35%` 或 `center center`,不要用 `top center` 截人脸
- 图片容器只用 `.frame-img`;**不要** `border-radius` / `box-shadow`
- UI / 信息图 / 流程图若是用户原始截图或文字密集图,使用 `.fit-contain`;若已按槽位重生成,必须用对应比例类铺满容器,例如 `.frame-img.r-21x9`,不能再用固定短高度把图片缩小
- 多图同组必须统一槽位、比例、高度,不要混用
- GPT-M 2.0 提示词必须写明:Swiss Style、单一 accent、直角、无渐变/阴影/圆角、无页眉页脚标题角标

**自检命令**:
- `grep -E "frame-img.*border-radius|box-shadow" index.html`——命中就删
- `grep -n "data-image-slot" index.html`——每张本地图片都应有槽位声明
- 目视:图片内部如果自带大标题、页码、页脚、角标,优先重生成,不要在页面里再裁切硬救

### 0-D-2. 瑞士风底部分页安全区:最低处不要碰 nav

**现象**:图片 caption、脚注、timeline 下方 label、底部 KPI 被分页小方块挡住,或者视觉上贴得太近。

**根因**:`#nav` 固定在 `bottom:2vh`,如果主体内容用 `align-self:end` / `align-items:end` / `margin-top:auto` 贴到底,最低处会进入分页区域。

**做法**:
- 主内容最低边缘与分页组件之间至少留 `3vh` 呼吸空间
- P23 需要底部对齐时用 `.swiss-img-split.align-image-bottom`,模板已内置 `--nav-safe-bottom:8vh`
- 其他页面需要贴底时,给主体容器加 `.nav-safe-bottom` 或 `.nav-safe-bottom-tight`
- 不要手写 `bottom:2vh` / `bottom:0` 放说明文字;这会和 nav 抢位置

**自检**:
- 视觉:翻到该页,看最后一行 caption/label 是否明显高于分页组件
- 代码:`grep -E "align-items:end|align-self:end|bottom:0|bottom:2vh|margin-top:auto" index.html`,命中后逐个确认是否有 nav safe zone

---

### 0-E. Swiss 模板还原度守卫:原始 PPT 是 golden source

**现象**:生成页看起来像瑞士风,但和原始参考 PPT 的实际字重、间距、时间线、卡片密度不一致;越迭代越偏离参考。

**根因**:把新增图片版式或实验结构写成了全局样式修改,或无意改动了原始基座类,例如 `.h-hero` / `.h-xl` 字重、`.tl-node` 列宽、`.duo-compare` 间距。

**做法**:
- 原始参考文件 `/Users/guohao/Documents/op7418的仓库/项目/Thin-Harness-Fat-Skills/ppt/index.html` 是 Swiss 主题的 golden source,但要以**实际页面用法**为准,不要只看未使用的 CSS helper
- 原始页面的大标题大量使用 `font-weight:200`,强调词/数字用 `300`;`.h-hero` / `.h-xl` / `.h-hero-zh` / `.h-xl-zh` 在本模板里必须保持轻字重,不要恢复成 800/900
- 除新增封面/封底 ASCII 机制、S22 图片槽位修复、横向时间线 label 居中修复、以及把标题 helper 校正为实际轻字重外,不要改动原始基座 CSS/JS recipe
- 新增图片能力必须绑定到 S22/S15/S16 原始槽位,不要发明新正文结构
- 如果要修改 `assets/template-swiss.html`,先做原始参考对比;可接受差异只应是 ASCII 类、S22 图片定位类、轻字重标题 helper 和已知动效修复

**自检命令**:
- 运行本次测试目录里的 `compare-swiss-base.mjs`,确认输出里 `missing in template: 0`
- 目视对比原始 PPT 的同类页面:大标题字重、chrome-min 位置、timeline dot/label、卡片密度必须一致

### 0-F. 视觉 + 代码双核对:不要只看 HTML

**现象**:代码看起来类名正确,但实际页面拥挤、图文关系不对、可选组件堆太多,或者用了不适合内容的版式。

**做法**:
- 同时打开原始参考 PPT、当前模板或生成页、测试 PPT,先做视觉并排判断
- 等入场动效稳定后再截图或下判断,不要把动画中间态当成内容缺失
- 先打开网页逐页看视觉:标题字重、头部间距、正文密度、图片对齐、nav 安全区
- 再回代码看结构:该页是否用了正确版式,必选组件是否齐,可选组件是否过度
- 对照原始 PPT 时以实际画面为准;raw CSS helper 只能辅助,不能替代视觉判断
- 判断问题来源:版式选错 / 必选组件缺失 / 可选组件滥用 / 间距和安全区问题
- 通用版式(S03/S08/S11/S19)可多用;数据专用(S06/S07/S20/S21/S22)必须有真实数据或案例;结构专用(S14/S15/S17)必须有闭环、矩阵或层级关系
---

### 0. 生成前必须通过的类名校验(最重要)

**现象**：直接把 layouts.md 的骨架粘到新 HTML,结果样式全部丢失——大标题变成非衬线、数据大字报字体小得像正文、pipeline 多页糊成一坨、图片堆到浏览器底部。

**根因**：如果当前模板的 `<style>` 里没有这些类的定义,浏览器就 fallback 到默认样式。

**做法**：
- **生成 PPT 前,必须先 `Read` 当前风格对应模板**:风格 A 读 `assets/template.html`,风格 B 读 `assets/template-swiss.html`,确认 layouts 里用到的类都已定义
- 最常见遗漏的类:`h-hero / h-xl / h-sub / h-md / lead / meta-row / stat-card / stat-label / stat-nb / stat-unit / stat-note / pipeline-section / pipeline-label / pipeline / step / step-nb / step-title / step-desc / grid-2-7-5 / grid-2-6-6 / grid-2-8-4 / grid-3-3 / frame / img-cap / callout-src`
- 如果某个类确实缺了,**在模板的 `<style>` 里补上**,不要在每页 inline 重写
- 生成后打开浏览器,如果看到"大标题是非衬线"或"pipeline 步骤挤在一行",几乎 100% 是这个问题

### 1. 不要用 emoji 作图标

**现象**：在中式杂志风格里用 emoji（🎯 💡 ✅）会立刻破坏格调。

**做法**：用 Lucide 图标库，CDN 方式引用：

```html
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
...
<i data-lucide="target" class="ico-md"></i>
...
<script>lucide.createIcons();</script>
```

常用图标名：`target / palette / search-check / compass / share-2 / crown / check-circle / x-circle / plus / arrow-right / grid-2x2 / network`

### 2. 图片只允许裁底部，左右和顶部绝对不能切

**现象**：用 `aspect-ratio` 撑图，网格会在父容器不足时堆叠或切掉图片关键信息（比如截图上部的标题栏）。

**做法**：图片容器用**固定 height + overflow hidden**，图片走 `object-fit:cover + object-position:top`：

```html
<figure class="frame-img" style="height:26vh">
  <img src="screenshot.png">
</figure>
```

CSS 里 `.frame-img img` 已经预设 `object-position:top`，只裁底。

**绝不用这种写法**（会在网格中撑破容器）：

```html
<!-- 坏例 -->
<figure class="frame-img" style="aspect-ratio: 16/9">...</figure>
```

**例外**：单张主视觉（非网格内）可以用 `aspect-ratio + max-height`，因为父容器会兜底。

### 2b. 亮页面配暗 WebGL = 灰蒙蒙(主题切换没生效)

**现象**:所有 light 页面背景都像蒙了一层灰,甚至 hero light 也灰。

**根因**:JS 根据 slide 的主题切换两张 canvas 的 opacity。如果整个 deck 开场是 hero dark,而没有任何机制能把 bg 切到 light,body 永远不加 `light-bg` 类,`canvas#bg-dark` 一直在上面。

**做法**:
- 模板里 `go()` 函数已改为从 `classList` 推断主题(`light` / `dark`),所以 **slide 必须明确带 `light` 或 `dark` 类**。不要漏写,更不要用其他自定义主题名
- hero 页用 `hero light` / `hero dark`,正文页用 `light` / `dark`。只写 `hero` 不带主题色是坏的
- 一个 deck 里必须至少有一个 **非 hero 的 light 页**,确保 body 有机会加 `light-bg`

### 2b-2. 整个 deck 全是 light,没有节奏

**现象**:除封面 `hero dark` 外,其余所有页面默认写 `light`——视觉平淡,没有呼吸感,白花花一片。

**根因**:layouts.md 的骨架默认全写 `light`,如果只是粘贴骨架不调整主题,就会全亮。

**做法**:
- **生成前画"主题节奏表"**:每一页写清 `hero dark` / `hero light` / `light` / `dark` 中的哪一个,对齐后再写代码
- **硬规则**:连续 3 页以上同主题 = 不允许;8 页以上必须有 ≥1 `hero dark` + ≥1 `hero light`;不能全是 `light` 正文页——必须有 `dark` 正文页
- **按布局选主题**(详见 layouts.md 开头"主题节奏规划"):
  - 左文右图(Layout 4)、大引用(Layout 8)、图文混排(Layout 10)→ **`light` / `dark` 交替**
  - 大字报、图片网格、Pipeline、对比页 → `light`(截图/数字/流程需要亮底)
  - 封面、问题页 → `hero dark`
  - 章节幕封 → `hero dark` 与 `hero light` 交替
- **生成后自检**:`grep 'class="slide' index.html`,目视确认节奏有交错

### 2c. chrome 和 kicker 不要写同一句话

**现象**:左上角 `.chrome` 写"Design First · 设计先行",同一页里 `.kicker` 又写"Phase 01 · 设计阶段"——同义翻译,AI 味浓。

**做法**:
- **chrome = 杂志页眉 / 导航标签**:跨多页可相同(如 "Act II · Workflow"、"Data · Result"、"lukew.com · 2026.04")
- **kicker = 本页独一份的引导句**:短、有钩子、是大标题的"小前缀"(如 "BUT"、"一个人,做了什么。"、"The Question")
- 一个描述栏目,一个描述这一页——绝不互相翻译

### 3. 大标题字号不能超过屏宽 / 单字数

**现象**：中文大标题字号设太大（比如 13vw），结果每行只容 1 个字，强制换行非常难看。

**做法**：
- `h-hero`（最大）：10vw，**且标题长度 ≤ 5 字**
- `h-xl`（次大）：6vw-7vw
- 长标题用 `<br>` 手工断行，不要依赖自动换行
- 必要时加 `white-space:nowrap`

**示例**：`我不是程序员。`（6 字）用 `h-xl` 7.2vw + nowrap，一行排完。

### 4. 字体分工：标题衬线、正文非衬线

**做法**：
- 大标题、重点 quote、数字大字 → **衬线字体**（Noto Serif SC + Playfair Display + Source Serif）
- 正文、描述、pipeline 步骤名 → **非衬线字体**（Noto Sans SC + Inter）
- 元数据、代码、标签 → **等宽字体**（IBM Plex Mono + JetBrains Mono）

所有字体用 Google Fonts CDN 引入，模板里已预设。

### 4b. 图片不要用 `align-self:end` 贴底

**现象**：左文右图布局里,为了让右列图片和左列 callout 底部对齐,在 `<figure>` 上加 `align-self:end`。结果:
- 如果父容器不是 grid(比如类名没定义),`align-self` 完全失效,图片掉到文档流最下面被浏览器底栏遮挡
- 即使是 grid,图片会在 cell 里贴底,低分屏上仍然被 `.foot` 和 `#nav` 圆点遮挡

**做法**:
- 图文混排**必须用 `.frame.grid-2-7-5`**(或 `.grid-2-6-6`/`.grid-2-8-4`)
- 右列 `<figure class="frame-img r-16x10">` 或 `<figure class="frame-img r-4x3">` 自然贴顶即可
- 要让左列 callout 看起来"贴底",给**左列**加 flex column + `justify-content:space-between`,不要动右列
- 如果图片与大标题顶端齐平但正文从标题下方开始,给图片加 `margin-top:7vh` 到 `9vh`,让图片跟正文内容区对齐

### 4c. 图片不要用原图奇葩比例

**现象**:`aspect-ratio: 2592/1798` 这种从原图复制的比例,在不同屏幕下撑出奇怪的空白或溢出。

**做法**:无论原图什么比例,占位器固定用标准比例 **16/10 / 4/3 / 3/2 / 1/1 / 16/9**。图片自动 `object-fit:cover + object-position:top`,顶部不裁,底部裁掉一点无伤大雅。

### 5. 不要给图片加厚边框 / 阴影

**现象**：为了"高级感"加了强阴影或黑框，瞬间变成商务 PPT。

**做法**：最多 1-4px 的微圆角 + **极淡的底噪**（已在模板里）。不要加 `box-shadow`，不要加 `border`（除非 1px 极淡的灰）。

---

## 🟡 P1 · 排版节奏

### 6. Hero 页和非 hero 页要交替

**推荐节奏**（25-30 页）：
```
Hero Cover → Act Divider (hero) → 3-4 pages non-hero → Act Divider (hero)
→ 4-5 pages non-hero → Hero Question → ... → Hero Close
```

连续 2 页以上 hero 会让人疲劳，连续 4 页以上 non-hero 会让节奏死。

### 7. 大字报页和密集页要交替

大字报（big numbers / hero question）和密集页（pipeline / image grid）交替出现，听众眼睛才不累。

### 8. 同一概念的英文/中文用法要统一

**现象**：一会儿写 "Skills"，一会儿写 "技能"，一会儿写 "薄承载厚技能"，全篇不一致。

**做法**：
- 术语优先用**英文单词**（Skills / Harness / Pipeline / Workflow），这些都是圈内熟悉词
- **别硬翻译**，硬翻译反而生硬
- 整个 deck 里同一个词 1 个写法

### 9. 底部 chrome 的页码要一致

用 `XX / 总页数` 的格式（比如 `05 / 27`）。**不要在右上角加动态页码**（会和 `.chrome` 重复）。

### 9b. 动效系统:每一页都要有 data-anim 标记

**现象**:生成后打开浏览器,翻页时内容直接"啪"地出来,没有任何节奏感——杂志风完全靠排版硬撑,少了层级展开的仪式感。

**根因**:完全没给任何元素加 `data-anim`,Motion One 脚本找不到可播的元素,整页静态出现。

**做法**:
- 所有正文页,**至少给 kicker / 主标题 / lead / callout / stat-card / figure 这些叶子元素加 `data-anim`**
- **Hero 页**(开场/幕封/问题/结尾):所有核心块(kicker + 大标题 + lead + meta-row)都要加
- **不需要特殊 recipe 的页**:什么也不用写,默认 cascade 就好看
- **需要特殊 recipe 的 4 类页**:必须在 `<section>` 上加对应 `data-animate`
  - 大引用 → `data-animate="quote"` + 每行 `<span data-anim="line" style="display:block">`
  - Before/After 对比 → `data-animate="directional"` + 左列 `data-anim="left"` + 右列 `data-anim="right"`
  - Pipeline 流水线 → `data-animate="pipeline"` + 每 step 加 `data-anim="step"`
  - Hero 页(自动用 hero recipe,但仍需给元素加 `data-anim`)

**自检**:生成后 `grep -c 'data-anim' index.html`,应该数十条以上。如果只有个位数,一定漏标了。

### 9c. Pipeline 页必须加 data-animate="pipeline"

**现象**:流水线页直接全部淡入,失去"一步步讲"的节奏,但切到下一页时又只能往前翻,没法回到上一个 step。

**做法**:Layout 6 的 `<section>` 必须加 `data-animate="pipeline"`。演示时按 →/空格/滚轮下滑可以**逐个点亮 step**,全部点亮之后再按 → 才会翻到下一页。这个节奏是刻意的,不是 bug。

---

## 🟢 P2 · 视觉打磨

### 10. WebGL 背景的遮罩透明度

**dark hero**：遮罩 12-15%（WebGL 明显透出）
**light hero**：遮罩 16-20%（WebGL 隐约可见，不抢字）
**普通 light/dark 页**：遮罩 92-95%（几乎不透）

如果页面文字非常少（hero question），遮罩可以再薄些；如果正文密集，必须加厚遮罩确保可读。

### 11. Light hero 的 shader 不能有强中心点

**现象**：Spiral Vortex、径向涟漪在 light 主题下太显眼，像 Windows 98 屏保。

**做法**：light hero 用 FBM 域扭曲驱动的无中心流动，底色保持银/纸色（接近 #F0F0F0 / #FBF8F3），彩虹偏色 subtle（0.05 以下）。

### 12. Dark hero 允许更多视觉冲击

Dark hero 可以用 Holographic Dispersion（钛金色散）等带中心结构的 shader，因为黑底能容纳更多视觉信息。

### 13. 左文右图的对齐

- 左列的文字组 `justify-content:space-between`：标题贴顶，引用框贴底
- 右列图片保持自然顶对齐,不要加 `align-self:end`
- 右列图片通常要跟正文内容区对齐,不是跟大标题顶端对齐;必要时加 `margin-top:7vh` 到 `9vh`
- 网格整体 `align-items:start`（不是 `center` / `end`）

### 13b. 标题与正文间距

- 顶部标题 + 下方长文章/引用/图表的两段式布局,中间必须有明显间距,推荐 `margin-top:6vh` 到 `8vh`
- 居中大标题页必须整体水平居中,不要只让文字块左对齐居中摆放
- 复杂内容页用大标题定调,下方内容用 grid / rowline 两端对齐,不要把大标题、小标题、正文挤成一坨

### 13c. UI 情景图不要拉成巨长条

- 单张 UI 截图如果放满宽后变成长条,优先拆成 2-3 个局部面板
- 多面板拼排时每个 `.frame-img` 用同一个固定高度类,如 `.h-16` / `.h-18` / `.h-22`,不要用同一个超宽容器硬塞
- 同一组图片的视觉大小必须一致,不要混用不同高度、不同缩放和不同边距密度
- 如果确实需要全宽,必须生成比例足够长的横向图片,并在 prompt 里明确"ultra-wide horizontal strip"

### 13d. 生成配图不要自带 slide 元素

- GPT-M 2.0 生成的配图只是嵌入素材,不要让图片自带页眉、页脚、标题、页码、角标、署名或装饰边框
- 流程图/信息图只保留核心图形和必要短标签,PPT 自己负责标题、页脚和 chrome
- 如果生成图已经带了这些元素,优先重生成;不要在 PPT 里再叠一层 chrome 造成干扰

### 13e. Swiss 图文混排不能只用一种

- 7-8 页 Swiss 测试 deck 至少使用 6 个不同 P 编号版式
- 有 2-3 张配图时,至少使用两种图片承载方式:P22 主视觉 / P23 单图解释 / P24 证据墙 / P15 矩阵 / P16 小报
- P23 默认底对齐:文字块和图片底部对齐,不要因为担心 nav 就退回顶部对齐;先控制图片高度
- 白底信息图容器必须白底、无描边;不要用灰框包白图

### 13f. Swiss 中文大标题要降级

- 中文 2 行标题默认从 `min(5.8vw,10.2vh)` 起步,不要直接用英文页的 `6.8vw-7vw`
- 任一行 9-12 个中文字符时降到 `min(5.2vw,9.2vh)`
- 3 行标题优先改写,不能为了标题大而挤掉下方图文内容

### 14. 图片的微弱圆角

风格 A 可以有轻微圆角。风格 B Swiss 必须直角: `.frame-img` 和图片本身都不要圆角、阴影或消费 app 式卡片感。
---

## 🔵 P3 · 操作细节

### 15. 图片路径用相对路径

图片放在 `images/` 文件夹下，HTML 里用相对路径 `images/xxx.png`，不要用绝对路径。

### 16. 页码在 `.chrome` 里写死

JS 会动态算总页数并扩展底部翻页圆点，但 `.chrome` 里的 `XX / N` 是写死的。加页/删页时要手工改 N。

### 17. 翻页导航要保留

模板默认支持：← → / 滚轮 / 触屏滑动 / 底部圆点 / Home·End。不要删 JS 里的导航逻辑。

### 18. 不要用 `height:100vh` 硬设，用 `min-height:80vh`

`100vh` 会让内容刚好卡满屏幕，但浏览器工具栏、标签栏会吃掉一部分高度，导致内容溢出。用 `min-height:80vh + align-content:center` 更稳。

---

## 🧪 最终自检清单

生成完 PPT 后，逐项对照这个清单（勾一下）：

```
预检(生成前)
  □ 已读过 template.html 的 <style>,确认所需类都存在
  □ 已决定每页用哪个 Layout(1-10)
  □ 已画出"主题节奏表":每页明确 hero dark / hero light / light / dark
  □ 节奏表满足硬规则:无连续 3 页同主题 / 有 ≥1 hero dark + ≥1 hero light(8 页以上) / 至少有 1 个 dark 正文页
  □ `<title>` 已改为实际 deck 标题(grep "[必填]" 应无结果)
  □ 瑞士风:封面是 `slide accent` 满屏 IKB + `<canvas class="ascii-bg">`(不是 `slide light` 白底)
  □ 瑞士风:封底是 `slide split` + 左 `b-accent` + ASCII canvas / 右 paper 3 条 takeaway,第 03 条用 var(--accent)
  □ 瑞士风:`grep -c "ascii-bg" index.html` ≥ 2(封面 + 封底各一)
  □ 瑞士风:封面没有"01"等大编号(chrome 已显示 01/N,不要重复)
  □ 瑞士风:IKB 背景上的强调字用 `font-style:italic`,禁止用 `color:var(--accent)`(蓝压蓝)

内容
  □ 每一幕的页数比例合理(不会头重脚轻)
  □ 没有使用 emoji 作图标
  □ Skills / Harness 等术语用法统一
  □ 每页的 kicker + 标题 + 正文 三级信息清晰

排版
  □ 所有大标题没有出现 1 字 1 行的换行
  □ 图片网格用 height:Nvh 而非 aspect-ratio
  □ 图片只裁底部，顶部和左右完整
  □ 衬线/非衬线字体分工符合模板
  □ Pipeline 多组之间有明显分隔

视觉
  □ hero 页和 non-hero 页交替
  □ WebGL 背景在 hero 页可见
  □ 图片有微弱圆角
  □ 没有沉重的阴影和边框

交互
  □ ← → 翻页正常
  □ 底部圆点数量与总页数匹配
  □ chrome 里的页码和实际页号一致
  □ ESC 键触发索引视图（如果保留）
  □ B 键触发静态/低功耗模式,右下角提示在 `B 静态` / `B 动态` 之间切换

动效
  □ `assets/motion.min.js` 存在(本地兜底)
  □ 低功耗模式下 WebGL/ASCII canvas 不再挂 RAF 循环,当前页内容仍全部可见
  □ 翻页时内容逐个淡入,不是"啪"一下全出
  □ 大引用页 `<section>` 带 `data-animate="quote"`,每行 `<span data-anim="line">`
  □ Before/After 对比页 `<section>` 带 `data-animate="directional"`,左右列标 left/right
  □ Pipeline 页 `<section>` 带 `data-animate="pipeline"`,每 step 标 data-anim="step"
  □ `grep -c 'data-anim' index.html` 数量 ≥ 页数 × 3(平均每页 3 个以上标记)
```

全勾完，才是合格的 PPT。

# 组件参考 · Components

这是 `guizang-ppt-skill` skill 的组件手册。template.html 已经定义好了所有样式，这里只写"这个组件长什么样、怎么用"。

## 目录

- [基础 Slide 外壳](#基础-slide-外壳)
- [字体 Typography](#字体-typography)
- [Chrome & Foot](#chrome--foot)
- [Callout 引用框](#callout-引用框)
- [Stat 数字矩阵](#stat-数字矩阵)
- [Platform 平台卡](#platform-平台卡)
- [Rowline 表格行](#rowline-表格行)
- [Pillar 支柱卡](#pillar-支柱卡)
- [Tag & Kicker](#tag--kicker)
- [Figure 图片框](#figure-图片框)
- [Icons 图标](#icons-图标)
- [Ghost 巨型背景字](#ghost-巨型背景字)
- [Highlight 荧光标记](#highlight-荧光标记)
- [Motion 动效系统](#motion-动效系统)

---

## 基础 Slide 外壳

每一页都是一个 `<section class="slide ...">`。必须包含 `data-theme` 属性（`light` 或 `dark`），JS 翻页时会根据这个属性切换背景。

```html
<section class="slide light" data-theme="light">   <!-- 浅色页 -->
<section class="slide dark" data-theme="dark">     <!-- 深色页 -->
<section class="slide light hero" data-theme="light">  <!-- Hero 页：浅色 + 薄遮罩透出 WebGL -->
<section class="slide dark hero" data-theme="dark">    <!-- Hero 页：深色 + 薄遮罩 -->
```

**light vs dark 的使用：交替使用**，每 2-3 页切换一次主题，避免连续超过 3 页同色。翻页时 WebGL 背景会自动在两个 shader 之间渐变过渡。

**hero 类的使用**：只给视觉主导的页面加（封面、金句页、章节过渡、结尾）。加 `hero` 后遮罩降到 12-16%，WebGL 背景会大幅透出，所以不要在 hero 页上放太多文字。

---

## 字体 Typography

字体分工是本模板最重要的规则，严禁混用。

| Class | 用途 | 字体 |
|---|---|---|
| `.display` | 超大号英文（Hero 页） | Playfair Display 700, 11vw |
| `.display-zh` | 超大号中文标题 | Noto Serif SC 700, 7.8vw |
| `.h1-zh` | 页面主标题 | Noto Serif SC 700, 4.6vw |
| `.h2-zh` | 副标题 | Noto Serif SC 600, 3.2vw |
| `.h3-zh` | 流水线步骤标题 | Noto Serif SC 500, 1.9vw |
| `.lead` | 引导段（比 body 大） | Noto Serif SC 400, 1.9vw |
| `.body-zh` | **正文/描述（非衬线）** | Noto Sans SC 400, 1.22vw |
| `.body-serif` | 正文（衬线） | Noto Serif SC 400, 1.3vw |
| `.kicker` | 小节提示（标题上方） | IBM Plex Mono, 12px uppercase |
| `.meta` | 元信息标签 | IBM Plex Mono, 0.88vw uppercase |
| `.big-num` | 巨型数字 | Playfair Display 800, 10vw |
| `.mid-num` | 中号数字 | Playfair Display 700, 5.5vw |

**核心规则**：
- **衬线**（`serif-zh` / `serif-en`）：标题、重点金句、数字 —— 用于"视觉重音"
- **非衬线**（`sans-zh`）：正文描述、大段阅读内容 —— 用于"信息密度"
- **等宽**（`mono`）：kicker、meta、foot 的英文标签 —— 用于"装饰节奏"

**强调技巧**：
- `<em class="en">英文词</em>` —— 把英文词渲染成 Playfair Display 斜体（很好看）
- `<em style="opacity:.65">短语</em>` —— 让标题后半段淡出，制造节奏

---

## Chrome & Foot

每一页的顶部和底部的元信息条。几乎所有页都应该有。

```html
<div class="chrome">
  <div class="left">
    <span>第一幕 · 硬数据</span>
    <span class="sep"></span>
    <span>Act I</span>
  </div>
  <div class="right"><span>02 / 27</span></div>
</div>

<!-- ... 页面主体 ... -->

<div class="foot">
  <div class="title">项目名 · CodePilot　|　github.com/codepilot</div>
  <div>Act I · Dev Numbers</div>
</div>
```

**规则**：
- `chrome.right` 总是放页码 `NN / TOTAL` （TOTAL 为总页数）
- `foot.title` 是中文说明，`foot.right` 是英文 act 标记
- chrome 和 foot 共同构成杂志感的"页眉页脚"

---

## Callout 引用框

展示金句 / 关键观点 / 他人引言。

```html
<div class="callout" style="max-width:80vw">
  <div class="q-big">"这东西在三年前，<br>需要一个十人团队做一年。"</div>
  <span class="cite">— 一个观察者的判断</span>
</div>
```

变体：
- 不带 cite：去掉 `<span class="cite">` 即可
- 带英文金句：`<em class="en">"Thin Harness, Fat Skills."</em>`
- 在 hero 页使用：外层加 `style="position:relative;z-index:2"`（避免被背景遮罩盖住）

---

## Stat 数字矩阵

展示数据指标，常与 `.grid-6` / `.grid-4` 配合。

```html
<div class="grid-6">
  <div class="stat">
    <span class="m">Duration</span>
    <span class="n">64<em style="font-size:.4em;opacity:.5;font-style:normal"> 天</em></span>
    <span class="l">从 0 到现在</span>
  </div>
  <!-- ... 更多 stat ... -->
</div>
```

三段式结构：`.m` 等宽小标签 → `.n` 巨型数字 → `.l` 描述说明。数字后的单位用 `<em>` 缩小到 0.4em，opacity 0.5。

**常用布局容器**：
- `.grid-6` — 3×2 网格（最常用，6 个 stat）
- `.grid-4` — 2×2 网格（4 个 stat）
- `.grid-3` — 3 等分单行（3 个 stat / pillar）

---

## Platform 平台卡

展示社交平台 / 渠道 + 粉丝数。

```html
<div class="plat">
  <div class="sub">Weibo</div>
  <div class="name">微博</div>
  <div class="nb">289K</div>
</div>
```

可选第四行（补充说明）：
```html
<div class="body-zh" style="font-size:max(11px,.8vw);opacity:.5;margin-top:.6vh">
  含小绿书同步
</div>
```

**"Also On" 变体**（补充平台）：
```html
<div class="plat" style="border-top-style:dashed;opacity:.72">
  <div class="sub">Also On</div>
  <div class="body-zh" style="font-weight:600;margin-top:.8vh">
    B 站　·　知乎
  </div>
</div>
```

---

## Rowline 表格行

列表式内容，每行一个条目。

```html
<div class="rowline">
  <div class="k">CLAUDE.md</div>
  <div class="v">你该怎么做事 —— 行为规则 + 工作偏好 + 禁止事项</div>
  <div class="m">EMPLOYEE · HANDBOOK</div>
</div>
```

三列结构：`.k` 衬线关键词 · `.v` 正文描述 · `.m` 等宽标签（右对齐）。第一个和最后一个 rowline 自动加上下边框。

**变体：2 列**：`style="grid-template-columns:1fr 3fr"` 去掉 `.m` 列。

---

## Pillar 支柱卡

三支柱结构，常用于"概念并列"类型页面。

```html
<div class="grid-3">
  <div class="pillar">
    <div class="ic">01</div>
    <div class="t">三层<br>文档体系</div>
    <div class="d">CLAUDE.md<br>+ 项目知识库<br>+ 护栏文件</div>
  </div>
  <!-- ... 更多 pillar ... -->
</div>
```

**带图标的 pillar（用于强调性页面）**：
```html
<div class="pillar" style="padding:4vh 2vw;border:1px solid currentColor;border-color:rgba(10,10,11,.2)">
  <div class="ic"><i data-lucide="compass" class="ico-lg"></i></div>
  <div class="t">判断力</div>
  <div class="d">决策和方向的权威。<br>取舍、品味、方向感。</div>
</div>
```

`.ic` 可以是序号（`01 / 02 / 03` 或 `A. / B. / C.`），也可以是 Lucide 图标。

---

## Tag & Kicker

**Kicker** 是标题上方的小提示文字（等宽、全大写、小字号）：
```html
<div class="kicker">过去 64 天 · 开发篇</div>
<div class="h1-zh">一个人，做了什么。</div>
```

**Tag** 是独立的标签胶囊（带边框）：
```html
<div style="display:flex;gap:1.6vw;flex-wrap:wrap">
  <div class="tag">早上 10 点起床</div>
  <div class="tag">周二 / 四下午健身</div>
  <div class="tag">晚上照样看剧 · 玩游戏</div>
</div>
```

---

## Figure 图片框

**这是本模板最容易踩坑的组件，务必遵守以下规则**。

### 基础结构

```html
<figure class="tile">
  <div class="frame-img" style="height:26vh">
    <img src="图片素材/xxx.png" alt="说明">
  </div>
  <figcaption class="frame-cap">
    <span class="pf">推特 · Twitter</span>
    <span class="nb">137K</span>
  </figcaption>
</figure>
```

### 关键约束（血泪经验，不要违反）

1. **图片网格必须用 `height:Nvh` 固定高度**，不要用 `aspect-ratio`。
   - 原因：网格里用 aspect-ratio 容易撑破父容器，导致图片堆叠。
   - 推荐尺寸：`.h-16` (小型面板) / `.h-18` (紧凑条形) / `.h-22` (标准网格) / `.h-26` (突出展示) / `.h-28` (大图)。
   - 单张主图可以用模板提供的比例类：`.r-16x9` / `.r-16x10` / `.r-4x3` / `.r-3x2` / `.r-3x4` / `.r-1x1`。
   - 同一组图片必须使用同一个高度类,不要一张 `25vh`、一张 `21vh` 混用。

2. **`object-position:top center`（已在 CSS 里设好）**，只允许裁掉底部。
   - 严禁裁剪左右和顶部 —— 这是图片的核心身份信息区。

3. **网格里多张图时，用内联 grid 而不是 `grid-3`**：
   ```html
   <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1vh 1.2vw">
     <figure class="tile">...</figure>
     <figure class="tile">...</figure>
     <figure class="tile">...</figure>
   </div>
   ```

4. **图片与布局其他部分对齐**：使用 `.grid-2-7-5` / `.grid-2-6-6` / `.grid-2-8-4` 的 grid 结构自然顶对齐。不要给图片加 `align-self:end`。

5. **信息图 / 截图再设计**：给 `.frame-img` 同时加 `.fit-contain`，避免图内文字和标注被裁切。

6. **用户原始截图比例不合适时**：优先重新生成"截图再设计 / UI 情景图"到目标比例,不要把原图硬塞成长条。

### Frame Caption 变体

```html
<!-- 标准：左 figure 名，右数字 -->
<figcaption class="frame-cap">
  <span class="pf">推特 · Twitter</span>
  <span class="nb">137K</span>
</figcaption>

<!-- 带编号 -->
<figcaption class="frame-cap">
  <span class="idx">01</span>
  <span class="pf">AI 润色</span>
  <span>Polish</span>
</figcaption>
```

### 图片占位（设计阶段占位符）

图片还没有就位时，用虚线框占位：
```html
<div class="img-slot r-4x3">  <!-- r-4x3 / r-16x9(default) / r-3x2 / r-1x1 -->
  <span class="plus">+</span>
  <span class="label">GitHub 截图位置</span>
</div>
```

---

## Icons 图标

**严禁使用 emoji**。用 Lucide via CDN（template.html 已引入）。

```html
<i data-lucide="compass" class="ico-lg"></i>     <!-- 大图标（pillar 用） -->
<i data-lucide="target" class="ico-md"></i>      <!-- 中图标（列表项用） -->
<i data-lucide="check-circle" class="ico-sm"></i>  <!-- 小图标（inline 用） -->
```

**常用 Lucide 图标名**（按含义分组）：

- 判断类：`compass`, `target`, `crosshair`, `search-check`
- 关系类：`share-2`, `users`, `network`, `link`, `handshake`
- 品牌类：`crown`, `gem`, `award`, `star`, `badge-check`
- 流程类：`workflow`, `route`, `arrow-right-left`, `repeat`
- 数据类：`grid-2x2`, `bar-chart-3`, `trending-up`, `activity`
- 审美类：`palette`, `brush`, `eye`, `sparkles`
- 对错类：`check-circle`, `x-circle`, `check`, `x`
- 方向类：`arrow-right`, `arrow-up-right`, `corner-down-right`

**图标与文字 inline 组合**：
```html
<div class="h3-zh" style="display:flex;align-items:center;gap:.8em">
  <i data-lucide="target" class="ico-md"></i>
  判断 — 什么值得写
</div>
```

---

## Ghost 巨型背景字

用作"装饰性背景字"，极低透明度，营造杂志感。

```html
<div class="ghost" style="right:-6vw;top:-8vh">BUT</div>
<div class="ghost" style="left:-8vw;bottom:-18vh;font-style:italic">Harness</div>
```

- 字号 34vw，opacity 0.06
- 常用定位：`right:-6vw;top:-8vh`（右上超出）/ `left:-8vw;bottom:-18vh`（左下超出）
- 内容：英文单词或数字（章节序号 01/02/03、关键词 BUT/NOW/HERE）

**注意**：使用 ghost 的页面里，其他内容要加 `position:relative;z-index:2` 避免被压到下面。

---

## Highlight 荧光标记

行内短语的"荧光笔"效果：

```html
<span class="hi">不是</span>
<span class="hi">一次性爆发</span>
```

在文字底部生成一条半透明高亮条。深色主题用亮条，浅色主题用暗条（CSS 已处理）。

**适合场景**：只对关键 1-3 个词使用，不要大面积用。

---

## Motion 动效系统

整套 deck 默认开启翻页入场动画,由 Motion One(vanilla 版 Framer Motion,约 4KB)驱动。

### 加载方式

`assets/template.html` 底部的 module script 会先尝试**本地** `assets/motion.min.js`,失败则回落到 **jsdelivr CDN**,两者都失败则强制把所有带 `data-anim` 的元素设为 `opacity:1`—— 内容永远可读,演示不依赖网络。

```js
// template 里的核心加载器(不用改)
let motion;
try { motion = await import('./assets/motion.min.js'); }
catch(e1) {
  try { motion = await import('https://cdn.jsdelivr.net/npm/motion@11.11.17/+esm'); }
  catch(e2) {
    document.querySelectorAll('[data-anim]').forEach(el=>{el.style.opacity='1';el.style.transform='none'});
  }
}
```

### 数据属性驱动

你只需要在 HTML 里加两种属性:

```html
<!-- 1. 在 section 上选 recipe(可选,默认 cascade / hero 自动) -->
<section class="slide light" data-animate="quote">

<!-- 2. 在需要入场的元素上加 data-anim(可选值:left/right/line/step/divider) -->
<h1 class="h-xl" data-anim>大标题</h1>
<div class="stat-card" data-anim>...</div>
<div data-anim="left">左列内容</div>
<span data-anim="line" style="display:block">引用第一行</span>
```

### 5 种 recipe 一览

| recipe | 触发方式 | 行为 | 代表布局 |
|---|---|---|---|
| `cascade`(默认) | 不加 `data-animate` 即为此值 | 所有 `data-anim` 逐个 stagger 淡入,75ms/step | Layout 3 / 4 / 5 / 10 |
| `hero` | `.hero` slide 自动用此值 | 慢节奏 stagger,仪式感更强,160ms/step | Layout 1 / 2 / 7 |
| `quote` | `data-animate="quote"` | 其他元素先出,`data-anim="line"` 的行 550ms 间隔逐句揭示 | Layout 8 |
| `directional` | `data-animate="directional"` | `data-anim="left"` 从左滑入 → divider → `data-anim="right"` 从右滑入 | Layout 9 |
| `pipeline` | `data-animate="pipeline"` | 翻到此页 step 保持 15% 透明;按 →/空格/滚轮逐个点亮,最后一步才放行翻页 | Layout 6 |

### 给 slide 选 recipe 的决策树

1. **它是 `.hero` slide 吗?** → 不用加 `data-animate`,自动用 `hero`
2. **它是大引用金句页?** → `data-animate="quote"`,每句用 `<span data-anim="line" style="display:block">`
3. **它是左右对比 Before/After?** → `data-animate="directional"`,左列 `data-anim="left"`、右列 `data-anim="right"`
4. **它是流水线分步讲解?** → `data-animate="pipeline"`,每步 `data-anim="step"`
5. **其他所有正文页** → 什么也不加,自动用 `cascade`

### 什么元素该加 `data-anim`?

- ✅ 每一层有独立语义的块:kicker / h1 / h-xl / lead / callout / stat-card / figure / tag / rowline
- ✅ 多列结构里每一列,让它们逐列淡入而不是一起
- ❌ 不要在容器(`.grid-6` / `.frame`)上加,只加给叶子元素
- ❌ 不要在每个 `<li>` 上加,一般在 `<ul>` 层加就够
- ❌ 如果某页不想要任何动画(比如过渡页),整页不加 `data-anim` 即可 — Motion One 只对带标记的元素生效

### 常见问题

- **图片闪一下再出现?** 这是预期行为,翻页中段(450ms 时)触发动画
- **Pipeline 页卡住翻不下页?** 正确的,按 → 一步一步点亮 step,全部点亮后再按 → 才翻页
- **内容静态时也不显示?** 检查 motion.min.js 是否在 `assets/` 下;或者浏览器控制台看错误信息

# GPT-M 2.0 配图提示词

用于 Codex 环境下为本 skill 生成 PPT 配图。提示词只负责定基调,不要写成长篇说明。先判断图片落位和比例,再选择类型。

## 通用规则

- 先判断当前 deck 风格:风格 A = 电子杂志 × 电子墨水;风格 B = 瑞士国际主义 / Swiss Style
- 风格 A 基调:电子杂志 × 电子墨水,克制、真实、留白充足,适合横向网页 PPT
- 风格 B 基调:Swiss International Typographic Style,12/16 列网格、Helvetica/Inter 气质、单一高饱和 accent、直角纯色、发丝线、极大留白
- 信息图、图表、截图再设计中的文字语言必须跟随用户语言:中文 deck 用中文,英文 deck 用英文
- 不生成卡通、3D、霓虹科技感、SaaS 模板感、过度装饰或假 logo
- 图片要给标题或正文留出可叠加空间,不要满屏堆细节
- 同一页或同一组图片必须使用同一比例、同一视觉缩放、同一边距密度
- 配图是嵌入 PPT 的素材,不是一张独立 slide:不要生成页眉、页脚、页码、标题栏、角标、署名、装饰边框或 slide chrome
- 生成后保存到 `images/`,命名为 `{页号}-{语义}.{ext}`

## 比例选择

| 用途 | 推荐比例 | HTML 落位 |
|------|---------|-----------|
| 章节封面 / 全屏主视觉 | 16:9 | `.frame-img.r-16x9` 或 hero 背景参考 |
| 瑞士风顶部横幅 / Image Hero | 16:9 或 21:9 | P22 顶图 cover / `.frame-img.r-21x9` |
| 左文右图主图 | 16:10 或 4:3 | `.frame-img.r-16x10` / `.frame-img.r-4x3` |
| 信息图 / 系统关系图 | 16:9 或 16:10 | 原始截图用 `.fit-contain`;按槽位重生成则用 `.frame-img.r-16x9` / `.frame-img.r-16x10` 铺满 |
| 截图再设计 / UI 情景图 | 16:10 或 21:9 | 原始截图用 `.fit-contain`;重生成到 S15/S16 时用 `.frame-img.r-21x9` 铺满 |
| 图文混排小图 | 3:2 或 3:4 | `.frame-img.r-3x2` / `.frame-img.r-3x4` |
| 图片网格 | 统一横图 | `.frame-img.h-22` / `.frame-img.h-26` |
| 小型面板组 | 统一横图 | `.frame-img.h-16` / `.frame-img.h-18` |

信息图和截图再设计如果来自不可控原始素材,优先用 `fit-contain`,避免文字被裁切;如果是 GPT-M 2.0 按槽位重新生成,必须生成同槽位比例并铺满容器,不要让小图漂在白框里。纪实照片优先用默认 `cover`,保持画面张力。

## 图片标准化策略

### A. 先选目标槽位

不要先生成图片再硬塞进页面。先决定图片落位:

1. 主视觉:16:9
2. 左文右图:16:10 或 4:3
3. 信息图/截图再设计:16:9 或 16:10,并使用 `fit-contain`
4. 多图网格/面板组:统一高度类,同一组内禁止混用高度

### B. 用户原始图片/截图的处理

原始截图比例通常不可控,不要直接作为最终视觉标准。按下面顺序处理:

1. 如果原图比例接近目标槽位,直接放入统一 `.frame-img` 中,用 `cover` 或 `fit-contain`
2. 如果原图过高、过窄、过长,优先用"截图再设计 / UI 情景图"重新生成到目标比例
3. 如果一张 UI 图被拉成巨长条,拆成 2-3 张同尺寸局部面板;每个面板使用同一高度类
4. 如果必须保留原图,用 `fit-contain` 放进统一 frame,接受留白,不要裁掉关键文字

### C. 生成提示词后缀

每个配图提示词最后都补一句规格约束:

```text
输出必须是[16:9/16:10/4:3/3:2]横向构图,主体居中但保留边距,画面密度中等,与同组图片保持相同视觉缩放和边距。只保留核心图形/画面本身,不要生成页眉、页脚、标题、页码、角标、署名、装饰边框、超长条、竖图或不规则比例。
```

同一页需要多张图时,补一句:

```text
这是一组图片中的一张,请保持与同组图片相同的画面比例、元素大小、边距、线条粗细和标注密度。
```

## 类型 1: 人文纪实照片

用于增加现场感、情绪和真实世界锚点。

```text
生成一张横向纪实摄影配图,主题是:[页面概念]。风格像 Fujifilm / Leica editorial documentary,自然光、低饱和、轻微胶片颗粒、真实工作或生活现场,克制有人文温度。适合电子杂志 × 电子墨水 PPT,留出标题空间。不要商业摆拍、科幻界面、AI 机器人、logo 或水印。输出必须是[16:9/16:10/4:3]横向构图,主体居中但保留边距,画面密度中等。只保留核心照片本身,不要生成页眉、页脚、标题、页码、角标、署名、装饰边框、超长条、竖图或不规则比例。
```

## 类型 2: 杂志风信息图

用于解释概念、流程、对比、系统关系。

```text
生成一张横向杂志风信息图,解释:[概念/流程/关系]。电子墨水风格,黑白灰为主,少量低饱和强调色,细线条、网格、编号、短标签、留白充足。图中文字使用[中文/英文],保持简短可读。不要卡通、3D、霓虹科技感或模板感。输出必须是[16:9/16:10]横向构图,主体居中但保留边距,画面密度中等。只保留核心信息图本身,不要生成页眉、页脚、标题、页码、角标、署名、装饰边框、超长条、竖图或不规则比例。
```

## 类型 3: 流程 / Pipeline 图

用于讲清从 A 到 B 到 C 的过程。

```text
生成一张横向流程信息图,展示:[步骤 1] → [步骤 2] → [步骤 3] → [结果]。风格为电子杂志 × 电子墨水,细箭头、分段编号、短注释、克制留白。图中文字使用[中文/英文]。只保留核心流程图本身,不要页眉、页脚、标题、页码、角标、署名或装饰边框。比例:16:9。
```

## 类型 4: 对比图

用于 before / after、新旧模式、两种协作方式对照。

```text
生成一张横向对比信息图,左侧是[旧模式],右侧是[新模式]。风格像高端独立杂志里的分析图,黑白灰和一个低饱和强调色,细线分栏、短标签、清晰层级。图中文字使用[中文/英文]。只保留核心对比图本身,不要页眉、页脚、标题、页码、角标、署名或装饰边框。比例:16:9。
```

## 类型 5: 系统关系图

用于多角色、多工具、多模块之间的关系。

```text
生成一张横向系统关系图,展示:[角色/工具/模块]之间如何连接。电子墨水杂志风,节点、细线、箭头、编号和少量短注释,结构清晰,留白充足。图中文字使用[中文/英文]。只保留核心关系图本身,不要页眉、页脚、标题、页码、角标、署名或装饰边框。比例:16:9。
```

## 类型 6: 截图再设计 / UI 情景图

用于把真实截图、代码、设计稿、工作区处理成统一视觉素材。

```text
生成一张横向 UI 情景图,把[截图/界面/工作区内容]再设计成适合杂志风 PPT 的视觉。保留真实产品工作流的感觉,使用纸张底色、细线框、网格、少量标注和克制阴影。图中文字使用[中文/英文],短而清晰。不要真实品牌 logo、花哨 dashboard、霓虹渐变或过度拟物。输出必须是16:10横向构图,主体居中但保留边距,画面密度中等。只保留核心 UI 画面本身,不要生成页眉、页脚、标题、页码、角标、署名、装饰边框、超长条、竖图或不规则比例。
```

## 类型 7: 数据大字报图

用于突出一个关键数字或少量指标。

```text
生成一张横向数据大字报视觉,核心数字是:[数字],含义是:[含义]。风格为电子墨水杂志版式,超大衬线数字、少量短注释、细线、留白和纸张质感。图中文字使用[中文/英文]。只保留核心数据视觉本身,不要页眉、页脚、标题、页码、角标、署名或装饰边框。比例:16:9。
```

---

## 风格 B:瑞士国际主义配图规则

当 deck 选择 `assets/template-swiss.html` / `layouts-swiss.md` 时,优先使用下面这组提示词。它们和 GPT-M 2.0 配套,目标是生成能直接放进原始登记版式的图片槽位,尤其是 S22 顶部横幅、S15/S16 多图网格。

### Swiss 配图硬规则

- 视觉锚点:International Typographic Style / Swiss modernism / Helvetica / Josef Müller-Brockmann / Massimo Vignelli
- 构图:严格 12/16 列网格、非对称留白、左对齐、发丝线、直角模块
- 色彩:只使用黑、白、灰和**一个**主题 accent(默认 IKB 蓝;如果用户选柠檬黄/绿/安全橙,就替换为对应 accent)
- 禁止:渐变、阴影、圆角、玻璃拟态、霓虹、3D、卡通、SaaS 模板感、伪 logo、装饰边框
- 图片内部不要生成 PPT 外壳:不要页眉、页脚、页码、标题栏、角标、署名、外框
- UI / 信息图文字必须短,保持中文/英文语言一致;真实照片尽量不要带文字
- 先确定版式槽位再生成图片:单张大图用 `s22-hero-21x9`;多图格用 `s15-grid-21x9` 或 `s16-brief-21x9`
- 21:9 图片必须让核心主体落在中央 70% 安全区,四周留白;不要把人脸、关键节点或 UI 文字贴边

### Swiss 类型 1:纪实照片 / 案例主图

用于 S22 Image Hero,增加真实场景锚点。

```text
生成一张 21:9 超宽横向纪实摄影配图,主题是:[页面概念]。风格是 Swiss editorial documentary:高对比、低饱和、冷静克制、真实办公/城市/产品使用场景,构图有大量负空间,主体位于中央 70% 安全区,适合放入瑞士国际主义 PPT 的顶部横幅。不要 AI 机器人、科幻界面、商业摆拍、logo、水印或文字。只保留核心照片本身,不要页眉、页脚、标题、页码、角标、署名、装饰边框或 PPT 外壳。
```

### Swiss 类型 2:信息图 / 系统关系图

用于解释概念、架构、流程、数据与表现分离等抽象内容。

```text
生成一张横向 Swiss Style 信息图,解释:[概念/流程/系统关系]。使用 Helvetica/Inter 气质的无衬线短标签、12/16 列网格、直角模块、1px 发丝线、黑白灰和一个 [IKB 蓝/柠檬黄/柠檬绿/安全橙] accent。图中文字使用[中文/英文],每个标签不超过 8 个字/词。不要渐变、阴影、圆角、3D、卡通、霓虹或 SaaS 模板感。输出比例为[21:9/16:10],主体居中但保留大留白。只保留核心信息图本身,不要页眉、页脚、标题、页码、角标、署名、装饰边框或 PPT 外壳。
```

### Swiss 类型 3:截图再设计 / UI 情景图

用于把截图、工作区、代码、dashboard 重绘成统一 Swiss 风视觉。

```text
生成一张横向 UI 情景图,把[截图/界面/工作区内容]再设计成 Swiss International Typographic Style。画面使用极简 dashboard / workspace 结构,直角面板、发丝线、12 列网格、少量 [IKB 蓝/柠檬黄/柠檬绿/安全橙] accent,无阴影无圆角。图中文字使用[中文/英文],短而清晰,不要真实品牌 logo。输出必须是16:10横向构图,视觉密度中等,适合放进 `.frame-img.r-16x10.fit-contain`。只保留核心 UI 画面本身,不要页眉、页脚、标题、页码、角标、署名、装饰边框或 PPT 外壳。
```

### Swiss 类型 4:多图网格单张素材

用于 S15/S16 图片格改造,一组 2-6 张图片并列时逐张生成。

```text
生成一张横向证据图,主题是:[证据 A/B/C]。这是一组 Swiss Style 图片中的一张,请保持直角模块、黑白灰、单一 [IKB 蓝/柠檬黄/柠檬绿/安全橙] accent、相同边距、相同线条粗细、相同视觉缩放。图中文字使用[中文/英文],短标签即可。输出必须是[21:9/16:10]横向构图,适合放入 S15/S16 统一图片格。只保留核心图像本身,不要页眉、页脚、标题、页码、角标、署名、装饰边框或 PPT 外壳。
```

### Swiss 类型 5:极简图表 / 数据块

用于 S21 或 S15/S16 图片格中的小型数据解释图。

```text
生成一张横向 Swiss Style 数据图,核心数据是:[数字/对比/排名],含义是:[说明]。使用极大无衬线数字、1px 发丝线、直角色块、黑白灰和一个 [IKB 蓝/柠檬黄/柠檬绿/安全橙] accent,像瑞士海报里的数据版式。图中文字使用[中文/英文],只保留必要标签。不要渐变、阴影、圆角、3D 或装饰边框。比例:[16:9/16:10]。只保留核心数据图本身,不要页眉、页脚、标题、页码、角标、署名或 PPT 外壳。
```

# Layouts · 风格 B 瑞士国际主义

22 个原始登记版式 · 严格模块化网格 · 每个版式说明用途、骨架、关键类名、专属动效。

> ⚠️ 这套版式与风格 A(电子杂志/电子墨水)**不通用**。类名同名但语义不同(例如 `h-hero` 在风格 A 是衬线,在风格 B 是无衬线极细 200)。一份 deck 只能选一套。

---

## Swiss locked mode(必须先读)

本主题的 golden source 是:

`/Users/guohao/Documents/op7418的仓库/项目/Thin-Harness-Fat-Skills/ppt/index.html`

生成正文页时不要把 Swiss 当成“自由组合的风格包”。默认只能使用 `references/swiss-layout-lock.md` 登记的 `S01-S22`。每个 slide 都必须在 `<section>` 上写 `data-layout="Sxx"`。

**关键约束**:

- 顶部中文标题默认左对齐并处在左上内容轴;不要把标题放到页面中间。
- 不允许临时发明原始 22P 之外的正文结构。本文档末尾的 P23/P24 属于历史实验区,默认禁用。
- 需要单张大图时使用 `S22 Image Hero`;需要多图时用 `S15/S16` 的原始矩阵/小报骨架改造成图片格。
- SVG 只画几何,不写可见文字。标签放 HTML 里。
- 生成完成后运行 `node scripts/validate-swiss-deck.mjs index.html`。

---

## 设计语言基线

**配色**(`--accent` 由主题决定,见 `themes-swiss.md`)
- `--paper` 纸白底 #ffffff(主背景)
- `--ink` 黑墨字 #0a0a0a(主文字 / Ink 反转块)
- `--accent` 单色锚点(IKB 蓝默认 / 黄 / 绿 / 橙 四套)
- `--text-primary / secondary / helper` 三级文字灰阶
- `--border-subtle` 1px 发丝细线 #e0e0e0

**排版**
- 字体:`var(--sans)` Inter / Helvetica Neue + `var(--mono)` JetBrains Mono
- 字重:**200 (ExtraLight) 大字** / **300 (Light) 正文** / **600 (SemiBold) t-cat 小标**
- 大标题遵循原始 PPT 的实际页面用法:主标题 `font-weight:200`,重点词/数字 `font-weight:300`;不要因为旧 CSS helper 里残留过 800/900 就把 Swiss 大标题加粗
- 大字号收紧:`letter-spacing:-.04em` / `line-height:.9`
- mono 数字:`font-feature-settings:"tnum","ss01"`

**中文大标题字号分档**
中文方块字的视觉面积比英文更重,不能直接套英文页的 `6.8vw-7vw`。生成前先按中文标题长度降级:

| 中文标题形态 | 推荐字号 |
|---|---|
| 1 行,≤ 8 个中文字符 | `min(6.4vw,11.2vh)` |
| 2 行,每行≤ 8 个中文字符 | `min(5.8vw,10.2vh)` |
| 2 行,任一行 9-12 个中文字符 | `min(5.2vw,9.2vh)` |
| 3 行或更长标题 | 改写标题;实在不能改时用 `min(4.6vw,8.2vh)` |

规则:中文标题优先改短,其次降字号;不要让标题挤占下方图文区域。英文、数字型 hero 可以更大,中文方法论页必须更克制。

**网格**(IBM Carbon 2x Grid 改造)
- 16 列 grid:`grid-template-columns:repeat(16,1fr)` + `gap:16px`
- spacing token:`--sp-3` 8 / `--sp-4` 12 / `--sp-5` 16 / `--sp-6` 24 / `--sp-7` 32 / `--sp-8` 40 / `--sp-9` 48 / `--sp-10` 64 / `--sp-11` 80 / `--sp-12` 96 / `--sp-13` 160

**画布**
- `.canvas-card`:`100vw × 100vh`,直角无圆角,padding `5.6vh 5vw 4.4vh`
- `body{background:var(--paper)}` — 不用 WebGL 背景
- 必须保留右下角 `B 静态` 快捷键。低功耗模式使用 `body.low-power`,停止 WebGL/ASCII canvas RAF 与 Motion 入场动画,刷新后通过 `localStorage` 保持用户选择。

---

### P0 对齐法则(每生成一页都先过这 4 条,违反 = 整页报废)

**1. 不要二次叠加水平 padding** ⚠️ 最常踩
`.canvas-card` 已自带 `padding:5.6vh 5vw 4.4vh`。
chrome-min(页眉)、主体内容、底部 footnote 都是 canvas-card 的子元素,**共用同一条 5vw 边线**。
如果在主体那层再写 `padding:5vh 5vw 4vh`,水平方向就变成 `5vw + 5vw = 10vw`,主体比 chrome-min 多内缩一圈,左右对不齐。

```html
<!-- ❌ 错:主体多缩了 5vw -->
<div class="canvas-card">
  <div class="chrome-min">...</div>
  <div style="flex:1;padding:5vh 5vw 4vh;...">主体内容</div>
</div>

<!-- ✅ 对:主体 padding 为 0,只用 grid gap 控垂直间距 -->
<div class="canvas-card">
  <div class="chrome-min">...</div>
  <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr auto;gap:3vh">主体内容</div>
</div>
```

例外:`.slide.split .canvas-card{padding:0}` 已被 CSS 覆盖,split 模式下两个 `.half` 自己控制 padding(常用 `5.6vh 3.6vw 4.4vh`),与本法则不冲突。

**2. kicker 必须在大标题"上方",不要压成左右**
小标题(`.t-meta` / `.t-cat`)与大标题之间是从属关系,版式上必须**上下结构**。

```html
<!-- ❌ 错:auto 1fr 把 kicker 和大标题挤成左右两列 -->
<div data-anim="head" style="display:grid;grid-template-columns:auto 1fr;gap:3vw;align-items:end">
  <div class="t-meta">METHODOLOGY · 03</div>
  <h2 class="h-xl-zh">为什么是 N+1</h2>
</div>

<!-- ✅ 对:flex column 上下叠 -->
<div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
  <div class="t-meta">METHODOLOGY · 03</div>
  <h2 class="h-xl-zh">为什么是 N+1</h2>
</div>
```

**3. 双约束限高 `min(Xvw, Yvh)` 中 Y ≥ X × 1.6**
标准 16:9 屏 1vw : 1vh ≈ 1.78,如果 Y 太严(例如 `min(7vw, 10vh)`),大字号会被高度上限截断到 10vh,不再受 7vw 主导,显得整体缩小。
经验数值:

| 用途 | 推荐 |
|---|---|
| h-hero 巨字宣言 | `min(11.6vw, 19vh)` |
| h-xl 章节标题 | `min(7vw, 12vh)` ~ `min(7.4vw, 13vh)` |
| 大数字 KPI | `min(8.4vw, 14vh)` |
| 中数字 / 编号 | `min(4.6vw, 8.5vh)` ~ `min(5.6vw, 10vh)` |

**4. canvas-card 子元素之间用 grid `gap`,不要靠 margin/padding 堆**
`.canvas-card` 默认 `display:flex;flex-direction:column`,chrome-min 自带 `margin-bottom:48px`(`--sp-9`)。
主体区往下排几行(head / 内容 / footnote),**首选** `display:grid;grid-template-rows:...;gap:Nvh`,**次选** flex column + gap,**禁用** 在每个子块里加 `margin-top` / `padding-top` 调间距(会和 chrome-min 的 margin-bottom 重叠或撕裂)。

**5. 底部分页安全区:主内容最低处不要触及 nav**
底部分页 dot 固定在 `bottom:2vh`,视觉上占据约 `93vh` 之后的区域。主内容、图片 caption、图表说明、timeline label 的最低处必须停在安全区上方。

- 模板提供 `--nav-safe-bottom:8vh`,可用 `.nav-safe-bottom` / `.nav-safe-bottom-tight`
- P23 使用 `.swiss-img-split.align-image-bottom` 时,模板会自动给底部加安全区,避免图片 caption 被分页组件挡住
- 如果为某页手写 `align-items:end` / `margin-top:auto` / `position:absolute;bottom:...`,必须肉眼检查最低处是否越过 nav
- 视觉自检:打开页面到该页,确认内容最低边缘与分页 dot 之间至少有 `3vh` 呼吸空间

---

**卡片填充规则(必须遵守)**
| 类型 | 类名 | 角色 | 用法 |
|---|---|---|---|
| Ink 黑底 | `.card-ink` | 反转 / 宣言 | hero 块、收束页一半 |
| Accent 蓝填充 | `.card-accent` | 唯一焦点 | 一组中突出一项 |
| Grey 灰底 | `.card-fill` | 默认中性 | 多卡并列、统计卡 |
| Outlined 描边 | `.card-outlined` | 锚点(非卡片) | hairline 分割框 |

❌ 禁止混用(蓝色背景+蓝色描边、灰底+描边等)

**装饰极简原则**
- 1px hairline 分隔(`hr-hairline` / `border-bottom`)
- 8×8 / 12×12 直角小方块替代圆点
- 点阵 `dot-mat` / 描边圆 `ring-mat` / 叉 `cross-mat`(SVG mask)

**图片使用原则(Swiss + GPT-M 2.0)**
- 图片是网格中的"证据块",不是装饰背景;必须有明确功能:案例、实拍证据、UI 截图、系统图、概念信息图
- 所有图片容器保持直角、无阴影、无圆角;默认**不加图片外框**,让 caption 或页面网格承担层级
- 白底信息图 / 流程图 / UI 图:容器背景必须是 `var(--paper)`,不要用灰底包白图,也不要加 `.swiss-keyline` 描边
- 只有当图片本身边缘无法和页面区分时,才用 `.swiss-lined` 加一条顶部 accent 线;不要给每张图都套边框
- 纪实照片用 `object-fit:cover` 只裁底部/边缘;原始截图或文字密集图用 `.fit-contain`,避免文字被裁
- 如果信息图、流程图、UI 情景图是按 S15/S16 槽位重新生成的,必须用 `.frame-img.r-21x9` / `.frame-img.r-16x10` 铺满槽位;不要再加 `.fit-contain`,否则会变成小图漂在白框里
- 瑞士风图片优先比例:S22 顶部横幅 `21:9`;S15/S16 多图格统一 `21:9` 或统一 `16:10`
- 生成 2-3 张配图时,必须先绑定原始版式槽位:单张大图 = S22;多图 = S15/S16 网格改造;不要使用未登记的 P23/P24
- S22 的照片主体必须位于中央安全区,HTML 用 `object-position:center 35%` 或 `center center`,不要用 `top center` 截人脸
- GPT-M 2.0 生成图必须遵守单一 accent 色、Helvetica/Inter 气质、12/16 列网格、直角纯色、无渐变/阴影/圆角
- 生成图只保留核心图像本身,不要把页眉、页脚、标题、页码、角标、边框、署名画进图片里

**版式多样性硬规则**
Swiss 主题有 22 个登记版式,生成时要主动展示版式系统,不要把所有内容都做成 `head + grid-reveal + card`:

- 7-8 页 deck 至少使用 **6 个不同 S 编号版式**
- 不允许连续 3 页使用同一种主体结构(如三页连续 S19 / 普通卡片)
- 如果是"测试模板"或"我想看看效果",必须覆盖:封面、收尾、至少 1 个对比/时间线(S08/S11/S02)、至少 1 个结构图(S14/S17/S15)、至少 1 个图片版式(S22 或 S15/S16 图片格)
- 图片页不等于新发明一页。单图用 S22,多图用 S15/S16 的原始网格骨架改造
- 每页写代码前先列 `页码 → data-layout → 为什么选它 → 图片槽位`;生成后用 validator 检查

**动效原则(每页一个语义化 recipe)**
- 不是统一 fade-up,而是**与图形语义耦合**:数字 scale 弹入、bar scaleY 拉起、SVG 圆环 stroke-dashoffset 描线、时间线节点序列点亮
- 缓动:`EASE_PROD` `cubic-bezier(.2,0,.38,.9)` 用于 productive(120-240ms)、`EASE_ENTRY` `cubic-bezier(0,0,.3,1)` 用于 expressive(400-700ms)
- playSlide 入口要 reveal 所有 `[data-anim]` 容器到 opacity:1,recipe 内再用 motion `{opacity:[0,1]}` 覆盖

---

## 视觉 + 代码双维审核(生成后必须做)

不要只看 HTML/CSS。Swiss 模板的还原度要同时从**浏览器视觉**和**代码结构**判断:

1. 同时打开三份页面:原始参考 PPT、当前 `template-swiss.html` 或生成页、正在修改的测试 PPT。原始参考路径是 `/Users/guohao/Documents/op7418的仓库/项目/Thin-Harness-Fat-Skills/ppt/index.html`。
2. 截图前先等入场动效稳定(约 1-2 秒)。不要把动画中间态误判成"内容缺失"或"版式空白"。
3. 先看视觉:标题重量、头部距离、图片落位、底部安全区、caption 是否被 nav 挡住。
4. 对照原始参考 PPT 的同类版式,不要只对照 CSS helper;以实际页面结构和视觉结果为准。
5. 再回到代码,检查该页是否误用了不属于该版式的组件,例如把 P24 的三图证据墙塞进 P23,或把 P7 图表用于没有真实数值的概念列表。
6. 若视觉不一致,优先判断是**版式选择错**、**必选组件缺失**、**可选组件滥用**还是**间距/安全区问题**,不要直接靠调 `margin` 硬救。
7. 修改模板时,新增能力必须用新类隔离;不要因为一页出问题去改全局基座类。

### 原始 PPT 视觉锚点(对照时优先看这些)

| 视觉锚点 | 原始 PPT 的实际做法 | 生成时的规则 |
|---|---|---|
| 大标题重量 | 实际页面大量使用 `font-weight:200/300`;即使 raw CSS helper 里有 700/800/900,也不能直接当视觉标准 | 大标题保持轻字重,字号越大越细 |
| 留白 | 页面经常只占上半屏或中部,底部留给 nav 和少量 footnote | 不要为了"填满"而把内容推到底 |
| 分割线 | 只在章节边界、证据墙、卡片层级处使用 1px hairline | 不要给每个内容块都加线 |
| 标题与内容 | 标题区和正文/图表之间有明显空气感 | 复杂页用 grid `gap`,不要让内容贴着标题 |
| Timeline | 轴线在中下部,但 label 不碰底部 nav | 横向 timeline 必须同时检查上下 label 和 nav 安全区 |
| 图片页 | 图片是证据块,要么做 S22 主视觉,要么放进 S15/S16 原始网格 | 不要使用未登记图文结构 |

### 组件必选 / 可选 / 可省略

| 组件 | 规则 |
|---|---|
| `.canvas-card` / `.chrome-min` | 基础页必选;split 页左右 half 各自有 chrome-min |
| `t-meta` / `t-cat` kicker | head 区必选,但正文卡片内可省略;必须在大标题上方 |
| 大标题 | 章节/论点页必选;列表型小卡页可以用较小标题,但不能缺页级信息锚点 |
| `lead` 说明 | 可选;如果标题已经解释清楚,可以省略,但不能用长段正文贴着标题 |
| 图片 caption | S15/S16 多图格必选;S22 大图可选,因为图已经是主视觉且下方有 KPI/说明 |
| 发丝线 / border-bottom | 可选;只能用于建立层级,不能为了装饰堆线 |
| KPI / 数字 | 只在有真实数据时使用;不要为概念解释编造数值 |
| `footnote` / 底部说明 | 可选;如果使用,必须避开 nav 安全区 |

### 通用版式 / 非通用版式

| 类型 | 版式 | 使用边界 |
|---|---|---|
| 通用 | S01, S03, S08, S09, S10, S11, S19 | 大多数叙事 deck 都能用,但仍要满足内容形状 |
| 条件通用 | S04, S05, S13, S16 | 取决于数量是否刚好匹配:3/4/6 项 |
| 数据专用 | S02, S06, S07, S18, S20, S21, S22 | 必须有真实时间、数值、指标或案例数据 |
| 结构专用 | S14, S15, S17 | 必须有闭环、矩阵、层级/生态关系;不适合普通段落 |

---

## 22 个登记版式

### P1 · Cover · 封面页

**用途**:整套 deck 起手 / 主题宣言。
**适用内容类型**:封面 / 章节首页 / 主题宣言。**纯文字结构**(主标题 + 副标 + 元信息),不承载数据。

**默认推荐:IKB 满屏 + ASCII 呼吸场** ⭐
- `<section class="slide accent">` 满屏 IKB,**不是** light 白底
- `.canvas-card` 内首位插入 `<canvas class="ascii-bg" aria-hidden="true">`,模板底部 IIFE 自动驱动 sin/cos 二维噪声呼吸场
- 主标题反白 weight 200,微强调字用斜体(`font-style:italic;font-weight:300`)而非 IKB 蓝(底已是蓝、蓝压蓝看不见)
- **不要**再放编号大字"01"——chrome-min 已经标 01/NN
- 与 P9 Closing 的 IKB 半屏配合形成"开场全 IKB ↔ 收尾半 IKB"色彩闭环

**关键类**:`.slide.accent` `.ascii-bg` + `min(11.6vw,19vh)` 双约束大字
**动效 recipe**:`hero` — ASCII 字符场持续呼吸,文字 fade-up 序列入场

**示例代码(IKB 默认变体)**:
```html
<section class="slide accent" data-animate="hero">
  <div class="canvas-card">
    <canvas class="ascii-bg" aria-hidden="true"></canvas>
    <div class="chrome-min">
      <div class="l">[必填] Deck 标题 · Issue/Field Note 编号</div>
      <div class="r">SS · 26.05.10 · 01 / NN</div>
    </div>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr auto;gap:2.6vh">
      <div data-anim="kicker" class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em">[必填] 章节英文 / Section En</div>
      <h1 data-anim="title" style="align-self:center;font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(11.6vw,19vh);line-height:.94;letter-spacing:-.025em;color:#fff">[必填] 中文主标题<br/>(可在某字加 <span style="font-style:italic;font-weight:300">italic</span> 微强调)</h1>
      <div data-anim="bottom" style="display:grid;grid-template-rows:auto auto;gap:1.6vh;border-top:1px solid rgba(255,255,255,.22);padding-top:2vh">
        <div data-anim="lead" class="lead" style="max-width:52ch;color:rgba(255,255,255,.86);font-weight:300">[必填] 一段 1-2 行的副标 / 引子,定调全场.</div>
        <div style="display:flex;justify-content:space-between;align-items:end">
          <div class="t-meta" style="color:rgba(255,255,255,.6)">[选填] 作者 · 日期 · 出处</div>
          <div class="t-meta" style="color:rgba(255,255,255,.6)">→ swipe / arrow keys</div>
        </div>
      </div>
    </div>
  </div>
</section>
```

**经典变体(左 ink + 右 paper 对开)** — 仅当全 IKB 不合内容调性时使用:
```html
<section class="slide" data-animate="cover-reveal">
  <div class="canvas-card cover-split">
    <div class="cover-ink">
      <span class="t-cat">Volume 18 · 2026</span>
      <h1 class="h-hero">Thin Harness,<br>Fat Skills.</h1>
      <span class="t-meta">— Kevin · 2026-05</span>
    </div>
    <div class="cover-paper">
      <p class="lead">薄型承载层,厚重技能。</p>
      <ul class="meta-list">
        <li>22 PAGES</li><li>SWISS · IKB</li><li>MP-75</li>
      </ul>
    </div>
  </div>
</section>
```

---

### P2 · Vertical Timeline · 纵向时间轴

**用途**:演化对比、年代变迁、版本迭代(2-5 个时间节点)。
**适用内容类型**:**带量化数据的时间演化**。每节点必须有「年份 + 量化数值(如 1× / 4× 倍数 / 单位数字)+ 描述」三件套。如果只有节点名没有数据,改用 P11 横向时间线。
**骨架**:左侧 axis 列 12px 圆点 + 1px 虚线轴 / 右侧节点信息(年份 + 大字数据 + 小标 + 描述)。
**关键类**:`.timeline-v` `.tl-node` `.tl-axis`(12px 固定列宽,绝对定位 dot 防错位) `.kpi-row-4`
**动效 recipe**:`timeline-vertical` — 节点按时间顺序由上到下点亮(dot 先 pop 再扩 → 文字横向滑入)
**网格规则**:axis 列 = 12px 固定;dot 用 `position:absolute;left:50%;transform:translateX(-50%)` 与虚线对齐
**示例代码**:
```html
<section class="slide" data-animate="timeline-vertical">
  <div class="canvas-card">
    <header class="chrome-min">...</header>
    <div class="timeline-v">
      <div class="tl-node">
        <div class="tl-axis"><span class="dot"></span></div>
        <div class="tl-body">
          <span class="yr">2023</span>
          <span class="multi">1<small>×</small></span>
          <p class="desc">Prompt Engineering Era</p>
        </div>
      </div>
      <!-- 重复 N 个 tl-node,axis 列贯穿 -->
    </div>
  </div>
</section>
```

---

### P3 · Statement · 极简陈述

**用途**:中心论点、章节起始、口号。一页只放一句话 + 简单装饰。
**适用内容类型**:**纯定性论断 / 口号 / 章节切换**。一句话压缩到 8-12 词,**不承载任何数据或列表**。如果需要数据支撑,改用 P18 Why Now;如果是封面,用 P1。
**骨架**:左 1/3 空白 + 中段巨字陈述(8-10vw, weight 200) + 右下小字注脚 + 底部 hairline。
**关键类**:`.h-statement`(9.6vw,letter-spacing:-.05em) `.stmt-anchor`
**动效 recipe**:`statement-rise` — 大字按词序错峰升起(每词延迟 180ms)+ 注脚 fade in
**示例代码**:
```html
<section class="slide" data-animate="statement-rise">
  <div class="canvas-card">
    <header class="chrome-min">...</header>
    <h1 class="h-statement">
      <span>Build it</span> <span>once.</span><br>
      <span>It runs</span> <span>forever.</span>
    </h1>
    <span class="stmt-anchor">— Statement 03</span>
  </div>
</section>
```

---

### P4 · Six Cells · 六格定义

**用途**:6 个并列概念定义、6 项功能并列。
**适用内容类型**:**6 个对等概念 / 功能列举**(数量必须 = 6,过少用 P5,过多用 P15/P16)。每格仅承载「图标 + 编号 + 短标题 + 一行描述」,**不承载需要展开的数据 / 段落**。
**骨架**:2×3 网格 / 每格上方 lucide 图标 + 编号 + 短标题 + 一行描述 / 单元间用 hairline 分隔。
**关键类**:`.cell-6` `.cell-icon-row` `.cell-num`
**动效 recipe**:`six-cells` — 6 格按 z 形顺序点亮(L→R, T→B,每格延迟 90ms)
**注意**:**不要自己画 SVG 图标**,用 `<i data-lucide="bookmark"></i>` 引线上 lucide。
**示例代码**:
```html
<div class="cell-6">
  <div class="cell">
    <i data-lucide="square-stack"></i>
    <span class="cell-num">01</span>
    <h4>Skill File</h4>
    <p>纯 markdown,可手写、可重写</p>
  </div>
  <!-- 5 more -->
</div>
```

---

### P5 · Three Sub-cards · 三子卡

**用途**:三步流程、三类对比(轻度差异)。
**适用内容类型**:**3 个对等概念 / 步骤**(数量必须 = 3)。结构同质、**无强烈数据差异**(若数据可比,改用 P6 KPI Tower)。每卡内容比 P4 略多(编号 + 标题 + 1-2 行描述)。
**骨架**:左侧大标题 + 描述 + 顶部 hairline / 右侧 3 张水平堆叠 sub-card。
**关键类**:`.sub-card-stack` `.sub-card`(`.card-fill` 灰底,直角)
**动效 recipe**:`sub-stack` — 主标题先入 → 3 卡阶梯式从右滑入(每卡延迟 140ms)
**示例代码**:
```html
<div class="grid-2-9">
  <div class="lead-col">
    <span class="t-cat">Three Forces</span>
    <h2 class="h-xl">压成三个事实</h2>
  </div>
  <div class="sub-card-stack">
    <article class="card-fill sub-card">
      <span class="big-num">01</span>
      <h4>Skill File</h4>
      <p>...</p>
    </article>
    <!-- 2 more -->
  </div>
</div>
```

---

### P6 · KPI Tower · 不等高柱状 KPI

**用途**:4 项数据用视觉高度表达层级差异。
**适用内容类型**:**4 项可比量化数据**(必须有真实数值,bar 高度由数据决定)。典型如:成本、容量、计数、效率指标。**禁止**用于无数据的概念列举(那是 P4/P5 的事)。
**骨架**:4 列均分,每列底部一根不同高度的 IKB 蓝矩形(数据决定高度)+ 顶部图标 + 中段巨数 + 底部标签。
**关键类**:`.kpi-tower-row` `.bar-tower`(min-height:6vh, max:36vh) `.tower-cap`
**动效 recipe**:`tower-grow` — 标签先入 → 数字 scale 弹入 → tower scaleY 从 0 拉起(transform-origin:bottom)
**示例代码**:
```html
<div class="kpi-tower-row">
  <div class="tower-col">
    <i data-lucide="layers"></i>
    <span class="num-mega">90K</span>
    <span class="lbl">Skills</span>
    <div class="bar-tower" style="--h:36vh"></div>
  </div>
  <!-- 3 more,h 不同 -->
</div>
```

---

### P7 · H-Bar Chart · 横向条形图

**用途**:多项排名比较 / 占比对比(5-10 项)。
**适用内容类型**:**5-10 项可比量化数据**(必须有真实百分比 / 评分 / 数值,bar 宽度由数据决定)。典型如:benchmark 排名、市场份额、问卷占比。⚠️ **严禁用于无量化数据的概念列举**(那是 P4/P5/P15)— 编造数字会被识破。
**骨架**:顶部大标题 / 中段空 / 下半部条形列表(每行:文字标签 + 1px 蓝条 0→target width + 末端数字)。
**关键类**:`.h-bar-chart` `.bar-row` `.bar-fill`(scaleX 动画)
**动效 recipe**:`hbar-grow` — 大标题先入 → 每行依序 width 0→target(transform-origin:left)+ 末端数字 count-up
**示例代码**:
```html
<div class="h-bar-chart">
  <div class="bar-row">
    <span class="bar-lbl">Anthropic Advisor</span>
    <span class="bar-fill" style="--w:84%"></span>
    <span class="bar-num">84</span>
  </div>
  <!-- N more -->
</div>
```

---

### P8 · Duo Compare · 双轨对照

**用途**:Before/After、A vs B、旧/新对比。
**适用内容类型**:**二元对照**(必须正好 2 项)。两侧结构同质(t-cat 标签 + 大字标题 + 段落 / 列表说明)。典型如:旧/新工作流、传统/AI、客户视角/团队视角。
**骨架**:左右两半屏中间一根纵向 1px 长线分隔 / 各自顶部 t-cat + 大字标题 + 下方说明。
**关键类**:`.duo-compare` `.duo-half` `.vrule`(scaleY 拉开)
**动效 recipe**:`duo-mirror` — 中线 vrule 先 scaleY 0→1 → 左右各自标题、文字镜像入场
**示例代码**:
```html
<div class="duo-compare">
  <div class="duo-half">
    <span class="t-cat">Before</span>
    <h2>交给模型</h2>
  </div>
  <span class="vrule"></span>
  <div class="duo-half">
    <span class="t-cat">After</span>
    <h2>交给代码</h2>
  </div>
</div>
```

---

### P9 · Closing Manifesto · 收束宣言

**用途**:整套 deck 收尾页。
**适用内容类型**:**deck 收尾**(每个 deck 只有一页)。固定结构:左侧宣言短句 + 右侧 3 条 takeaway(编号 + 标题 + 一行说明)。**不能在中间页使用**(那会与 P1 封面重复)。

**默认推荐:左 IKB+ASCII / 右 paper takeaway** ⭐
- 用 `<section class="slide split">` + 左半 `.half.b-accent` + ASCII canvas + 右半白底 takeaway
- 与 P1 封面的全 IKB 形成"开场全 IKB ↔ 收尾半 IKB"色彩闭环
- 右侧第 03 条 takeaway 用 `var(--accent)` 强调,把 IKB 蓝从左半穿到右半,完成色彩缝合
- 大标题反白 weight 200,强调字用斜体(底已是蓝、不要再用 `var(--accent)` 标蓝)

**关键类**:`.slide.split` `.half.b-accent` `.ascii-bg`(IIFE 自动启动)
**动效 recipe**:`split-statement` — 左 ink/IKB 标题字符序列升起 → 右白半 takeaway 三条尾随

**示例代码(IKB 默认变体)**:
```html
<section class="slide split" data-animate="split-statement">
  <div class="canvas-card">
    <div class="split-half">
      <!-- 左半 · IKB + ASCII 呼吸场 -->
      <div class="half b-accent" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between;position:relative;overflow:hidden">
        <canvas class="ascii-bg" aria-hidden="true"></canvas>
        <div class="chrome-min" style="margin-bottom:0;position:relative;z-index:1">
          <div class="l">NN / NN</div>
          <div class="r">CLOSING</div>
        </div>
        <div data-anim="manifesto" style="display:flex;flex-direction:column;gap:2vh;position:relative;z-index:1">
          <div class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em;margin-bottom:1.6vh">MANIFESTO</div>
          <h2 style="font-family:var(--sans),var(--sans-zh);font-size:min(8vw,14vh);line-height:.94;letter-spacing:-.025em;font-weight:200;color:#fff">[必填] Build a model.<br/>Run <span style="font-style:italic;font-weight:300">forever</span>.</h2>
          <div style="font-family:var(--sans),var(--sans-zh);font-size:max(13px,1vw);line-height:1.6;color:rgba(255,255,255,.82);font-weight:300;max-width:36ch;margin-top:1.4vh">[必填] 一句中英文落地注脚.</div>
        </div>
        <div data-anim="signature" style="display:flex;justify-content:space-between;align-items:end;border-top:1px solid rgba(255,255,255,.22);padding-top:2vh;position:relative;z-index:1">
          <div class="t-meta" style="color:rgba(255,255,255,.62)">[选填] 作者 · 头衔</div>
          <div class="t-meta" style="color:rgba(255,255,255,.62)">YY.MM.DD</div>
        </div>
      </div>
      <!-- 右半 · 白底 takeaway,第 03 条用 IKB 蓝强调,首尾色彩闭环 -->
      <div class="half" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between">
        <div class="chrome-min"><div class="l">TAKEAWAYS</div><div class="r">03 RULES</div></div>
        <div data-anim="rules">...</div>
        <div class="t-meta" style="color:var(--text-helper);text-align:right">→ 完 · END OF FIELD NOTE</div>
      </div>
    </div>
  </div>
</section>
```

**经典变体(`.closing-split` ink 双半屏)** — 当封面没有用 IKB 满屏时,改用经典 ink 收束:
```html
<div class="closing-split">
  <div class="cl-ink">
    <p class="line-mega">Build it<br>once.</p>
    <p class="line-mega">It runs<br>forever.</p>
  </div>
  <div class="cl-paper">
    <ul class="takeaway-list">
      <li><span class="num">01</span><h4>Skill</h4><p>...</p></li>
      <!-- 2 more -->
    </ul>
  </div>
</div>
```

---

### P10 · Dot Matrix Statement · 点阵宣言

**用途**:第二张陈述页 / 章节切换 / 视觉透气页。
**适用内容类型**:**口号 / 隐喻 / 章节切换**(同 P3,但加几何点阵装饰)。用于一个 deck 内**避免连续两页都是 P3**;通常用作"概念定义"前的视觉调味页。
**骨架**:中段 7vw 巨字三行宣言 / 右上角 36vw 圆点矩阵 + 左下角描边圆环矩阵。
**关键类**:`.dot-mat`(SVG mask 实心点)`.ring-mat`(描边圆)`.cross-mat`(× 网格)
**动效 recipe**:`matrix-statement` — 文字逐行入 → 点阵 mask-position 从左推到右
**示例代码**:
```html
<div class="canvas-card">
  <span class="ring-mat" style="left:5vw;bottom:5vh;width:18vw;height:18vw"></span>
  <h1 class="h-statement">Build a thin harness.<br>Write fat skills.<br>Codify everything.</h1>
  <span class="dot-mat" style="right:0;top:0;width:36vw;height:36vw"></span>
</div>
```

---

### P11 · Horizontal Timeline · 横向时间线

**用途**:多步骤流程(4-7 步)、时间演进。
**适用内容类型**:**4-7 步线性流程**(每步只有一个名称,不需要展开数据 / 描述)。如果每步要展开,改用 P5;如果有量化数据,改用 P2。**禁止**用于循环结构(那是 P14)。
**骨架**:顶部大标题 / 中段一根 1px hairline 横线 + N 个均布节点(8×8 直角方块 + 上方 mono 编号 + 下方步骤名)。
**关键类**:`.timeline-h` `.tl-h-node` `.tl-h-axis`
**动效 recipe**:`timeline-walk` — 节点沿轴左→右依次点亮(每节点 220ms)
**对齐注意**:横向时间线 label 的 CSS 依赖 `translateX(-50%)` 居中。动效里如果要做上下位移,必须写完整 `transform: translate(-50%, y)` 序列,不能只写 `y`,否则动画结束后 label 会偏离 dot。
**示例代码**:
```html
<div class="timeline-h">
  <span class="tl-h-axis"></span>
  <div class="tl-h-node">
    <span class="num">01</span>
    <span class="dot"></span>
    <span class="lbl">Investigate</span>
  </div>
  <!-- 4-6 more -->
</div>
```

---

### P12 · Manifesto + Ink Banner · 宣言 + 通栏 ink 条

**用途**:阶段性结论、章节封底、口号 + 视觉强收束。
**适用内容类型**:**章节性收束 / 阶段性宣言**(用于 deck 中段而非结尾,P9 是 deck 终结)。承载「主张 + 简短说明 + ink 通栏宣言」三段结构,无数据。
**骨架**:上半屏左侧 t-cat + 大字 4 行宣言 + 右侧短段说明 / 下半屏 ink 通栏(无左右下边距)+ 反白短句 + lucide 图标矩阵。
**关键类**:`.manifesto-top` `.ink-banner-full`(`margin:0 -5vw -4.4vh` 取消父级 padding)
**动效 recipe**:`manifesto` — 大字三段错峰升起 → 底 ink 条横向 scaleX 0→1 铺开 → 反白文字 fade in
**注意**:Skill File 那段小字 **顶对齐于右侧大字基线**(`align-items:flex-start;padding-top:1.2vw`)

---

### P13 · Three Forces Cards · 三力卡片小报

**用途**:3 个对等概念展示(每个 = 巨数 + 标题 + 双列描述)。
**适用内容类型**:**3 个对等概念深化**(数量 = 3,比 P5 承载更多文字)。每卡内容比较丰富(巨编号 + 标题 + 双列段落描述)。01/02/03 为编号锚点而非真实数据。典型如:三大反驳、三种力量、三大主张。
**骨架**:左 5/16 ink hero 块(t-cat + 4 行标题 + 点阵装饰)/ 右 11/16 三张水平卡堆叠。
**关键类**:`.three-forces` `.hero-ink-col` `.force-card`(`.card-fill`)`.force-num`(9.2vw IKB 蓝)
**动效 recipe**:`three-forces` — 左 hero 横移入 → 右 3 卡阶梯式从右滑入 → 巨蓝数字单独 pop
**注意**:**3 张卡片必须统一样式**(都用 `.card-fill` 灰底,不要混用描边/蓝底);若需突出一张,改用 `.card-accent`,**禁止**蓝底+描边。

---

### P14 · Loop Diagram · 闭环流程图

**用途**:自学闭环、自动化流程(3-5 步循环)。
**适用内容类型**:**循环 / 闭环流程**(终点回到起点,3-5 步)。如自学循环、CI/CD、反馈闭环、agent loop。**线性流程禁用**(那是 P11)。
**骨架**:左 4 行编号步骤(顶对齐) / 右侧 SVG 同心圆环 / 中央巨字 LOOP / 节点统一灰底直角方块(不用圆点交替色)。
**关键类**:`.loop-diagram` `.loop-steps` `.loop-svg`
**动效 recipe**:`loop-form` — 左侧步骤纵向序列 → 右 SVG 圆环 stroke-dashoffset 描线 → 节点序列点亮
**注意**:左右**整体居中对齐**(顶部对齐 + 高度等同)

---

### P15 · Image Matrix + Hero Stat · 矩阵 + 大字底注

**用途**:大量同类项展示(8-12 项 skill / 团队成员 / 案例图标),底部一个总数据收束。
**适用内容类型**:**8-12 项同类型小项 + 一个汇总指标**。每项只承载短标题(无展开),底部巨数为「汇总值」(项目总数 / 总流量 / 总用户)。**项数过少改用 P4(6 项)**。
**骨架**:顶部标题(留 9vh 间距)/ 中段 4×3 矩阵卡(每卡 12vh 固定高度)/ 底部巨数 + 标签(margin-top:auto 推到底)。
**关键类**:`.matrix-fill`(grid-template-columns:repeat(4,1fr))`.matrix-cell`(`.card-fill` 灰底,**禁止描边**)`.hero-stat-bottom`
**动效 recipe**:`matrix-fill` — 12 格随机棋盘渐显(每格 random delay)→ 底部巨数 count-up
**注意**:卡片高度限定(避免大数字溢出);**所有卡用 `.card-fill` 灰底**,只突出强调项时单独换 `.card-accent`

---

### P16 · Multi-card Brief · 微卡小报

**用途**:6 项小卡并列(快讯、tip 集合、特性概览)。
**适用内容类型**:**6 项轻量短讯 / tip / 注脚**(数量 = 6,每项主文短 + 小字注脚)。比 P4 内容更碎,适合快讯类。**只允许一张 accent 蓝突出**(单焦点法则)。
**骨架**:顶部大标题(留 9vh)/ 下方 3×2 微卡(每卡:左上主文 + 右下小字 + 中间留空)。
**关键类**:`.brief-grid` `.brief-card`(`.card-fill` 灰底)`.brief-card.is-accent`(单一蓝底强调)
**动效 recipe**:`field-notes` — 6 卡按 z 形顺序点亮(L→R, T→B,90ms 错开)
**注意**:卡内排版**左上主文 + 右下小字**,中间空出(避免内容散);**只允许一张 accent 蓝**

---

### P17 · System Diagram · 同心圆系统图

**用途**:层级架构(core→middle→outer)、生态地图。
**适用内容类型**:**严格三层嵌套关系**(core 内核 / middle 中间层 / outer 外圈)。典型如:技术栈层级、生态分层、影响力辐射。**非三层结构禁用**(扁平用 P4,层级不清用 P5)。
**骨架**:左半屏标题 + 三段说明 / 右半屏 SVG 三层同心圆 + 标签外引线。
**关键类**:`.system-diagram` `.sys-svg` `.sys-label`
**动效 recipe**:`system-diagram` — 同心圆从外向内 scale 入 → 标签序列出现

---

### P18 · Why Now · 三列递进 + 巨数

**用途**:三论点 + 各自支撑数据(为什么是现在)。
**适用内容类型**:**3 个论点 + 每个论点对应一个量化数据**。每论点结构 = t-cat 标签 + 一句标题 + 段落 + 一个底部巨数(可以是百分比/年份/倍数)。最后一列 IKB 蓝强调表示「重点支撑论据」。
**骨架**:顶部大标题 / 中段 3 列(每列:t-cat + 标题 + 描述)/ 列底各一个 8.4vw 巨数(01 / 02 / 03,最后一列 IKB 蓝强调)。
**关键类**:`.why-now-grid` `.why-col` `.why-num-bottom`(8.4vw, weight 200)
**动效 recipe**:`why-now` — 三列垂直递进 → 底部巨数 count-up
**注意**:巨数字号统一,只用颜色(IKB 蓝)突出最后一列,**不要**用粗体

---

### P19 · Four Cards · 四列均分卡

**用途**:4 项功能/特性并列(等权重)。
**适用内容类型**:**4 项等权特性 / 模块**(数量 = 4,结构完全同质)。每项 = t-meta 编号 + 大字标题 + 一段描述。无数据维度,纯定性。比 P5(三步)更平均,比 P6(数据高度)更纯文字。
**骨架**:顶部 80px IKB 蓝短发丝顶线 + 大字双行标题 / 下方 4 列均分卡(每卡:t-meta 顶部 "— 01 / SLASH" + 大字标题 + 段落描述)。
**关键类**:`.four-cards` `.fc-col`
**动效 recipe**:`four-cards` — 顶部蓝线 width 0→100% → 4 列从下向上推入(每列 110ms 错开)
**注意**:**不要**用 9px 圆形装饰点(不符合直角语言),用 `.t-meta` 文字代替

---

### P20 · Stacked KPI Ledger · 纵向账单 KPI

**用途**:4-6 行核心数据账单式展示(每行=数字+标签+图标)。
**适用内容类型**:**4-6 项核心数据账单**(每行必须有真实数值 + 标签 + 图标)。垂直 ledger 形式适合财务数据、KPI 仪表板、关键指标列表。比 P6 KPI Tower 容纳数据更多但视觉化弱(无 bar 高度对比)。
**骨架**:每行一道 hairline 分隔 / 左侧巨数(限高 `min(13vw,16vh)` 防溢出) / 中部标签 / 右侧 lucide 图标。
**关键类**:`.stacked-ledger` `.ledger-row`(border-bottom:1px solid var(--border-subtle))`.ledger-num`
**动效 recipe**:`stacked-ledger` — 每行数字升起 → 标签左滑 → 图标 pop(每行 180ms 错开)
**注意**:**字号必须限高**(`font-size:min(13vw, 16vh)`),否则在标准 16:9 屏底部行会被挤出

---

### P21 · Tech Spec Sheet · 规格说明书

**用途**:产品规格、benchmark 数据、性能基线展示(多 KPI + 视觉化竖线装饰)。
**适用内容类型**:**产品规格 / benchmark / 性能基线**(必须有真实多维数据,3 KPI + 9 根竖线 = 12+ 数据点)。典型如:模型评分、API 性能、压测结果。是 deck 中数据密度最高的版式。
**骨架**:左 4 行大标题 / 中部 3 KPI(顶部 hairline + 数字 + 单位)/ 右下 9 根高低不一的垂直竖线 / 底部巨数 + Yearly goal + 三 tag + 右下角 MP-XX + 页码。
**关键类**:`.tech-spec` `.spec-title-col` `.spec-kpi-grid` `.spec-bars`(`.bar-vert`,scaleY 弹起,transform-origin:bottom)
**动效 recipe**:`tech-spec` — hero 区淡入 → 标题入 → KPI 顶线一根根画出 → 底巨数 pop → 竖线从底部 scaleY 弹起(50ms 错开)
**注意**:右下 bars 矩阵必须**底对齐**且**不超出右边距**

---

### P22 · Image Hero · 图文混排封面

**用途**:案例展示、产品图 + 数据落地、章节封面带图。
**适用内容类型**:**案例展示 / 产品发布 / 章节带图封面**(必须有真实图片资源 + 3 个核心数据)。典型如:产品截图 + 关键指标、案例图 + ROI、用户反馈图 + 复购率。**没有真实图源时禁用**(占位灰图破坏视觉)。
**骨架**:上半屏 60% 全幅图片 + 左上白底标题块叠加(top:11vh,留出充分缓冲)/ 下半屏 40% 长说明 + 三列 KPI($ / 127× / 100%)。
**关键类**:`.image-hero` `.hero-img-wrap`(60vh)`.hero-overlay-block` `.hero-stats`
**动效 recipe**:`image-hero` — 图缓慢 zoom-out(scale 1.05→1)→ 白块 scaleX 0→1 推开 → 三 KPI 顶线依序画出
**注意**:
- 图片优先用 `images/{页号}-{语义}.png` 本地文件(GPT-M 2.0 或用户提供素材),不要默认外链 unsplash
- 图片下方内容不要贴着图下沿,使用 `.image-hero-body` 统一给下半屏增加顶部缓冲
- 三列 KPI 大字号要限高(`min(4.6vw, 7.6vh)`),小字用 `margin-top:auto` 锚定列底,防止溢到 nav 圆点
- 列高度统一(grid 不要 `align-items:start`,让列拉伸到同一高度)

**示例代码**:
```html
<section class="slide light" data-animate="image-hero">
  <div class="canvas-card" style="padding:0;display:flex;flex-direction:column;overflow:hidden">
    <div data-anim="img" style="position:relative;flex:0 0 60%;overflow:hidden;background:var(--grey-1)">
      <img src="images/22-product-scene.png" alt="[必填] 图片说明" loading="eager"
           style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 30%">
      <div class="chrome-min" style="position:absolute;top:0;left:0;right:0;color:rgba(255,255,255,.9);padding:5.6vh 5vw 0">
        <div class="l">Section · Case / Visual Evidence</div>
        <div class="r">22 / NN</div>
      </div>
      <div data-anim="title-block" style="position:absolute;left:5vw;top:11vh;background:var(--paper);padding:3.2vh 3.2vw;max-width:40vw">
        <div style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.2vw,9vh);line-height:1;letter-spacing:-.035em;color:var(--text-primary)">
          [必填] Image<br>Evidence
        </div>
      </div>
    </div>
    <div data-anim="kpi" class="image-hero-body">
      <div style="max-width:48ch;font-family:var(--sans),var(--sans-zh);font-size:max(15px,1.3vw);line-height:1.55;font-weight:300;color:var(--text-primary);letter-spacing:-.005em">
        [必填] 1-2 行解释这张图为什么重要,不要重复标题.
      </div>
      <div class="image-hero-stats" style="gap:4vw">
        <div style="display:flex;flex-direction:column;gap:.6vh"><div style="height:1px;background:var(--ink)"></div><div class="t-meta">Metric 01</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.6vw,7.6vh);line-height:.95;letter-spacing:-.04em">12×</div><div style="height:1px;background:var(--border-subtle);margin-top:auto"></div><p class="body-sm">[必填] 指标解释</p></div>
        <div style="display:flex;flex-direction:column;gap:.6vh"><div style="height:1px;background:var(--ink)"></div><div class="t-meta">Metric 02</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.6vw,7.6vh);line-height:.95;letter-spacing:-.04em">3.4h</div><div style="height:1px;background:var(--border-subtle);margin-top:auto"></div><p class="body-sm">[必填] 指标解释</p></div>
        <div style="display:flex;flex-direction:column;gap:.6vh"><div style="height:1px;background:var(--ink)"></div><div class="t-meta">Metric 03</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.6vw,7.6vh);line-height:.95;letter-spacing:-.04em;color:var(--accent)">100%</div><div style="height:1px;background:var(--border-subtle);margin-top:auto"></div><p class="body-sm">[必填] 指标解释</p></div>
      </div>
    </div>
  </div>
</section>
```

---

## 历史实验区(默认禁用)

下面的 P23/P24 是早期为了探索图文混排加入的实验版式。它们不属于原始 22P,默认不要用于正式生成。除非用户明确说“我要实验新图文版式”,否则请使用 S22 或 S15/S16 的图片槽位。

### P23 · Swiss Image Split · 左文右图 / 右文左图(实验,默认禁用)

**用途**:解释一个观点时配一张纪实照片、信息图、UI 情景图或系统关系图。
**适用内容类型**:**一个核心论点 + 一张核心图片**。适合"左侧大标题 + 右侧图片证据"或"左图右说明"。如果图片是整页主角且需要 KPI,用 P22;如果是多张图片,用 P24。
**骨架**:`.canvas-card` 内 head 上下叠 / 主体 `.swiss-img-split` 两列(5:7 或 reverse 7:5) / 图片下方 `.swiss-img-caption`。
**关键类**:`.swiss-img-split` `.swiss-img-copy` `.frame-img.r-16x10.fit-contain|cover` `.swiss-img-caption`
**动效 recipe**:`grid-reveal` — head 先入,图片和文字块错峰出现
**注意**:
- 图片通常与正文首行对齐,不要与大标题顶端齐平;可在图片列加 `padding-top:1vh` 到 `3vh`
- 如果希望左侧内容块与右侧图片底部对齐,使用 `.swiss-img-split.align-image-bottom`,不要靠额外空行硬推
- `.align-image-bottom` 已内置底部 nav safe zone;不要再额外把图片或 caption 往页面底部推
- 左侧内容块避免无意义分割线;除非需要章节感,不要额外插入 `.rule`
- 信息图/UI 图必须 `.fit-contain`;纪实照片默认 cover
- 右图宽度大,标题不要超过 3 行,正文控制在 2-3 个短段或 3 条 bullet

```html
<section class="slide light" data-animate="grid-reveal">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">Section · Visual Argument</div>
      <div class="r">23 / NN</div>
    </div>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:5vh">
      <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
        <div class="t-meta">Evidence · GPT-M 2.0</div>
        <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(7vw,12vh);line-height:.96;letter-spacing:-.035em">[必填] 一句核心论点</h2>
      </div>
      <div class="swiss-img-split align-image-bottom" data-anim="up">
        <div class="swiss-img-copy">
          <div class="t-cat" style="color:var(--accent)">Why it matters</div>
          <p class="lead" style="font-weight:300;max-width:36ch">[必填] 2-3 行解释图片与论点的关系.</p>
          <div class="body" style="font-weight:300;color:var(--text-secondary)">[必填] 可以放 2-3 条短 bullet 或一段说明,保持左对齐和充足留白.</div>
        </div>
        <figure class="tile">
          <div class="frame-img r-16x10 fit-contain">
            <img src="images/23-visual-evidence.png" alt="[必填] 图片说明">
          </div>
          <figcaption class="swiss-img-caption"><strong>[必填] 图片标题</strong><span>16:10 · fit-contain</span></figcaption>
        </figure>
      </div>
    </div>
  </div>
</section>
```

---

### P24 · Swiss Evidence Grid · 多图证据墙(实验,默认禁用)

**用途**:三张同类型图片/截图/图表并列,展示证据链或多案例对比。
**适用内容类型**:**2-3 张同类图片**。适合 UI 截图重绘、流程图三段、三个案例实拍、三张数据小图。不同类型混放会破坏瑞士风秩序。
**骨架**:head 上下叠 / `.swiss-img-grid` 三列 / 每张 tile 用同一个 `.h-22` 或 `.h-26`。
**关键类**:`.swiss-img-grid` `.frame-img.h-22|h-26` `.fit-contain` `.swiss-img-caption`
**动效 recipe**:`grid-reveal`
**注意**:
- 同组图片必须同一比例、同一高度、同一边距密度;不要一张 16:9、一张 4:3、一张长条截图混排
- 标题区和图片区之间必须有明显缓冲;模板里的 `.swiss-img-grid` 默认带顶部间距,只有在外层 grid 已经给足 gap 时才加 `.tight`
- UI/信息图统一 `.fit-contain`;照片统一 cover
- 如果用户原始截图比例混乱,先用 GPT-M 2.0 重生成同一比例的"截图再设计"

```html
<section class="slide light" data-animate="grid-reveal">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">Section · Evidence Grid</div>
      <div class="r">24 / NN</div>
    </div>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:6vh">
      <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
        <div class="t-meta">Three visual proofs</div>
        <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(6.6vw,11.6vh);line-height:.96;letter-spacing:-.035em">[必填] 三个证据,一个结论</h2>
      </div>
      <div class="swiss-img-grid" data-anim="up">
        <figure class="tile"><div class="frame-img h-26 fit-contain"><img src="images/24-proof-a.png" alt="[必填]"></div><figcaption class="swiss-img-caption"><strong>01</strong><span>[必填] 证据 A</span></figcaption></figure>
        <figure class="tile"><div class="frame-img h-26 fit-contain"><img src="images/24-proof-b.png" alt="[必填]"></div><figcaption class="swiss-img-caption"><strong>02</strong><span>[必填] 证据 B</span></figcaption></figure>
        <figure class="tile"><div class="frame-img h-26 fit-contain swiss-lined"><img src="images/24-proof-c.png" alt="[必填]"></div><figcaption class="swiss-img-caption"><strong>03</strong><span>[必填] 关键证据</span></figcaption></figure>
      </div>
    </div>
  </div>
</section>
```

---

## 选版式索引(给 LLM 的决策表)

| 内容意图 | 推荐版式 |
|---|---|
| Deck 起手封面 | P1 Cover |
| 演化对比 / 时间轴(纵) | P2 Vertical Timeline |
| 一句口号 / 章节起 | P3 Statement / P10 Dot Matrix |
| 6 项概念定义 | P4 Six Cells |
| 三步流程(轻) | P5 Three Sub-cards |
| 4 项数据视觉化高度对比 | P6 KPI Tower |
| 5-10 项排名比较 | P7 H-Bar Chart |
| Before/After / 双轨对照 | P8 Duo Compare |
| 整 deck 收尾 | P9 Closing Manifesto |
| 多步流程(横,4-7 步) | P11 Horizontal Timeline |
| 阶段性结论 + ink 通栏 | P12 Manifesto + Banner |
| 3 个对等概念深化 | P13 Three Forces Cards |
| 闭环流程 / 自学循环 | P14 Loop Diagram |
| 8-12 项矩阵 + 总数据 | P15 Image Matrix |
| 6 项快讯小卡 | P16 Multi-card Brief |
| 层级架构 / 同心圆系统 | P17 System Diagram |
| 三论点 + 数据支撑 | P18 Why Now |
| 4 项等权特性 | P19 Four Cards |
| 4-6 行账单式 KPI | P20 Stacked Ledger |
| 产品规格 / benchmark | P21 Tech Spec |
| 案例图 + 数据落地 | P22 Image Hero |
| 单图解释论点 / 图文混排 | P23 Swiss Image Split |
| 2-3 张图片/截图/图表证据链 | P24 Swiss Evidence Grid |

---

## 选版式 P0 原则:内容数据类型必须匹配版式

> 这是写 deck 时**最容易踩雷**的地方。版式承载内容的「形状」是固定的——你必须先看内容,再选版式,**绝不能先选版式再编内容硬塞**。

| 内容类型 | 必须用 | 严禁用 |
|---|---|---|
| 有真实量化数据(百分比/数值) | P6 KPI Tower / P7 H-Bar / P20 Ledger / P21 Tech Spec | P3 / P4 / P10 / P13(无数据版式) |
| 无数据,纯定性论断 | P3 / P10 Statement / P12 / P13 / P19 | ⚠️ **P7 H-Bar / P6 KPI Tower**(编造数据会被识破) |
| 4 项对等 | P19 Four Cards / P6(若有数据) | 不能强凑成 6 用 P4 |
| 6 项对等 | P4 Six Cells / P16 Brief | 不能强凑成 4 用 P19 |
| 3 项对等 | P5 Sub-cards / P13 Three Forces | |
| Before/After | P8 Duo Compare(必须正好 2 项) | |
| 闭环结构 | P14 Loop Diagram | P11 横向流程(线性 ≠ 闭环) |
| 三层嵌套 | P17 System Diagram | |
| 时间演化(有数据) | P2 Vertical Timeline | |
| 多步骤流程(无数据) | P11 Horizontal Timeline | |
| 8-12 项同类 | P15 Image Matrix | |
| deck 收尾 | P9 Closing(每 deck 仅 1 次) | |
| 1 张核心图片 + 一段解释 | P23 Swiss Image Split | P22(除非图片是主角且有 KPI) |
| 2-3 张同类图片 | P24 Evidence Grid | P4/P16(文字卡片,不是图片证据) |

**雷区案例**:用 P7 H-Bar Chart 展示「智能补全 / 实时协作 / 自主代理」这种**无可比百分比的概念列举**,编造 96/88/78 之类数字 → **数据不可信,版式滥用**。这种内容应该用 P2(若有时间维度)或 P3 Statement(若是论断)。

---

## 常犯错误(P0 检查项)

1. ❌ 给卡片加 `border-radius` → ✅ 必须直角
2. ❌ 在 `.card-accent` 上又加描边 → ✅ 卡片填充类型互斥
3. ❌ 自己画 SVG 图标 → ✅ 用 `lucide` 线上库,棱角风格
4. ❌ 时间线 dot 用 grid `justify-self` 对齐虚线 → ✅ axis 列固定 12px + dot 绝对定位
5. ❌ 大字号不限高(`13vw`)→ ✅ 永远 `min(Xvw, Yvh)` 双约束
6. ❌ ESC 索引页缩略图看不到带动效内容 → ✅ 给 cloned slide 加可见性 override CSS
7. ❌ 所有页用同一个 fade-up recipe → ✅ 每页一个语义化 recipe,与图形耦合
8. ❌ 标题 + 卡片间距 < 5vh → ✅ 章节级标题至少 9vh
9. ❌ 9px 圆形装饰点 → ✅ 8×8 直角小方块 / mono `t-meta` 文字
10. ❌ 装饰元素超出页面边距 → ✅ 严格在 grid 内,不贴边

# 页面布局库（Layouts）

本文档收录 10 种最常用的页面布局骨架。每种都是一个完整可粘贴的 `<section class="slide ...">...</section>` 代码块，直接替换文案/图片即可使用。

---

## ⚠️ 生成前必读（Pre-flight）

### A. 类名必须来自 template.html

layouts.md 使用的所有类（`h-hero` / `h-xl` / `h-sub` / `h-md` / `lead` / `meta-row` / `stat-card` / `stat-label` / `stat-nb` / `stat-unit` / `stat-note` / `pipeline-section` / `pipeline-label` / `pipeline` / `step` / `step-nb` / `step-title` / `step-desc` / `grid-2-7-5` / `grid-2-6-6` / `grid-2-8-4` / `grid-3-3` / `grid-6` / `grid-3` / `grid-4` / `frame` / `frame-img` / `img-cap` / `callout` / `callout-src` / `kicker`）都在 `assets/template.html` 的 `<style>` 块里预定义。

**不要发明新类名**。如果必须自定义，用 `style="..."` inline 写。生成前若不确定某个类是否存在，grep template.html 确认。

### B. 图片比例规范（非常重要）

**永远用标准比例**，不要用原图 `aspect-ratio: 2592/1798` 这种奇葩比例：

| 场景 | 推荐比例 | 写法 |
|------|---------|------|
| 左文右图 主图 | 16:10 或 4:3 | `.frame-img.r-16x10` 或 `.frame-img.r-4x3` |
| 图片网格（多图对比） | 统一 | `.frame-img.h-22` / `.frame-img.h-26`，不用 aspect-ratio |
| 小型面板组 | 统一 | `.frame-img.h-16` / `.frame-img.h-18`，同组必须同高 |
| 左小图 + 右文字 | 1:1 或 3:2 | `.frame-img.r-1x1` 或 `.frame-img.r-3x2` |
| 全屏主视觉 | 16:9 | `.frame-img.r-16x9` |
| 信息图 / 截图再设计 | 16:9 或 16:10 | `.frame-img.r-16x9.fit-contain` 或 `.frame-img.r-16x10.fit-contain` |
| 图文混排小插图 | 3:2 或 3:4 | `.frame-img.r-3x2` 或 `.frame-img.r-3x4` |

图片必须包在 `<figure class="frame-img">` 里。默认照片会 `object-fit:cover + object-position:top center`,只裁底部,不裁顶/左/右。信息图和截图再设计必须加 `.fit-contain`,避免文字或标注被裁切。

### B2. 图片与内容的垂直对齐

图片应该跟正文内容区对齐,不要默认贴到大标题顶端。特别是左文右图和图文混排页:

- 如果左列是 kicker + 大标题 + 正文 + callout,右列图片通常从正文高度开始,可给图片加 `style="margin-top:7vh"` 到 `9vh`
- 如果图片是信息图或 UI 情景图,优先对齐正文首行或说明文字,不要和超大标题顶端齐平
- 如果一张截图/UI 情景图在横向页面里变成很长的条,不要硬拉满宽;改成极宽横图素材,或拆成 2-3 个局部面板拼排
- 多图面板必须使用同一个高度类,不要混用 `h-16` / `h-22` 或手写不同 `height`

### B3. 标题与正文的间距

- 两段式页面(顶部标题 + 下方长正文/引用/图表)必须在标题和内容之间留出明显间距,推荐 `margin-top:6vh` 到 `8vh`
- 居中大标题页必须让主标题在页面水平居中,使用 `.center` 或 `text-align:center; margin-inline:auto`
- 复杂内容页(大标题 + 小标题 + 详细内容)要让大标题和下方内容分层,下方内容使用左右两端对齐的 grid 或 rowline,不要全部堆在一条中轴线上

### C. 图片定位准则（避免图片堆到页面最底部、被浏览器工具栏遮挡）

**错误做法**（已踩坑，不要再犯）：
- 在非 grid 容器里用 `align-self:end`：`align-self` 在 flex/grid 之外完全无效，图片会掉到文档流末尾堆底
- 用 `position:absolute + bottom:0` 把图"固定"到底：会被底部 `.foot` 和 `#nav` 圆点遮挡
- 单张图片只写 `height:N vh` 不限 `max-height`：在低分屏会撑出视口

**正确做法**：
- 图文混排**必须用 `.frame.grid-2-7-5`**（或 `.grid-2-6-6` / `.grid-2-8-4`）的 grid 结构
- grid 容器默认 `align-items:start`（已在 template 中设置），图片自然贴到 cell 顶端
- 如果需要"图片底对齐左列 callout"：**左列用 flex column + `justify-content:space-between`**（让 callout 自己贴左列底），**右列 figure 直接保持 align-items:start 即可**，不要加 `align-self:end`
- 所有 grid 父容器建议加 inline `style="padding-top:6vh"`，给标题区留呼吸空间

### D. 主题色与主题节奏

- 主题色从 `references/themes.md` 的 5 套预设里选一套,不允许自定义 hex 值
- 主题节奏(每页用 light / dark / hero light / hero dark 哪一个)在下文"主题节奏规划"一节有硬规则,生成前必读
- 两件事都要在挑布局之前决定,避免返工

### E. 动效系统(默认开启 · Motion One 驱动)

**核心机制**:template.html 底部的 module script 会在翻页时触发入场动画。所有带 `data-anim` 的元素初始不可见,翻到当前页时由 Motion One 逐个淡入。

**动效策略**:在 `<section>` 上加 `data-animate="<recipe>"` 选择动画风格;每个需要入场动画的元素加 `data-anim`(可选附值,如 `left` / `right` / `line` / `step`)。

| recipe | 用法 | 适合布局 |
|---|---|---|
| 默认(cascade) | 什么也不加,自动级联淡入 | 大部分正文页(Layout 3 / 4 / 5 / 10) |
| `hero` | `.hero` 页自动启用,节奏更慢更仪式感 | Layout 1 / 2 / 7(所有 hero 页) |
| `quote` | 一句一句揭示,慢节奏(550ms stagger) | Layout 8 大引用 |
| `directional` | 左进 → 分割 → 右进,用于对比 | Layout 9 Before/After |
| `pipeline` | 手动推进,按 →/空格 一步步点亮 | Layout 6 流水线 |

**降级保底**:如果 motion.min.js 本地 + CDN 都加载失败,脚本会强制把所有 `data-anim` 元素设为 `opacity:1`,内容永远可读。

**不需要动效的页面**:如果某页想完全跳过动效,不加任何 `data-anim` 即可 —— Motion One 只对带标记的元素生效。

---

## 0. 基础结构（所有 slide 都一样）

```html
<section class="slide [light|dark|hero light|hero dark]">
  <div class="chrome">
    <div>上下文标签 · 子标签</div>
    <div>ACT · 页号 / 总页数</div>
  </div>
  <!-- 主内容 -->
  <div class="foot">
    <div>页码说明 · Page Description</div>
    <div>— · —</div>
  </div>
</section>
```

- 非 hero 页建议加 `light` 或 `dark` 主题；hero 页加 `hero light` 或 `hero dark`（参与 WebGL 主题插值）
- `chrome` 和 `foot` 是可选但推荐保留的上下左右四角元数据
- **hero 页用于章节封面/开场/收束/转场**，非 hero 页用于正文

### ⚠️ chrome 和 kicker 不要写同一句话

这是最常见的内容重复问题。两者在语义上完全不同的维度：

| 位置 | 角色 | 内容性质 | 例子 |
|------|------|---------|------|
| `.chrome` 左上 | **杂志页眉 / 导航元数据** | 稳定的"栏目名"或"章节分类"，跨多页可以相同 | "Act II · Workflow" / "Data · Result" / "lukew.com · 2026.04" |
| `.chrome` 右上 | **页号 + 幕号** | 固定格式 | "Act II · 15 / 25" |
| `.kicker` | **这一页独一份的引导句** | 是大标题的"小前缀"，像杂志大标题上方的一行话，每页都应不同 | "BUT" / "一个人,做了什么。" / "Phase 01 · 设计阶段" |

**反例**（已踩坑）：chrome 写"设计先行 · Design First"，kicker 又写"Phase 01 · 设计阶段"——意思重复，读者一眼就觉得 AI 生成的。

**正确做法**：chrome 是**栏目标签**（稳定、跨页可复用），kicker 是**本页钩子**（短句、有戏剧性），两者互为补充，不互相翻译。

### ⚠️ 主题节奏规划（必读 · 生成前必做)

**核心机制**:每页 `<section>` 必须带 `light` / `dark` / `hero light` / `hero dark` 之一。JS 根据 class 推断主题,决定 body 加不加 `light-bg`,从而切换暗/亮两张 WebGL canvas 哪张在前。不带主题或写自定义名 = fallback 出错。

#### 按布局的主题默认值

| Layout | 默认主题 | 原因 |
|---|---|---|
| 1. 开场封面 | `hero dark` | 开场仪式感,暗底强冲击 |
| 2. 章节幕封 | `hero dark` 与 `hero light` **必须交替** | 呼吸节奏 |
| 3. 大字报(数据) | `light` | 数字需纸白底;多幕连发时可偶插 `dark` |
| 4. 左文右图 | **`light` / `dark` 交替** | 正文节奏主力 |
| 5. 图片网格 | `light` | 截图需亮底 |
| 6. Pipeline | `light` | 流程图需清晰 |
| 7. 问题页 | `hero dark` | 强视觉冲击默认 |
| 8. 大引用 | **`dark` 优先**,偶用 `light` | 金句仪式感靠暗底 |
| 9. 对比页 | `light` | 双列需清晰 |
| 10. 图文混排 | **`light` / `dark` 交替** | 节奏 |

#### 节奏硬规则(生成后 grep 自检)

- ❌ **禁止**连续 3 页以上相同主题(包括 light 堆叠和 dark 堆叠)
- ❌ **禁止**8 页以上的 deck 没有至少 1 个 `hero dark` + 1 个 `hero light`
- ❌ **禁止**整个 deck 只有 `light` 正文页没有任何 `dark` 正文页——会显得平淡、没呼吸
- ✅ **推荐**每 3-4 页插入 1 个 hero(封面/幕封/问题/大引用)

#### 8 页节奏模板(可直接套用)

| 页 | 主题 | 布局 | 备注 |
|---|---|---|---|
| 1 | `hero dark` | 封面 | 开场 |
| 2 | `light` | 大字报 | 数据抛出 |
| 3 | `dark` | 左文右图 | 对比/故事 |
| 4 | `light` | Pipeline | 流程 |
| 5 | `hero light` | 章节幕封 | 呼吸 |
| 6 | `dark` | 左文右图 or 大引用 | |
| 7 | `hero dark` | 问题页 | 悬念收束 |
| 8 | `light` | 大引用/结尾 | 收尾 |

**先画这张表对齐,再动手写 slide**。跳过规划直接粘骨架 = 全是 light。

---

## Layout 1: 开场封面（Hero Cover）

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>A Talk · 2026.04.22</div>
    <div>Vol.01</div>
  </div>
  <div class="frame" style="display:grid; gap:4vh; align-content:center; min-height:80vh">
    <div class="kicker" data-anim>私享会 · 李继刚</div>
    <h1 class="h-hero" data-anim>一人公司</h1>
    <h2 class="h-sub" data-anim>被 AI 折叠的组织</h2>
    <p class="lead" style="max-width:60vw" data-anim>
      一个 AI 创作者 —— 在 64 天里做了 11 万行代码、在 9 个平台上持续输出，生活节奏几乎没有被改变。
    </p>
    <div class="meta-row" data-anim>
      <span>歸藏 Guizang</span><span>·</span><span>独立创作者 / CodePilot 作者</span>
    </div>
  </div>
  <div class="foot">
    <div>一场关于 AI · 组织 · 个体的分享</div>
    <div>— 2026 —</div>
  </div>
</section>
```

**要点**：
- 用 `hero dark` 让 WebGL 背景在大部分区域透出
- `h-hero` 是最大字号（10vw），这里作标题主视觉
- 用 `min-height:80vh + align-content:center` 让内容整体垂直居中
- 不需要 `.chrome` 里写页码，封面页自成一体

---

## Layout 2: 章节幕封（Act Divider）

```html
<section class="slide hero light">
  <div class="chrome">
    <div>第一幕 · 硬数据</div>
    <div>Act I · 01 / 25</div>
  </div>
  <div class="frame" style="display:grid; gap:6vh; align-content:center; min-height:80vh">
    <div class="kicker" data-anim>Act I</div>
    <h1 class="h-hero" style="font-size:8.5vw" data-anim>硬数据</h1>
    <p class="lead" style="max-width:55vw" data-anim>
      先看数字，再谈方法。
    </p>
  </div>
  <div class="foot">
    <div>第一幕引子</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：
- 极简，只需要 kicker + 大标题 + 一行引语
- 两个幕的封面可以交替 `hero light` / `hero dark`，制造节奏
- `h-hero` 字号可以从 10vw 调到 8.5vw 适配长短

---

## Layout 3: 数据大字报（Big Numbers Grid）

```html
<section class="slide light">
  <div class="chrome">
    <div>过去 64 天 · 开发篇</div>
    <div>Act I / Dev · 02 / 25</div>
  </div>
  <div class="frame" style="padding-top:6vh">
    <div class="kicker" data-anim>一个人，做了什么。</div>
    <h2 class="h-xl" data-anim>过去 64 天</h2>
    <p class="lead" style="margin-bottom:5vh" data-anim>从 0 到开源 CodePilot。</p>

    <div class="grid-6" style="margin-top:6vh">
      <div class="stat-card" data-anim>
        <div class="stat-label">Duration</div>
        <div class="stat-nb">64 <span class="stat-unit">天</span></div>
        <div class="stat-note">从 0 到现在</div>
      </div>
      <div class="stat-card" data-anim>
        <div class="stat-label">Lines of Code</div>
        <div class="stat-nb">110K+</div>
        <div class="stat-note">一行行写到 11 万+</div>
      </div>
      <div class="stat-card" data-anim>
        <div class="stat-label">GitHub Stars</div>
        <div class="stat-nb">5,166</div>
        <div class="stat-note">一个开源仓库</div>
      </div>
      <div class="stat-card" data-anim>
        <div class="stat-label">Downloads</div>
        <div class="stat-nb">41K+</div>
        <div class="stat-note">装到了几万台电脑里</div>
      </div>
      <div class="stat-card" data-anim>
        <div class="stat-label">AI Providers</div>
        <div class="stat-nb">19</div>
        <div class="stat-note">跨平台接入</div>
      </div>
      <div class="stat-card" data-anim>
        <div class="stat-label">Commits</div>
        <div class="stat-nb">608+</div>
        <div class="stat-note">没有协作者</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>项目 · CodePilot　|　github.com/codepilot</div>
    <div>Act I · Dev Numbers</div>
  </div>
</section>
```

**要点**：
- 3×2 或 4×2 网格最稳（见 `.grid-6`）
- 每个 `stat-card` 结构固定：label（英文小字）→ nb（大字数字）→ note（注释）
- 数字建议 2-3 位字符（太长会溢出），用 K / M 简写
- 留 5vh 以上的上方缓冲，让标题区先抢眼球

---

## Layout 4: 左文右图（Quote + Image）

```html
<section class="slide light">
  <div class="chrome">
    <div>身份反差 · The Twist</div>
    <div>03 / 25</div>
  </div>
  <div class="frame grid-2-7-5" style="padding-top:6vh">
    <!-- 左列：标题 + 正文 + callout，flex column 让 callout 贴列底 -->
    <div style="display:flex; flex-direction:column; justify-content:space-between; gap:3vh">
      <div>
        <div class="kicker" data-anim>BUT</div>
        <h2 class="h-xl" style="white-space:nowrap; font-size:7.2vw" data-anim>
          我不是程序员。
        </h2>
        <p class="lead" style="margin-top:3vh" data-anim>
          大学毕业之后再也没写过一行代码。过去十年做的是 UI 设计和 AI 特效。
        </p>
      </div>
      <div class="callout" data-anim>
        "这东西在三年前，<br>
        需要一个十人团队做一年。"
        <div class="callout-src">— 一个观察者的判断</div>
      </div>
    </div>
    <!-- 右列：图片用标准 16/10 比例 + max-height，不要 align-self:end -->
    <figure class="frame-img r-16x10" data-anim>
      <img src="images/codepilot.png" alt="CodePilot 产品截图">
      <figcaption class="img-cap">CodePilot · 产品截图</figcaption>
    </figure>
  </div>
  <div class="foot">
    <div>Page 03 · 我不是程序员</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：
- 用 `grid-2-7-5`（左 7 份、右 5 份），`align-items:start` 已在 template 预设
- **左列**用 flex column + `justify-content:space-between`：标题贴顶，callout 自然贴底
- **右列图片** **不要加 `align-self:end`**。会让图片滑到 cell 底部，低分屏下被浏览器工具栏遮挡
- 图片必须用 **标准比例类 `.r-16x10` 或 `.r-4x3`**，不要用原图奇葩比例（`2592/1798` 这种）

---

## Layout 5: 图片网格（多图对比）

```html
<section class="slide light">
  <div class="chrome">
    <div>平台粉丝实证</div>
    <div>Act I / Ops · 05 / 27</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker" data-anim>Proof · 粉丝实证</div>
    <h2 class="h-xl" data-anim>10 个平台 · 6 张截图</h2>

    <div class="grid-3-3" style="margin-top:4vh">
      <figure class="frame-img" style="height:26vh" data-anim>
        <img src="images/weibo.png" alt="微博 289K">
        <figcaption class="img-cap">微博 · 289K</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh" data-anim>
        <img src="images/twitter.png" alt="推特 137K">
        <figcaption class="img-cap">推特 · 137K</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh" data-anim>
        <img src="images/wechat.png" alt="公众号 96K">
        <figcaption class="img-cap">公众号 · 96K</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh" data-anim>
        <img src="images/jike.png" alt="即刻 26K">
        <figcaption class="img-cap">即刻 · 26K</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh" data-anim>
        <img src="images/xhs.png" alt="小红书 19K">
        <figcaption class="img-cap">小红书 · 19K</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh" data-anim>
        <img src="images/douyin.png" alt="抖音 10K">
        <figcaption class="img-cap">抖音 · 10K</figcaption>
      </figure>
    </div>
  </div>
  <div class="foot">
    <div>截图时间 · 2026.04</div>
    <div>Page 05 · 粉丝实证</div>
  </div>
</section>
```

**要点**：
- 关键：每个 `frame-img` 必须写死 `height:NNvh`（不要用 `aspect-ratio`），否则网格会撑破
- 图片会自动 `object-fit:cover + object-position:top`，只裁底部
- 用 `.grid-3-3`（3×2）或 `.grid-3`（3×1）承载

---

## Layout 6: 两列流水线（Pipeline）

```html
<section class="slide light" data-animate="pipeline">
  <div class="chrome">
    <div>我的工作流 · Workflow</div>
    <div>Act II · 15 / 27</div>
  </div>
  <div class="frame">
    <div class="kicker">Pipeline · 流水线</div>
    <h2 class="h-xl">两条流水线</h2>

    <!-- 第一组：文本侧 -->
    <div class="pipeline-section">
      <div class="pipeline-label">文本侧 · Text Pipeline</div>
      <div class="pipeline">
        <div class="step" data-anim="step">
          <div class="step-nb">01</div>
          <div class="step-title">Draft</div>
          <div class="step-desc">AI 帮我起草初稿</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-nb">02</div>
          <div class="step-title">Polish</div>
          <div class="step-desc">AI 润色去 AI 味</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-nb">03</div>
          <div class="step-title">Morph</div>
          <div class="step-desc">AI 变形成推特 / 小红书</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-nb">04</div>
          <div class="step-title">Illustrate</div>
          <div class="step-desc">AI 生成信息图</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-nb">05</div>
          <div class="step-title">Distribute</div>
          <div class="step-desc">一键分发 9 平台</div>
        </div>
      </div>
    </div>

    <!-- 第二组：视频侧 -->
    <div class="pipeline-section">
      <div class="pipeline-label">视觉 · 视频侧 · Video Pipeline</div>
      <div class="pipeline">
        <div class="step" data-anim="step">
          <div class="step-nb">06</div>
          <div class="step-title">Cut</div>
          <div class="step-desc">AI 帮我剪辑</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-nb">07</div>
          <div class="step-title">Wrap</div>
          <div class="step-desc">AI 帮我包装</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-nb">08</div>
          <div class="step-title">Cover</div>
          <div class="step-desc">AI 生成封面</div>
        </div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 15 · 我的内容工厂</div>
    <div>Workflow</div>
  </div>
</section>
```

**要点**：
- 用 `.pipeline-section` 分组 + `.pipeline-label` 作组标题
- 两组之间用 3.6vh 的间距 + 顶部细分隔线（已在 CSS 中预设）
- 每个 step 是固定的 nb → title → desc 结构
- 步骤数不限但单行最好 ≤5 个，否则换到第二 pipeline
- **动效**:`<section>` 加 `data-animate="pipeline"`,每个 `.step` 加 `data-anim="step"`。翻到此页时步骤默认 `opacity:.15`,按 →/空格/滚轮下滑时一次点亮一个 step;**所有 step 点亮完才会翻到下一页**,可制造演讲互动感

---

## Layout 7: 悬念收束 / 问题页（Hero Question）

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>留给你的问题</div>
    <div>24 / 27</div>
  </div>
  <div class="frame" style="display:grid; gap:8vh; align-content:center; min-height:80vh">
    <div class="kicker" data-anim>The Question</div>
    <h1 class="h-hero" style="font-size:7vw; line-height:1.15">
      <span data-anim style="display:block">你的公司里，</span>
      <span data-anim style="display:block">哪些岗位本来就</span>
      <span data-anim style="display:block">不该由人来做？</span>
    </h1>
    <p class="lead" style="max-width:50vw" data-anim>
      这个问题，不是技术问题，是架构问题。
    </p>
  </div>
  <div class="foot">
    <div>Page 24 · The Question</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：
- Hero 页留白越多越好，只放一个问题
- `h-hero` 字号视长度调整（7vw 适合 3 行，10vw 适合 1 行）
- 用 `<br>` 手工断行，确保断点在语义处
- 尾巴可以再给一行 `lead` 作为点破

---

## Layout 8: 大引用页（Big Quote · 衬线金句）

```html
<section class="slide light" data-animate="quote">
  <div class="chrome">
    <div>The Takeaway · 核心金句</div>
    <div>18 / 25</div>
  </div>
  <div class="frame" style="display:grid; gap:5vh; align-content:center; min-height:80vh">
    <div class="kicker" data-anim>Quote · 金句</div>
    <blockquote style="font-family:var(--serif-zh); font-weight:700; font-size:5.8vw; line-height:1.2; letter-spacing:-.01em; max-width:72vw">
      <span data-anim="line" style="display:block">"没有交接,</span>
      <span data-anim="line" style="display:block">所有人都在构建。"</span>
    </blockquote>
    <p class="lead" style="max-width:55vw; opacity:.65" data-anim>
      Without the handoff, everyone builds.<br>
      And that makes all the difference.
    </p>
    <div class="meta-row" data-anim>
      <span>— Luke Wroblewski</span><span>·</span><span>2026.04.16</span>
    </div>
  </div>
  <div class="foot">
    <div>Page 18 · 金句</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：
- 整页留白,只放一个大引用 + 出处
- `<blockquote>` 用 inline style 单独放大（5-6vw）,不要用 `h-hero`（那是页面主标题的命名）
- 下面跟随英文原文（lead · opacity:.65）制造层级
- 配 `meta-row` 写出处 · 日期

---

## Layout 9: 并列对比（A vs B · 旧 vs 新）

```html
<section class="slide light" data-animate="directional">
  <div class="chrome">
    <div>旧 vs 新 · The Shift</div>
    <div>12 / 25</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker" data-anim>Before / After · 范式转变</div>
    <h2 class="h-xl" style="margin-bottom:4vh" data-anim>从交接到共建</h2>

    <div class="grid-2-6-6" style="gap:5vw 4vh">
      <!-- 左列：旧 -->
      <div data-anim="left" style="padding:3vh 2vw; border-left:3px solid currentColor; opacity:.55">
        <div class="kicker" style="opacity:.9">Before · 旧模式</div>
        <h3 class="h-md" style="margin-top:2vh">设计 → 开发 → 交接</h3>
        <ul style="margin-top:3vh; padding-left:1.2em; display:flex; flex-direction:column; gap:1.4vh; font-family:var(--sans-zh); font-size:max(14px,1.1vw); line-height:1.55">
          <li>设计师在 Figma 做稿</li>
          <li>开发者盯着文件翻译像素</li>
          <li>反复 PR 沟通对齐</li>
          <li>非技术人员无法触碰代码</li>
        </ul>
      </div>
      <!-- 右列:新 -->
      <div data-anim="right" style="padding:3vh 2vw; border-left:3px solid currentColor">
        <div class="kicker" style="opacity:.9">After · 新模式</div>
        <h3 class="h-md" style="margin-top:2vh">同工具 · 并行 · 共建</h3>
        <ul style="margin-top:3vh; padding-left:1.2em; display:flex; flex-direction:column; gap:1.4vh; font-family:var(--sans-zh); font-size:max(14px,1.1vw); line-height:1.55">
          <li>三个角色同时在 Intent 工作</li>
          <li>agents.md 作为共享上下文</li>
          <li>代理处理对齐 / 冲突 / 动画</li>
          <li>任何人都能安全贡献代码</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 12 · 范式转变</div>
    <div>Before / After</div>
  </div>
</section>
```

**要点**：
- 用 `.grid-2-6-6`（1:1）左右分半
- 左列 `opacity:.55` 做"旧"的视觉弱化,右列满亮度做"新"的突出
- 两列都用 `border-left:3px solid` + `padding-left` 做引用块感
- 每列结构统一:`kicker` → `h-md` → `<ul>` 要点,节奏一致

---

## Layout 10: 图文混排（Lead Image + Side Text）

```html
<section class="slide light">
  <div class="chrome">
    <div>Design First · 设计先行</div>
    <div>08 / 16</div>
  </div>
  <div class="frame grid-2-8-4" style="padding-top:6vh">
    <!-- 左列:大段正文 + 引用 -->
    <div>
      <div class="kicker" data-anim>Phase 01 · 设计阶段</div>
      <h2 class="h-xl" style="margin-top:1vh; margin-bottom:3vh" data-anim>设计先行 · 2 周</h2>

      <p class="lead" style="margin-bottom:3vh" data-anim>
        在 Figma 中完成视觉探索与设计系统,网格 / 排版 / 颜色变量 / 可复用组件,桌面和移动端稿件几轮反馈迭代。
      </p>

      <p data-anim style="font-family:var(--sans-zh); font-size:max(14px,1.15vw); line-height:1.75; opacity:.78; margin-bottom:2.4vh">
        两周之内,视觉风格、粗略结构、方向性内容全部稳定。这是扎实的传统设计流程——在这里还没什么新鲜事。
      </p>

      <div class="callout" style="margin-top:3vh" data-anim>
        "This phase was pretty standard.<br>Just a solid Web design process."
        <div class="callout-src">— Luke Wroblewski</div>
      </div>
    </div>
    <!-- 右列:辅助图 · 竖版或方形 -->
    <figure class="frame-img r-3x4" data-anim>
      <img src="images/figma.png" alt="Figma design system">
      <figcaption class="img-cap">Figma · Design System</figcaption>
    </figure>
  </div>
  <div class="foot">
    <div>Page 08 · Design First</div>
    <div>约 2 周</div>
  </div>
</section>
```

**要点**：
- `.grid-2-8-4`(8:4) 让正文占主导,图片作辅助
- 左列包含多种信息层级:kicker → 大标题 → lead → 正文段落 → callout(引用)
- 右列图片用 **竖版 3:4** 或方形 1:1,避免和左列文本竞争注意力
- 这种布局适合**页面信息量偏大**的场景(不像 Layout 4 只有一句金句)

---

## 附录：常用网格模板

| 类名 | 配比 | 用途 |
|---|---|---|
| `.grid-2-6-6` | 6:6（1:1） | 对半分 |
| `.grid-2-7-5` | 7:5 | 文字为主 + 辅助图 |
| `.grid-2-8-4` | 8:4（2:1） | 大段文字 + 小图/数据 |
| `.grid-3` | 1:1:1 | 3 项并列（案例/截图） |
| `.grid-3-3` | 3×2 | 6 图矩阵 |
| `.grid-6` | 3×2 | 6 个数据卡片 |

所有网格都预留 `gap: 3vw 4vh`（水平 3vw、竖直 4vh），可以单独覆写。

---

## 页面节奏建议

一场 25-30 页的分享，推荐以下节奏：

1. **Hero Cover**（第 1 页）
2. **Act Divider**（第一幕开场，hero light 或 hero dark）
3. **Big Numbers**（抛硬数据制造冲击）
4. **Quote + Image**（讲身份反差/挂钩）
5. **Image Grid**（证据支撑）
6. **Hero Question**（幕收束，留悬念）
7. ... 第二幕、第三幕同样节奏 ...
8. **Hero Close**（最后一页，问题或致谢）

hero 页与 non-hero 页应该 **2-3 : 1 比例交错**，不要连续超过 3 页 non-hero，也不要连续超过 2 页 hero。

# Swiss Layout Lock

本文件是瑞士主题的硬约束。它的目的不是增加灵感,而是防止生成时“看起来像 Swiss,但已经脱离原始模板”。

## Golden Source

原始参考文件:

`/Users/guohao/Documents/op7418的仓库/项目/Thin-Harness-Fat-Skills/ppt/index.html`

瑞士主题生成时,除用户明确要求实验版式外,只能从下面登记的 22 个版式中选择。新增首页/尾页可以使用 Skill 里的 IKB ASCII 版本,但正文页必须来自这 22 个版式。

## 生成前硬规则

1. 每个正文页都必须先选一个登记版式,并在 `<section>` 上写 `data-layout="Sxx"`。
2. 不允许临时发明 `P23/P24` 这类未出现在原始 22P 的正文结构。需要图片时,优先使用 `S22 Image Hero`;多图时使用 `S15/S16` 的原始网格骨架做图片格改造,不要发明新的证据墙。
3. 顶部中文标题默认左对齐并贴近左上内容轴。除原始 `S03/S09/S10` 这种 statement/split 版式外,不要把大标题放到页面水平中心。
4. SVG 只能负责几何线条、圆、箭头、路径。不要在 SVG 里写可见文字;所有文字标签用 HTML 放在网格、卡片或 caption 里。
5. 图片槽位和图片生成比例必须绑定。先确定版式和槽位,再生成图片。

## 登记版式

| ID | 原始页 | 名称 | 必须保留的骨架 | 图片规则 |
|---|---:|---|---|---|
| S01 | 01 | Index Cover | 三行 `cover-row`,左大编号,右大标题 | 无 |
| S02 | 02 | Vertical Timeline + KPI | 顶部左对齐标题,中部 `.timeline-v`,底部 `.kpi-row-4` | 无 |
| S03 | 03 | Split Statement | `.slide.split` 双半屏,左巨字,右灰底解释 | 无 |
| S04 | 04 | Six Cells | 顶部左对齐标题,下方 `.sub-grid-3-2` 六卡 | 可把卡片内部换成小图标,不放大图 |
| S05 | 05 | Three Layers | 顶部左对齐标题,下方 `.stack-row` 三大块 | 无 |
| S06 | 06 | KPI Tower | 左标题+右说明,下方不等高 KPI 塔 | 无 |
| S07 | 07 | Horizontal Bar | 左对齐标题,横向条形图 | 无 |
| S08 | 08 | Duo Compare | `.duo-compare` 两列 + 中线 | 无 |
| S09 | 09 | Dot Matrix Statement | 大号 statement + 点阵装饰 | 无 |
| S10 | 10 | Split Closing | `.slide.split` 左巨字右列表 | 无 |
| S11 | 11 | Horizontal Timeline | 原始 `grid-template-columns:auto 1fr` 头部 + `.timeline-h` | 无 |
| S12 | 12 | Manifesto + Ink Banner | 大字 statement + 底部通栏 ink 条 | 无 |
| S13 | 13 | Three Forces | 左 ink hero 块 + 右 3 张卡 | 无 |
| S14 | 14 | Loop Form | 左 4 步列表 + 右几何 loop | SVG 禁止文字,标签改 HTML |
| S15 | 15 | Matrix + Hero Stat | 顶部左对齐标题,中段 6×2 矩阵,底部巨数 | 多图可改造矩阵格,同组统一 `21:9` |
| S16 | 16 | Multi-card Brief | 顶部左对齐标题,下方 3×2 微卡 | 多图可改造卡片内容,同组统一 `21:9` |
| S17 | 17 | System Diagram | 顶部左小标题+右段落,中部几何系统图,底部三列解释 | SVG 禁止文字,标签改 HTML |
| S18 | 18 | Why Now | 三列递进 + 底部巨数 | 无 |
| S19 | 19 | Four Cards | 顶部蓝线 + 四列均分 | 无 |
| S20 | 20 | Stacked KPI Ledger | 纵向账单式巨数 | 无 |
| S21 | 21 | Tech Spec Sheet | 大标题 + 三 KPI + 右下竖线矩阵 | 无 |
| S22 | 22 | Image Hero | 顶部全宽图 + 左上白块标题 + 下方三列 KPI | 主图按 `21:9` 生成,关键主体放中央安全区 |

## 图片槽位规则

### S22 · Hero Strip

- 生成比例: `21:9`
- 图片用途:实拍场景、产品场景、UI 情景图。
- 生成提示词必须包含: `21:9 ultra-wide strip`, `subject centered in the safe middle area`, `no title, no footer, no page chrome, no logo, no border`.
- HTML 容器必须使用原始 S22 的顶部全宽图骨架;不要改成普通居中大图。
- 照片用 `object-fit:cover;object-position:center 35%`。如果是人像/会议场景,不要用 `top center`。
- 信息图/UI 截图如果放 S22,必须重新生成接近 `21:9`,并用 `object-fit:contain` 或保证核心内容在中央 70% 安全区。

### S15/S16 · Multi Image Grid

- 生成比例:统一 `21:9` 或统一 `16:10`,不要混用。
- 同一组图片必须同高、同宽、同一容器背景。
- 图片格必须吸附原始卡片网格,不要让图片自己决定宽高。
- 如果图片是按槽位重新生成的 `s15-grid-21x9` / `s16-brief-21x9`,容器必须用 `.frame-img.r-21x9` 铺满槽位,不要再加 `.fit-contain`,也不要用固定 `height:18vh` 这类短槽把长图缩小。
- `.fit-contain` 只用于必须保留原始比例的用户截图或文字密集图片;一旦决定重生成图片,就应该按槽位比例重生成并铺满。
- 如果原始截图比例不可控,先用 GPT-M 2.0 重生成“截图再设计”,再插入固定槽位。

## 禁止清单

- 禁止 `text-align:center` 用在顶部中文大标题。
- 禁止将顶部标题写进右侧 7.8fr 栏,造成视觉居中。
- 禁止未登记正文页:例如临时 `Swiss Image Split`、`Evidence Grid`、三圆图自绘页。
- 禁止图片容器灰底包白底信息图。
- 禁止 SVG 中出现 `<text>` 作为可见标签。
- 禁止图片默认 `object-position:top center` 用于照片。

# 瑞士国际主义风格 · 主题色预设（Swiss Themes）

4 套基于瑞士国际主义风格（Swiss Style）的高反差配色。**每套都遵循"高级灰白底 + 单一高饱和高亮色"的极简原则**——这是瑞士风的灵魂,不允许混搭多个高亮色。

---

## 使用方法

1. 问用户选哪套（或基于内容推荐一套）
2. 打开 `assets/template-swiss.html` 的 `<style>` 块
3. 找到开头的 `:root{` 块
4. **整体替换**标有"主题色"注释的所有变量：`--paper` / `--paper-rgb` / `--ink` / `--ink-rgb` / `--grey-1` / `--grey-2` / `--grey-3` / `--accent` / `--accent-rgb` / `--accent-on`
5. 其他 CSS 都走 `var(--...)`,无需任何其他改动

---

## 🔵 克莱因蓝 (IKB · International Klein Blue)

**适合**：通用场合、商业发布、AI/科技产品、设计领域分享。最经典的瑞士风配色,绝不出错。
**调性**：纯白底 + IKB 克莱因蓝,极致冷静、理性、有学术感,像 Helvetica Forever 或 Massimo Vignelli 的作品集。

```css
--paper:#fafaf8;
--paper-rgb:250,250,248;
--ink:#0a0a0a;
--ink-rgb:10,10,10;
--grey-1:#f0f0ee;
--grey-2:#d4d4d2;
--grey-3:#737373;
--accent:#002FA7;
--accent-rgb:0,47,167;
--accent-on:#ffffff;
```

**使用要点**：
- IKB 是高饱和深蓝,在大色块（如 `.accent-block`）上极有视觉冲击
- KPI 数字加 `.accent` 类用蓝色,但不要满屏蓝——IKB 一旦泛滥就掉档
- 推荐配合 `dark` 主题页交替使用,黑底高亮 IKB 同样高级

---

## 🟡 柠檬黄 (Lemon · Cadmium Yellow)

**适合**：年轻、运动、零售、消费品、活力主题、Y2K 复古设计。
**调性**：浅米白底 + 柠檬黄,鲜亮、有活力、警示感强,像 IKEA 或 Beck Design 的视觉语言。

```css
--paper:#fafaf8;
--paper-rgb:250,250,248;
--ink:#0a0a0a;
--ink-rgb:10,10,10;
--grey-1:#f0f0ee;
--grey-2:#d4d4d2;
--grey-3:#737373;
--accent:#FFD500;
--accent-rgb:255,213,0;
--accent-on:#0a0a0a;
```

**使用要点**：
- 柠檬黄属于浅色高饱和,**`.accent-on` 必须用纯黑**（不是白）才能保证可读性
- 黄色色块上不要放白字——会糊掉
- 柠檬黄做单字符高亮（`.mark` / `.underline-accent`）效果最强

---

## 🟢 柠檬绿 (Lemon Green · Highlighter Green)

**适合**：生态、可持续、健康、新兴科技、Z 世代品牌、AI 创业项目。
**调性**：浅米白底 + 荧光柠檬绿,有未来感、年轻、当代,像 Acne Studios 或 Off-White 的视觉。

```css
--paper:#fafaf8;
--paper-rgb:250,250,248;
--ink:#0a0a0a;
--ink-rgb:10,10,10;
--grey-1:#f0f0ee;
--grey-2:#d4d4d2;
--grey-3:#737373;
--accent:#C5E803;
--accent-rgb:197,232,3;
--accent-on:#0a0a0a;
```

**使用要点**：
- 荧光绿和黄色一样属于浅色,**`.accent-on` 必须用纯黑**
- 屏幕显色比印刷漂亮,适合演讲投影场景
- 推荐用于"新兴技术"、"未来"主题

---

## 🟠 安全橙 (Safety Orange)

**适合**：工业、警示、运动、施工、汽车工业、技术发布会的"警告/重点"页。
**调性**：浅米白底 + 安全橙,工业感、紧迫感、视觉锚点感,像 Saul Bass 海报或 Highway Gothic 标识系统。

```css
--paper:#fafaf8;
--paper-rgb:250,250,248;
--ink:#0a0a0a;
--ink-rgb:10,10,10;
--grey-1:#f0f0ee;
--grey-2:#d4d4d2;
--grey-3:#737373;
--accent:#FF6B35;
--accent-rgb:255,107,53;
--accent-on:#ffffff;
```

**使用要点**：
- 橙色介于浅色和深色之间,**白字勉强能读但建议加粗**（`font-weight:600` 以上）
- 工业感强,适合涉及"警告"、"决策"、"转折点"的内容
- 不建议整页 `.accent` 模式,橙色满屏会过于刺眼,做局部高亮即可

---

## 推荐选择参考

| 如果是... | 推荐主题 |
|---|---|
| 不知道选啥 / 第一次用 / AI/科技/设计 | 🔵 克莱因蓝 |
| 年轻、活力、消费、零售 | 🟡 柠檬黄 |
| 生态、未来、Z 世代、新兴 | 🟢 柠檬绿 |
| 工业、警示、汽车、紧迫感 | 🟠 安全橙 |

---

## 切换原则

- **一份 deck 只用一套主题**,不要中途换 accent 色
- 灰阶变量（`--grey-1/2/3`）在 4 套主题里完全相同,无需调整
- WebGL 网格背景会自动读取 `--accent` 变量,翻页时鼠标附近会偷渡一抹高亮色
- 选定主题后,可以在 chrome 文案里用一个相关词强化语义（如 IKB 配 `International / Helvetica` ,柠檬黄配 `Active / Living`）

---

## ❌ 不要做的事

- ❌ **不允许混搭**（例如 IKB 蓝 + 柠檬黄同时出现作高亮）——彻底违反瑞士风"单一锚点色"原则
- ❌ **不允许用户自定义任意 hex 值**——委婉拒绝,展示 4 套预设让选
- ❌ **不要改灰阶变量**——`--paper` / `--grey-1/2/3` / `--ink` 跨主题统一,只换 accent
- ❌ **不要用渐变**——瑞士风拒绝任何渐变,所有色块必须纯色
- ❌ **不要给 accent 加阴影 / 圆角 / 透明度**——直角、纯色、不透明,这是瑞士风的硬规则

---

## 关于灰阶（跨主题统一）

| 变量 | 值 | 用途 |
|---|---|---|
| `--paper` | `#fafaf8` | 主底色（极浅暖白） |
| `--grey-1` | `#f0f0ee` | 浅灰底（用于 `.grey-block` / 区块底） |
| `--grey-2` | `#d4d4d2` | 中灰（分割线、border） |
| `--grey-3` | `#737373` | 暗灰（辅助文字 / meta） |
| `--ink` | `#0a0a0a` | 文字主色（近黑） |

这套灰阶是经过校色的"高级灰",在任何 accent 色下都不抢戏。**不要**改成纯白（`#fff`）或纯黑（`#000`）——会损失瑞士风的"克制"质感。

---

选定主题后,告诉用户："用 🔵 克莱因蓝 / 🟡 柠檬黄 ..." 并在 deck 项目记录里备注,方便后续迭代时保持一致。

# 主题色预设（Themes）

5 套精心调配的主题色板,保证"电子杂志 × 电子墨水"的美学不垮。**不允许用户自定义颜色——色彩搭配错了画面瞬间变丑**,只从以下预设中挑选。

---

## 使用方法

1. 问用户选哪套(或基于内容推荐一套)
2. 打开 `assets/template.html` 的 `<style>` 块
3. 找到开头的 `:root{` 块
4. **整体替换**标有"主题色"注释的那几行 `--ink` / `--ink-rgb` / `--paper` / `--paper-rgb` / `--paper-tint` / `--ink-tint`
5. 其他 CSS 都走 `var(--...)`,无需任何其他改动

---

## 🖋 墨水经典 (Monocle 默认)

**适合**:通用分享、商业发布、科技产品、任何场景都安全的默认选择。
**调性**:纯墨黑 + 暖米白,杂志感最强,Monocle / Apricot / A Book Apart 风。

```css
--ink:#0a0a0b;
--ink-rgb:10,10,11;
--paper:#f1efea;
--paper-rgb:241,239,234;
--paper-tint:#e8e5de;
--ink-tint:#18181a;
```

---

## 🌊 靛蓝瓷 (Indigo Porcelain)

**适合**:科技/研究/数据分享、工程师文化、深度内容、技术发布会。
**调性**:深靛蓝 + 瓷白,冷静、理性、有深度,像学术期刊或蓝印花瓷器。

```css
--ink:#0a1f3d;
--ink-rgb:10,31,61;
--paper:#f1f3f5;
--paper-rgb:241,243,245;
--paper-tint:#e4e8ec;
--ink-tint:#152a4a;
```

---

## 🌿 森林墨 (Forest Ink)

**适合**:自然/可持续/文化/非虚构内容、户外品牌、环保主题。
**调性**:深森林绿 + 象牙,沉稳、有呼吸感,像旧版《国家地理》。

```css
--ink:#1a2e1f;
--ink-rgb:26,46,31;
--paper:#f5f1e8;
--paper-rgb:245,241,232;
--paper-tint:#ece7da;
--ink-tint:#253d2c;
```

---

## 🍂 牛皮纸 (Kraft Paper)

**适合**:怀旧/人文/阅读/历史/文学分享、独立杂志、手作品牌。
**调性**:深棕 + 暖米,像牛皮信封或老笔记本,温暖、有年代感。

```css
--ink:#2a1e13;
--ink-rgb:42,30,19;
--paper:#eedfc7;
--paper-rgb:238,223,199;
--paper-tint:#e0d0b6;
--ink-tint:#3a2a1d;
```

---

## 🌙 沙丘 (Dune)

**适合**:艺术/设计/创意/时尚分享、画廊手册、审美优先的私享会。
**调性**:炭灰 + 沙色,克制、高级、中性,像沙漠黄昏或建筑设计图册。

```css
--ink:#1f1a14;
--ink-rgb:31,26,20;
--paper:#f0e6d2;
--paper-rgb:240,230,210;
--paper-tint:#e3d7bf;
--ink-tint:#2d2620;
```

---

## 推荐选择参考

| 如果是... | 推荐主题 |
|---|---|
| 不知道选啥 / 第一次用 | 🖋 墨水经典 |
| AI / 技术 / 产品发布 | 🌊 靛蓝瓷 |
| 内容 / 行业观察 / 文化 | 🌿 森林墨 |
| 书评 / 生活方式 / 人文 | 🍂 牛皮纸 |
| 设计 / 艺术 / 品牌 | 🌙 沙丘 |

---

## 切换原则

- **一份 deck 只用一套主题**,不要中途换色
- WebGL shader 的默认主色(钛金色散 / 银色流动)适配所有 5 套(经测试可接受)
- `currentColor` 驱动的 border / icon 会跟随 section 的 text color 自动适配,无需额外调整
- 选定主题后,`<title>` 文字和 `chrome` 文案可以强化该主题的语义(例如牛皮纸配"Vol.03 · 秋"这种)

## ❌ 不要做的事

- ❌ **不允许混搭**(例如 ink 取墨水经典的,paper 取沙丘的)——会彻底违和
- ❌ **不允许用户随便给一个 hex 值**——需委婉拒绝并展示 5 套预设让选
- ❌ **不要直接修改 template.html 其他地方的颜色**——所有散落 rgba 都走 var,改 :root 一处即可

选定主题后在 skill 对话中告诉用户:"用 🖋 墨水经典 / 🌊 靛蓝瓷 ..."并在 deck 项目记录里备注,方便后续迭代时保持一致。

