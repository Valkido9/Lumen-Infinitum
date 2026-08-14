#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根据设定集 2025.4.28 的提取 JSON，生成网页版 SETTING_DATA（JS 数据字面量）。

节点结构：
  {id, title, badge?, empty?, body:[block...], children:[node...]}
  block 支持：
    ('p', idx)            -> 段落
    ('quote', idx)        -> 引言块（居中等宽引用）
    ('img', file, caption) -> 图片
    ('trait', [label_idx, list_idx]) -> 院区特质行
    ('note', text)        -> 自定义注记
输出：
  data/setting_data.js   —— 只含 `const SETTING_DATA = [...]`（无引号、无尾分号），
                           供插入 world.html 使用。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data', 'setting_2025_4_28_structure.json')
OUT = os.path.join(ROOT, 'data', 'setting_data.js')

data = json.load(open(SRC, encoding='utf-8'))

def T(i):
    """第 i 项的文本（去掉首尾空白）。"""
    return data[i]['text'].strip()

# ---- 便捷构造器（文本已内联）----
def p(*idx):
    return [('p', T(i)) for i in idx]

def quote(idx):
    return [('quote', [T(i) for i in idx])]

def attrib(idx):
    return [('p_attrib', T(idx))]

def trait(rows):
    """rows: list of (label_idx, list_idx)"""
    return [('trait', [T(l), T(v)]) for l, v in rows]

def img(seq, cap):
    return [('img', seq, cap)]

def node(node_id, title, body=None, children=None, badge=None, empty=False):
    return {
        'id': node_id, 'title': title,
        'body': body or [],
        'children': children or [],
        'badge': badge, 'empty': empty,
    }

# ---- 时间线空二级标题 ----
TL_SUB = [
    ('geo', '地理与环境'),
    ('hist', '历史沿革'),
    ('power', '政治与势力'),
    ('now', '现状与故事关联'),
]
def tl_subs(tl_id):
    return [node(f'{tl_id}-{k}', v, empty=True) for k, v in TL_SUB]

def tl_node(tl_id, title, body_idx):
    return node(tl_id, title, p(*body_idx), tl_subs(tl_id))

# ---- 组装树 ----
SETTING_DATA = [
    node('st-ch1', '第一章 基础设定部分', quote([0]) + p(1), [
        node('st-tlspace', '一、时间线与时间线空间', p(4, 5, 6, 7, 8), [
            node('st-order', '二、关于指令之力', p(10, 11, 12, 13, 14)),
            node('st-tloverview', '三、特异时间线概述',
                 p(16, 17, 18, 19) + attrib(20) + p(21, 22, 23, 24, 25), [
                tl_node('st-tl-luna', '卢纳森特时间线', [27, 28, 29, 30]),
                tl_node('st-tl-wok', '沃克加德时间线', [32, 33, 34]),
                tl_node('st-tl-hoy', '霍因佩兹时间线', [36, 37, 38]),
                tl_node('st-tl-luo', '洛琛顿时间线', [40, 41, 42, 43, 44, 45, 46, 47]),
                tl_node('st-tl-ke', '柯洛雯时间线', [49, 50, 51, 52, 53]),
                tl_node('st-tl-fen', '芬奈法拉时间线', [55, 56, 57, 58, 59, 60, 61]),
            ]),
        ]),
        node('st-tech', '超能力相关科技树', quote([63]) + p(64) + attrib(65) + p(66), [
            node('st-yeli', '业理猜想 · 鸿荧',
                 p(67, 68, 69) + img('image1.png', T(71))),
            node('st-omni', '全知视角下的科技树体系',
                 p(72) + img('image2.png', T(74)) + p(75), [
                node('st-orderp', '指令之力', p(78, 79) + img('image3.png', T(76)), [
                    node('st-core', '本我核心',
                         p(81, 82) + img('image4.png', T(84)) + p(85), [
                        node('st-core-center', '中心院区 · 永恒院', p(87, 88)),
                        node('st-core-inner', '内部四区', p(90, 91, 92, 93)),
                        node('st-core-outer', '外部四区',
                             p(95, 96, 97) + img('image2.jpeg', T(99)) + p(100, 101)),
                        node('st-core-term', '终端四区', p(103, 104)),
                        node('st-core-echo', '留声 · 神谕 · 终界碎片',
                             p(105, 106, 107, 108, 109) + attrib(110)),
                        node('st-core-time', '永恒院与时间原理', p(111, 112)),
                        node('st-core-trait', '院区特质',
                             p(113, 114) + img('image5.png', T(116)) + p(117, 118), [
                            node('st-core-trait-in', '内部四区 ·「个人」',
                                 p(119) + trait([[120, 121], [122, 123], [124, 125], [126, 127]])),
                            node('st-core-trait-out', '外部四区 ·「世界」',
                                 p(128) + trait([[129, 130], [131, 132], [133, 134], [135, 136]])),
                            node('st-core-trait-rule', '共鸣与能力特性', p(137, 138, 139, 140, 141, 142)),
                        ]),
                    ]),
                    node('st-equip', '指令之力装备 / 反指令之力装备',
                         p(145, 146, 147, 148) + img('image6.png', T(143)), badge='施工中 · 未写完'),
                    node('st-timepower', '时光机能力', p(151) + img('image7.png', T(149))),
                ]),
                node('st-magic', '魔法', p(154, 155, 156) + img('image8.png', T(152)), [
                    node('st-magic-pharm', '魔药学', p(157, 158)),
                    node('st-magic-white', '白魔法与黑魔法', p(159, 160), [
                        node('st-magic-ele', '元素魔法', p(161)),
                        node('st-magic-const', '构造魔法', p(162)),
                        node('st-magic-hi', '高能魔法', p(163)),
                    ]),
                ]),
                node('st-pure', '纯粹业理',
                     p(167, 168) + [('note', '【原文在此截断——设定集文档尚未写完】')] +
                     img('image9.png', T(164)), badge='未写完 · 施工中'),
            ]),
        ]),
    ]),
]

# ---- 生成 JS 字面量 ----
body = json.dumps(SETTING_DATA, ensure_ascii=False, indent=1)
# 安全检查
for bad in ['</script', '</Script', '<!--', '-->']:
    if bad in body:
        raise SystemExit(f'! 内容含危险片段 {bad!r}')

js = 'const SETTING_DATA = ' + body + ';\n'
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(js)

# 统计
def count(n):
    c = 1
    for ch in n['children']:
        c += count(ch)
    return c
total = sum(count(n) for n in SETTING_DATA)
paras = 0
imgs = 0
for n in json.loads(body):
    def walk(node):
        global paras, imgs
        for b in node['body']:
            if isinstance(b, list):
                if b[0] == 'img':
                    imgs += 1
                elif b[0] in ('p', 'quote'):
                    paras += 1
        for ch in node['children']:
            walk(ch)
    walk(n)
print(f'完成：节点总数 {total}（含空占位），段落块 {paras}，图片 {imgs}')
print('输出 ->', os.path.relpath(OUT, ROOT))
