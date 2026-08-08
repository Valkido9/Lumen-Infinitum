"""Parser for 永恒流光能力设定集 - section-based extraction with faithful recovery.

Rules:
- Ability header: [常态阶段-|解放阶段-]「Name」[(...)]  or bare "万机簦"
- A header is a NEW ability only if 持有者/原持有者/现持有者 appears within the
  next ~12 lines WITHOUT crossing a —— attribution line, a section header, or
  another ability header. This kills the old 挺好。/摄影师/气球狗 parse bugs and
  keeps mid-desc references (「永黯双子」——温蒂与维利斯 etc.) inside their block.
- desc starts at 能力： line, or (no 能力：) at the first prose line after the notes.
- Standalone 【...】 lines that look like faction-membership notes are dropped.
- quote = trailing quoted line + ——attribution at desc END (multi-quote capable).
- Content fixes: #23 艾沃→艾弗里, #25 无效。。→无效。, #34 （积攒的）, #37 admin strip,
  #38 挺好。 folded into 粥娘's quote, #39 间力乱流 d/q/qb split.
"""
import re, json, os, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('../src/永恒流光能力设定集（2026.6.10）（工地状态）(2).txt', 'r', encoding='utf-8') as f:
    content = f.read()
lines = content.split('\n')

# ---- structural section headers (NOT faction-membership notes) ----
SECTION_HEADERS = set([
    '【卢纳森特阵营-序章】','【第二代时之秩序】','【圣标联合】',
    '【沃克加德阵营】','【潮涌居士号】','【蓝河明船】','【第一章 最终战部分】','【浪庄游击队】','【深雾城阵营】',
    '【霍因佩兹时间线】','【珀利贝尔实业-亲卫队"渊海明灯"】','【珀利贝尔实业-部门领导组】',
    '【寒城工坊】','【长夜事务所】','【第二章最终战部分】','【神国】',
    '【出镜率不高的其他能力】',
    '【洛琛顿时间线】','【牧人】','【爱丽丝马戏团】','【洛琛顿中，不属于任何阵营的角色】','【第三章最终战部分】',
    '【第四章部分】','【卢纳森特时间线】','【初代时之秩序】','【基地其他部门】',
    '【柯洛雯时间线】','【"没名字的组合"】','【柯洛雯中，不属于任何阵营的角色】',
    '【柯洛雯第三帝国】','【第四章最终战部分】','【卢纳森特基地】',
    '【芬奈法拉】','【芬奈法拉战线】',
    '【第五章最终战部分】','【第五章施工区域】','【前传能力，暂时不作更新】','【大后期能力，暂时不作更新】',
    '【前传相关能力——大部分不是瓦斯狗写的】',
    '【十七前传】','【正义前传】','【卢纳森特共和国】','【圣奈特莉学院】','【碎暮异团】',
    '【在正义前传中，不属于任何阵营的角色】','【正义前传最终战部分】',
])

# Ability header regex, e.g. 「双生烈阳」 / 解放阶段-「冰冷残阳」（3，4，5阶段）
HEADER_RE = re.compile(r'^((?:常态阶段|解放阶段)-)?「([^」]*)」([（(][^）)]*[）)])?$')

# Trailing reference line: 「某能力」——持有者  (navigation hint, drop from desc)
REF_RE = re.compile(r'^「[^」]*」——')

# Standalone 【...】 note (one bracketed segment to end of line)
NOTE_RE = re.compile(r'^【[^】]*】$')

# Faction-membership notes we should drop from desc
FACTION_KEYWORDS = ('能力使', '其他时间线', '成员', '没有能力')

HOLDER_RE = re.compile(r'^(?:原|现)?持有者[：:]\s*(.+)$')
CRT_RE = re.compile(r'^CRT[：:\-－]?\s*(.+)$')

def is_quoted_line(s):
    """True if the whole line is a quoted evaluation line ("" or 「」)."""
    s = s.strip()
    if len(s) < 2:
        return False
    return ((s[0] == '"' or s[0] == '“' or s[0] == '「') and
            (s[-1] == '"' or s[-1] == '”' or s[-1] == '」'))

# ---------- Pass 1: find block starts ----------
block_starts = []  # (line_idx, 'section'|'ability', payload)
i = 0
while i < len(lines):
    s = lines[i].strip()
    # normalize curly quotes so source headers like 【“没名字的组合”】 match ASCII keys
    s_norm = s.replace('“', '"').replace('”', '"')
    if s_norm in SECTION_HEADERS:
        block_starts.append((i, 'section', s))
        i += 1
        continue
    if s == '万机簦':
        block_starts.append((i, 'ability', {'name': '万机簦', 'stage': ''}))
        i += 1
        continue
    m = HEADER_RE.match(s)
    if m:
        stage = (m.group(1) or '').rstrip('-')
        name = m.group(2) + (m.group(3) or '')
        # lookahead for 持有者 within next 12 lines
        found = False
        for j in range(1, min(13, len(lines) - i)):
            sj = lines[i + j].strip()
            if HOLDER_RE.match(sj):
                found = True
                break
            sj_norm = sj.replace('“', '"').replace('”', '"')
            if sj.startswith('——') or sj_norm in SECTION_HEADERS or sj == '万机簦':
                break
            if HEADER_RE.match(sj):
                break
        if found:
            block_starts.append((i, 'ability', {'name': name, 'stage': stage}))
    i += 1

# ---------- Pass 2: parse each ability block ----------
def parse_ability(block, payload, section):
    name = payload['name']
    stage = payload['stage']
    holder = ''
    crt = ''
    stats = {}
    range_notes = []
    zpn = ''            # 镇压院区 note
    orig_holder = ''    # 置换法则 原持有者
    desc = ''

    # Split block into header lines and desc region.
    # desc starts after 能力： if present, else after the last note line.
    desc_start = None
    for k in range(1, len(block)):
        s = block[k].strip()
        if s.startswith('能力：') or s.startswith('能力:'):
            desc_start = k + 1
            break
    if desc_start is None:
        # no 能力： -> first prose line after the header block
        for k in range(1, len(block)):
            s = block[k].strip()
            if not s:
                continue
            if HOLDER_RE.match(s) or CRT_RE.match(s):
                continue
            if re.search(r'(破坏力|侵蚀力|力量|速度|耐力|范围|狂热性|狂热|理智|防御)[\-：:]', s):
                continue
            if s.startswith('*'):
                continue
            if NOTE_RE.match(s):
                continue
            if is_quoted_line(s):
                continue
            desc_start = k
            break
    if desc_start is None:
        desc_start = len(block)

    # ---- header fields (lines before desc_start) ----
    for k in range(1, desc_start):
        s = block[k].strip()
        hm = HOLDER_RE.match(s)
        if hm:
            h = hm.group(1).strip()
            if s.startswith('原持有者'):
                orig_holder = h
            elif s.startswith('现持有者'):
                holder = h
            else:
                holder = h
            continue
        cm = CRT_RE.match(s)
        if cm:
            crt = cm.group(1).strip()
            continue
        if s.startswith('*'):
            range_notes.append(s.lstrip('*').strip())
            continue
        if NOTE_RE.match(s):
            if '镇压院区' in s:
                zpn = s
            continue
        # stats lines (狂热性 must precede 狂热 in alternation)
        if re.search(r'(破坏力|侵蚀力|力量|速度|耐力|范围|狂热性|狂热|理智|防御)[\-：:]\s*[A-ZEX0]', s):
            for m in re.finditer(r'(破坏力|侵蚀力|力量|速度|耐力|范围|狂热性|狂热|理智|防御)[\-：:]\s*([A-ZEX0]+)', s):
                key, val = m.group(1), m.group(2)
                if key == '狂热性':
                    key = '狂热'
                stats[key] = val
            continue
        # everything else in the header block (standalone quotes etc.) -> skip

    # ---- desc region ----
    desc_lines = [block[k] for k in range(desc_start, len(block))]
    desc = '\n'.join(desc_lines).strip()

    # drop faction-membership standalone 【...】 notes + trailing reference lines
    kept = []
    for dl in desc.split('\n'):
        dls = dl.strip()
        if NOTE_RE.match(dls) and any(kw in dls for kw in FACTION_KEYWORDS):
            continue
        if REF_RE.match(dls):
            continue
        kept.append(dl)
    desc = '\n'.join(kept).strip()

    # ---- 空屿: truncate at the 宝物 narrative (belongs to 斯帕里森 the character) ----
    if name == '空屿' and '在本作品的大部分剧情流程中' in desc:
        desc = desc[:desc.index('在本作品的大部分剧情流程中')].strip()

    # ---- #37: strip 珀利贝尔 admin structure from 新星冲击 ----
    if name == '新星冲击':
        desc = re.sub(r'【珀利贝尔实业的行政结构为：[^】]*】', '', desc, flags=re.S).strip()

    # ---- quote extraction (trailing quoted line + ——attribution, multi-quote) ----
    quote = ''
    while True:
        dl = desc.split('\n')
        while dl and not dl[-1].strip():
            dl.pop()
        if not dl:
            break
        last = dl[-1].strip()
        if last.startswith('——') and len(dl) >= 2 and is_quoted_line(dl[-2]):
            pair = dl[-2].strip() + '\n' + last
            quote = pair + ('\n' + quote if quote else '')
            desc = '\n'.join(dl[:-2]).strip()
        else:
            break

    # ---- #39: 间力乱流 - separate recorder quote from Administrator red-box ----
    qb = ''
    if name == '间力乱流' and holder == '红猫':
        marker = '「她好像很喜欢把能力加在鞭刃上。我觉得看起来像在玩蛇。」'
        idx = desc.find(marker)
        if idx != -1:
            real_desc = desc[:idx].strip()
            tail = desc[idx:].strip()
            tlines = tail.split('\n')
            q_end = None
            for k, tl in enumerate(tlines):
                if '已重命名录音3535' in tl:
                    q_end = k
                    break
            if q_end is not None:
                new_q = '\n'.join(tlines[:q_end + 1]).strip()
                admin = '\n'.join(tlines[q_end + 1:]).strip()
                admin = (admin + '\n' + quote).strip() if quote else admin
                desc = real_desc
                quote = new_q
                qb = admin

    # ---- content fixes ----
    if name == '暗月淑女':
        quote = quote.replace('艾沃', '艾弗里')
    if name == '无名':
        desc = desc.replace('无效。。', '无效。')
    if name == '酒吧幻境':
        desc = desc.replace('在酒吧中醉酒感，饱腹感也会一并消失',
                            '在酒吧中（积攒的）醉酒感和饱腹感也会一并消失')

    # ---- 无名解放: spaces-name -> 无名, replace 「         」 in desc ----
    if name.strip() == '' and holder == '本尼艾诺':
        name = '无名'
        stage = '解放阶段'
        desc = desc.replace('「         」', '「无名」')

    # ---- stat normalization ----
    stat_map = {'破坏力': 'pow', '侵蚀力': 'pow', '力量': 'pow',
                '速度': 'spd', '耐力': 'end', '范围': 'rng',
                '狂热': 'frz', '狂热性': 'frz', '理智': 'frz', '防御': 'def'}
    out_stats = {'pow': '', 'spd': '', 'end': '', 'rng': '', 'frz': '', 'def': ''}
    for key, val in stats.items():
        out_stats[stat_map.get(key, '')] = val

    return {
        'name': name,
        'holder': holder,
        'crt': crt,
        'pow': out_stats['pow'], 'spd': out_stats['spd'], 'end': out_stats['end'],
        'rng': out_stats['rng'], 'frz': out_stats['frz'], 'def': out_stats['def'],
        'desc': desc,
        'quote': quote,
        'qb': qb,
        'note': '\n'.join(range_notes),
        'zpn': zpn,
        'section': section,
        'stage': stage,
    }

abilities = []
current_section = None
for idx, (pos, typ, payload) in enumerate(block_starts):
    if typ == 'section':
        current_section = payload.strip('【】').replace('“', '"').replace('”', '"')
        continue
    end = block_starts[idx + 1][0] if idx + 1 < len(block_starts) else len(lines)
    block = lines[pos:end]
    a = parse_ability(block, payload, current_section)
    if a is not None:
        abilities.append(a)

print(f'Found {len(abilities)} abilities', file=sys.stderr)
with open('../data/abilities_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(abilities, f, ensure_ascii=False, indent=2)
print('Saved to data/abilities_parsed.json')

# Summary for verification
for a in abilities:
    stage_tag = f"[{a['stage']}]" if a['stage'] else ''
    zpn_tag = '[镇压院区]' if a['zpn'] else ''
    print(f"  {a['name']}{stage_tag}{zpn_tag} <- {a['section']} (holder={a['holder']})")
