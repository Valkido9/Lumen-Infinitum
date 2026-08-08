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
function escHtml(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
const RADAR_LABELS = ['破坏力', '速度', '耐力', '范围', '狂热', '防御'];
const ZPN_LABELS   = ['侵蚀力', '速度', '耐力', '范围', '理智', '防御'];
const abilityMap = {};
abilityData.forEach(a => { abilityMap[a.id] = a; });

// Highest numeric value in a CRT string (handles "(-15.8)", "15.4/16.1", "16.7")
function maxCrt(c) {
  if (!c) return 0;
  const nums = (String(c).match(/\\d+(\\.\\d+)?/g) || []).map(Number);
  return nums.length ? Math.max.apply(null, nums) : 0;
}

function drawRadarChart(stats, isZpn) {
  const size = 200, cx = 100, cy = 100, r = 78, levels = 4; // A sits on the outer edge; EX bursts beyond it
  const labels = isZpn ? ZPN_LABELS : RADAR_LABELS;
  let svg = '<svg viewBox="0 0 ' + size + ' ' + size + '">';
  // Background grid (4 rings; A = outermost ring)
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
  // Data polygon: A(4) -> edge (r), EX(5) -> 1.25r (bursts out past the rim)
  const dataCls = isZpn ? 'radar-data-zpn' : 'radar-data';
  const dotCls  = isZpn ? 'radar-dot-zpn' : 'radar-dot';
  let dpts = [];
  for (let i = 0; i < 6; i++) {
    const a = (Math.PI * 2 * i) / 6 - Math.PI / 2;
    const v = Math.max(0.25, stats[i] || 0);
    const d = (r / levels) * v;
    dpts.push((cx + d * Math.cos(a)).toFixed(1) + ',' + (cy + d * Math.sin(a)).toFixed(1));
  }
  svg += '<polygon points="' + dpts.join(' ') + '" class="' + dataCls + '"/>';
  // Dots
  for (let i = 0; i < 6; i++) {
    const a = (Math.PI * 2 * i) / 6 - Math.PI / 2;
    const v = Math.max(0.25, stats[i] || 0);
    const d = (r / levels) * v;
    svg += '<circle cx="' + (cx + d * Math.cos(a)).toFixed(1) + '" cy="' + (cy + d * Math.sin(a)).toFixed(1) + '" r="3" class="' + dotCls + '"/>';
  }
  // Labels
  for (let i = 0; i < 6; i++) {
    const a = (Math.PI * 2 * i) / 6 - Math.PI / 2;
    const lr = r + 16;
    const lx = cx + lr * Math.cos(a);
    const ly = cy + lr * Math.sin(a) + 4;
    svg += '<text x="' + lx.toFixed(1) + '" y="' + ly.toFixed(1) + '" class="radar-label">' + labels[i] + '</text>';
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
        const isZpn = !!a.zn;                     // 镇压院区 (suppression-zone) ability
        const siege = !isZpn && maxCrt(a.c) > 14; // 攻城级 (siege-tier) -> red frame
        const labels = isZpn ? ZPN_LABELS : statLabels;
        const statStr = a.s.map((v, i) => labels[i] + '-' + (grades[v] || '?')).join('  ');
        let cls = 'ability-card';
        if (isZpn) cls += ' ability-card-zpn';
        if (siege) cls += ' ability-card-siege';
        let html = '<div class="' + cls + '" id="ab-' + a.id + '">';
        // Card top: name + badges + meta bar
        html += '<div class="ability-card-top">';
        html += '<div class="ability-name">「' + escHtml(a.n) + '」';
        if (a.st) html += '<span class="release-badge">解放阶段</span>';
        if (isZpn) html += '<span class="zpn-badge">镇压院区</span>';
        if (siege) html += '<span class="siege-badge">攻城级</span>';
        html += '</div>';
        html += '<div class="ability-meta-bar">';
        html += '<span>👤 ' + escHtml(a.h) + '</span>';
        if (a.c) html += '<span>⚡ CRT ' + escHtml(a.c) + '</span>';
        html += '<span class="ability-stats">' + statStr + '</span>';
        html += '</div></div>';
        // 镇压院区 note at the start of the card body
        if (a.zn) html += '<div class="zpn-note">' + escHtml(a.zn) + '</div>';
        // Card body: radar chart (left) + content (right)
        html += '<div class="ability-card-body">';
        html += '<div class="radar-chart-wrap">' + drawRadarChart(a.s, isZpn) + '</div>';
        html += '<div class="ability-content">';
        if (a.d) {
          const paras = a.d.split('\\n').filter(p => p.trim());
          html += '<div class="ability-desc">' + paras.map(p => '<p>' + escHtml(p.trim()) + '</p>').join('') + '</div>';
        }
        if (a.q) {
          const qParts = a.q.split('\\n');
          let quoteInner = qParts.length > 1
            ? '<span class="quote-text">' + escHtml(qParts[0]) + '</span><span class="quote-attribution">' + escHtml(qParts[1]) + '</span>'
            : escHtml(a.q);
          if (a.sp) {
            quoteInner = '<span class="spoiler-mark">（评价可能涉及剧透，点击查看）</span><span class="spoiler-content">' + quoteInner + '</span>';
          }
          html += '<div class="ability-quote">' + quoteInner + '</div>';
        }
        if (a.qb) {
          const qbLines = a.qb.split('\\n').filter(p => p.trim());
          html += '<div class="ability-admin"><span class="ability-admin-tag">⚠ 管理员</span>' + qbLines.map(p => '<p>' + escHtml(p.trim()) + '</p>').join('') + '</div>';
        }
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

// Initialize ability archive
renderAbilityArchive();
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
