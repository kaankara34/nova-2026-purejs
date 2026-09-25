"""One-off: side menu footer — company line + only Instagram/LinkedIn/WhatsApp/Mail icons."""
import glob
import re

SOCIALS = """      <div class="socials">
        <a href="https://www.instagram.com/novakonut/" target="_blank" rel="noopener noreferrer" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="0.8" fill="currentColor"/></svg></a>
        <a href="#" aria-label="LinkedIn"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 11-.01 5.01A2.5 2.5 0 014.98 3.5zM3 9h4v12H3V9zm7 0h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05C21.6 8.65 22 11.1 22 14.3V21h-4v-5.9c0-1.4-.03-3.2-1.95-3.2-1.95 0-2.25 1.52-2.25 3.1V21h-4V9z"/></svg></a>
        <a href="https://wa.me/905335061972" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg></a>
        <a href="mailto:iletisim@nova.istanbul" aria-label="E-posta"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></a>
      </div>"""

COMPANY = '      <div class="menu-company">NOVA KONUT \u0130N\u015eAAT YATIRIM A.\u015e</div>\n'
TERMS = '      <div class="terms">TERMS AND CONDITIONS</div>'

socials_re = re.compile(r'[ \t]*<div class="socials">.*?</div>\s*\n(?=\s*</div>)', re.S)
changed = []
for path in sorted(glob.glob('/app/frontend/*.html')):
    src = open(path, encoding='utf-8').read()
    if 'side-menu-foot' not in src:
        continue
    out = socials_re.sub(SOCIALS + '\n', src, count=1)
    if 'menu-company' not in out:
        out = out.replace(TERMS, COMPANY + TERMS, 1)
    if out != src:
        open(path, 'w', encoding='utf-8').write(out)
        changed.append(path.split('/')[-1])
print(len(changed), changed)
