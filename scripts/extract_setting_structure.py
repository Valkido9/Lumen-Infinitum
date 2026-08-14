#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 永恒流光设定集2025.4.28.docx 提取结构化内容：标题层级 + 段落 + 图片锚点。

docx 是 zip。解析 word/document.xml（顺序保留）、word/_rels/document.xml.rels
（r:embed -> media 文件名）、word/media/*（图片文件）。

输出 JSON 到 data/setting_2025_4_28_structure.json，每项：
  {"type": "heading", "level": 1-9, "text": "..."}
  {"type": "para", "text": "...", "image": "image1.png" | null}
图片同时已由 scripts/extract_docx_images.py 提取到 docx-images/<文档名>/。

用法：python scripts/extract_setting_structure.py
"""
import json
import os
import re
import zipfile
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX = os.path.join(ROOT, 'src', '永恒流光设定集2025.4.28.docx')
OUT = os.path.join(ROOT, 'data', 'setting_2025_4_28_structure.json')

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
}


def get_text(p):
    """段落全部 <w:t> 文本拼接。"""
    parts = []
    for t in p.iter('{%s}t' % NS['w']):
        parts.append(t.text or '')
    return ''.join(parts)


def heading_level(p):
    """从 pStyle 推断标题级别；非标题返回 0。"""
    ppr = p.find('w:pPr', NS)
    if ppr is None:
        return 0
    style = ppr.find('w:pStyle', NS)
    if style is None:
        return 0
    val = style.get('{%s}val' % NS['w']) or ''
    m = re.match(r'(?:Heading|heading|标题)?\s*(\d)$', val)
    if m:
        return int(m.group(1))
    if val in ('Title', 'titre', '标题'):
        return 1
    # 常见中文模板：标题1
    m = re.match(r'标题(\d)', val)
    if m:
        return int(m.group(1))
    return 0


def embedded_images(p):
    """段落中内嵌图片的 media 文件名列表（去重、保序）。"""
    imgs = []
    for blip in p.iter('{%s}blip' % NS['a']):
        rid = blip.get('{%s}embed' % NS['r'])
        if rid and rid in RELS:
            target = RELS[rid]
            if target.startswith('media/'):
                imgs.append(os.path.basename(target))
    # 去重但保持顺序
    seen = set()
    out = []
    for i in imgs:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def main():
    z = zipfile.ZipFile(DOCX)
    rels_xml = z.read('word/_rels/document.xml.rels').decode('utf-8')
    rroot = ET.fromstring(rels_xml)
    global RELS
    RELS = {}
    # 关系命名空间
    rn = 'http://schemas.openxmlformats.org/package/2006/relationships'
    for rel in rroot.iter('{%s}Relationship' % rn):
        rid = rel.get('Id')
        target = rel.get('Target')
        if rid and target:
            RELS[rid] = target.lstrip('/')
    doc_xml = z.read('word/document.xml').decode('utf-8')
    root = ET.fromstring(doc_xml)

    items = []
    body = root.find('w:body', NS)
    for el in body:
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            level = heading_level(el)
            text = get_text(el).strip()
            imgs = embedded_images(el)
            if level:
                items.append({'type': 'heading', 'level': level, 'text': text})
            else:
                if text or imgs:
                    items.append({'type': 'para', 'text': text,
                                  'image': imgs[0] if imgs else None})
        elif tag == 'tbl':
            # 表格：提取每个单元格文本，拼接为简化行
            rows = []
            for tr in el.iter('{%s}tr' % NS['w']):
                cells = []
                for tc in tr.findall('{%s}tc' % NS['w']):
                    ct = ' '.join(get_text(p) for p in tc.iter('{%s}p' % NS['w']))
                    cells.append(ct.strip())
                if any(cells):
                    rows.append(cells)
            items.append({'type': 'table', 'rows': rows})

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=1)

    heads = [i for i in items if i['type'] == 'heading']
    imgs = [i for i in items if i['type'] == 'para' and i.get('image')]
    paras = [i for i in items if i['type'] == 'para']
    print(f'完成：{len(items)} 项（标题 {len(heads)}，段落 {len(paras)}，含图段落 {len(imgs)}，表格 {sum(1 for i in items if i["type"]=="table")}）')
    print('输出 ->', os.path.relpath(OUT, ROOT))


if __name__ == '__main__':
    main()
