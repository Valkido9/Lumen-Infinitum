"""Insert ability data + rendering code into index.html before </script>."""
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Read index.html
with open('../index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Read ability_archive.js (skip the auto-generation comment)
with open('../data/ability_archive.js', 'r', encoding='utf-8') as f:
    ability_js = f.read()

# Remove the auto-generated comment lines
lines = ability_js.split('\n')
# Skip first 2 lines (comments)
data_lines = []
for line in lines:
    if line.startswith('// Auto-generated') or (line.startswith('// ') and 'abilities' in line):
        continue
    data_lines.append(line)
ability_data = '\n'.join(data_lines)

# The rendering functions
rendering_js = '''
// ===== ABILITY ARCHIVE RENDERING =====
const RADAR_LABELS = ['破坏力', '速度', '耐力', '范围', '狂热', '防御'];
const abilityMap = {};
abilityData.forEach(a => { abilityMap[a.id] = a; });

function drawRadarChart(stats) {
  const size = 150, cx = 75, cy = 75, r = 58, levels = 5;
  let svg = '<svg viewBox="0 0 ' + size + ' ' + size + '">';
  // Background grid
  for (let l = 1; l <= levels; l++) {
    let pts = [];
    for (let i = 0; i < 6; i++) {
      const a = (Math.PI * 2 * i) / 6 - Math.PI / 2;
      const d = (r / levels) * l;
      pts.push((cx + d * Math.cos(a)).toFixed(1) + ',' + (cy + d * Math.sin(a)).toFixed(1));
    }
    svg += '<polygon points="' + pts.join(' ') + '" class="radar-bg"/>';
  }
  // Axis lines
  for (let i = 0; i < 6; i++) {
    const a = (Math.PI * 2 * i) / 6 - Math.PI / 2;
    svg += '<line x1="' + cx + '" y1="' + cy + '" x2="' + (cx + r * Math.cos(a)).toFixed(1) + '" y2="' + (cy + r * Math.sin(a)).toFixed(1) + '" stroke="var(--border)" stroke-width="0.5"/>';
  }
  // Data polygon
  let dpts = [];
  for (let i = 0; i < 6; i++) {
    const a = (Math.PI * 2 * i) / 6 - Math.PI / 2;
    const v = Math.max(0.3, stats[i] || 0);
    const d = (r / levels) * v;
    dpts.push((cx + d * Math.cos(a)).toFixed(1) + ',' + (cy + d * Math.sin(a)).toFixed(1));
  }
  svg += '<polygon points="' + dpts.join(' ') + '" class="radar-data"/>';
  // Dots
  for (let i = 0; i < 6; i++) {
    const a = (Math.PI * 2 * i) / 6 - Math.PI / 2;
    const v = Math.max(0.3, stats[i] || 0);
    const d = (r / levels) * v;
    svg += '<circle cx="' + (cx + d * Math.cos(a)).toFixed(1) + '" cy="' + (cy + d * Math.sin(a)).toFixed(1) + '" r="2.5" class="radar-dot"/>';
  }
  // Labels
  for (let i = 0; i < 6; i++) {
    const a = (Math.PI * 2 * i) / 6 - Math.PI / 2;
    const lr = r + 15;
    const lx = cx + lr * Math.cos(a);
    const ly = cy + lr * Math.sin(a) + 3;
    svg += '<text x="' + lx.toFixed(1) + '" y="' + ly.toFixed(1) + '" class="radar-label">' + RADAR_LABELS[i] + '</text>';
  }
  svg += '</svg>';
  return svg;
}

function renderAbilityArchive() {
  const nav = document.getElementById('abilityNav');
  const archive = document.getElementById('abilityArchive');
  if (!nav || !archive) return;

  // Build nav
  let navHTML = '';
  abilityTimelines.forEach(tl => {
    navHTML += '<div class="tl-label">' + escHtml(tl.name) + '</div>';
    tl.factions.forEach(f => {
      navHTML += '<button class="ability-nav-btn" onclick="scrollToFaction(\\'' + f.abIds[0] + '\\')">' + escHtml(f.name) + '</button>';
    });
  });
  nav.innerHTML = navHTML;

  // Build archive
  let archiveHTML = '';
  const grades = ['', 'D', 'C', 'B', 'A', 'EX'];
  const statLabels = ['破坏力', '速度', '耐力', '范围', '狂热', '防御'];

  abilityTimelines.forEach(tl => {
    archiveHTML += '<div class="ability-timeline-title">' + escHtml(tl.name) + '</div>';
    tl.factions.forEach(f => {
      archiveHTML += '<div class="ability-faction-title" id="faction-' + f.abIds[0] + '">' + escHtml(f.name) + '</div>';
      f.abIds.forEach(id => {
        const a = abilityMap[id];
        if (!a) return;
        const statStr = a.s.map((v, i) => statLabels[i] + '-' + (grades[v] || '?')).join(' ');
        let html = '<div class="ability-card" id="ab-' + a.id + '">';
        html += '<div class="ability-card-header">';
        html += '<div class="radar-chart-wrap">' + drawRadarChart(a.s) + '</div>';
        html += '<div class="ability-info">';
        html += '<div class="ability-name">「' + escHtml(a.n) + '」</div>';
        html += '<div class="ability-meta"><span>👤 ' + escHtml(a.h) + '</span>';
        if (a.c) html += '<span>⚡ CRT ' + escHtml(a.c) + '</span>';
        html += '</div>';
        html += '<div class="ability-meta" style="font-size:0.75em;color:var(--text-muted);">' + statStr + '</div>';
        if (a.d) {
          const paras = a.d.split('\\n').filter(p => p.trim());
          html += '<div class="ability-desc">' + paras.map(p => '<p style="text-indent:2em;margin:4px 0;">' + escHtml(p.trim()) + '</p>').join('') + '</div>';
        }
        if (a.q) html += '<div class="ability-quote">' + escHtml(a.q) + '</div>';
        if (a.nt) html += '<div class="ability-note">📏 ' + escHtml(a.nt) + '</div>';
        html += '</div></div></div>';
        archiveHTML += html;
      });
    });
  });
  archive.innerHTML = archiveHTML;
}

function scrollToAbility(id) {
  document.getElementById('abilities').scrollIntoView({ behavior: 'smooth', block: 'start' });
  setTimeout(() => {
    const card = document.getElementById('ab-' + id);
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      card.style.transition = 'all 0.3s';
      card.style.borderColor = 'var(--accent)';
      card.style.boxShadow = '0 0 20px rgba(88,166,255,0.5)';
      setTimeout(() => {
        card.style.borderColor = '';
        card.style.boxShadow = '';
      }, 2500);
    }
  }, 500);
}

function scrollToFaction(firstId) {
  document.getElementById('abilities').scrollIntoView({ behavior: 'smooth', block: 'start' });
  setTimeout(() => {
    const card = document.getElementById('ab-' + firstId);
    if (card) card.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 400);
}

// Character → ability link mapping
function getCharAbilityHtml(charKey) {
  const c = characters[charKey];
  if (!c) return '';

  // Non-ability characters: keep original detail text
  if (c.ability === '无' || c.ability === 'N/A' || c.ability === '未知' || !c.ability) {
    return c.abilityDetail || '非能力使';
  }

  // Search abilityData for abilities matching this character
  // Extract base character name (remove parenthetical notes)
  const charName = c.name.replace(/[（(].*[）)]/g, '').trim();

  const matched = abilityData.filter(a => {
    const holderClean = a.h.replace(/[（(].*[）)]/g, '').replace(/【.*】/g, '').trim();
    // Match by holder name containing character name, or vice versa
    if (holderClean.includes(charName) || charName.includes(holderClean)) return true;
    // Also match by ability name being in character's ability field
    const charAbilities = c.ability.split(/[+、,\\/]/).map(s => s.trim());
    return charAbilities.some(ab => a.n.includes(ab) || ab.includes(a.n));
  });

  if (matched.length === 0) {
    // Fallback: show the original abilityDetail
    return c.abilityDetail || '<strong>' + c.ability + '</strong>';
  }

  return matched.map(a =>
    '<span class="char-link" onclick="scrollToAbility(\\'' + a.id + '\\')" title="点击跳转至能力档案查看完整详情">「' + escHtml(a.n) + '」</span>'
  ).join('、') + '<br><span style="font-size:0.75em;color:var(--text-muted);">⬆ 点击能力名跳转至能力档案</span>';
}
'''

# Find the insertion point: before </script>
insert_pos = html.rfind('</script>')
if insert_pos == -1:
    print("ERROR: Could not find </script> tag!")
    exit(1)

# Insert the ability data + rendering code
new_html = html[:insert_pos] + '\n' + ability_data + '\n' + rendering_js + '\n' + html[insert_pos:]

# Write back
with open('../index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"Successfully inserted ability archive into index.html")
print(f"  Inserted at position {insert_pos}")
print(f"  Final file size: {len(new_html)} bytes")
