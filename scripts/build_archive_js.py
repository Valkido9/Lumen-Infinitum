"""Convert parsed abilities JSON to JS code for index.html."""
import json, os, re

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('../data/abilities_parsed.json', 'r', encoding='utf-8') as f:
    abilities = json.load(f)

# Stat mapping: EX=5, A=4, B=3, C=2, D=1
stat_val = {'EX':5, 'A':4, 'B':3, 'C':2, 'D':1, 'S':5, '':0, '?':0}

def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n')

# Group by timeline/faction based on order and naming patterns
# We'll organize them manually since the document structure varies
# For now, generate a flat list with timeline/faction tags based on the order
# The abilities are in document order, so we can infer structure

# Actually, let's just output a flat JS array keyed by ability ID
# The timeline/faction organization will be done in the rendering code

lines = []
lines.append('// Auto-generated from 永恒流光能力设定集 (2026.6.10)')
lines.append(f'// {len(abilities)} abilities')
lines.append('const abilityData = [')

# Track seen ability names to avoid duplicates
seen = set()
count = 0
for a in abilities:
    name = a['name'].strip()
    holder = a['holder'].strip()
    crt = a['crt'].strip()

    # Annotation #1: 马萨卡's 暴走-state 天平 is its 解放阶段 (release-stage) form
    if holder == '马萨卡（暴走）':
        name = '天平（解放阶段）'
        holder = '马萨卡（解放阶段）'

    # Skip garbage entries
    if not name or len(name) < 1:
        continue
    if name.startswith('……') or name.startswith('"'):
        continue
    if not holder:
        continue

    # Deduplicate
    key = f"{name}|{holder}"
    if key in seen:
        continue
    seen.add(key)

    # Clean CRT
    crt_clean = crt.replace('（', '(').replace('）', ')').replace('：', ':').strip()

    # Map stats to numeric
    import re
    stats = []
    for k in ['pow','spd','end','rng','frz','def']:
        v = a.get(k, '').replace('*','').replace('：','').replace(':','').strip()
        # Handle ranges like "B/A" or special cases
        v = v.split('/')[0].strip()
        # Remove Chinese prefixes (e.g. "狂热-B" -> "B", "范围-A*" -> "A")
        v = re.sub(r'^[^\x00-\x7F]+', '', v)  # remove leading CJK chars
        v = v.strip('-').strip()
        if v in stat_val:
            stats.append(str(stat_val[v]))
        else:
            stats.append('0')

    desc = a.get('desc', '').strip()
    quote = a.get('quote', '').strip()
    note = a.get('note', '').strip()

    # Spoiler flag: 司明's evaluation quote reveals 马萨卡's true strength
    spoiler = ('虽然这个能力经过更合理的运用' in quote)

    # Annotation #10: remove 斯帕里森's '强运加持/大难不死' self-claim quote.
    # The claim is wrapped in curly quotes “...”, then attribution follows.
    if holder == '斯帕里森' and '强运加持' in quote:
        open_q = quote.find('“')  # “
        attrib = quote.find('——《')  # ——《
        if open_q != -1 and attrib != -1 and open_q < attrib:
            quote = quote[attrib:]

    # Clean desc: remove the quote that got embedded in desc
    if quote and desc.endswith(quote):
        desc = desc[:-len(quote)].strip()
    if quote and desc.endswith(quote.strip('"')):
        desc = desc[:-len(quote.strip('"'))].strip()

    # Generate a safe ID
    aid = f"ab{count}"
    count += 1

    lines.append(f'  {{id:"{aid}",n:"{esc(name)}",h:"{esc(holder)}",c:"{esc(crt_clean)}",')
    lines.append(f'   s:[{",".join(stats)}],')
    lines.append(f'   d:"{esc(desc)}",')
    if quote:
        lines.append(f'   q:"{esc(quote)}",')
    if spoiler:
        lines.append(f'   sp:1,')
    if note:
        lines.append(f'   nt:"{esc(note)}",')
    lines.append(f'  }},')

lines.append('];')

# Add timeline/faction organization
lines.append('''
// Timeline & faction organization
const abilityTimelines = [
  {
    name: "卢纳森特阵营 · 序章",
    factions: [
      {
        name: "第二代时之秩序",
        abIds: ["ab0","ab1","ab2","ab3","ab4","ab5","ab6"]
      },
      {
        name: "圣标联合",
        abIds: ["ab7","ab8","ab9","ab10","ab11"]
      }
    ]
  },
  {
    name: "沃克加德阵营",
    factions: [
      {
        name: "潮涌居士号",
        abIds: ["ab12","ab13"]
      },
      {
        name: "蓝河明船",
        abIds: ["ab14","ab15","ab16","ab17","ab18","ab19","ab20"]
      },
      {
        name: "浪庄游击队",
        abIds: ["ab21"]
      },
      {
        name: "深雾城阵营",
        abIds: ["ab22"]
      }
    ]
  },
  {
    name: "霍因佩兹时间线",
    factions: [
      {
        name: "珀利贝尔实业 · 亲卫队",
        abIds: ["ab23","ab24","ab25"]
      },
      {
        name: "珀利贝尔实业 · 部门领导组",
        abIds: ["ab26"]
      },
      {
        name: "寒城工坊",
        abIds: ["ab27","ab28","ab29","ab30","ab31","ab32"]
      },
      {
        name: "长夜事务所",
        abIds: ["ab33","ab34","ab35","ab36","ab37"]
      },
      {
        name: "第二章最终战",
        abIds: ["ab38","ab39","ab40","ab41"]
      }
    ]
  },
  {
    name: "洛琛顿时间线",
    factions: [
      {
        name: "牧人",
        abIds: ["ab42","ab43","ab44","ab45"]
      },
      {
        name: "爱丽丝马戏团",
        abIds: ["ab46","ab47"]
      },
      {
        name: "其他势力",
        abIds: ["ab48","ab49","ab50","ab51","ab52","ab53"]
      },
      {
        name: "第三章最终战",
        abIds: ["ab54","ab55","ab56","ab57"]
      }
    ]
  },
  {
    name: "卢纳森特基地 · 初代时之秩序",
    factions: [
      {
        name: "初代时之秩序",
        abIds: ["ab58","ab59","ab60","ab61","ab62"]
      },
      {
        name: "基地其他部门",
        abIds: ["ab63","ab64","ab65"]
      }
    ]
  },
  {
    name: "柯洛雯时间线",
    factions: [
      {
        name: "没名字的组合",
        abIds: ["ab66","ab67","ab68","ab69"]
      },
      {
        name: "其他角色",
        abIds: ["ab70","ab71","ab72","ab73","ab74"]
      },
      {
        name: "柯洛雯第三帝国 · 第四章最终战",
        abIds: ["ab75","ab76","ab77"]
      }
    ]
  },
  {
    name: "芬奈法拉战线",
    factions: [
      {
        name: "芬奈法拉战线",
        abIds: ["ab78","ab79","ab80","ab81","ab82"]
      }
    ]
  },
  {
    name: "其他时间线 & 角色",
    factions: [
      {
        name: "其他势力",
        abIds: ["ab83","ab84","ab85","ab86","ab87"]
      }
    ]
  },
  {
    name: "前传相关",
    factions: [
      {
        name: "十七前传",
        abIds: ["ab88","ab89","ab90"]
      },
      {
        name: "正义前传",
        abIds: ["ab91","ab92","ab93","ab94","ab95","ab96","ab97","ab98","ab99"]
      }
    ]
  }
];
''')

with open('../data/ability_archive.js', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'Generated {count} abilities to data/ability_archive.js')

# Print the first few IDs for reference
for i in range(min(20, count)):
    a = abilities[i]
    print(f'  ab{i}: {a["name"]} - {a["holder"]}')
