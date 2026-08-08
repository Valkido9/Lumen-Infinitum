#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zipfile
import json
import os

OUTPUT = r"C:\Users\王宣溟\Desktop\永恒流光\永恒流光故事讲解.docx"
DATA_FILE = r"C:\Users\王宣溟\Desktop\永恒流光\story_data.json"

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    sections = json.load(f)

CT_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''

RELS_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

DOC_RELS_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''

def styles_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:pPr><w:jc w:val="center"/><w:spacing w:before="600" w:after="240"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="\u5fae\u8f6f\u96c5\u9ed1" w:hAnsi="\u5fae\u8f6f\u96c5\u9ed1" w:eastAsia="\u5fae\u8f6f\u96c5\u9ed1"/><w:b/><w:sz w:val="56"/><w:color w:val="1F3864"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/>
    <w:pPr><w:spacing w:before="480" w:after="120"/><w:outlineLvl w:val="0"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="\u5fae\u8f6f\u96c5\u9ed1" w:hAnsi="\u5fae\u8f6f\u96c5\u9ed1" w:eastAsia="\u5fae\u8f6f\u96c5\u9ed1"/><w:b/><w:sz w:val="44"/><w:color w:val="1F3864"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/>
    <w:pPr><w:spacing w:before="360" w:after="80"/><w:outlineLvl w:val="1"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="\u5fae\u8f6f\u96c5\u9ed1" w:hAnsi="\u5fae\u8f6f\u96c5\u9ed1" w:eastAsia="\u5fae\u8f6f\u96c5\u9ed1"/><w:b/><w:sz w:val="36"/><w:color w:val="2E75B6"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/>
    <w:pPr><w:spacing w:before="240" w:after="60"/><w:outlineLvl w:val="2"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="\u5fae\u8f6f\u96c5\u9ed1" w:hAnsi="\u5fae\u8f6f\u96c5\u9ed1" w:eastAsia="\u5fae\u8f6f\u96c5\u9ed1"/><w:b/><w:sz w:val="30"/><w:color w:val="404040"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:rPr><w:rFonts w:ascii="\u7b49\u7ebf" w:hAnsi="\u7b49\u7ebf" w:eastAsia="\u7b49\u7ebf"/><w:sz w:val="24"/><w:color w:val="333333"/></w:rPr>
    <w:pPr><w:spacing w:line="360" w:lineRule="auto" w:after="120"/></w:pPr>
  </w:style>
</w:styles>'''

def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

def make_para(style, text, bold_parts=None):
    text = text.replace('\n', '<w:br/>')
    runs = ''
    if bold_parts:
        i = 0
        for b_start, b_end in sorted(bold_parts):
            if b_start > i:
                runs += f'<w:r><w:rPr><w:rFonts w:ascii="\u7b49\u7ebf" w:hAnsi="\u7b49\u7ebf" w:eastAsia="\u7b49\u7ebf"/><w:sz w:val="24"/></w:rPr><w:t xml:space="preserve">{esc(text[i:b_start])}</w:t></w:r>'
            runs += f'<w:r><w:rPr><w:b/><w:rFonts w:ascii="\u7b49\u7ebf" w:hAnsi="\u7b49\u7ebf" w:eastAsia="\u7b49\u7ebf"/><w:sz w:val="24"/><w:color w:val="C00000"/></w:rPr><w:t xml:space="preserve">{esc(text[b_start:b_end])}</w:t></w:r>'
            i = b_end
        if i < len(text):
            runs += f'<w:r><w:rPr><w:rFonts w:ascii="\u7b49\u7ebf" w:hAnsi="\u7b49\u7ebf" w:eastAsia="\u7b49\u7ebf"/><w:sz w:val="24"/></w:rPr><w:t xml:space="preserve">{esc(text[i:])}</w:t></w:r>'
    else:
        runs = f'<w:r><w:rPr><w:rFonts w:ascii="\u7b49\u7ebf" w:hAnsi="\u7b49\u7ebf" w:eastAsia="\u7b49\u7ebf"/><w:sz w:val="24"/></w:rPr><w:t xml:space="preserve">{esc(text)}</w:t></w:r>'
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>{runs}</w:p>\n'

def build_body():
    body = '<w:body>\n'
    for sec in sections:
        stype = sec.get('type', 'normal')
        text = sec.get('text', '')
        bold = sec.get('bold')
        if stype == 'title':
            body += make_para('Title', text)
        elif stype == 'h1':
            body += make_para('Heading1', text)
        elif stype == 'h2':
            body += make_para('Heading2', text)
        elif stype == 'h3':
            body += make_para('Heading3', text)
        elif stype == 'empty':
            body += '<w:p><w:pPr><w:pStyle w:val="Normal"/></w:pPr></w:p>\n'
        else:
            body += make_para('Normal', text, bold)
    body += '</w:body>'
    return body

def make_doc():
    doc_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
{build_body()}
</w:document>'''
    return doc_xml

with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('[Content_Types].xml', CT_XML)
    zf.writestr('_rels/.rels', RELS_XML)
    zf.writestr('word/_rels/document.xml.rels', DOC_RELS_XML)
    zf.writestr('word/styles.xml', styles_xml())
    zf.writestr('word/document.xml', make_doc())

print(f'Word document created: {OUTPUT}')
