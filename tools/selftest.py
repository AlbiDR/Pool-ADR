#!/usr/bin/env python3
"""
Proves that tools/check.py actually detects things.

    python3 tools/selftest.py

A check that has never failed is indistinguishable from a check that cannot
fail. This injects one realistic fault per check, confirms check.py reports it,
and puts the repository back with "git checkout --". It refuses to run unless
the working tree is clean, so a crash mid-test can never cost you work.
"""

import os, re, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURVEY = "01_survey/pool-plant-room-survey.html"

def git(*a):
    return subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True, text=True)

CREATED = []          # files a fault makes, removed by name rather than by git clean

def touch(rel, data=b""):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f: f.write(data)
    CREATED.append(rel)
    return True

def copy_file(src, dst):
    shutil.copyfile(os.path.join(ROOT, src), os.path.join(ROOT, dst))
    CREATED.append(dst)
    return True


def edit(rel, old, new):
    p = os.path.join(ROOT, rel)
    s = open(p, encoding="utf-8").read()
    if old not in s: return False
    open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
    return True

# each fault is something that has genuinely gone wrong in this repo before
FAULTS = [
    ("C1",  "stray closing brace in the stylesheet",
     lambda: edit(SURVEY, "code{display:inline-block", "}\ncode{display:inline-block")),
    ("C2",  "the code{} rule deleted",
     lambda: edit(SURVEY, "code{display:inline-block", "codeXX{display:inline-block")),
    ("C3",  "a section number left at the old value",
     lambda: edit(SURVEY, '<span class="n">&#167;3</span>', '<span class="n">&#167;9</span>')),
    ("C4",  "a nav entry pointing at a renamed section",
     lambda: edit(SURVEY, 'href="#fault"', 'href="#faults"')),
    ("C5",  "an internal link with no target",
     lambda: edit(SURVEY, 'href="#kit"', 'href="#equipmentxx"')),
    ("C6",  "a folder added but not listed in the table",
     lambda: touch("12_newfolder/.keep")),
    ("C7",  "prose referring to a file that was deleted",
     lambda: edit("README.md", "## Start here",
                  "See 04_plant-room/99_does-not-exist.jpg\n\n## Start here")),
    ("C8",  "an image pulled from the network instead of embedded",
     lambda: edit(SURVEY, "<body>", '<body><img src="https://example.com/x.png">')),
    ("C9",  "an em dash typed into the prose",
     lambda: edit("README.md", "## Start here", "## Start here — read this")),
    ("C10", "third-party attribution reintroduced",
     lambda: edit("README.md", "## Start here", "Told to me by my father.\n\n## Start here")),
    ("C11", "a superseded verdict asserted straight",
     lambda: edit("README.md", "## Start here",
                  "The tank is correctly sized.\n\n## Start here")),
    ("C12", "a canonical number changed in one file only",
     lambda: edit(SURVEY, "4.52 m&#178;, below ground", "9.99 m&#178;, below ground")),
    ("C13", "prose citing a section by number",
     lambda: edit(SURVEY, "<body>", "<body><p>See section 7 for details.</p>")),
    ("C14", "a file named outside the convention",
     lambda: touch("04_plant-room/Untitled Copy 2.jpg")),
    ("C15", "the published URL changed in one place only",
     lambda: edit("README.md", "https://albidr.github.io/Pool-ADR/", "https://example.com/")),
    ("C17", "a stated photograph count gone stale",
     lambda: edit("README.md", "| `04_plant-room/` | 34 photographs",
                              "| `04_plant-room/` | 41 photographs")),
    ("C18", "the survey edited without rebuilding the PDF",
     lambda: edit(SURVEY, "<body>", "<body><!-- a change the PDF has not seen -->")),
    ("C19", "a second near-identical frame filed alongside the first",
     lambda: copy_file("04_plant-room/27_pump-strainer-lid_t2214.jpg",
                       "04_plant-room/35_pump-strainer-lid_t2214.jpg")),
    ("C16", "a file over the 100 MB hard limit",
     lambda: touch("00_inbox/huge.bin", b"\0" * (101 * 1024 * 1024))),
]

def restore():
    while CREATED:
        rel = CREATED.pop()
        p = os.path.join(ROOT, rel)
        if os.path.exists(p): os.remove(p)
        d = os.path.dirname(p)
        if d != ROOT and os.path.isdir(d) and not os.listdir(d): os.rmdir(d)
    git("checkout", "--", ".")
    git("clean", "-qfd")

def main():
    if git("status", "--porcelain").stdout.strip():
        print("working tree is not clean. commit or stash first, so a fault can be undone.")
        return 2
    print("injecting one fault per check\n")
    bad = 0
    for cid, what, apply_fault in FAULTS:
        try:
            ok = apply_fault()
            if ok is False:
                print("  SKIP  %-4s could not inject: %s" % (cid, what)); bad += 1; continue
            r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/check.py"), cid],
                               capture_output=True, text=True)
            caught = "FAIL  " + cid in r.stdout
            print("  %s  %-4s %s" % ("caught" if caught else "MISSED", cid, what))
            if not caught:
                bad += 1
                print("        check.py said:\n" + "\n".join("        " + l for l in r.stdout.strip().split("\n")))
        finally:
            restore()
    print()
    print("  every check detects its fault" if not bad else "  %d check(s) did not detect their fault" % bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
