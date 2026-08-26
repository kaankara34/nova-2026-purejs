#!/usr/bin/env python3
"""Presentation-layer restructure of construction.html.

Moves existing nodes only: section intros/notes leave the pinned stages so every
interactive stage can hold one readable state at a time. No text is added,
removed, reworded or reordered — verified by a text-integrity check.
"""
import pathlib, re, sys

P = pathlib.Path('/app/frontend/construction.html')
src = P.read_text()


def text_of(html):
    t = re.sub(r'<[^>]+>', ' ', html)
    return re.sub(r'\s+', ' ', t).strip()


def balanced(s, start, tag='div'):
    """return substring of the balanced element starting at index `start`"""
    i, depth = start, 0
    open_re = re.compile(r'<%s\b' % tag)
    close_re = re.compile(r'</%s>' % tag)
    while i < len(s):
        o = open_re.search(s, i)
        c = close_re.search(s, i)
        if c and (not o or c.start() < o.start()):
            depth -= 1
            i = c.end()
            if depth == 0:
                return s[start:i]
        elif o:
            depth += 1
            i = o.end()
        else:
            break
    raise ValueError('unbalanced')


def section(s, marker):
    a = s.index(marker)
    b = s.index('</section>', a) + len('</section>')
    return a, b, s[a:b]


out = src

# ------------------------------------------------------------------ structural
a, b, sec = section(out, '<section class="cx-sec cx-struct"')
copy_head = re.search(r'<div class="cx-el-copy">(.*?)<div class="cx-el-list"', sec, re.S).group(1)
el_list = balanced(sec, sec.index('<div class="cx-el-list"'))
note = re.search(r'<p class="cx-note".*?</p>', sec, re.S).group(0)
model = balanced(sec, sec.index('<div class="cx-struct-model">'))
idx = re.search(r'<span class="cx-idx">.*?</span>', copy_head, re.S).group(0)
h2 = re.search(r'<h2 class="cx-h2".*?</h2>', copy_head, re.S).group(0)
intro = re.search(r'<p class="cx-p cx-p--s">.*?</p>', copy_head, re.S).group(0)

new_struct = f'''<section class="cx-sec cx-secintro" data-testid="cx-section-structural-intro">
    <div class="cx-wrap">
      <div class="cx-sechead">
        <div>{idx}{h2}</div>
        <div>{intro}{note}</div>
      </div>
      <div class="cx-tickrule"></div>
    </div>
  </section>

  <section class="cx-struct" data-testid="cx-section-structural">
    <div class="cx-struct-stage">
      <div class="cx-el-copy">{el_list}</div>
      {model}
    </div>
  </section>'''
out = out[:a] + new_struct + out[b:]

# --------------------------------------------------------------------- seismic
a, b, sec = section(out, '<section class="cx-sec cx-seis"')
viz = balanced(sec, sec.index('<div class="cx-seis-viz">'))
state_list = balanced(sec, sec.index('<div class="cx-state-list"'))
idx = re.search(r'<span class="cx-idx">.*?</span>', sec, re.S).group(0)
h2 = re.search(r'<h2 class="cx-h2".*?</h2>', sec, re.S).group(0)
lbl = re.search(r'<p class="cx-lbl".*?</p>', sec, re.S).group(0)
intro = re.search(r'<p class="cx-p cx-p--s".*?</p>', sec, re.S).group(0)

new_seis = f'''<section class="cx-sec cx-secintro" data-testid="cx-section-seismic-intro">
    <div class="cx-wrap">
      <div class="cx-sechead">
        <div>{idx}{h2}{lbl}</div>
        <div>{intro}</div>
      </div>
      <div class="cx-tickrule"></div>
    </div>
  </section>

  <section class="cx-seis" data-testid="cx-section-seismic">
    <div class="cx-seis-stage">
      {viz}
      <div class="cx-seis-copy">{state_list}</div>
    </div>
  </section>'''
out = out[:a] + new_seis + out[b:]

# ---------------------------------------------------------------------- ground
a, b, sec = section(out, '<section class="cx-sec cx-cut"')
sechead = balanced(sec, sec.index('<div class="cx-sechead">'))
depth = balanced(sec, sec.index('<div class="cx-depth">'))
strata = [balanced(sec, m.start()) for m in re.finditer(r'<div class="cx-stratum"', sec)]
hatch = re.search(r'<div class="cx-hatch"[^>]*></div>', sec).group(0)
gnote = re.findall(r'<p class="cx-note".*?</p>', sec, re.S)[-1]

new_ground = f'''<section class="cx-sec cx-secintro" data-testid="cx-section-ground-intro">
    <div class="cx-wrap">
      {sechead}
      <div class="cx-tickrule"></div>
    </div>
  </section>

  <section class="cx-cut" data-testid="cx-section-ground">
    <div class="cx-cut-stage">
      {depth}
      <div class="cx-panels" data-testid="cx-ground-panels">{''.join(strata)}</div>
    </div>
  </section>

  <section class="cx-sec cx-secoutro" data-testid="cx-section-ground-note">
    <div class="cx-wrap">
      {hatch}
      {gnote}
    </div>
  </section>'''
out = out[:a] + new_ground + out[b:]

# -------------------------------------------------------------------- concrete
a, b, sec = section(out, '<section class="cx-conc"')
heads = [balanced(sec, m.start()) for m in re.finditer(r'<div class="cx-flow-head"', sec)]
track = balanced(sec, sec.index('<div class="cx-track">'))
band = balanced(sec, sec.index('<div class="cx-flow-band">'))
c_intro, c_note = heads[0], heads[-1]

new_conc = f'''<section class="cx-sec cx-secintro" data-testid="cx-section-concrete-intro">
    <div class="cx-wrap">{c_intro}<div class="cx-tickrule"></div></div>
  </section>

  <section class="cx-conc" data-testid="cx-section-concrete">
    <div class="cx-flow-stage">
      {track}
      {band}
    </div>
  </section>

  <section class="cx-sec cx-secoutro" data-testid="cx-section-concrete-note">
    <div class="cx-wrap">{c_note}</div>
  </section>'''
out = out[:a] + new_conc + out[b:]

# integrity check: identical visible text
from collections import Counter
if Counter(text_of(src).split()) != Counter(text_of(out).split()):
    ca, cb = Counter(text_of(src).split()), Counter(text_of(out).split())
    print('TEXT CHANGED — aborting')
    print('lost:', (ca - cb).most_common(20))
    print('gained:', (cb - ca).most_common(20))
    sys.exit(1)

P.write_text(out)
print('restructured; text integrity OK; len', len(out))
