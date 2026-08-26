"""Wrap the copy column of each pinned Construction stage in a clip window +
moving inner block, so the original composition can carry the longer approved
content without clipping. Text is never touched."""
import re, sys

P = '/app/frontend/construction.html'
src = open(P, encoding='utf-8').read()
before_text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', src))


def match_div(s, open_start):
    """index just after the opening tag, index of its matching </div>"""
    gt = s.index('>', open_start)
    depth, i = 1, gt + 1
    while depth:
        nxt_o = s.find('<div', i)
        nxt_c = s.find('</div>', i)
        if nxt_c == -1:
            raise ValueError('unbalanced')
        if nxt_o != -1 and nxt_o < nxt_c:
            depth += 1
            i = nxt_o + 4
        else:
            depth -= 1
            i = nxt_c + 6
            if depth == 0:
                return gt + 1, nxt_c
    raise ValueError


def wrap(s, open_start):
    inner_start, close_at = match_div(s, open_start)
    gt = s.index('>', open_start)
    tag = s[open_start:gt + 1]
    if 'cx-copywin' in tag:
        return s
    if 'class="' in tag:
        newtag = tag.replace('class="', 'class="cx-copywin ', 1)
    else:
        newtag = tag[:-1] + ' class="cx-copywin">'
    return (s[:open_start] + newtag + '<div class="cx-copymove">' +
            s[inner_start:close_at] + '</div>' + s[close_at:])


def first_child_div(s, stage_cls):
    i = s.index(stage_cls)
    return s.index('<div', s.index('>', i))


# structural: named copy column
src = wrap(src, src.index('<div class="cx-el-copy"'))
# reinforcement + waterproofing: first child of the stage is the copy column
for cls in ('cx-cage-stage', 'cx-wp-stage'):
    src = wrap(src, first_child_div(src, cls))
# seismic: copy column is the div holding the state list
i = src.index('cx-state-list')
j = src.rindex('<div', 0, src.rindex('<div', 0, i))
# walk back to the div that directly contains the state list
cands = [m.start() for m in re.finditer(r'<div', src[:i])]
for c in reversed(cands):
    try:
        a, b = match_div(src, c)
    except ValueError:
        continue
    if a < i < b and 'cx-state-list' not in src[c:src.index('>', c)]:
        src = wrap(src, c)
        break

after_text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', src))
if before_text != after_text:
    sys.exit('TEXT CHANGED — aborting')
open(P, 'w', encoding='utf-8').write(src)
print('wrapped; text integrity OK; len', len(src))
