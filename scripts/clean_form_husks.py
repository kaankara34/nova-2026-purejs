"""Clean up the empty wrappers left behind after stripping the mock form handlers."""
import re
from pathlib import Path

JS = Path("/app/frontend/js")

BLOCKS = [
    ("about.js", """  /* ---- Register form (UI-only mock, matches projects.html pattern) ---- */
  const form = document.getElementById('abForm');
  if (form) {
  }

"""),
    ("bahar-residence.js", None),
    ("contact.js", """  /* register interest — UI only, same behaviour as the project pages */
  const form = document.getElementById('ctRegisterForm');
  if (form) {
    const msg = document.createElement('p');
    msg.className = 'ct-form-msg';
    msg.setAttribute('role', 'status');
    msg.dataset.testid = 'contact-register-message';
    form.appendChild(msg);
  }

"""),
    ("projects.js", """  /* Form submit (UI-only) */
  const form = $('#pjForm');
  if (form) {
  }

"""),
    ("script.js", """  /* ========== Register form (mock) ========== */

"""),
    ("the-apartments-ana.js", """  /* enquiry form — UI only, same validation pattern as the other project pages */
  const form = document.getElementById('anaEnquireForm');
  const msg = document.getElementById('anaFormMsg');
  if (form && msg) {
  }

"""),
]

for name, block in BLOCKS:
    if block is None:
        continue
    p = JS / name
    s = p.read_text(encoding="utf-8")
    if block not in s:
        print(name, "NOT FOUND")
        continue
    p.write_text(s.replace(block, "", 1), encoding="utf-8")
    print(name, "cleaned")

# generic sweep for the remaining `if (form...) {\n  }` husks
PATTERN = re.compile(
    r"\n[ \t]*/\*[^\n]*\*/\n"                      # comment line
    r"(?:[ \t]*const (?:form|msg)[^\n]*\n)+"       # const form / msg lines
    r"[ \t]*if \((?:form|msg)[^\n]*\) \{\n[ \t]*\}\n"
)
for p in sorted(JS.glob("*.js")):
    s = p.read_text(encoding="utf-8")
    new, n = PATTERN.subn("\n", s)
    if n:
        p.write_text(new, encoding="utf-8")
        print(p.name, f"swept {n}")
