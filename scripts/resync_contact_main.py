"""Resyncs scripts/contact_main.html from the current frontend/contact.html."""
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent
about = (root / "frontend" / "about.html").read_text(encoding="utf-8")
page = (root / "frontend" / "contact.html").read_text(encoding="utf-8")

hero_marker = "  <!-- ============================= HERO ============================= -->"
foot_marker = "  <footer class=\"site-footer\">"

chrome = about.split(hero_marker)[0]
chrome = chrome.replace('<title>About Us | Nova Konut</title>', '<title>Contact | Nova Konut</title>')
chrome = re.sub(r'<meta name="description"[^>]*>',
                '<meta name="description" content="Contact Nova Konut — enquiries, project information and resident support, with offices on Bağdat Caddesi and in Etiler, Istanbul." />',
                chrome, count=1)
chrome = chrome.replace('<meta name="theme-color" content="#0b0b0b" />',
                        '<meta name="theme-color" content="#F1EBE3" />')
chrome = re.sub(r'\n *<link rel="preload"[^>]*>', '', chrome, count=1)
chrome = chrome.replace(
    '  <link rel="stylesheet" href="css/projects.css" />\n  <link rel="stylesheet" href="css/about.css" />',
    '  <link rel="stylesheet" href="css/contact.css" />')
chrome = chrome.replace('<body class="page-about">', '<body class="page-contact">')
chrome = chrome.replace('media/images/nova-logo.png', 'media/images/nova-logo-dark.png')
chrome = chrome.replace('class="logo-img" / decoding="async"', 'class="logo-img" decoding="async"')

assert page.startswith(chrome), "chrome drifted — resync manually"
main = page[len(chrome):].split(foot_marker)[0]
(pathlib.Path(__file__).parent / "contact_main.html").write_text(main.rstrip() + "\n", encoding="utf-8")
print("contact_main.html resynced:", len(main.splitlines()), "lines")
