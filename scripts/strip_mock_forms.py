"""Remove the legacy mock form-submit handlers; nova-forms.js owns submission now."""
import re
from pathlib import Path

JS = Path("/app/frontend/js")

# (file, start line 1-based of the addEventListener line)
TARGETS = {
    "about.js": 11,
    "bahar-residence.js": 219,
    "contact.js": 41,
    "east-west.js": 210,
    "marti-residence.js": 219,
    "mercan-bosphorus.js": 219,
    "portfolio-project.js": 111,
    "projects.js": 44,
    "the-apartments-ana.js": 126,
    "the-apartments-tac.js": 116,
    "script.js": 392,
}

for name, lineno in TARGETS.items():
    p = JS / name
    lines = p.read_text(encoding="utf-8").split("\n")
    start = lineno - 1
    indent = len(lines[start]) - len(lines[start].lstrip())
    # walk forward to the line that closes the listener at the same indent
    end = None
    for i in range(start + 1, len(lines)):
        stripped = lines[i].strip()
        cur_indent = len(lines[i]) - len(lines[i].lstrip())
        if stripped.startswith("});") and cur_indent == indent:
            end = i
            break
    if end is None:
        print(name, "SKIP — closing brace not found")
        continue
    removed = "\n".join(lines[start:end + 1])
    if "addEventListener('submit'" not in removed:
        print(name, "SKIP — unexpected block")
        continue
    del lines[start:end + 1]
    p.write_text("\n".join(lines), encoding="utf-8")
    print(name, f"removed lines {lineno}-{end + 1} ({end + 1 - lineno + 1} lines)")
