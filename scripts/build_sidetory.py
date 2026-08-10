#!/usr/bin/env python3
"""Rebuild sidetory.html with full CSS/JS framework from index.html."""
import re

BASE = r'E:\永恒流光\永恒流光'

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Wrote {path}')

# Read source files
index = read(f'{BASE}/sidetory_new.html')
old_side = read(f'{BASE}/sidetory.html')

# ============================================================
# Extract sidetory's body content (everything between <main> and </main>)
# From the OLD sidetory.html
# ============================================================
main_start = old_side.find('<main class="main">')
main_end = old_side.find('</main>')
old_body = old_side[main_start:main_end + len('</main>')]

# Remove character wiki entries from old_body
# Find #char-wiki section start and end
char_wiki_start = old_body.find('<!-- ===== 角色Wiki ===== -->')
# Find the next section after char-wiki
char_bg_start = old_body.find('<!-- ===== 人物背景 ===== -->')
# Keep everything except the wiki entries
before_wiki = old_body[:char_wiki_start]
after_wiki = old_body[char_bg_start:]

# Build new body: before wiki + after wiki (skip character wiki)
new_body = before_wiki + after_wiki

# Add id="main-content" to the main tag
new_body = new_body.replace('<main class="main">', '<main class="main" id="main-content">')

# ============================================================
# Insert into index.html framework
# ============================================================
idx_main_start = index.find('<!-- Main Content -->')
idx_main_end = index.find('    <!-- Footer -->')

before = index[:idx_main_start]
after = index[idx_main_end:]

# Build new content
new_content = before + '  ' + new_body.strip() + '\n\n' + after

# Update title
new_content = new_content.replace(
    '<title>永恒流光 - 可视化故事网站</title>',
    '<title>永恒流光 · SideStory 时空遗闻</title>'
)

# Update nav - make 时空遗闻 active
OLD_NAV = '''  <nav>
    <a href="index.html" class="active">故事主线</a>
    <a href="sidetory.html">时空遗闻</a>
    <a href="world.html">世界设定</a>
    <a href="abilities.html">能力档案</a>
    <a href="characters.html">角色百科</a>
  </nav>'''

NEW_NAV = '''  <nav>
    <a href="index.html">故事主线</a>
    <a href="sidetory.html" class="active">时空遗闻</a>
    <a href="world.html">世界设定</a>
    <a href="abilities.html">能力档案</a>
    <a href="characters.html">角色百科</a>
  </nav>'''

new_content = new_content.replace(OLD_NAV, NEW_NAV)

# Remove buildCharCards, switchWorldTab from early init
new_content = new_content.replace('''// ===== INIT =====
initTheme();
buildCharCards();
switchWorldTab('terms', null);''', '''// ===== INIT =====
initTheme();''')

# Remove renderAbilityArchive from end init, keep applyStoredEdits
new_content = new_content.replace('''// Initialize ability archive
renderAbilityArchive();
applyStoredEdits();''', '''// Initialize stored edits
applyStoredEdits();''')

write(f'{BASE}/sidetory.html', new_content)
print('Done!')
