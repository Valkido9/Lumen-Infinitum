#!/usr/bin/env python3
"""Split index.html into 5 separate pages with full CSS/JS framework."""
import re

BASE = r'E:\永恒流光\永恒流光'

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  Wrote {path}')

# ============================================================
# Shared nav templates
# ============================================================
OLD_NAV = '''  <nav>
    <a href="#story" class="active" onclick="scrollToSection('story')">故事主线</a>
    <a href="sidetory.html">时空遗闻</a>
    <a href="#world" onclick="scrollToSection('world')">世界设定</a>
    <a href="#abilities" onclick="scrollToSection('abilities')">能力档案</a>
    <a href="sidetory.html#char-wiki">角色百科</a>
  </nav>'''

def make_nav(active_page):
    pages = [
        ('index.html', '故事主线'),
        ('sidetory.html', '时空遗闻'),
        ('world.html', '世界设定'),
        ('abilities.html', '能力档案'),
        ('characters.html', '角色百科'),
    ]
    links = []
    for href, label in pages:
        cls = ' class="active"' if href == active_page else ''
        links.append(f'    <a href="{href}"{cls}>{label}</a>')
    return '  <nav>\n' + '\n'.join(links) + '\n  </nav>'

# ============================================================
# Create world.html from world_base.html
# ============================================================
print('=== Creating world.html ===')
content = read(f'{BASE}/world_base.html')

# Update nav
content = content.replace(OLD_NAV, make_nav('world.html'))

# Remove story content: keep only world section in main
main_start = content.find('<!-- Main Content -->')
world_start = content.find('<!-- ===== WORLD SECTION ===== -->')
abilities_start = content.find('<!-- ===== ABILITY ARCHIVE SECTION ===== -->')
footer_start = content.find('    <!-- Footer -->')

before = content[:main_start]
world_section = content[world_start:abilities_start]
after = content[footer_start:]

new_content = before + '''  <!-- Main Content -->
  <main class="main" id="main-content">

''' + world_section + '\n' + after

write(f'{BASE}/world.html', new_content)

# ============================================================
# Create abilities.html from abilities_base.html
# ============================================================
print('=== Creating abilities.html ===')
content = read(f'{BASE}/abilities_base.html')

content = content.replace(OLD_NAV, make_nav('abilities.html'))
content = content.replace(
    '<title>永恒流光 - 可视化故事网站</title>',
    '<title>永恒流光 · 能力档案</title>'
)

abilities_start = content.find('<!-- ===== ABILITY ARCHIVE SECTION ===== -->')
footer_start = content.find('    <!-- Footer -->')

before = content[:main_start]
abilities_section = content[abilities_start:footer_start]
after = content[footer_start:]

new_content = before + '''  <!-- Main Content -->
  <main class="main" id="main-content">

''' + abilities_section + '\n' + after

write(f'{BASE}/abilities.html', new_content)

# ============================================================
# Create characters.html from characters_base.html
# ============================================================
print('=== Creating characters.html ===')
content = read(f'{BASE}/characters_base.html')

content = content.replace(OLD_NAV, make_nav('characters.html'))
content = content.replace(
    '<title>永恒流光 - 可视化故事网站</title>',
    '<title>永恒流光 · 角色百科</title>'
)

# Make character section visible and keep only it
# Find the hidden character div
char_section_start = content.find('<!-- ===== CHARACTERS SECTION (hidden; cards still callable from story text) ===== -->')
footer_start = content.find('    <!-- Footer -->')

# Extract the character section content (remove the display:none wrapper)
char_block = content[char_section_start:footer_start]
# Remove the opening <div style="display:none;"> and closing </div>
char_block = char_block.replace('<!-- ===== CHARACTERS SECTION (hidden; cards still callable from story text) ===== -->\n    <div style="display:none;">\n', '')
# Find the last </div> before the next section comment
char_block = re.sub(r'\n    </div>\n\n    <!-- ===== WORLD SECTION', '', char_block)
# Actually let me be more precise - just strip the display:none wrapper

before = content[:main_start]
after = content[footer_start:]

# Rebuild: just the character section (without display:none)
char_content = '''  <!-- Main Content -->
  <main class="main" id="main-content">

    <!-- ===== CHARACTERS SECTION ===== -->
    <h2 class="section-title" id="characters" style="color:var(--gold);"><span class="icon">👥</span>角色档案</h2>
    <div class="search-bar">
      <input type="text" id="charSearch" placeholder="搜索角色（输入名字、代号或能力名）..." oninput="filterCharacters()">
    </div>
    <div class="chapter-grid" id="charGrid">
    </div>

'''

new_content = before + char_content + after
write(f'{BASE}/characters.html', new_content)

print('\nDone creating pages!')
