"""Parse 永恒流光能力设定集.txt into structured JavaScript data."""
import re, json, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('../src/永恒流光能力设定集（2026.6.10）（工地状态）(2).txt', 'r', encoding='utf-8') as f:
    text = f.read()

outfile = open('../data/abilities_output.js', 'w', encoding='utf-8')
def p(*args, **kwargs):
    print(*args, file=outfile, **kwargs)

lines = text.split('\n')

# Parse structure: timeline headers like 【卢纳森特阵营-序章】, faction headers like 【第二代时之秩序】
# Ability entries start with 「ability_name」
# Fields: 持有者：name, CRT-xx, 破坏力-X 速度-X 耐力-X 范围-X 狂热-X 防御-X, 能力：desc, quotes with "——"

timelines = []  # [{name, factions: [{name, abilities: [...]}]}]
current_timeline = None
current_faction = None
current_ability = None
in_ability_desc = False
desc_lines = []

TIMELINE_RE = re.compile(r'【(.+?)】$')
FACTION_RE = re.compile(r'【(.+?)】$')
ABILITY_RE = re.compile(r'^「(.+?)」$')
HOLDER_RE = re.compile(r'^持有者[：:](.+)')
CRT_RE = re.compile(r'^CRT[：:－-]?\s*([\d.?]+)')
STATS_RE = re.compile(r'破坏力-(\S+)\s+速度-(\S+)\s+耐力-(\S+)')
RANGE_RE = re.compile(r'范围-(\S+)')
FRENZY_RE = re.compile(r'狂热[性]?-(\S+)')
DEFENSE_RE = re.compile(r'防御-(\S+)')
QUOTE_RE = re.compile(r'^[「"“](.+?)[」"”]')
QUOTE_SRC_RE = re.compile(r'^——(.+)')
RANGE_NOTE_RE = re.compile(r'^\*(\S.*)')

def finalize_ability():
    global current_ability, desc_lines, in_ability_desc
    if current_ability and desc_lines:
        full_desc = '\n'.join(desc_lines).strip()
        # Extract quote (last part starting with ——)
        quote = ''
        desc_parts = full_desc.split('——')
        if len(desc_parts) > 1:
            quote = '——' + desc_parts[-1].strip()
            main_desc = '——'.join(desc_parts[:-1]).strip()
        else:
            main_desc = full_desc

        # Also extract * range notes
        range_note = ''
        rm = RANGE_NOTE_RE.match(main_desc)
        if rm:
            range_note = rm.group(1).strip()

        current_ability['description'] = main_desc
        current_ability['quote'] = quote
        current_ability['rangeNote'] = range_note
        if current_faction is not None:
            current_faction['abilities'].append(current_ability)
    current_ability = None
    desc_lines = []
    in_ability_desc = False

def parse_stat_line(line):
    """Parse the 6 stats from a line like '破坏力-B 速度-A 耐力-B 范围-C* 狂热-A 防御-B'"""
    stats = {'破坏力': '', '速度': '', '耐力': '', '范围': '', '狂热': '', '防御': ''}
    parts = line.replace('\t', ' ').split()
    for part in parts:
        for key in stats:
            if part.startswith(key):
                val = part[len(key):]
                if val.startswith('-') or val.startswith('：') or val.startswith(':'):
                    val = val[1:]
                stats[key] = val.strip()
                break
    return stats

# Main parse loop
i = 0
while i < len(lines):
    line = lines[i].strip()

    # Skip empty, file header
    if not line or line.startswith('FILE:') or line.startswith('===') or line.startswith('【2026'):
        i += 1
        continue

    # Timeline/faction headers
    m = re.match(r'^【(.+?)】$', line)
    if m:
        name = m.group(1)
        # Skip notes like "第二代时之秩序中，亡灵兔与莱克丝为非能力使"
        if '非能力使' in name or '均为能力使' in name or '不是能力使' in name or '没有能力' in name:
            i += 1
            continue
        # Skip descriptive notes
        if name.startswith('沃克加德阵营') or name.startswith('前传') or name.startswith('卢纳森特基地的行政') or name.startswith('拓展') or name.startswith('注意') or name.startswith('该能力为') or name.startswith('本章') or name.startswith('第四章') or name.startswith('霍因佩兹时间线') or name.startswith('柯洛雯时间线') or name.startswith('洛琛顿时间线'):
            # These are descriptive, treat as potential timeline headers
            if any(kw in name for kw in ['阵营', '时间线', '前传']):
                finalize_ability()
                current_timeline = {'name': name, 'factions': []}
                timelines.append(current_timeline)
                current_faction = None
            i += 1
            continue

        # Check if this is a faction header (under a timeline)
        if current_timeline is not None:
            finalize_ability()
            # This could be a faction name
            current_faction = {'name': name, 'abilities': []}
            current_timeline['factions'].append(current_faction)
        else:
            # Standalone timeline
            finalize_ability()
            current_timeline = {'name': name, 'factions': []}
            timelines.append(current_timeline)
            current_faction = None
        i += 1
        continue

    # Ability name
    m = re.match(r'^「(.+?)」$', line)
    if m and i + 1 < len(lines):
        # Check if next few lines contain holder/CRT
        next_lines = [l.strip() for l in lines[i+1:i+4]]
        has_holder = any(HOLDER_RE.match(l) for l in next_lines)
        if has_holder:
            finalize_ability()
            current_ability = {
                'name': m.group(1),
                'holder': '',
                'crt': '',
                'stats': {},
                'description': '',
                'quote': '',
                'rangeNote': '',
                'variants': []  # for alternate forms like 暴走, 解放阶段 etc.
            }
            desc_lines = []
            in_ability_desc = False
            i += 1
            continue

    # Parse ability fields
    if current_ability is not None:
        hm = HOLDER_RE.match(line)
        if hm:
            current_ability['holder'] = hm.group(1).strip()
            i += 1
            continue

        cm = CRT_RE.match(line)
        if cm:
            current_ability['crt'] = cm.group(1).strip()
            i += 1
            continue

        # Stats line
        if '破坏力-' in line or '破坏力：' in line:
            current_ability['stats'] = parse_stat_line(line)
            # Range note might be on next line
            if i + 1 < len(lines) and lines[i+1].strip().startswith('*'):
                current_ability['rangeNote'] = lines[i+1].strip().lstrip('*').strip()
                i += 1
            i += 1
            continue

        # Special stats line pattern for 镇压院区 abilities
        if '侵蚀力-' in line or '力量-' in line:
            current_ability['stats'] = parse_stat_line(line.replace('侵蚀力', '破坏力').replace('理智', '狂热').replace('力量', '破坏力'))
            if i + 1 < len(lines) and lines[i+1].strip().startswith('*'):
                current_ability['rangeNote'] = lines[i+1].strip().lstrip('*').strip()
                i += 1
            i += 1
            continue

        # Range note
        if line.startswith('*') and current_ability['stats']:
            current_ability['rangeNote'] = line.lstrip('*').strip()
            i += 1
            continue

        # Ability description start
        if line == '能力：' or line == '能力:' or line.startswith('能力：') or line.startswith('能力:'):
            in_ability_desc = True
            i += 1
            continue

        # Poem/special text lines (short lines in quotes or verse)
        if line.startswith('"') and len(line) < 80 and not in_ability_desc:
            desc_lines.append(line)
            i += 1
            continue

        if in_ability_desc:
            # Stop conditions
            if re.match(r'^【.+】$', line) or ABILITY_RE.match(line):
                finalize_ability()
                continue
            if HOLDER_RE.match(line) and current_ability.get('description'):
                finalize_ability()
                continue
            desc_lines.append(line)

    i += 1

# Finalize last ability
finalize_ability()

# Clean up: merge empty timelines/factions, handle variant abilities
# Remove empty timelines
timelines = [t for t in timelines if t['factions']]
for t in timelines:
    t['factions'] = [f for f in t['factions'] if f['abilities']]

# Print as JS
def escape_js(s):
    return s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')

p('// Auto-generated ability data from 永恒流光能力设定集')
p(f'// {len(timelines)} timelines parsed')
p('const abilityArchive = [')
for ti, t in enumerate(timelines):
    p(f'  {{ // {t["name"]}')
    p(f'    timeline: \'{escape_js(t["name"])}\',')
    p(f'    factions: [')
    for fi, f in enumerate(t['factions']):
        p(f'      {{ // {f["name"]}')
        p(f'        faction: \'{escape_js(f["name"])}\',')
        p(f'        abilities: [')
        for ai, a in enumerate(f['abilities']):
            stats = a.get('stats', {})
            p(f'          {{')
            p(f'            name: \'{escape_js(a["name"])}\',')
            p(f'            holder: \'{escape_js(a.get("holder", ""))}\',')
            p(f'            crt: \'{escape_js(a.get("crt", ""))}\',')
            p(f'            pow: \'{stats.get("破坏力", "")}\',')
            p(f'            spd: \'{stats.get("速度", "")}\',')
            p(f'            end: \'{stats.get("耐力", "")}\',')
            p(f'            rng: \'{stats.get("范围", "")}\',')
            p(f'            frz: \'{stats.get("狂热", "")}\',')
            p(f'            def: \'{stats.get("防御", "")}\',')
            p(f'            desc: \'{escape_js(a.get("description", ""))}\',')
            p(f'            quote: \'{escape_js(a.get("quote", ""))}\',')
            p(f'            note: \'{escape_js(a.get("rangeNote", ""))}\'')
            p(f'          }}{"," if ai < len(f["abilities"]) - 1 else ""}')
        p(f'        ]')
        p(f'      }}{"," if fi < len(t["factions"]) - 1 else ""}')
    p(f'    ]')
    p(f'  }}{"," if ti < len(timelines) - 1 else ""}')
p('];')
outfile.close()

# Print summary
total = sum(len(a) for t in timelines for f in t['factions'] for a in f['abilities'])
print(f'// Total abilities: {total}', file=__import__('sys').stderr)
for t in timelines:
    count = sum(len(a) for f in t['factions'] for a in f['abilities'])
    print(f'//   {t["name"]}: {count} abilities', file=__import__('sys').stderr)
    for f in t['factions']:
        print(f'//     {f["name"]}: {len(f["abilities"])} abilities', file=__import__('sys').stderr)
