"""Targeted parser for 永恒流光能力设定集 - extracts ability entries with stats."""
import re, json, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('../src/永恒流光能力设定集（2026.6.10）（工地状态）(2).txt', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Find all ability entries: lines starting with 「...」 that are followed by 持有者
abilities = []
i = 0
while i < len(lines):
    line = lines[i].strip()

    # Match ability name header: 「Name」
    m = re.match(r'^「(.+?)」$', line)
    if not m:
        i += 1
        continue

    name = m.group(1)

    # Look ahead for 持有者 within next 5 lines
    holder = ''
    crt = ''
    stat_line = ''
    range_note = ''
    desc_lines = []
    quote = ''

    found_ability = False
    for j in range(1, min(8, len(lines) - i)):
        ahead = lines[i + j].strip()

        hm = re.match(r'^持有者[：:]\s*(.+)', ahead)
        if hm:
            holder = hm.group(1).strip()
            found_ability = True
            continue

        cm = re.match(r'^CRT[：:\-－]?\s*(.+)$', ahead)
        if cm:
            crt = cm.group(1).strip()
            continue

        # Stat line with 破坏力
        if re.search(r'(破坏力|力量|侵蚀力)[\-：:]', ahead):
            stat_line = ahead
            # Also check next line for 范围/狂热/防御
            if i + j + 1 < len(lines):
                next_line = lines[i + j + 1].strip()
                if re.search(r'(范围|狂热|防御|理智)[\-：:]', next_line):
                    stat_line += ' ' + next_line
            continue

        # Range note
        if ahead.startswith('*') and not ahead.startswith('**'):
            range_note = ahead.lstrip('*').strip()
            continue

        # Poem/verse line (short quoted lines before 能力：)
        if (ahead.startswith('"') or ahead.startswith('「')) and len(ahead) < 100:
            if not desc_lines:  # Only as pre-description
                continue

    if not found_ability:
        i += 1
        continue

    # Find the description start (能力：)
    desc_start = -1
    for j in range(1, min(15, len(lines) - i)):
        ahead = lines[i + j].strip()
        if ahead == '能力：' or ahead == '能力:' or ahead.startswith('能力：') or ahead.startswith('能力:'):
            desc_start = i + j + 1
            break

    if desc_start > 0:
        # Collect description until next ability or section header
        for j in range(desc_start, min(desc_start + 40, len(lines))):
            dl = lines[j].strip()
            # Stop conditions
            if re.match(r'^【.+】$', dl) or re.match(r'^「.+」$', dl):
                break
            if re.match(r'^持有者[：:]', dl) and desc_lines:
                break
            if dl == '能力：' or dl == '能力:':
                break
            desc_lines.append(lines[j])  # Keep original line breaks

    # Parse stats from stat_line
    stats = {'破坏力':'','速度':'','耐力':'','范围':'','狂热':'','防御':''}
    if stat_line:
        parts = stat_line.replace('\t', ' ').split()
        key_map = {'破坏力':'破坏力','力量':'破坏力','侵蚀力':'破坏力',
                   '速度':'速度','耐力':'耐力','范围':'范围',
                   '狂热':'狂热','狂热性':'狂热','理智':'狂热',
                   '防御':'防御'}
        for part in parts:
            for long_key, short_key in key_map.items():
                if part.startswith(long_key):
                    val = part[len(long_key):]
                    if val.startswith('-') or val.startswith('：') or val.startswith(':'):
                        val = val[1:]
                    stats[short_key] = val.strip()
                    break

    # Build description text
    desc = '\n'.join(desc_lines).strip()

    # Extract quote (lines starting with —— at end of desc)
    desc_parts = desc.rsplit('\n——', 1)
    if len(desc_parts) > 1:
        desc = desc_parts[0].strip()
        quote = '——' + desc_parts[1].strip()
    elif desc.startswith('——'):
        # Quote at the beginning
        quote = desc
        desc = ''

    # Clean up desc: remove leading range notes that were captured
    desc_lines_clean = []
    for dl in desc.split('\n'):
        dl = dl.strip()
        if dl.startswith('*') and not dl.startswith('**'):
            if not range_note:
                range_note = dl.lstrip('*').strip()
            continue
        if dl.startswith('"') and len(dl) < 120:
            # Check if this is an evaluation quote
            if not quote and ('——' in dl or '录音来源' in dl):
                quote = dl
                continue
        desc_lines_clean.append(dl)

    desc = '\n'.join(desc_lines_clean).strip()
    # Remove standalone quotes from desc
    desc = re.sub(r'\n[""][^""]+[""](?:\n|$)', '', desc).strip()
    desc = re.sub(r'^[""][^""]+[""]$', '', desc).strip()

    # Skip if no meaningful description or not an ability
    # Filter out misidentified quotes
    if name.startswith('……') or name.startswith('"') or name.startswith('「') and len(name) > 15:
        i += 1
        continue
    if not desc and not stats['破坏力']:
        i += 1
        continue

    # Skip quote-only entries misidentified as abilities
    if holder == name or (not holder and not crt):
        i += 1
        continue

    abilities.append({
        'name': name,
        'holder': holder,
        'crt': crt,
        'pow': stats['破坏力'],
        'spd': stats['速度'],
        'end': stats['耐力'],
        'rng': stats['范围'],
        'frz': stats['狂热'],
        'def': stats['防御'],
        'desc': desc,
        'quote': quote,
        'note': range_note
    })

    i += 1

print(f'Found {len(abilities)} abilities', file=__import__('sys').stderr)

# Save as JSON
with open('../data/abilities_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(abilities, f, ensure_ascii=False, indent=2)

print(f'Saved to data/abilities_parsed.json')

# Print summary
for a in abilities[:5]:
    print(f"  {a['name']} - {a['holder']} - CRT:{a['crt']} - Stats:{a['pow']}/{a['spd']}/{a['end']}/{a['rng']}/{a['frz']}/{a['def']}")
print(f"  ... and {len(abilities)-5} more")
