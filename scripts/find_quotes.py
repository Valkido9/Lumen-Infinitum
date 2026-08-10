# -*- coding: utf-8 -*-
"""在序幕/第一卷正文文档中查找指定角色的对白（用于补百科经典台词）。"""
import re

docs = [
    'src/序章正文（2025.8待改）(1)(1).txt',
    'src/第一章正文 2024.1.25 工地状态.txt',
    'src/第一章正文（第二部分）.txt',
]

chars = [
    ('克诺', ['克诺']),
    ('莱克丝', ['莱克丝', '莱克斯']),
    ('粥娘', ['粥娘']),
    ('无名', ['无名']),
    ('六八', ['六八']),
    ('歌涅法', ['歌涅法']),
    ('琉璐珀', ['琉璐珀']),
    ('斯帕里森', ['斯帕里森']),
    ('梅纳德', ['梅纳德']),
    ('亚因森特', ['亚因森特']),
    ('卢卡森', ['卢卡森', '卢克森']),
    ('康明德', ['康明德']),
    ('艾索利', ['艾索利', '艾苏里']),
    ('斯卡娜', ['斯卡娜']),
    ('吉贝玲', ['吉贝玲']),
    ('紫珊瑚', ['紫珊瑚']),
]

texts = {}
for p in docs:
    try:
        with open(p, encoding='utf-8') as f:
            texts[p] = f.read()
    except Exception as e:
        texts[p] = ''
        print('ERROR', p, e)

Q = re.compile(r'[“”「」]')
out = []
for name, aliases in chars:
    out.append('=' * 24)
    out.append('角色: ' + name)
    found = 0
    for p, text in texts.items():
        lines = text.split('\n')
        short = p.split('/')[-1][:10]
        for i, ln in enumerate(lines):
            if not any(a in ln for a in aliases):
                continue
            # 本行或相邻行是否有引号（对白）
            window = lines[max(0, i - 1):i + 2]
            if not any(Q.search(w) for w in window):
                continue
            if found >= 10:
                break
            found += 1
            ctx = ' ‖ '.join(w.strip()[:90] for w in window if w.strip())
            out.append(f'  [{short} L{i+1}] {ctx}')
    if found == 0:
        out.append('  （在序幕/第一卷未找到含引号的对白）')
    out.append('')

with open('_quotes_scan.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('done')
