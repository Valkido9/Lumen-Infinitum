"""Convert parsed abilities JSON to JS code for index.html (section-based timelines)."""
import json, os, re

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('../data/abilities_parsed.json', 'r', encoding='utf-8') as f:
    abilities = json.load(f)

stat_val = {'EX': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1, 'S': 5, '': 0, '?': 0, '？': 0}

def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n')

# ---- annotations that DELETE entries ----
# #33 删除 真视魔瞳（明风）
# #27 曾删除 恶血天堂（十七）与其下的 幻血之梦（达克多）；用户要求恢复 恶血天堂，已在 index.html 手工补入（ab118），故不再删除
DELETED = {'幻血之梦', '真视魔瞳'}

# ---- section → (timeline, faction) ----
SECTION_MAP = {
    '第二代时之秩序': ('卢纳森特阵营 · 序章', '第二代时之秩序'),
    '圣标联合': ('卢纳森特阵营 · 序章', '圣标联合'),
    '潮涌居士号': ('沃克加德阵营', '潮涌居士号'),
    '蓝河明船': ('沃克加德阵营', '蓝河明船'),
    '第一章 最终战部分': ('沃克加德阵营', '第一章最终战'),
    '浪庄游击队': ('沃克加德阵营', '浪庄游击队'),
    '深雾城阵营': ('沃克加德阵营', '深雾城阵营'),
    '珀利贝尔实业-亲卫队"渊海明灯"': ('霍因佩兹时间线', '珀利贝尔实业 · 亲卫队'),
    '珀利贝尔实业-部门领导组': ('霍因佩兹时间线', '珀利贝尔实业 · 部门领导组'),
    '寒城工坊': ('霍因佩兹时间线', '寒城工坊'),
    '长夜事务所': ('霍因佩兹时间线', '长夜事务所'),
    '第二章最终战部分': ('霍因佩兹时间线', '第二章最终战'),
    '神国': ('霍因佩兹时间线', '神国'),
    '牧人': ('洛琛顿时间线', '牧人'),
    '爱丽丝马戏团': ('洛琛顿时间线', '爱丽丝马戏团'),
    '洛琛顿中，不属于任何阵营的角色': ('洛琛顿时间线', '其他势力'),
    '第三章最终战部分': ('洛琛顿时间线', '第三章最终战'),
    '初代时之秩序': ('卢纳森特基地 · 初代时之秩序', '初代时之秩序'),
    '基地其他部门': ('卢纳森特基地 · 初代时之秩序', '基地其他部门'),
    '卢纳森特基地': ('卢纳森特基地 · 初代时之秩序', '基地其他部门'),
    '"没名字的组合"': ('柯洛雯时间线', '没名字的组合'),
    '柯洛雯中，不属于任何阵营的角色': ('柯洛雯时间线', '其他角色'),
    '柯洛雯第三帝国': ('柯洛雯时间线', '柯洛雯第三帝国 · 第四章最终战'),
    '第四章最终战部分': ('柯洛雯时间线', '柯洛雯第三帝国 · 第四章最终战'),
    '芬奈法拉战线': ('芬奈法拉战线', '芬奈法拉战线'),
    '第五章最终战部分': ('第五章最终战', '第五章最终战'),
    '十七前传': ('前传相关', '十七前传'),
    '卢纳森特共和国': ('前传相关', '正义前传'),
    '圣奈特莉学院': ('前传相关', '正义前传'),
    '碎暮异团': ('前传相关', '正义前传'),
    '在正义前传中，不属于任何阵营的角色': ('前传相关', '正义前传'),
    '正义前传最终战部分': ('前传相关', '正义前传'),
}
TIMELINE_ORDER = ['卢纳森特阵营 · 序章', '沃克加德阵营', '霍因佩兹时间线',
                  '洛琛顿时间线', '卢纳森特基地 · 初代时之秩序', '柯洛雯时间线',
                  '芬奈法拉战线', '第五章最终战', '前传相关']
FALLBACK = ('其他时间线 & 角色', '其他势力')

# ---- build abilityData ----
lines = []
lines.append('// Auto-generated from 永恒流光能力设定集 (2026.6.10)')
lines.append('const abilityData = [')

seen = set()
count = 0
ids_by = {}       # (timeline, faction) -> list of abIds
fallback_ids = []
unmapped_names = []

# first collect abIds per ability in document order
entry_ids = {}    # name -> abId (for cross-ref during timeline assembly)

order = []
for a in abilities:
    name = a['name'].strip()
    holder = a['holder'].strip()
    crt = a['crt'].strip()
    stage = a['stage']

    # deletions
    if name in DELETED:
        continue
    if not name or not holder:
        continue

    # renames
    if holder == '马萨卡（暴走）':
        name = '天平（解放阶段）'
        holder = '马萨卡（解放阶段）'
        stage = '解放阶段'
    if stage == '解放阶段' and '阶段' not in name:
        # mark liberation-stage abilities (name keeps distinct 解放-stage naming)
        name = name + '（解放阶段）'
    # 无名（本尼艾诺）解放阶段：名字为纯空白（原文档以「         」指代，观测不到能力真名；用全角空格填充，避免HTML折叠，约五个字宽度）
    if holder == '本尼艾诺' and stage == '解放阶段':
        name = '　　　　　'

    key = f"{name}|{holder}"
    if key in seen:
        continue
    seen.add(key)

    # CRT cleanup (siege detection happens in the renderer: max CRT > 14, non-zpn)
    crt_clean = crt.replace('（', '(').replace('）', ')').replace('：', ':').strip()
    zpn_note = (a.get('zpn') or '').strip().strip('【】').strip()

    # stats
    stats = []
    for k in ['pow', 'spd', 'end', 'rng', 'frz', 'def']:
        v = (a.get(k) or '').replace('*', '').replace('：', '').replace(':', '').strip()
        v = v.split('/')[0].strip()
        v = v.strip('-').strip()
        stats.append(str(stat_val.get(v, 0)))

    desc = (a.get('desc') or '').strip()
    quote = (a.get('quote') or '').strip()
    note = (a.get('note') or '').strip()
    qb = (a.get('qb') or '').strip()

    spoiler = ('虽然这个能力经过更合理的运用' in quote)

    # #10: strip 斯帕里森's self-claim, keep attribution
    if holder == '斯帕里森' and '强运加持' in quote:
        attrib = quote.find('——《')
        if attrib != -1:
            quote = quote[attrib:]

    # section-based timeline/faction
    section = a.get('section', '')
    if section in SECTION_MAP:
        tl, fac = SECTION_MAP[section]
    else:
        tl, fac = FALLBACK
        unmapped_names.append(name)

    aid = f"ab{count}"
    count += 1
    entry_ids[name] = aid

    ids_by.setdefault((tl, fac), []).append(aid)

    # extra fields
    extra = ''
    if quote:
        extra += f'q:"{esc(quote)}",'
    if qb:
        extra += f'qb:"{esc(qb)}",'
    if note:
        extra += f'nt:"{esc(note)}",'
    if zpn_note:
        extra += 'zn:"' + esc(zpn_note) + '",'
    if stage == '解放阶段':
        extra += 'st:"解放阶段",'
    if spoiler:
        extra += 'sp:1,'

    lines.append(f'  {{id:"{aid}",n:"{esc(name)}",h:"{esc(holder)}",c:"{esc(crt_clean)}",')
    lines.append(f'   s:[{",".join(stats)}],')
    lines.append(f'   d:"{esc(desc)}",')
    if extra:
        lines.append(f'   {extra}')
    lines.append(f'  }},')

lines.append('];')
ability_count = count

# ---- #30: move 海拉克利斯's 魔导之王 + 乐土 to the very bottom ----
# they already live in 前传相关/正义前传; ensure they are the LAST entries there.
hercules = {}
for a in abilities:
    n = a['name'].strip()
    if n in ('魔导之王', '乐土'):
        # compute the same transformed name as above
        nn = n
        if a['stage'] == '解放阶段' and '阶段' not in nn:
            nn = nn + '（解放阶段）'
        hid = entry_ids.get(nn)
        if hid:
            hercules.setdefault('all', []).append(hid)

# remove from current positions, then append to last faction
last_tl_fac = ('前传相关', '正义前传')
ids_by[last_tl_fac] = [i for i in ids_by.get(last_tl_fac, []) if i not in set(hercules.get('all', []))]
ids_by[last_tl_fac] = ids_by[last_tl_fac] + hercules.get('all', [])

# ---- build abilityTimelines ----
lines.append('')
lines.append('// Timeline & faction organization')
lines.append('const abilityTimelines = [')
for tl in TIMELINE_ORDER:
    factions = [(f, ids) for (t, f), ids in ids_by.items() if t == tl and ids]
    if not factions:
        continue
    lines.append(f'  {{')
    lines.append(f'    name: "{esc(tl)}",')
    lines.append(f'    factions: [')
    for fac, ids in factions:
        ids_str = ','.join(f'"{i}"' for i in ids)
        lines.append(f'      {{ name: "{esc(fac)}", abIds: [{ids_str}] }},')
    lines.append(f'    ]')
    lines.append(f'  }},')
# fallback timeline for anything unmapped (should be empty)
for fac, ids in sorted(ids_by.items()):
    if fac[0] not in TIMELINE_ORDER and ids:
        ids_str = ','.join(f'"{i}"' for i in ids)
        lines.append(f'  {{ name: "{esc(fac[0])}", factions: [ {{ name: "{esc(fac[1])}", abIds: [{ids_str}] }} ] }},')
lines.append('];')

with open('../data/ability_archive.js', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'Generated {ability_count} abilities to data/ability_archive.js')
if unmapped_names:
    print(f'WARNING: unmapped sections -> {unmapped_names}')
