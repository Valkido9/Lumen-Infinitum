# -*- coding: utf-8 -*-
"""为缺经典台词的百科词条补引语块（插在 wiki-sub 之后、基本档案之前）。"""
import re

path = 'sidetory.html'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

quotes = {
  'char-wiki-kenuo':      ('我绝对不能向一根蠢棍子投降！', '——克诺，序幕'),
  'char-wiki-laikesi':    ('我真是对你们这群能力使羡慕嫉妒恨……', '——莱克丝，序幕'),
  'char-wiki-zhouniang':  ('哎呀，不要紧！我能解决这个问题的。', '——粥娘，序幕'),
  'char-wiki-wuming':     ('现在我暂且将你的能力命名为\'双生烈阳\'。', '——无名，序幕'),
  'char-wiki-liuba':      ('来喝点鲜奶吧。我们边喝边聊。', '——六八，第一卷'),
  'char-wiki-gieniefa':   ('……斯帕里森先生只是有什么事情，一定是这样的！', '——歌涅法，第一卷'),
  'char-wiki-liulupo':    ('我哪来的性子看书。……啧，内城人……', '——琉璐珀，第一卷'),
  'char-wiki-meinade':    ('我名为梅纳德·庞奇，是教皇城海域海盗的头领。', '——梅纳德，第一卷'),
  'char-wiki-yayinsente': ('我名为，亚因森特·埃德加……告诉我，你的棺材上会刻上什么名字，刺客。', '——亚因森特，第一卷'),
  'char-wiki-lukasen':    ('内城军务部执事领事，伦道夫·卢卡森。', '——卢卡森，第一卷'),
  'char-wiki-kangmingde': ('大航海时代，通融一下。', '——康明德，序幕'),
}

# 定位每个 entry 及其 wiki-sub 行
entries = []
cur = None
for idx, line in enumerate(lines):
    m = re.search(r'<div class="wiki-entry" id="([^"]+)"', line)
    if m:
        cur = {'id': m.group(1), 'sub': None}
        entries.append(cur)
    if cur is not None and '<div class="wiki-sub">' in line and cur['sub'] is None:
        cur['sub'] = idx

# 收集待插入 (行号, 块)，按行号降序插入以避免索引漂移
plan = []
for e in entries:
    if e['id'] in quotes and e['sub'] is not None:
        qt, src = quotes[e['id']]
        block = f'      <div class="wiki-quote">"{qt}"\n        <span class="q-src">{src}</span>\n      </div>\n'
        plan.append((e['sub'], block))
plan.sort(key=lambda x: x[0], reverse=True)
for sub, block in plan:
    lines.insert(sub + 1, block)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('inserted:', len(plan))
for _, b in plan:
    m = re.search(r'<span class="q-src">([^<]+)</span>', b)
    print('  ', m.group(1))
