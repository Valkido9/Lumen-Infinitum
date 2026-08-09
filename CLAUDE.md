# 永恒流光 (Lumen Infinitum) — 项目文档

## 项目概述

这是一个中国原创网络小说的可视化故事网站。小说名为《永恒流光》（英文名 Lumen Infinitum），讲述了一个横跨多个平行世界的宏大故事——以后时光机时代为背景，围绕卢纳森特基地"第二代时之秩序"小队展开的冒险。

网站是单文件 HTML 应用（`index.html`），所有 CSS 和 JavaScript 内联。部署在 GitHub Pages：**https://valkido9.github.io/Lumen-Infinitum/**，仓库：`Valkido9/Lumen-Infinitum`，分支：`main`，发布源：`/ (root)`。

## 项目结构

```
E:\永恒流光\永恒流光\
├── index.html              ← 主文件（网站全部内容）
├── CLAUDE.md               ← 本文档（给 AI 的项目指引）
├── .gitignore
├── src/                    ← 原始小说文档
│   ├── 序章正文（2025.8待改）.docx / .txt
│   ├── 第一章正文 2024.1.25 工地状态.docx / .txt
│   ├── 永恒流光能力设定集（2026.6.10）.docx / .txt
│   └── 永恒流光设定集2025.4.28.docx / .txt
├── data/                   ← .nosdb 数据库文件（写作辅助工具）
├── assets/videos/          ← 视频素材（.mp4）
├── scripts/                ← Python 工具脚本
│   ├── build_docx.py
│   └── create_docx.py
└── docs/                   ← 额外的故事讲解 HTML
    └── 永恒流光故事讲解.html
```

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

#### 7. 审阅模式 / 批注系统（ANNOTATION SYSTEM）
- **密码保护**：密码存储在常量 `REVIEW_PASSWORD`，当前值为 `1T1Gsdxsp!!!`
- **流程**：点击"📝 审阅模式"按钮 → 弹出密码对话框 → 输入正确密码 → 进入批注模式
- **添加批注**：点击任意段落 → 弹出批注弹窗 → 输入批注内容 → 保存到 localStorage
- **查看批注**：已批注段落显示蓝色圆形数字徽章（`.ann-badge`），点击徽章查看批注线程
- **处理批注**：每条批注旁有"✓ 已处理"按钮，点击后标记为已解决
- **导出批注**：审阅模式下显示"📋 导出批注"按钮 → 格式化导出所有未处理批注 → 可复制
- **存储**：localStorage 键 `lumen-annotations`，数据结构：`{elementPath: [{id, text, time, resolved}]}`
- **退出**：再次点击审阅按钮退出，清除所有徽章和弹窗

### localStorage 键一览
| 键 | 用途 |
|---|---|
| `lumen-theme` | 主题偏好（`'dark'` 或不存在） |
| `lumen-annotations` | 批注数据 |
| `lumen-annotations-backup` | 清除批注前自动备份的上一版本批注（`{time, data}`） |

### 审阅模式辅助按钮
- 审阅模式下，右下角会依次出现三个按钮：`📋 导出批注`（左140px）、`🗑 清除批注`（左260px）、`💾 备份到本地`（左380px）
- `🗑 清除批注`：确认后先将当前批注**备份为本地文档**（自动下载 `.txt`）+ 写入 `lumen-annotations-backup`，再清空 `lumen-annotations`
- `💾 备份到本地`：用 `showSaveFilePicker` 弹出系统保存对话框选择位置（Chrome/Edge），其它浏览器自动下载带时间戳的 `.txt` 文档
- 备份文档文件名格式：`永恒流光-批注备份-YYYYMMDD-HHMMSS.txt`

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

## 给接手 AI 的工作指引

### 当你听到"最新的批注已经修订，请根据批注进行修改"时：
1. 从 localStorage 键 `lumen-annotations` 读取所有批注
2. 每条批注包含：位置路径（`el-N`，N 为 `#main-content` 内元素的索引）、批注文本（用户的修改要求）、时间戳
3. 根据批注文本修改 `index.html` 中对应的 HTML 内容
4. 修改完成后，清除 localStorage 中的 `lumen-annotations` 键
5. Git commit 并 push 到 GitHub

### 导出批注的替代方式：
如果无法访问 localStorage，用户可以：
1. 在审阅模式下点击"📋 导出批注"按钮
2. 复制格式化后的批注文本
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
- 所有内容在单文件 `index.html` 中（~2600+ 行，~140KB），CSS 在 `<style>` 中，JS 在 `<script>` 中
- 不要拆分文件，保持单文件结构
- CSS 变量定义在 `:root`（日间）和 `.dark`（夜间）中
- 角色数据在 JS 对象 `characters` 中，术语在 `terms` 中，能力数据在 `abilityData` 数组中
- 能力档案的筛选依赖 `tg` 标签（阵营/时间线/院区/卷目）；新增能力时需确保 `tg` 的各值都在 `abilityTags.*.values` 词表中，否则筛选不到
- `abilityMap` 是按 ID 快速查找能力的映射表
- 批注系统的密码常量 `REVIEW_PASSWORD` 在 JS 中
- `.spoiler-content` 元素在 HTML 中的位置可能在 `.spoiler-mark` 之前（通过 `<br>` 分隔），查找时需双向搜索
- 修改 `abilityData` 后需调用 `renderAbilityArchive()` 刷新视图
- 修改 `characters` 数据中的 `abilityDetail` 只需保留基础描述，详细能力介绍在 `abilityData` 中
