#!/usr/bin/env python3
"""
Rebuilds everything generated from the survey HTML, then refreshes the hashes in
01_survey/DERIVED.txt so tools/check.py agrees.

    python3 tools/rebuild.py            rebuild both
    python3 tools/rebuild.py pdf        just the PDF
    python3 tools/rebuild.py diagram    just the diagram PNG

Needs Google Chrome, which is what produced both files in the first place.
Copying hashes by hand is exactly the tedium this avoids.

One caveat. The survey uses font stacks rather than embedded fonts, so a machine
without Barlow installed will render the diagram in the fallbacks. Rebuilding it
there changes how it looks. On the machine this was built on, a rebuild differs
from the tracked PNG in 112 pixels out of 14.8 million, which is antialiasing.
"""

import os, re, subprocess, sys, hashlib, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "01_survey/pool-plant-room-survey.html")
PDF = os.path.join(ROOT, "01_survey/pool-plant-room-survey.pdf")
PNG = os.path.join(ROOT, "01_survey/pool-plant-room-diagram.png")
DERIVED = os.path.join(ROOT, "01_survey/DERIVED.txt")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DIAGRAM_RE = r'<svg viewBox="0 0 1560 2370"[\s\S]*?</svg>'
SCALE = 2                     # the tracked PNG is 3120x4740, twice the viewBox


def survey():
    return open(HTML, encoding="utf-8").read()


def build_pdf():
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=35000", "--print-to-pdf=" + PDF,
                    "file://" + HTML], capture_output=True, text=True)
    if not os.path.exists(PDF): raise SystemExit("chrome produced no PDF")
    print("  pdf      %.2f MB" % (os.path.getsize(PDF) / 1024**2))


def build_diagram():
    m = re.search(DIAGRAM_RE, survey())
    if not m: raise SystemExit("could not find the schematic svg in the survey")
    svg = m.group(0)
    # the diagram inherits its colours from the page, so the palette has to come
    # with it or every stroke renders as the browser default
    css = "".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", survey()))
    root = re.search(r":root\{([^}]*)\}", css)
    tmp = tempfile.mkdtemp()
    try:
        page = ("<!doctype html><meta charset=utf-8><style>"
                ":root{%s} html,body{margin:0;background:#fff}"
                "svg{display:block;width:%dpx;height:%dpx}</style>%s"
                % (root.group(1) if root else "", 1560 * SCALE, 2370 * SCALE, svg))
        src = os.path.join(tmp, "d.html")
        open(src, "w", encoding="utf-8").write(page)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", "--default-background-color=FFFFFFFF",
                        "--screenshot=" + os.path.join(tmp, "d.png"),
                        "--window-size=%d,%d" % (1560 * SCALE, 2370 * SCALE),
                        "file://" + src], capture_output=True, text=True)
        out = os.path.join(tmp, "d.png")
        if not os.path.exists(out): raise SystemExit("chrome produced no screenshot")
        shutil.move(out, PNG)
        print("  diagram  %dx%d" % (1560 * SCALE, 2370 * SCALE))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def refresh_hashes():
    s = survey()
    m = re.search(DIAGRAM_RE, s)
    want = {
        "pool-plant-room-survey.pdf": hashlib.sha256(s.encode()).hexdigest(),
        "pool-plant-room-diagram.png": hashlib.sha256(m.group(0).encode()).hexdigest(),
    }
    lines = open(DERIVED, encoding="utf-8").read().split("\n")
    for i, line in enumerate(lines):
        if "||" not in line or line[:1].isspace(): continue
        f, src, _ = [x.strip() for x in line.split("||")]
        if f in want: lines[i] = "%s || %s || %s" % (f, src, want[f])
    open(DERIVED, "w", encoding="utf-8").write("\n".join(lines))
    print("  hashes   DERIVED.txt refreshed")


if __name__ == "__main__":
    what = sys.argv[1:] or ["pdf", "diagram"]
    if not os.path.exists(CHROME): raise SystemExit("Google Chrome not found at " + CHROME)
    if "pdf" in what: build_pdf()
    if "diagram" in what: build_diagram()
    refresh_hashes()
    print("\n  now run: python3 tools/check.py")
