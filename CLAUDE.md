# 永恒流光 (Lumen Infinitum) — 项目文档

## 项目概述

这是一个中国原创网络小说的可视化故事网站。小说名为《永恒流光》（英文名 Lumen Infinitum），讲述了一个横跨多个平行世界的宏大故事——以后时光机时代为背景，围绕卢纳森特基地"第二代时之秩序"小队展开的冒险。

网站由五个独立的 HTML 页面组成，每个页面共享相同的 CSS 框架和 JavaScript（内联），均支持审阅模式。部署在 GitHub Pages：**https://valkido9.github.io/Lumen-Infinitum/**，仓库：`Valkido9/Lumen-Infinitum`，分支：`main`，发布源：`/ (root)`。

## 项目结构

```
E:\永恒流光\永恒流光\
├── index.html              ← 故事主线（序幕 + 第一卷）
├── sidetory.html           ← 时空遗闻（人物背景 / 前传 / 番外 / 特殊事件）
├── world.html              ← 世界设定（设定集 / 名词解释 / 阵营简介）
├── abilities.html          ← 能力档案（122 个能力条目）
├── characters.html         ← 角色百科（角色搜索网格）
├── CLAUDE.md               ← 本文档（给 AI 的项目指引）
├── .gitignore
├── src/                    ← 原始小说文档
├── data/                   ← .nosdb 数据库文件（写作辅助工具）
├── assets/videos/          ← 视频素材（.mp4）
├── scripts/                ← Python 工具脚本
└── docs/                   ← 额外的故事讲解 HTML
```

## 五个页面及导航

| 页面 | 标题 | 内容 |
|---|---|---|
| `index.html` | 故事主线 | 序幕 + 第一卷章节、时间线一览、角色卡片弹窗 |
| `sidetory.html` | 时空遗闻 | 支线故事选择器、人物背景、前传、番外、特殊事件 |
| `world.html` | 世界设定 | 设定集标签页（默认）+ 名词解释标签页 + 阵营简介标签页 |
| `abilities.html` | 能力档案 | 122 个能力条目、四维筛选、排序、六维雷达图 |
| `characters.html` | 角色百科 | 角色搜索网格（`buildCharCards()` 动态渲染） |

每个页面的导航栏均包含指向全部五个页面的链接，当前页面高亮。审阅模式在所有五个页面上完全可用（密码、批注、编辑、历史、导出）。

## 网站技术架构

### CSS 系统
- **CSS 自定义属性**实现明暗主题切换（日间/夜间模式）
- 主题色系：`--accent`（主色蓝）、`--accent2`（强调色红）、`--accent3`（辅助色紫）、`--gold`（金色用于术语链接）、`--prologue`（序幕色）、`--wokgard`（沃克加德卷色）
- 响应式布局（`@media (max-width: 768px)`）
- 剧透系统：`.spoiler-mark`（点击按钮）+ `.spoiler-content`（隐藏内容）
- 批注系统：`.ann-badge`（段落上的批注计数徽章）、`.ann-popup`（批注弹窗）、`.annotated`（已批注段落左边框）
- 密码弹窗：`.pw-dialog`、导出弹窗：`.export-modal`
- 角色卡片弹窗：`.modal` + `.char-header`
- 固定定位按钮：`.theme-toggle`（右下主题切换）、`.review-toggle`（左下审阅模式）

### JavaScript 核心功能

#### 1. 导航系统
- `scrollToSection(id)` — 平滑滚动到指定章节
- 侧边栏章节链接高亮（IntersectionObserver）
- 移动端侧边栏折叠

#### 2. 主题切换
- `toggleTheme()` — 日间/夜间模式切换
- 通过 `localStorage` 键 `lumen-theme` 持久化

#### 3. 角色档案（`characters` 对象）
- `openChar(key)` — 打开角色卡片弹窗，显示：姓名、称号、CRT等级、身份、性格、能力（可点击跳转至能力档案）、核心羁绊、标志性台词、主要出场
- `getCharAbilityHtml(charKey)` — 根据角色key在 abilityData 中匹配对应的能力，生成可点击的能力名链接
- 已收录角色：云略、礼奈、马萨卡、正义、亡灵兔、优碧卡、六八、克诺、莱克丝、粥娘、boundary、兰尼尔、梅纳德、康明德、道杰斯、鸿荧、斯帕里森、无名
- **注意**：角色卡片中不再内联显示能力的详细描述，只显示能力名称作为链接，点击后跳转至能力档案板块

#### 3.5 能力档案（`abilityData` 数组 + 标签筛选系统）
- 从源文档 `永恒流光能力设定集（2026.6.10）` 解析生成，共 121 个能力条目
- **数据源**：`data/ability_archive.js`（自动生成），通过 `scripts/extract_abilities.py` 解析源文档 → `scripts/build_archive_js.py` 转换为紧凑 JS → `scripts/insert_ability_archive.py` 插入 index.html
- **数据结构**：每个能力包含 `{id, tg(标签串), n(名称), h(持有者), c(CRT), s(6维统计数组), d(描述), q(引文), nt(范围备注), zn(镇压院区), qb(管理员)}`
- **标签字段 `tg`**：`"阵营1|阵营2, 时间线, 院区, 卷目"` —— 逗号分隔 4 段，多个阵营用 `|` 分隔；`parseTg(a)` 解析为 `{camps, tl, ward, vol}`
- **六维统计**：破坏力、速度、耐力、范围、狂热、防御（EX=5, A=4, B=3, C=2, D=1, 0=未知）
- **筛选交互**：`abilityTags`（4 类标签词表：阵营/时间线/院区/初登场卷目）+ `abilityFilter`（当前选择状态，空数组=该行不限）+ `matchesFilter(a)`（每行内多选 OR，跨行 AND）+ `renderFilterBars()`（渲染 4 行筛选条）+ `setAbilityFilter(cat, val)`（切换选择，`val=''` 清空该行）
- **13 院区**：内部四区（真理/救赎/赦除/机遇）、外部四区（生命/均衡/重构/解放）、终端四区（绝望/希冀/决意/勇气，反能力型，CRT 常为负并设 `zn`）、永恒院（中央时间控制）；院区标签按设定集院区特质分配
- `renderAbilityArchive()` — 渲染能力档案板块（筛选条 + 扁平能力卡片列表，无匹配时显示空态提示）
- `drawRadarChart(stats)` — 绘制 SVG 六维雷达图
- `scrollToAbility(id)` — 从角色卡片/正文跳转至特定能力卡片
- `abilityMap` — 按 ID 快速查找能力的映射表

#### 4. 术语词典（`terms` 对象）
- `openTerm(key)` — 打开术语定义弹窗
- 收录世界观术语：时间线空间、指令之力、能力使、时间裂缝、灵魂投影式折跃、大炼金阵、苛志室、言语辐射病、耳译装置等

#### 5. 世界设定标签页
- `switchWorldTab(tab)` — 在"能力体系"/"时间线"/"组织势力"三个标签间切换
- 能力体系表格列出所有主要能力使的 CRT 等级、能力名、描述

#### 6. 剧透系统（SPOILER TOGGLE）
- 全局 click 事件监听 `.spoiler-mark` 元素
- 点击后切换相邻 `.spoiler-content` 的显示/隐藏
- `.spoiler-content` 可能在 `.spoiler-mark` 之前或之后，中间可能有 `<br>` 标签
- 按钮文字在"（可能涉及剧透，点击查看）"和"（收起剧透）"之间切换

#### 7. 审阅模式（双模式：批注 + 直接编辑）
- **密码保护**：密码存储在常量 `REVIEW_PASSWORD`，当前值为 `1T1Gsdxsp!!!`
- **流程**：点击"📝 审阅模式"按钮 → 弹出密码对话框 → 输入正确密码 → 进入审阅模式（默认批注模式）
- **两种模式**：右下角出现 `💬 批注模式` / `✏️ 编辑模式` 切换按钮（`setReviewMode(m)`）
  - **批注模式**：点击任意文字 → 弹出批注弹窗 → 输入批注内容 → 保存到 localStorage。已批注段落显示蓝色圆形数字徽章（`.ann-badge`），点击徽章查看批注线程；每条批注旁有"✓ 已处理"按钮
  - **编辑模式**：点击任意文字 → 该元素进入 contenteditable 直接编辑 → 点击其它位置保存、按 `Esc` 取消。修改持久化到 `lumen-edits`，页面重渲染（如能力档案筛选、世界设定切换）后自动重新应用（`applyStoredEdits`）
- **全站可审阅**：事件委托 + 捕获阶段监听（`reviewDocClick`），`getReviewableElement` 向上查找持有直接文本的元素，页面任何文字（正文、能力卡片、术语词典、世界设定等）均可批注/编辑
- **稳定路径**：`getStablePath(el)` 生成"最近带 id 祖先 + `:nth-child` 链"的 CSS 选择器路径（如 `#ab-ab81 > div:nth-child(2) > ...`），替代旧的 `el-N` 索引路径，重渲染后仍可定位
- **导出审阅**：审阅模式下"📋 导出审阅"按钮 → 格式化导出所有未处理批注 + 编辑模式存档（`// ===== 永恒流光 · 编辑模式存档 =====` 段）→ 可复制
- **存储**：批注在 localStorage 键 `lumen-annotations`（`{elementPath: [{id, text, time, resolved}]}`）；直接编辑在 `lumen-edits`
- **退出**：再次点击审阅按钮退出，清除所有徽章、弹窗、模式按钮和监听器（未提交的编辑先保存）

### localStorage 键一览
| 键 | 用途 |
|---|---|
| `lumen-theme` | 主题偏好（`'dark'` 或不存在） |
| `lumen-annotations` | 批注数据 |
| `lumen-edits` | 编辑模式的直接修改（`{path: html}`） |
| `lumen-edits-history` | 编辑历史（`{states:[...], index:n}`，最多 10 份快照，见第 17 次更新） |
| `lumen-annotations-backup` | 清除前自动备份的上一版本审阅数据（`{time, data}`） |

### 审阅模式辅助按钮
- 审阅模式下，右下角会依次出现三个按钮：`📋 导出审阅`（左140px）、`🗑 清除审阅`（左260px）、`💾 备份到本地`（左380px）
- 编辑历史按钮（第 17 次更新新增）：`↩ 撤回`（左500px）、`↪ 重做`（左620px）、`💾 存档`（左740px）、`📂 读档`（左860px）、存档状态文字（左980px）
- `🗑 清除审阅`：确认后先将当前批注与编辑**备份为本地文档**（自动下载 `.txt`）+ 写入 `lumen-annotations-backup`，再清空 `lumen-annotations`、`lumen-edits` 与 `lumen-edits-history`
- `💾 备份到本地`：用 `showSaveFilePicker` 弹出系统保存对话框选择位置（Chrome/Edge），其它浏览器自动下载带时间戳的 `.txt` 文档（同时包含批注和编辑存档）
- 备份文档文件名格式：`永恒流光-审阅备份-YYYYMMDD-HHMMSS.txt`

## 更新历史

### 第 1 次更新 — 初始部署与项目组织
**提交**: `0a0242e` + `ac1e31a`
- 创建 `index.html` 可视化故事网站
- 部署到 GitHub Pages: https://valkido9.github.io/Lumen-Infinitum/
- 初始化 Git 仓库，关联远程 `Valkido9/Lumen-Infinitum`
- 重组项目文件夹：源文档 → `src/`，数据库 → `data/`，视频 → `assets/videos/`，脚本 → `scripts/`，故事讲解 → `docs/`

### 第 2 次更新 — 内容修复（5项）
**提交**: `42590a8`
1. **手杖描述修正**：强调只有马萨卡的能力让手杖转动了一小圈，其余所有人完全无法移动；将"撑着"改为"靠在"；增加了不便之处（卡门框、戳天花板、反穿外套等）的描写
2. **马萨卡能力剧透处理**：删除前三卷中马萨卡能力是"操纵动能"的时间流表述；添加"可能涉及剧透"标签保护真实能力「天平」的真相
3. **礼奈动机补充**：明确她造访粥娘实验室的原因是治疗失忆——粥娘配置的显影液可读取被苛志室删除的记忆
4. **粥娘角色补充**：将粥娘添加到 `characters` 对象，含完整档案和能力「狂乱的鸡尾酒」描述
5. **能力详情更新**：用原始设定集文字更新了礼奈、云略、马萨卡、正义、克诺、六八的能力描述；添加剧透折叠系统

### 第 3 次更新 — 审阅模式改为批注系统
**提交**: `8f6a9ed`
- **移除**旧的 contenteditable 编辑模式（`toggleReviewMode()`, `saveEdit()` 等全部替换）
- **新增**密码保护的批注系统：
  - 密码弹窗 UI（`#pwDialog`）
  - 批注徽章（蓝色圆形数字，`.ann-badge`）
  - 批注弹窗（`.ann-popup`），含批注线程、文本框、保存/取消按钮
  - 批注导出功能（`#exportModal`），格式化输出供 AI 阅读
  - 全局 Escape 键关闭弹窗
  - localStorage 持久化
- 嵌入给未来 AI 的指引注释（CSS 和 JS 中各一处）

### 第 4 次更新 — 剧透展开修复 + 能力链接修正
**提交**: `7084852`
- **剧透修复**：原 JS 只查 `nextElementSibling`，但 `.spoiler-content` 实际在 `.spoiler-mark` 之前（中间有 `<br>`）。修复为双向查找，跳过 `<br>` 标签
- **能力链接修正**：故事梗概中的能力名（如 `「天平」`、`「双生烈阳」`）之前通过 `openTerm()` 只打开简短术语定义，现在改为 `openChar()` 打开完整角色卡片（含详细能力描述和剧透内容）
  - `「天平」` → 马萨卡角色卡
  - `「双生烈阳」` → 礼奈角色卡
  - `「空间断层」`（3处）→ 正义角色卡
  - `「孤尽幻怨」` → boundary 角色卡
  - `「狂乱的鸡尾酒」` → 粥娘角色卡

### 第 5 次更新 — 密码修改
**提交**: `8ac128a`
- 审阅密码从 `1T1Gsdxsp!!` 改为 `1T1Gsdxsp!!!`

### 第 6 次更新 — 能力档案板块
**提交**: `4f9de48`
- **新增**"能力档案"独立板块（`#abilities`），从头导航栏可直达
- 从源文档 `永恒流光能力设定集（2026.6.10）` 解析出 101 个能力条目
- **数据结构**：`abilityData` 数组（每个能力含6维数值统计）+ `abilityTimelines` 组织结构（按时间线→阵营分组）
- **六维雷达图**：SVG 绘制，展示破坏力/速度/耐力/范围/狂热/防御（EX=5, A=4, B=3, C=2, D=1）
- **界面布局**：能力名居中、描述首行缩进2字符、引文浅色字体、范围备注
- **导航索引**：按时间线和阵营组织的快速跳转按钮
- **角色卡片改造**：`openChar()` 中移除内联能力描述，改为可点击的能力名链接（通过 `getCharAbilityHtml()` 匹配 `abilityData`），点击跳转至能力档案板块
- **解析工具链**：`scripts/extract_abilities.py`（解析源文档） → `scripts/build_archive_js.py`（生成 JS 数据） → `scripts/insert_ability_archive.py`（插入 index.html）
- CSS 新增：`.ability-archive`, `.ability-nav-bar`, `.ability-nav-btn`, `.ability-card`, `.radar-chart-wrap`, `.ability-timeline-title`, `.ability-faction-title`

### 第 7 次更新 — 能力档案标签筛选系统 + 补全遗漏能力
**提交**: `a8dc1dc`
- **筛选重构**：放弃时间线→阵营层级分类（`abilityTimelines`/`factionOf`/`scrollToFaction` 已删除），改为**按标签筛选**
  - 每个能力新增 `tg` 字段：`"阵营1|阵营2, 时间线, 院区, 卷目"`
  - 4 类标签：阵营（可多个，`|` 分隔）、时间线、院区、初登场卷目
  - 筛选交互：每行内多选 OR，跨行 AND；`renderFilterBars()` 渲染 4 行筛选条；`setAbilityFilter(cat, val)` 切换选择，`val=''` 清空该行；无匹配时显示空态
  - 能力卡片 meta 栏改为显示 阵营+院区 chips
- **院区标签**：按《永恒流光设定集2025.4.28》院区特质为全部 121 个能力分配院区（内部四区/外部四区/终端四区/永恒院）
- **补全 3 个遗漏能力**（均为能力设定集源文档中已存在但之前未收录）：
  - `ab117` 幻血之梦（达克多，十七前传）
  - `ab119` 真视魔瞳（明风，亲卫队/霍因佩兹）
  - `ab120` 施术单元合奏模块（麦克罗斯，牧人/洛琛顿）
- CSS：新增 `.tag-filter-bar`, `.tag-filter-label`, `.tag-filter-btn`, `.ability-empty`；移除 `.tl-label`, `.ability-timeline-title`, `.ability-faction-title`
- 一次性注入脚本：`scripts/add_ability_tags.py`（含全部 abID→tg 映射表，可作标签分配参考）

### 第 8 次更新 — 阵营标签调整
**提交**: `0e78e67`
- **合并"其他"阵营**：'其他势力'/'其他角色'/'没名字的组合' → 统一为 `其他`（ab50-57、ab69-77）
- **新增"死神首席"阵营**：阿芙忒乐尔斯特（ab58-60）、契尔文孙（ab96-98）归入 `死神首席`
- **前传去阵营化**：前传能力（ab99-117）不再有阵营标签（删除 `十七前传`/`正义前传`），正传/前传通过 tl/vol='前传' 区分
- 词表 `abilityTags.camps.values` 同步更新；q 引文归属、世界设定组织数据不受影响
- 修订脚本：`scripts/update_camps.py`（区域限定仅改 tg 字段）

### 第 9 次更新 — 终端四院区持有者修正 + 司明剧透移除
**提交**: `5c09da6`
- **终端四区（勇气/希冀/绝望/决意）收紧**：这四区为"镇压院区"（反能力使），仅持有镇压院区能力者才可归属。将误标的非镇压院区能力移出：
  - 粥娘 `狂乱的鸡尾酒`（ab11）：勇气院 → 机遇院
  - 温蒂 `狂卷残鸣`（ab31）/ `永黯双子`（ab33）：决意院 → 重构院
  - 黎各多林 `锈蚀狂欢`（ab50）：勇气院 → 重构院
  - 巴瑞尔 `不动坚城`（ab53）：决意院 → 均衡院
  - 塞赫穆斯 `元首的冠冕`（ab79）：决意院 → 真理院
  - 海拉克利斯 `魔导之王`（ab113）：决意院 → 重构院
- **残余之梦（ab116）修正为勇气院**（原误标决意院）
- 修正后终端四区仅剩持有者：天平/马萨卡（ab1、ab2）、残余之梦/雷格罗提斯（ab116）→ 勇气院；青石棉（ab56）、道杰斯（ab82、ab83）→ 绝望院；本尼艾诺（ab67、ab81）→ 决意院；鸿荧（ab84、ab85）→ 希冀院。麦克罗斯（ab120）、阿芙忒乐尔斯特（ab58-60）为解放院（外部院区，不属于终端四区）
- **司明评价剧透移除**：ab3（司明）去掉 `sp:1` 标志，其 q 引文不再被剧透折叠包裹
- **修复 ab3 引号损坏**：ab3 的 `q:`/`nt:` 字段引号曾被误改为全角 `”`（JS 语法错误），已恢复为 ASCII `"` + 中文引号

### 第 10 次更新 — 新院区标签 + 神器技能「七·灾」 + 批注院区分配
**提交**: `3f595a1`
- **新增两个院区标签**：`无院区/未共鸣`（CRT<8 一律无院区；8-9 小部分有、大部分无；9-10 大部分有、小部分无；>10 必有院区）与 `特殊`（非常规归类，如麦克罗斯 `施术单元合奏模块` ab120）
- **追加新能力「七·灾」（ab121）**：持有者瓦伦缇娜，CRT 10.5，阵营 `其他`，时间线 `洛琛顿`，院区 `特殊`，初登场卷目 `第三章`。为**神器技能**类能力（神器武器技能），字段带 `sz:1`，卡片显示金色边框 + "神器技能"徽章
- **神器技能标记补全**：`buildAbilityCard()` 新增 `const shenqi = !!a.sz` 逻辑；万杰特的 `创世之耀`（ab61）、`日昳散`（ab62）补上 `sz:1`（此前遗漏）
- **神器技能样式**：CSS 新增 `.ability-card-shenqi`（金色卡片边框 + 光晕）与 `.shenqi-badge`（金色徽章）
- **应用 53 条批注院区分配**：按批注为各能力指定院区。注意仅改 `tg` 字段的院区段，采用**锚定到 abID 的正则替换**（`\{id:"abXX",tg:"...`），避免因共享 tg 字符串而误改其他条目
- 特殊说明：批注 #3 为 ab10 `蓝色贝斯`（兰尼尔，CRT 7.8）指定"我修院"（非已知院区），按 CRT<8 → 无院区规则解释为 `无院区/未共鸣`

### 第 11 次更新 — 自定义域名 + 卷目表述 + 神器能力规范化 + 审阅双模式 + 空白能力交互
**提交**: `6c5ef8f`（另 `09e00d0` 为 CNAME 文件提交）
- **自定义域名**：GitHub Pages 绑定 `story.lumeninfinitum.cn`（DNS CNAME → `valkido9.github.io`；`CNAME` 文件在仓库根；HTTPS 证书由 GitHub 自动签发，最长约 1 小时）
- **角色百科介绍句删除**：`sidetory.html` 删除开头"如同百科全书一般…"介绍段
- **初登场卷目统一为"卷"**：`tg` 末段 `第一章/第二章…` → `第一卷/第二卷…`（`abilityTags.vol.values` 同步为 `['序幕','第一卷','第二卷','第三卷','第四卷','第五卷','前传']`）；**六八**（ab23、ab24）、**恪钴**（ab34、ab41）、**莱诺**（ab64）、**十七**（ab118）的初登场挪到第一卷，**阵营不变**；本尼艾诺（ab81）保持第四卷
- **神器能力描述规范化**：术语 `神器技能` → `神器能力`；固定段落 `该能力为"神器能力"，表现为…失去几乎所有能力。`（去括号）提取为常量 `SHENQI_DESC`，`buildAbilityCard` 将其渲染为 `.shenqi-desc-box`（金色描边盒）；ab62 `日昳散` 描述开头补入该段；ab61/ab62/ab121 三处含此段落的描述均加框
- **审阅模式双模式**：详见上文「7. 审阅模式」——新增 `✏️ 编辑模式`（contenteditable 直接编辑 + `lumen-edits` 持久化），全站任意文字可批注/编辑，稳定路径 `getStablePath`，导出含编辑记录
- **本尼艾诺空白能力交互**：空白名 `「　　　　　」`（ab67/ab81 及 `getCharAbilityHtml`）点击后逐渐显现真名 **「世界的罪业」**（红色 + 闪烁抖动动画 `secretReveal`，约 2.4s），随后淡出恢复空白；悬停显示跟随鼠标的小气泡「你知道得太多了」（`.lumen-secret` / `#secretTooltip`）

### 第 12 次更新 — 新增神器设备能力「魔力引擎」+ CRT 规范化 + 台词修订 + 经典台词挪顶 + 部门领导组名单
**提交**: `c2bad73`
- **新增能力「魔力引擎」(ab122)**：持有者麦克罗斯，插在 ab120「施术单元合奏模块」之前。由魔力池 + 凝滞器组成的操纵指令之力的设备（不属于能力），含熟练度分级 A-D 与完整描述；`tg` 为 `牧人, 洛琛顿, 特殊, 第三卷`，CRT `N/A`（实际 6.0）、面板全 C
- **万机簦（ab89）CRT 规范化**：CRT 改为 `N/A`（实际 6.0）、面板全 C，描述追加"它属于特殊分类…"段
- **云略两能力 CRT 规范化**：流光（ab4，CRT 保持 `N/A`）、劣化长终（ab57，CRT `？`→`N/A`）描述均注明"实际上按照 18.0 计算"；CRT 字段保持 `N/A` 以免 `maxCrt>=14` 触发镇压院区边框判定
- **台词修正**：歌涅法示例台词删除"我的天呐！！小马保力！"（云略台词，能力档案中归属云略的引文保留）；鸿荧经典台词改为"若您在战线或桃源有事相托，请尽管与我诉说。"；道杰斯改为"幸会。我是道杰斯，一介学者，一名法师。"
- **琉璐珀人物介绍新增**："古灵精怪、神出鬼没、如猫头鹰一般狡黠的棕发少女…"一句（角色卡 + 百科 `sidetory.html`）
- **经典台词挪顶**：角色卡（`openChar`）「标志性台词」挪至头部（char-header 之后、身份之前）；百科 `sidetory.html` 全部 13 个词条的 `.wiki-quote` 挪到词条最顶（wiki-sub 之后、基本档案之前），一次性脚本 `scripts/move_quotes_top.py`
- **部门领导组能力使名单**："除了上文提到的人以外…" → "除了正义、本尼艾诺、莱诺、杏子、奇比、普兰奇昂、Twikyo以外，部门领导组的所有人都不是能力使。"

### 第 13 次更新 — 「世界的罪业」交互优化（桌面端悬停显现 / 移动端保持点击）
**提交**: `4243c24`（后续修订：小气泡改为两种设备都显示）
- **设备判定**：`matchMedia('(hover: hover) and (pointer: fine)')` → `isHover`；支持悬停为桌面端，否则移动端
  - **桌面端**：鼠标悬停空白名 → 显现真名「世界的罪业」（红色闪烁动画，保持显示）并显示"你知道得太多了"小气泡；鼠标离开 → 立即恢复空白并隐藏小气泡（`hideSecret` 清理定时器）
  - **移动端**：保持原交互——点击显现、2.4s 后淡出恢复；触摸时显示"你知道得太多了"小气泡
- `revealSecret(s, autoFade)` 新增 `autoFade` 参数：桌面悬停 `false`（不自动淡出，由 mouseout 恢复）；移动端点击 `true`（保留原淡出）

### 第 14 次更新 — 空白能力视觉微调 + 百科补经典台词 + 修瓦尔扎台词替换
**提交**: `（本次）`
- **「世界的罪业」红色调暗**：显现真名、悬停色统一由 `#e33/#e3291f` 调暗为 `#c2261b`（`text-shadow` 同步 `rgba(194,38,27,0.6)`）
- **措辞统一**：全站"你知道的太多了" → **"你知道得太多了"**（JS、CSS 注释、CLAUDE.md）
- **移动端气泡随闪烁消失**：移动端点击显现、2.4s 后淡出时，`autoFade` 完成回调同步隐藏 `#secretTooltip` 小气泡
- **百科补经典台词**（`sidetory.html`）：为 11 个缺台词词条从序幕/第一卷正文文档（`src/序章正文…`、`src/第一章正文…`）找到台词并插到词条最顶（wiki-sub 之后）：
  - 克诺「我绝对不能向一根蠢棍子投降！」（序幕）、莱克丝「我真是对你们这群能力使羡慕嫉妒恨……」（序幕）、粥娘「哎呀，不要紧！我能解决这个问题的。」（序幕）、无名「现在我暂且将你的能力命名为『双生烈阳』。」（序幕）、六八「来喝点鲜奶吧。我们边喝边聊。」（第一卷）、歌涅法「……斯帕里森先生只是有什么事情，一定是这样的！」（第一卷）、琉璐珀「我哪来的性子看书。……啧，内城人……」（第一卷）、梅纳德「我名为梅纳德·庞奇，是教皇城海域海盗的头领。」（第一卷）、亚因森特「我名为，亚因森特·埃德加……告诉我，你的棺材上会刻上什么名字，刺客。」（第一卷）、卢卡森「内城军务部执事领事，伦道夫·卢卡森。」（第一卷）、康明德「大航海时代，通融一下。」（序幕）
  - **留空 6 人**（序幕/第一卷无本人对白）：斯帕里森、良、艾索利、斯卡娜、吉贝玲、紫珊瑚
  - 一次性脚本：`scripts/find_quotes.py`（扫描对白）、`scripts/add_missing_quotes.py`（插入引语块）
- **修瓦尔扎经典台词替换**：`"时间将不再被称为时间。"` → `"请不要对艾威尔大人的意志作无谓的抗争。我们尽快结束吧。"`（`sidetory.html`）

### 第 15 次更新 — CRT 排序等效值（`ce` 字段）
**提交**: `（本次）`
- **新增排序等效 CRT 字段 `ce`**：部分能力 CRT 记录为 `N/A`（特殊分类），无法参与按 CRT 强弱排序。新增 `ce` 字段存放排序用等效值，`crtAbs()` 优先读取 `ce`（`if (a.ce != null) return Math.abs(a.ce)`），否则回落 `Math.abs(maxCrt(a.c))`
- **赋值**：云略/修瓦尔扎 `流光`（ab4）、`劣化长终`（ab57）→ `ce:17.9`；麦克罗斯 `魔力引擎`（ab122）、伞侠 `万机簦`（ab89）→ `ce:6.0`
- **N/A 注记删除**：四个能力描述中的等效说明句全部从显示内容中移除（ab4/ab57 的"（该能力 CRT 记录为 N/A，按 CRT 强弱排序时等效于 17.9。）"、ab89/ab122 的"它属于特殊分类，CRT为N/A，（实际上按照6.0计算），所有的面板都为C。"），页面不标注 N/A 等效值，但 `ce` 字段保留、排序仍按等效值执行
- **安全性**：`ce` 只影响 `crtAbs` 排序，`c` 字段保持 `"N/A"` —— 攻城级判定 `maxCrt(a.c) >= 14` 用 `maxCrt` 直读 `c`，云略的 17.9 不会误触发红色攻城框；卡片 CRT 展示仍显示 `N/A`

### 第 16 次更新 — 镇压院区攻城级徽章（显示框优先紫色）
**提交**: `（本次）`
- **攻城级判定放宽**：`buildAbilityCard` 中 `const siege = maxCrt(a.c) >= 14;`（去掉原先的 `!isZpn &&` 排除）。`maxCrt` 正则忽略负号，天然按绝对值比较，因此镇压院区的负 CRT（如 `(-15.8)`）同样满足攻城级
- **受影响能力（4 个）**：ab67「无名」（本尼艾诺，-15.8）、ab81「　　　　　」（本尼艾诺，-18）、ab83「噩梦解放」（道杰斯，-16.5）、ab85「狂梦解放」（鸿荧，-15.3）——卡片同时显示 `镇压院区` + `攻城级` 两个徽章
- **显示框优先级**：新增 CSS `.ability-card-zpn.ability-card-siege`（含 hover 变体，双类特异性 0,2,0 高于单类），强制紫色镇压院区边框并清除攻城级红色光晕（`box-shadow: none`）——同时满足时优先显示紫色镇压院区框，攻城级徽章仍显示

### 第 17 次更新 — 编辑历史系统（存档 / 撤回 / 重做 / 读档）
**提交**: `（本次）`
- **新增 localStorage 键 `lumen-edits-history`**：`{states:[...], index:n}`，`states` 最多 **10 份**快照，每份 `{time, data}`（`data` 为当时 `lumen-edits` 的深拷贝）；旧键 `lumen-edits` 格式不变、叠加兼容
- **历史引擎**：`loadHistory()` / `saveHistory()` / `commitEditHistory()`（剪掉重做分支→压入当前 `lumen-edits` 快照→超 10 份 `shift()`→更新 index）/ `undoEdit()` / `redoEdit()` / `loadSlot(i)` / `applySnapshot(data)`（写回 `lumen-edits` + 复用 `applyStoredEdits()` 全量重放）/ `refreshUndoButtons()`
- **自动存档**：`commitInlineEdit` 中内容变更并写入 `lumen-edits` 后调用 `commitEditHistory()`——每次编辑完成自动压一份快照；`💾 存档`（手动）走同一函数，上限一致
- **原文基线**：`editBaselines = {}`（内存态），`startInlineEdit` 首次编辑某元素时记录 `el.innerHTML` 作为导出"原文"
- **按钮**（审阅模式右下角，`addHistoryButtons`/`removeHistoryButtons`）：`↩ 撤回`（左500px）/ `↪ 重做`（左620px）/ `💾 存档`（左740px）/ `📂 读档`（左860px）+ 存档状态文字 `存档 当前/总数`（左980px）；`refreshUndoButtons` 按 index 置灰撤回/重做；读档弹窗 `.load-dialog` 列出最多 10 份 `time` 时间戳，点击任意项 `loadSlot(i)`
- **键盘快捷键**（`reviewKeydown`，进入/退出审阅时在 `document` 捕获阶段挂接/移除）：
  - `Ctrl+Z`（不带 Shift）→ 先 `commitInlineEdit` 收尾正在编辑的条目，再 `undoEdit()`（`preventDefault` 屏蔽输入框内原生撤销）
  - `Ctrl+Y` 或 `Ctrl+Shift+Z`（Shift 下 `e.key==='Z'`）→ `redoEdit()`
  - **不用 Ctrl+V**：它是浏览器原生粘贴键，编辑时仍需往输入框贴文字
- **导出扩展**：`showExport` 原"直接编辑的修改"段替换为 **`===== 永恒流光 · 编辑模式存档 =====`** 段——每条含 `路径`（稳定 CSS 选择器）/ `位置` / `原文`（取自 `editBaselines`，无则注明"（无原文记录）"）/ `新文`，外加 `编辑条目：N 条 | 存档 x/y` 与使用说明；AI 服务器端按"路径"在 `index.html` 定位节点、用"新文"替换即可
- CSS 新增：`.hist-btn:disabled`（置灰）、`.hist-status`、`.load-dialog` 系列（读档弹窗）

### 第 18 次更新 — 读档弹窗修复 + 最终战条目改卷数分类
**提交**: `（本次）`
- **读档弹窗修复**：点击 `.load-dialog` 读档项 / 关闭键不再触发编辑或批注——`getReviewableElement` 与 `reviewDocClick` 的排除列表加入 `.load-dialog`（此前点击读档会误触编辑功能、点击关闭键会误触发批注，导致无法正常读档）
- **最终战条目从阵营分类改为卷数分类**：`第X章最终战`（阵营）→ `第X卷最终战`（初登场卷目），共 30 个能力重新打标：
  - `ab19/ab20`（乌顿）→ `第一卷最终战`
  - `ab39/40/41/42`（拉伊法/九号/恪钴/芙萝妮）→ `第二卷最终战`
  - `ab58/59/60`（阿芙忒乐尔斯特，洛琛顿）→ `第三卷最终战`
  - `ab78-95`（柯洛雯第三帝国 + 卢纳森特 + 芬奈法拉战线的全部第四章最终战能力）→ `第四卷最终战`
  - `ab96/97/98`（契尔文孙，芬奈法拉）→ `第五卷最终战`
- **camp 段处理**：原本 camp 段仅有"第X章最终战"的 6 个条目（ab19/20/39/40/41/42）camp 置空（沿用前传的空 camp 写法 `, 时间线, ...`）；`abilityTags.camps.values` 移除 `第一章最终战`/`第二章最终战`；`abilityTags.vol.values` 新增 `第一卷最终战`…`第五卷最终战`（紧邻对应卷目）
- **3/4/5 卷最终战能力已确认全部在站**：此前未打最终战标签，故筛选"最终战"分类时看不到；本次全部补齐标签
- **叙事文字同步**：q 引文 / nt 备注中的"第X章最终战" → "第X卷最终战"（6 处）
- **恪钴 ab41 特别说明**：原 vol=第一卷（角色初登场），现按"该能力参与的战役"标记为 `第二卷最终战`（与 ab39/40/42 的第二章最终战归类一致）

### 第 19 次更新 — 五页面拆分 + 文本修正 + 审阅统一
**提交**: `（本次）`
- **五页面拆分**：将原单文件 `index.html`（含故事+世界+能力三板块）和 `sidetory.html`（含时空遗闻+角色百科两板块）拆分为五个独立页面：
  - `index.html` → 故事主线（保留序幕 + 第一卷章节内容）
  - `sidetory.html` → 时空遗闻（人物背景/前传/番外/特殊事件；使用完整 CSS/JS 框架，新增审阅模式支持）
  - `world.html` → 世界设定（设定集 + 名词解释 + 阵营简介标签页）
  - `abilities.html` → 能力档案（122 个能力条目）
  - `characters.html` → 角色百科（角色搜索网格）
- **审阅模式全覆盖**：所有五个页面共享完整的 CSS/JS 框架，审阅模式（密码、批注、编辑、历史、导出、清除）在每个页面上均可用
- **弹窗编辑持久化修复**：`openChar()`、`openTerm()`、`openTimeline()` 生成弹窗内容后调用 `applyStoredEdits()`，编辑后关闭再打开不再弹回
- **按钮统一**：
  - "📋 导出批注" + "💾 导出存档" → "📋 导出审阅"（合并导出批注与编辑存档）
  - "🗑 清除批注" → "🗑 清除审阅"（同时清除 `lumen-annotations` + `lumen-edits` + `lumen-edits-history`）
  - 备份文件名统一为 `永恒流光-审阅备份-*.txt`
- **文本修正**：
  - 全站"流光永佑" → "英勇为怀，广济众生"（8 处，跨 index.html 与 sidetory.html）
  - 琉璐珀人物卡/百科"过度热情"句修正："总是冷淡地打击琉璐珀过度的热情" → "总是冷淡地打击歌涅法过度的热情"
  - 可乐术语描述："在沃克加德也有售卖" → "在卢纳森特基地附近也有售卖"
- **导航更新**：所有页面导航栏统一为五页面链接，当前页高亮；wiki-jump 链接指向 `characters.html`；移除所有 `onclick="scrollToSection(...)"`（跨页不需要）

### 第 20 次更新 — 角色百科标签分类 + 新角色 + 筛选 UI + 审阅标签编辑器
**提交**: `（本次）`
- **角色 `tg` 字段**：为全部 35 个角色添加 `tg` 字段（格式同能力档案：`"阵营1|阵营2, 时间线, 院区, 卷目"`）
- **新增 10 个角色**：万杰特、红猫、靖珏、普兰奇昂、杏子、奇比、Twikyo、修瓦尔扎、阿芙忒乐尔斯特、温蒂（含完整档案：身份、性格、羁绊、台词、出场、能力描述）
- **角色筛选 UI**：复用能力档案标签筛选系统——4 行筛选条（阵营/时间线/院区/初登场卷目）、`characterFilter` 状态、`parseCharTg`/`matchesCharFilter`/`renderCharFilterBars`/`setCharFilter`；`buildCharCards` 结合文本搜索 + 标签筛选；无匹配时显示空态
- **审阅模式标签编辑器**（第三模式 `🏷 标签`）：
  - 标签模式下角色卡片显示当前标签 chips（彩色圆角，带 × 移除按钮）+ `＋ 添加` 按钮
  - `showTagPicker(key, ev)` — 浮动标签选择面板（4 类 tabs）
  - `⚙ 种类` 按钮 → `showCategoryManager()` — 弹窗管理标签种类（新增/删除值，持久化到 `lumen-ability-tags-custom`）
  - 角色标签覆盖持久化到 `lumen-char-tags` localStorage 键
  - `_charOrigTg` 备份原始 tg 值，`applyStoredCharTags()` 安全合并覆盖
- **`abilityTags` 词表同步**：新增阵营值 `圆翼党`、`蓝河明船`、`珀利贝尔实业 · 亲卫队`、`潮涌居士号`、`浪庄游击队`（同步到所有 5 个页面的 `abilityTags.camps.values`）
- **CSS 新增**：`.tag-picker`、`.cat-mgr-dlg`、`.tag-chips-row`、`.tag-chip`、`.tag-chip-x`、`.tag-chip-add`、`.tag-filter-container`
- **关键修复**：`buildCharCards` 中 `getEffectiveCharTg()` 的 TDZ 错误——该函数访问 `const _charOrigTg`（定义于第一轮 init 之后），改为仅在 `tagMode` 时调用（第二轮 init 之后才触发）
- **标题修正**：角色百科栏目标题从"角色档案"改回"角色百科"

### 第 21 次更新 — 视觉 MCP（识别文档内嵌图片）
**提交**: `（本次）`
- **背景**：当前底层模型（deepseek-v4-flash）为纯文本模型，内置 `Read` 读图返回 `[Unsupported Image]`。为满足"识别文档内嵌图片"需求，接入阿里 DashScope Qwen-VL 视觉能力。
- **新增 `scripts/vision_mcp_server.py`**：极简视觉 MCP 服务器（官方 `mcp` SDK 1.x 的 `FastMCP`），暴露 `analyze_image(image_path, question)` 工具——读取本地图片 → base64 → 调 DashScope OpenAI 兼容端点 `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`，模型 `qwen-vl-max` → 返回中文描述。HTTP 走标准库 `urllib`（避开 httpx/h11 依赖冲突），仅依赖 `mcp<2`。协议握手与端到端识别均已实测通过。
- **新增 `.mcp.json`**（项目根）：注册 `lumen-vision` 服务器，`command` 为 Python 绝对路径，`args` 指向该脚本；`DASHSCOPE_API_KEY` 以 `${DASHSCOPE_API_KEY}` 占位引用，`DASHSCOPE_MODEL=qwen-vl-max`。
- **密钥存储**：真实 key 存于 `.claude/settings.local.json` 的 `env.DASHSCOPE_API_KEY`（已 gitignore）；`.mcp.json` 内不落明文。若 MCP 启动后 key 未生效，用 `/mcp` 重连。
- **新增 `scripts/extract_docx_images.py`**：把 `src/*.docx` 内嵌图片（docx 是 zip，图片在 `word/media/`）提取到 `docx-images/<文档名>/`，该目录已 gitignore（派生产物）。可指定文件或默认全量提取。
- **使用流程**：`python scripts/extract_docx_images.py` 提取 → 通过 MCP 工具 `analyze_image` 识别 → 得到图片内容的中文描述（适合地图 / 思维导图 / 示意图 / 时间线图等）。
- **环境依赖**：pip 需走腾讯镜像 `-i https://mirrors.cloud.tencent.com/pypi/simple/` 安装 `mcp<2`（清华/阿里镜像对该包 403 或缺失；官方 PyPI 被本机代理拦截）。DashScope API 端点本机可达。

### 第 22 次更新 — 世界设定新增「设定集」标签页 + 待整理设定要点小结
**提交**: `bfb4e16`
- **新增「📕 设定集」标签页**（`world.html`，置于标签栏最左、为默认页，其后为名词解释/阵营简介）：把 `src/永恒流光设定集2025.4.28.docx` 的完整内容（113 段正文 + 10 张图）搬到网页，图片存 `assets/setting/`。
- **左侧目录 + 多级折叠联动**：`.setting-layout` 双栏（粘性左目录 `.setting-toc` + 正文 `.setting-main`）；目录节点与正文章节共享 `data-sec` 属性，`setSettingNode(id, collapsed)` 一次性切换两侧 `.collapsed`（`.toc-node` / `.set-sec`），折叠时页面条目跟着收起来，页面不臃肿；点击任意目录项展开祖先链（`expandSettingAncestors`）并平滑滚动到正文；默认只展开第一章根节点。
- **内容结构**：`const SETTING_DATA = [...]` 嵌套 JS 树（58 节点，块类型 `p`/`quote`/`p_attrib`/`note`/`img`/`trait`），`_settingBodyHtml` 渲染、`_buildSettingToc`/`_buildSettingContent` 递归生成目录与正文（标题级随深度递增）。
- **时间线空二级标题**：6 条时间线各挂 4 个空二级标题（地理与环境/历史沿革/政治与势力/现状与故事关联，`empty:true` → 渲染"（尚未撰写，等待补充）"），等待后续补写。
- **未写完明确标注**：`badge` 字段 → 金色 `.set-badge`；已标注"施工中 · 未写完"（指令之力装备）与"未写完 · 施工中"（纯粹业理，含原文截断 note）。
- **持久化容器**：`#settingTab` 独立 div 首建后常驻，切走再切回保持折叠状态；进入该标签时 `applyStoredEdits(document)` + `renderAllBadges()`，审阅模式（批注/编辑）在设定集内容上可用。
- **工具链**：`scripts/extract_setting_structure.py`（docx→JSON 结构，含图片锚点）→ `scripts/build_setting_data.py`（JSON→`data/setting_data.js`，注意 `data/` 已 gitignore、为派生产物）→ 拼接脚本把数据替换进 world.html 的 `SETTING_DATA = [...]`。
- **待整理设定**：`待整理设定/`（25 篇设定随笔 docx）已加入 `.gitignore`（本地保留、不进版本库、不发布）；每篇 docx 提取为同名 `.txt`（`scripts/extract_todo_settings.py`），并由后台 agent 提炼出【核心设定要点】写入（`scripts/apply_todo_summaries.py`，纯本地工具，不提交）。

### 第 23 次更新 — PC 端角色卡抽屉组件（宽屏右侧滑出，窄屏保持弹窗）
**提交**: `（本次）`
- **背景**：PC 端布局 `.sidebar`(260px) + `.main`(max-width 960px) 导致宽屏右侧大片空白；角色卡原为居中弹窗，PC 上不利用空白且遮挡正文。新增抽屉组件：PC（≥1280px）点击人物超链接 → 角色卡自**右侧滑出**为抽屉（360px 宽，覆盖在右侧空白上，正文不动）；手机/窄屏（<1280px）保持原居中弹窗。
- **结构**：新增 `.char-drawer`（fixed, top:54px, right:0, bottom:0, 360px, `transform:translateX(105%)` 滑入滑出）+ 内层 `.modal.char-drawer-inner`（复用 `.modal` 内部角色卡样式，覆盖宽度/圆角/动画，自身滚动）；`#charDrawer` 容器加在 `#charModal` overlay 之后；`@media (max-width:1279px){.char-drawer{display:none}}` 兜底隐藏。
- **分流逻辑**：新增 `drawerEnabled()`（`matchMedia('(min-width:1280px)')`）；`openChar()` 把角色卡 HTML 提为 `const html`，按 `drawerEnabled()` 写入 `#charDrawerContent`（+ `.show`）或 `#charModalContent`（原弹窗）；`applyStoredEdits` 应用于对应容器。
- **关闭**：新增 `closeCharDrawer()` / `closeCharCard()`（抽屉开则关抽屉，否则关弹窗）；角色卡关闭按钮 `onclick="closeModal('charModal')"` → `closeCharCard()`；全局 Escape 监听在关弹窗前补 `closeCharDrawer()`；`window resize` 跨断点缩窄时自动关闭开着的抽屉。
- **不动的部分**：术语 `openTerm` / 时间线 `tlModal` 保持居中弹窗；审阅模式（批注/编辑/历史/导出）在抽屉内照常可用（`applyStoredEdits` + `getStablePath` 不依赖容器类型）；能力链接跳转、wiki-jump 行为与弹窗一致；移动端样式不变。
- **注意**：1280–1580px 窗口下抽屉会覆盖正文右缘一小部分（1580px 以上完全在右侧空白区，不遮挡）。五页面 `openChar()` 函数体保持一致（改动同构），后续修改角色卡时五页需同步。

## 给接手 AI 的工作指引

### 当你听到"最新的批注已经修订，请根据批注进行修改"时：
1. 从 localStorage 键 `lumen-annotations` 读取所有批注，从 `lumen-edits` 读取直接编辑的修改
2. 每条批注包含：位置路径（CSS 选择器路径）、批注文本（用户的修改要求）、时间戳
3. 根据批注路径确定所属页面（`index.html` / `sidetory.html` / `world.html` / `abilities.html` / `characters.html`），修改对应 HTML 文件
4. 修改完成后，清除 localStorage 中的 `lumen-annotations` 与 `lumen-edits` 键
5. Git commit 并 push 到 GitHub

### 导出审阅的替代方式：
如果无法访问 localStorage，用户可以：
1. 在审阅模式下点击"📋 导出审阅"按钮
2. 复制格式化后的批注与编辑存档文本
3. 粘贴给你

### Git 工作流：
```bash
cd "E:\永恒流光\永恒流光"
git add index.html
git commit -m "<描述修改内容>"
git push origin main
```

### 发布：
推送后网站自动部署到 https://valkido9.github.io/Lumen-Infinitum/（GitHub Pages 从 main 分支 `/` 根目录发布）。

### 注意事项：
- 网站由五个独立 HTML 文件组成，每个页面共享相同的 CSS（~900行）和 JS（~2700行）框架，均为内联
- 五个页面：`index.html`（故事）、`sidetory.html`（时空遗闻）、`world.html`（世界设定）、`abilities.html`（能力档案）、`characters.html`（角色百科）
- **不要合并文件**，保持五页面结构
- CSS 变量定义在 `:root`（日间）和 `.dark`（夜间）中
- 角色数据在 JS 对象 `characters` 中，术语在 `terms` 中，能力数据在 `abilityData` 数组中
- 能力档案的筛选依赖 `tg` 标签（阵营/时间线/院区/卷目）；新增能力时需确保 `tg` 的各值都在 `abilityTags.*.values` 词表中，否则筛选不到
- `abilityMap` 是按 ID 快速查找能力的映射表
- 批注系统的密码常量 `REVIEW_PASSWORD` 在 JS 中，所有五页共享
- `.spoiler-content` 元素在 HTML 中的位置可能在 `.spoiler-mark` 之前（通过 `<br>` 分隔），查找时需双向搜索
- 修改 `abilityData` 后需调用 `renderAbilityArchive()` 刷新视图
- 修改 `characters` 数据中的 `abilityDetail` 只需保留基础描述，详细能力介绍在 `abilityData` 中
- 审阅模式（批注/编辑）在全站五个页面上均可使用，localStorage 键跨页共享
- **识别文档内嵌图片**：本机模型不支持视觉，需两步走——先用 `scripts/extract_docx_images.py` 把 `src/*.docx` 的 `word/media/` 图片提取到 `docx-images/`，再用 MCP 工具 `analyze_image`（DashScope qwen-vl-max）识别；见更新历史第 21 次更新
