# -*- coding: utf-8 -*-
"""将 sidetory.html 中所有 .wiki-quote 块挪到词条最顶（wiki-sub 之后、基本档案之前）。"""
import re

path = 'sidetory.html'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 定位每个 wiki-entry 的 start / sub_end / end
entries = []   # {start, sub_end, end, qblocks:[(s,e),...]}
cur = None
qstart = -1
for idx, line in enumerate(lines):
    if re.search(r'<div class="wiki-entry"', line):
        cur = {'start': idx, 'sub_end': None, 'end': None, 'qblocks': []}
        entries.append(cur)
    if cur is not None:
        if '<div class="wiki-sub">' in line and cur['sub_end'] is None and line.rstrip().endswith('</div>'):
            cur['sub_end'] = idx
        if '<div class="wiki-quote">' in line:
            qstart = idx
        if qstart >= 0 and '<div class="wiki-quote">' not in line and line.rstrip().endswith('</div>'):
            cur['qblocks'].append((qstart, idx))
            qstart = -1
        if re.match(r'^    </div>\s*$', line) and cur['sub_end'] is not None:
            cur['end'] = idx
            cur = None
if qstart >= 0:
    raise SystemExit('ERROR: unterminated wiki-quote block')

def reindent(block):
    """去掉块首行缩进基准 L0，统一缩进到 6 空格。"""
    base = len(block[0]) - len(block[0].lstrip(' '))
    out = []
    for ln in block:
        lead = len(ln) - len(ln.lstrip(' '))
        out.append('      ' + ' ' * max(0, lead - base) + ln.lstrip(' '))
    return out

out = []
i = 0
for e in entries:
    # 词条前的内容
    while i < e['start']:
        out.append(lines[i]); i += 1
    # 词条 start .. sub_end（含 wiki-sub）
    while i <= e['sub_end']:
        out.append(lines[i]); i += 1
    # 在 wiki-sub 之后插入引语块
    removed = set()
    for (qs, qe) in e['qblocks']:
        removed.update(range(qs, qe + 1))
        out.extend(reindent(lines[qs:qe + 1]))
    # 其余内容（跳过原引语位置）
    while i <= e['end']:
        if i not in removed:
            out.append(lines[i])
        i += 1
# 尾部
while i < len(lines):
    out.append(lines[i]); i += 1

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(out)

# 汇报
moved = 0
for e in entries:
    moved += len(e['qblocks'])
    names = []
print('moved quote blocks:', moved)
