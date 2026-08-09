# -*- coding: utf-8 -*-
"""一次性脚本：按用户要求调整 abilityData 的 tg 阵营字段。

改动：
1. '其他势力'/'其他角色'/'没名字的组合' → 合并为 '其他'
2. 阿芙忒乐尔斯特(ab58-60)、契尔文孙(ab96-98) → '死神首席'
3. '十七前传'/'正义前传' 不再是阵营 → 前传能力(ab99-117) 阵营置空，仅靠 tl/vol='前传' 区分
仅作用于 tg:"..." 字段；q 引文归属、世界设定组织数据等保持原样。
"""
import io, re, sys

INDEX_HTML = r"E:\永恒流光\永恒流光\index.html"
NL = "\r\n"  # 文件为 CRLF，词表替换需精确匹配行尾

with io.open(INDEX_HTML, "r", encoding="utf-8", newline="") as f:
    content = f.read()

# 区域：abilityData 数组 → 标签系统注释之前
start = content.find("const abilityData")
end = content.find("// ===== ABILITY TAG SYSTEM =====")
if start == -1 or end == -1 or end < start:
    sys.exit("FATAL: 找不到 abilityData / 标签系统边界")
region = content[start:end]

CAMP_MAP = {
    "其他势力": "其他",
    "其他角色": "其他",
    "没名字的组合": "其他",
    "第三章最终战": "死神首席",
    "第五章最终战": "死神首席",
    "十七前传": "",
    "正义前传": "",
}

def fix_tg(m):
    inner = m.group(1)
    for old, new in CAMP_MAP.items():
        inner = inner.replace(old, new)
    inner = inner.replace("|,", ",").replace(",|", ",")
    inner = re.sub(r'\s*\|\s*', '|', inner)
    inner = re.sub(r'\s*,\s*', ', ', inner).strip()
    return 'tg:"' + inner + '"'

region_new, count = re.subn(r'tg:"([^"]*)"', fix_tg, region)
content = content[:start] + region_new + content[end:]

# 更新阵营词表 abilityTags.camps.values（显式 CRLF）
OLD_VOCAB = (
    "  camps: { label: '阵营', values: [" + NL +
    "    '第二代时之秩序','圣标联合','潮涌居士号','蓝河明船','第一章最终战','浪庄游击队','深雾城阵营'," + NL +
    "    '珀利贝尔实业 · 亲卫队','珀利贝尔实业 · 部门领导组','寒城工坊','长夜事务所','第二章最终战','神国'," + NL +
    "    '牧人','爱丽丝马戏团','其他势力','第三章最终战','初代时之秩序','基地其他部门','没名字的组合'," + NL +
    "    '其他角色','柯洛雯第三帝国','芬奈法拉战线','第五章最终战','十七前传','正义前传'" + NL +
    "  ]},"
)
NEW_VOCAB = (
    "  camps: { label: '阵营', values: [" + NL +
    "    '第二代时之秩序','圣标联合','潮涌居士号','蓝河明船','第一章最终战','浪庄游击队','深雾城阵营'," + NL +
    "    '珀利贝尔实业 · 亲卫队','珀利贝尔实业 · 部门领导组','寒城工坊','长夜事务所','第二章最终战','神国'," + NL +
    "    '牧人','爱丽丝马戏团','其他','初代时之秩序','基地其他部门','柯洛雯第三帝国','芬奈法拉战线','死神首席'" + NL +
    "  ]},"
)
if OLD_VOCAB not in content:
    sys.exit("FATAL: 未找到旧阵营词表，检查换行/空格")
content = content.replace(OLD_VOCAB, NEW_VOCAB)

with io.open(INDEX_HTML, "w", encoding="utf-8", newline="") as f:
    f.write(content)

print("已更新 %d 个 tg 字段，词表已替换" % count)
if count != 121:
    print("警告: 期望 121 个 tg，实际 %d" % count)
