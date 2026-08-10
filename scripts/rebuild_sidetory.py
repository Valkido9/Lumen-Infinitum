#!/usr/bin/env python3
"""Clean rebuild of sidetory.html."""
BASE = r'E:\永恒流光\永恒流光'

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Wrote {path} ({len(content)} bytes)')

# Read the MODIFIED index.html (has text fixes + updated nav) as framework
index = read(f'{BASE}/index.html')

# Read the ORIGINAL sidetory.html (saved from git)
old_side = read(f'{BASE}/temp_old_side.html')

# Apply text replacements to old sidetory content
old_side = old_side.replace('流光永佑', '英勇为怀，广济众生')
old_side = old_side.replace('总是冷淡地打击琉璐珀过度的热情', '总是冷淡地打击歌涅法过度的热情')

# Extract sidetory's body (between <body> and </body>)
body_start = old_side.find('<body>')
body_end = old_side.find('</body>')
old_body = old_side[body_start + len('<body>'):body_end]

# Extract just the main content from old body (skip old header - framework provides its own)
# Keep: main content (without char-wiki)
# Remove: old CSS, old JS

# Find main content - skip the old header
main_start = old_body.find('<main class="main">')
main_end = old_body.find('</main>')
main_html = old_body[main_start:main_end]  # exclude </main>

# Remove character wiki from main_html
char_wiki_start = main_html.find('<!-- ===== 角色Wiki')
char_bg_start = main_html.find('<!-- ===== 人物背景 ===== -->')
if char_wiki_start >= 0 and char_bg_start >= 0:
    main_html = main_html[:char_wiki_start] + main_html[char_bg_start:]

# Add id="main-content" to main tag
main_html = main_html.replace('<main class="main">', '<main class="main" id="main-content">')

# Find footer (before <script>)
footer_start = old_body.find('<footer class="footer">')
footer_end = old_body.find('</footer>') + len('</footer>')
footer_html = old_body[footer_start:footer_end]

# Find theme toggle button
toggle_start = old_body.find('<button class="theme-toggle"')
toggle_end = old_body.find('</button>', toggle_start) + len('</button>')
toggle_html = old_body[toggle_start:toggle_end]

# Now build new sidetory from index.html framework
# Find the body content section in index to replace
idx_body_start = index.find('<body>')
idx_body_end = index.find('</body>') + len('</body>')

# Find main content area in index
idx_main_start = index.find('<!-- Main Content -->')
idx_footer_start = index.find('    <!-- Footer -->')

before = index[:idx_main_start]
after = index[idx_footer_start:]

# Build new body content
new_body_content = main_html + '\n\n'

# Build the full new file
new_content = before + '  ' + new_body_content.strip() + '\n\n' + after

# Update title
new_content = new_content.replace(
    '<title>永恒流光 - 可视化故事网站</title>',
    '<title>永恒流光 · SideStory 时空遗闻</title>'
)

# Update nav - make 时空遗闻 active
old_nav = '''  <nav>
    <a href="index.html" class="active">故事主线</a>
    <a href="sidetory.html">时空遗闻</a>
    <a href="world.html">世界设定</a>
    <a href="abilities.html">能力档案</a>
    <a href="characters.html">角色百科</a>
  </nav>'''
new_nav = '''  <nav>
    <a href="index.html">故事主线</a>
    <a href="sidetory.html" class="active">时空遗闻</a>
    <a href="world.html">世界设定</a>
    <a href="abilities.html">能力档案</a>
    <a href="characters.html">角色百科</a>
  </nav>'''
new_content = new_content.replace(old_nav, new_nav)

# Fix init: remove buildCharCards, switchWorldTab, renderAbilityArchive
new_content = new_content.replace('''// ===== INIT =====
initTheme();
buildCharCards();
switchWorldTab('terms', null);''', '''// ===== INIT =====
initTheme();''')

new_content = new_content.replace('''// Initialize ability archive
renderAbilityArchive();
applyStoredEdits();''', '''// Initialize stored edits
applyStoredEdits();''')

write(f'{BASE}/sidetory.html', new_content)
print('Done rebuilding sidetory.html!')
