#!/usr/bin/env python3
"""
Consistency checker for the pool plant room repository.

    python3 tools/check.py            run every check
    python3 tools/check.py -v         also print what passed
    python3 tools/check.py C6 C11     run only those checks

Nothing here needs installing. Standard library only, python3.9 or later.

Why it exists. This survey states the same fact in several places at once: the
HTML, the README, DIMENSIONS.txt, the folder READ-MEs. That is good for whoever
reads it and bad for whoever edits it, because a change in one file leaves the
others quietly wrong. Every check below is a mistake that actually happened
while the document was being built. Each one is now loud instead of silent.
"""

import os, re, sys, html, hashlib, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURVEY = "01_survey/pool-plant-room-survey.html"
TEXTY = (".html", ".md", ".txt", ".py")
SKIP_DIRS = {".git", "node_modules"}

# A NAME IN CAPITALS IS APPARATUS; A NAME WITH AN INDEX IS EVIDENCE.
# That is the whole rule. READ-ME.txt, CATALOGUE.txt and CONTACT-SHEET.jpg
# describe the folder they sit in and are not part of its numbering, so they
# take no index and are not counted as photographs. 01_survey is exempt too:
# its three files are the deliverable and are named by subject, because the
# README and anyone you send this to point straight at them.
APPARATUS = re.compile(r"^[A-Z][A-Z0-9-]*\.[a-z0-9]+$")
NAMING_EXEMPT = re.compile(r"^([A-Z][A-Z0-9-]*\.[a-z0-9]+|pool-plant-room-(survey\.(html|pdf)|diagram\.png))$")
NAME_OK = re.compile(r"^\d{2}_[a-z0-9]+(-[a-z0-9]+)*(_[a-zA-Z0-9-]+)*\.[a-z0-9]+$")

results = []           # (id, title, ok, [lines])
def check(cid, title):
    def deco(fn):
        results.append((cid, title, fn)); return fn
    return deco

def walk(exts=TEXTY, skip=()):
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in sorted(fns):
            rel = os.path.relpath(os.path.join(dp, fn), ROOT)
            if rel in skip: continue
            if exts is None or rel.lower().endswith(exts):
                yield rel

def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as f:
        return f.read()

def survey():
    return read(SURVEY)

def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))



# ---- the media library, shared by C21, C22 and C23 -------------------------
MEDIA_COLUMNS = ("path", "kind", "bytes", "pixels", "captured", "made", "sha256", "caption")
MEDIA_EXT = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".pdf", ".glb", ".svg")
SHEET = "CONTACT-SHEET.jpg"
SHEET_TAG = "contact-sheet-of:"
# 00_inbox is untracked staging and 01_survey is the deliverable, which has its
# own freshness record in DERIVED.txt. The library is the numbered folders.
MEDIA_SKIP = SKIP_DIRS | {"00_inbox", "01_survey", "tools"}


def media_on_disk():
    out = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in MEDIA_SKIP]
        for fn in sorted(fns):
            rel = os.path.relpath(os.path.join(dp, fn), ROOT)
            if fn.startswith(".") or fn == SHEET or not os.path.dirname(rel): continue
            if fn.lower().endswith(MEDIA_EXT): out.append(rel)
    return sorted(out)


def sheet_digest(path):
    """Reads the build digest out of a JPEG COM marker. No Pillow needed."""
    import struct
    with open(path, "rb") as f:
        d = f.read(1 << 16)
    i = 2
    while i + 4 < len(d):
        if d[i] != 0xFF: return None
        if d[i + 1] == 0xDA: return None                  # scan starts, no comment
        n = struct.unpack(">H", d[i + 2:i + 4])[0]
        if d[i + 1] == 0xFE:
            t = d[i + 4:i + 2 + n].decode("ascii", "replace")
            if t.startswith(SHEET_TAG): return t[len(SHEET_TAG):].strip()
        i += 2 + n
    return None


# --------------------------------------------------------------------------
@check("C1", "survey CSS braces balance")
def c1():
    css = "".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", survey()))
    depth, bad = 0, []
    for k, ch in enumerate(css):
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                bad.append("stray closing brace near: ..." + css[max(0, k-70):k+1].strip()[-70:])
                depth = 0
    if depth: bad.append("%d unclosed brace(s) at end of stylesheet" % depth)
    return bad


@check("C2", "survey key CSS rules survive")
def c2():
    css = "".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", survey()))
    out = []
    # a stray brace once glued itself to this selector and Chrome dropped the
    # whole rule, so 120 valve badges rendered as plain text
    # "code" must appear as a selector in its own right. Matching it loosely let
    # "h4 code{" stand in for it, so the check passed with the real rule deleted.
    if not re.search(r"(^|[};])\s*code\s*\{", css):
        out.append("the standalone code{} rule is missing; valve badges will render as plain text")
    for sel in (r"\.tb-qr\b", r"\.warn\b", r"\.steps\b", r"\.lg\b"):
        if not re.search(r"(^|[};\s,])" + sel, css):
            out.append("rule for %s is missing from the stylesheet" % sel.replace("\\", ""))
    return out


@check("C3", "section numbers run 1..n in document order")
def c3():
    s = survey()
    nums = [int(n) for n in re.findall(r'<span class="n">&#167;(\d+)</span>', s)]
    if not nums: return ["no numbered sections found at all"]
    want = list(range(1, len(nums) + 1))
    return [] if nums == want else ["numbering is %s but document order needs %s" % (nums, want)]


@check("C4", "nav matches the sections, in order")
def c4():
    s = survey()
    secs = re.findall(r'<section id="([^"]+)">', s)
    m = re.search(r'<nav class="toc"[^>]*>([\s\S]*?)</nav>', s)
    if not m: return ["no <nav class=\"toc\"> found"]
    nav = re.findall(r'href="#([^"]+)"', m.group(1))
    out = []
    extra = [a for a in nav if a not in secs and a != "quick"]
    missing = [x for x in secs if x not in nav]
    if extra: out.append("nav links to nothing: %s" % extra)
    if missing: out.append("sections with no nav entry: %s" % missing)
    ordered = [a for a in nav if a in secs]
    if not out and ordered != secs:
        out.append("nav order %s does not match document order %s" % (ordered, secs))
    return out


@check("C5", "every internal anchor resolves")
def c5():
    s = survey()
    ids = set(re.findall(r'\sid="([^"]+)"', s))
    out = []
    for a in sorted(set(re.findall(r'href="#([^"]+)"', s))):
        if a and a not in ids: out.append('href="#%s" has no matching id' % a)
    return out


@check("C6", "survey folder table matches the folders on disk")
def c6():
    disk = sorted(d + "/" for d in os.listdir(ROOT)
                  if re.match(r"^\d\d_", d) and os.path.isdir(os.path.join(ROOT, d)))
    table = re.findall(r'<td class="tag">(\d\d_[a-z-]+/)</td>', survey())
    out = []
    for d in disk:
        if d not in table: out.append("%s exists on disk but has no row in the folder table" % d)
    for t in table:
        if t not in disk: out.append("the folder table lists %s, which is not on disk" % t)
    if not out and table != disk:
        out.append("folder table order %s does not match disk order %s" % (table, disk))
    return out


@check("C7", "every file path mentioned in prose exists")
def c7():
    pat = re.compile(r"\b(\d\d_[a-z-]+/[A-Za-z0-9][A-Za-z0-9._-]*\.[a-z0-9]{2,4})\b")
    out = []
    for rel in walk(skip=("FACTS.txt", "tools/selftest.py")):
        for ref in sorted(set(pat.findall(read(rel)))):
            if not os.path.exists(os.path.join(ROOT, ref)):
                out.append("%s refers to %s, which does not exist" % (rel, ref))
    return out


@check("C8", "the survey stays self-contained and offline")
def c8():
    s = survey()
    out = []
    for m in re.finditer(r'\ssrc="([^"]+)"', s):
        if not m.group(1).startswith("data:"):
            out.append("external src: %s" % m.group(1)[:80])
    for m in re.finditer(r"<link[^>]+rel=[\"']?stylesheet[^>]*>", s, re.I):
        out.append("external stylesheet: %s" % m.group(0)[:80])
    if "@import" in s: out.append("stylesheet uses @import")
    return out


@check("C9", "plain ASCII punctuation only")
def c9():
    # written as escapes so this file does not fail its own check
    bad = {"\u2014": "em dash", "\u2013": "en dash", "\u2018": "curly quote",
           "\u2019": "curly quote", "\u201c": "curly quote", "\u201d": "curly quote",
           "\u2026": "ellipsis", "\u00a0": "non-breaking space"}
    out = []
    for rel in walk(skip=("tools/selftest.py",)):
        t = read(rel)
        for ch, name in bad.items():
            if ch in t: out.append("%s contains %d %s(s)" % (rel, t.count(ch), name))
        emoji = [c for c in t if unicodedata.category(c) == "So"]
        if emoji: out.append("%s contains %d emoji/symbol char(s): %r" % (rel, len(emoji), emoji[:6]))
    return out


@check("C10", "no third-party attribution in the prose")
def c10():
    out = []
    for rel in walk(skip=("FACTS.txt", "tools/check.py", "tools/selftest.py")):
        for m in re.finditer(r"\b(my|his|her|their) father\b", read(rel), re.I):
            out.append("%s says %r" % (rel, m.group(0)))
    return out


@check("C11", "no superseded wording anywhere (FACTS.txt NEVER list)")
def c11():
    facts = read("FACTS.txt")
    body = facts[facts.index("NEVER\n====="):]
    out = []
    WINDOW = 300      # chars either side that may carry the "this was corrected" label
    for line in body.split("\n"):
        if "||" not in line or line[:1].isspace(): continue     # indented lines are the template
        parts = [p.strip() for p in line.split("||")]
        needle, why = parts[0], parts[1]
        exempt, unless = set(), []
        for p in parts[2:]:
            low = p.lower()
            if low.startswith("except:"):
                exempt = {x.strip() for x in p.split(":", 1)[1].split(",")}
            elif low.startswith("unless:"):
                unless = [x.strip().lower() for x in p.split(":", 1)[1].split(",") if x.strip()]
        for rel in walk(skip=("FACTS.txt", "tools/check.py", "tools/selftest.py")):
            if rel in exempt: continue
            t = read(rel).lower()
            for m in re.finditer(re.escape(needle.lower()), t):
                ctx = re.sub(r"\s+", " ", t[max(0, m.start()-WINDOW):m.end()+WINDOW])
                # a banned string is allowed where the text explicitly marks it superseded
                if any(u in ctx for u in unless): continue
                out.append("%s still says %r  (%s)" % (rel, needle, why))
                break
    return out


@check("C12", "canonical numbers agree with FACTS.txt")
def c12():
    facts = {}
    for line in read("FACTS.txt").split("\n"):
        if line.startswith("#") or "=" not in line or "||" in line: continue
        k, _, v = line.partition("=")
        if re.match(r"^[a-z0-9_]+$", k.strip()): facts[k.strip()] = v.strip()
    s = survey()
    out = []
    # context patterns: the number is captured from its own sentence, so a stale
    # figure fails here instead of being read past
    probes = [
        ("plant_room_area_m2",      s, r"([\d.]+)\s*m&#178;,\s*below\s*ground"),
        ("balance_tank_capacity_m3",s, r"([\d.]+)\s*m&#179;,\s*next\s*door"),
        ("filter_sand_kg",          s, r"&#216;760,\s*([\d]+)\s*kg"),
        ("litres_per_cm_of_column", read("DIMENSIONS.txt"), r"1\s*cm\s+of\s+depth\s*=\s*([\d.]+)\s*litres"),
    ]
    for key, text, pat in probes:
        if key not in facts:
            out.append("FACTS.txt has no key %s" % key); continue
        m = re.search(pat, text)
        if not m:
            out.append("could not locate %s in its usual sentence (pattern moved?)" % key)
        elif m.group(1) != facts[key]:
            out.append("%s: FACTS.txt says %s, document says %s" % (key, facts[key], m.group(1)))
    return out


@check("C13", "prose cites sections by name, never by number")
def c13():
    s = survey()
    # the heading spans are the legitimate place for a number
    stripped = re.sub(r'<span class="n">&#167;\d+</span>', "", s)
    text = strip_tags(stripped)
    # citing another document's numbered section is legitimate; citing this
    # document's own is what breaks when the survey is reordered
    external = re.compile(r"(manual|sheet|datasheet|regulation|standard|annex|directive|norm)\b[^.]{0,40}$", re.I)
    out = []
    for m in re.finditer(r"(?:section|\u00a7)\s*(\d+)", text, re.I):
        before = text[max(0, m.start()-60):m.start()]
        if external.search(before): continue
        out.append("prose cites %r; cite the section by name so renumbering cannot break it" % m.group(0))
    return out


@check("C14", "file names follow NAMING.txt")
def c14():
    out = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        rel_dir = os.path.relpath(dp, ROOT)
        if rel_dir == "." or not re.match(r"^\d\d_", rel_dir): continue
        seen = {}
        for fn in sorted(fns):
            if fn.startswith("."): continue
            if NAMING_EXEMPT.match(fn): continue
            if not NAME_OK.match(fn):
                out.append("%s/%s does not match <index>_<subject>[_<qualifier>][_<token>].<ext>" % (rel_dir, fn))
                continue
            idx = fn[:2]
            if idx in seen:
                out.append("%s/: index %s used twice, by %s and %s" % (rel_dir, idx, seen[idx], fn))
            seen[idx] = fn
    return out


@check("C15", "the published URL is the same everywhere")
def c15():
    facts = read("FACTS.txt")
    url = re.search(r"pages_url\s*=\s*(\S+)", facts).group(1)
    short = re.search(r"pages_url_short\s*=\s*(\S+)", facts).group(1)
    out = []
    for rel in ("README.md", SURVEY):
        if url not in read(rel): out.append("%s does not carry %s" % (rel, url))
    if short not in read(SURVEY): out.append("%s does not show the short URL" % SURVEY)
    # presence is not enough: a second, different URL can sit happily beside it
    for rel in walk(skip=("FACTS.txt", "tools/check.py", "tools/selftest.py")):
        for m in re.finditer(r"https?://[A-Za-z0-9.-]*github\.io[^\s\"'<)\]]*", read(rel)):
            if not m.group(0).startswith(url):
                out.append("%s links to %s, which is not under %s" % (rel, m.group(0), url))
    m = re.search(r"\[Open the survey\]\(([^)]+)\)", read("README.md"))
    if not m:
        out.append("README.md has lost its 'Open the survey' link")
    elif m.group(1) != url:
        out.append("README.md 'Open the survey' points at %s, not %s" % (m.group(1), url))
    if 'src="qr-survey.png"' not in read("README.md"):
        out.append("README.md no longer shows qr-survey.png")
    svg = read("qr-survey.svg")
    if url not in svg:
        out.append("qr-survey.svg aria-label does not name %s (was the QR regenerated?)" % url)
    idx = read("index.html")
    if "01_survey/pool-plant-room-survey.html" not in idx:
        out.append("index.html no longer redirects to the survey")
    return out


@check("C16", "nothing here breaks GitHub Pages limits")
def c16():
    out, total = [], 0
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            p = os.path.join(dp, fn)
            if os.path.islink(p): continue
            n = os.path.getsize(p); total += n
            if n > 100 * 1024**2:
                out.append("%s is %.0f MB, over GitHub's 100 MB hard limit" % (os.path.relpath(p, ROOT), n/1024**2))
            elif n > 50 * 1024**2:
                out.append("NOTE %s is %.0f MB, past the 50 MB warning line" % (os.path.relpath(p, ROOT), n/1024**2))
    if total > 1024**3:
        out.append("the site is %.2f GB, over the 1 GB Pages limit" % (total/1024**3))
    return out


@check("C17", "counts stated in prose match the folders")
def c17():
    """The README says "34 photographs". Add one and that sentence is wrong, and
    nothing else in the world will tell you."""
    out = []
    for rel in ("README.md", SURVEY):
        text = read(rel)
        for m in re.finditer(r"(\d\d_[a-z-]+)/[^\n]{0,60}?\b(\d{1,3})\s+(photograph|photographs|files|images|videos|manuals|products)\b", text):
            folder, stated, noun = m.group(1), int(m.group(2)), m.group(3)
            d = os.path.join(ROOT, folder)
            if not os.path.isdir(d): continue
            actual = len([f for f in os.listdir(d)
                          if not f.startswith(".") and not APPARATUS.match(f)])
            if actual != stated:
                out.append("%s says %d %s in %s/, there are %d" % (rel, stated, noun, folder, actual))
    return out


@check("C18", "derived files match the source they were built from")
def c18():
    """The PDF and the diagram PNG are generated from the HTML. Editing the survey
    silently invalidates both, and neither one looks wrong afterwards."""
    rec = os.path.join(ROOT, "01_survey/DERIVED.txt")
    if not os.path.exists(rec): return ["01_survey/DERIVED.txt is missing"]
    s = survey()
    m = re.search(r'<svg viewBox="0 0 1560 2370"[\s\S]*?</svg>', s)
    sources = {
        "pool-plant-room-survey.pdf":  s,
        "pool-plant-room-diagram.png": m.group(0) if m else None,
    }
    out = []
    for line in read("01_survey/DERIVED.txt").split("\n"):
        if "||" not in line or line[:1].isspace(): continue
        f, src, want = [x.strip() for x in line.split("||")]
        if f not in sources:
            out.append("DERIVED.txt names %s, which this check does not know how to hash" % f); continue
        text = sources[f]
        if text is None:
            out.append("could not find %s in the survey any more" % src); continue
        got = hashlib.sha256(text.encode()).hexdigest()
        if got != want:
            out.append("%s is stale: %s changed. Rebuild it, then put %s in DERIVED.txt"
                       % (f, src, got[:16] + "..."))
        if not os.path.exists(os.path.join(ROOT, "01_survey", f)):
            out.append("01_survey/%s is listed in DERIVED.txt but does not exist" % f)
    return out


@check("C19", "no redundant near-duplicate images")
def c19():
    """Two frames of the pump strainer lid were taken in the same second and
    differed only by camera shake. They were not byte-identical, so the exact-hash
    audit that found the panorama duplicate walked straight past them.

    Needs Pillow. Every other check is standard library only; this one reports
    itself as skipped rather than failing when Pillow is absent."""
    try:
        from PIL import Image
    except ImportError:
        return ["NOTE C19 skipped: Pillow is not installed (pip install Pillow)"]
    import itertools

    def dhash(path, s=16):
        im = Image.open(path).convert("L").resize((s + 1, s), Image.LANCZOS)
        px = im.load()
        bits = 0
        for y in range(s):
            for x in range(s):
                bits = (bits << 1) | (1 if px[x, y] < px[x + 1, y] else 0)
        return bits

    imgs = [rel for rel in walk((".jpg", ".jpeg", ".png"))]
    H = {}
    for rel in imgs:
        try: H[rel] = dhash(os.path.join(ROOT, rel))
        except Exception: pass

    def siblings(a, b):
        """an annotated copy of a photograph is deliberate, not redundant"""
        base = lambda p: re.sub(r"_annotated", "", p)
        return base(a) != a or base(b) != b

    out = []
    for a, b in itertools.combinations(sorted(H), 2):
        d = bin(H[a] ^ H[b]).count("1")
        if d > 8: continue
        if siblings(a, b): continue
        out.append("%s and %s are near-identical (distance %d of 256). Keep the sharper one and register the gap in NAMING.txt" % (a, b, d))
    return out


@check("C20", "the activity log stays well formed and in order")
def c20():
    """A log is only worth keeping if it can be read back mechanically. This
    catches the two ways it rots: an entry filed out of order, and a category
    invented on the spot that no later search will think to look for."""
    if not os.path.exists(os.path.join(ROOT, "LOG.txt")):
        return ["LOG.txt is missing"]
    text = read("LOG.txt")
    cats = set(re.findall(r"^      ([A-Z]+)\s{2,}", text, re.M))
    if not cats:
        return ["could not read the CATEGORY vocabulary out of the header"]
    entry = re.compile(r"^(\d{4}-\d{2}-\d{2}) ~?(\d{2}:\d{2})\s+([A-Z]+)\s", re.M)
    out, prev = [], None
    for m in entry.finditer(text):
        date, time, cat = m.groups()
        if cat not in cats:
            out.append("%s %s uses category %r, which is not in the header list" % (date, time, cat))
        stamp = date + " " + time
        if prev is not None and stamp > prev:
            out.append("%s %s is newer than the entry above it; the log is newest-first" % (date, time))
        prev = stamp
    if prev is None:
        out.append("LOG.txt has a header but no entries")
    return out


@check("C21", "MEDIA.tsv describes exactly what is on disk")
def c21():
    """Ninety media files, cited by number all through the survey, and until
    there was a manifest the only way to answer "what is photograph 17?" was to
    open a 3 MB file and look. MEDIA.tsv is now the one home for that answer,
    and everything in it except the caption is computed, so it can go stale in
    three ways: a file added and not scanned, a file edited under a row that
    still carries the old hash, and a row with no caption written yet.

    tools/media.py scan fixes all three."""
    rel = "MEDIA.tsv"
    if not os.path.exists(os.path.join(ROOT, rel)):
        return ["MEDIA.tsv is missing. Build it with: python3 tools/media.py scan"]
    listed, order = {}, []
    for line in read(rel).split("\n"):
        if not line or line.startswith("#") or line.startswith("path\t"): continue
        f = line.split("\t")
        if len(f) < len(MEDIA_COLUMNS):
            return ["MEDIA.tsv row has %d columns, expected %d: %s" % (len(f), len(MEDIA_COLUMNS), f[0])]
        listed[f[0]] = dict(zip(MEDIA_COLUMNS, f))
        order.append(f[0])
    disk = media_on_disk()
    out = []
    for f in sorted(set(disk) - set(listed)):
        out.append("%s is on disk with no row in MEDIA.tsv" % f)
    for f in sorted(set(listed) - set(disk)):
        out.append("MEDIA.tsv lists %s, which is not on disk" % f)
    if order != sorted(order):
        out.append("MEDIA.tsv is not in path order, so two scans would produce different files")
    for f in sorted(set(disk) & set(listed)):
        row, full = listed[f], os.path.join(ROOT, f)
        size = os.path.getsize(full)
        if str(size) != row["bytes"]:
            out.append("%s is %d bytes, MEDIA.tsv says %s" % (f, size, row["bytes"]))
        elif hashlib.sha256(open(full, "rb").read()).hexdigest() != row["sha256"]:
            out.append("%s has changed since it was scanned: its sha256 no longer matches" % f)
        if not row["caption"].strip():
            out.append("%s has no caption in MEDIA.tsv" % f)
    return out


@check("C22", "every contact sheet still shows its whole folder")
def c22():
    """A contact sheet is derived, and a stale one does not look wrong: it just
    quietly leaves out the photograph you went looking for. Each sheet carries a
    digest of the files it was built from in its own JPEG comment, so the
    staleness is detectable without a second file to remember.

    Both sides of the comparison are computed from the folder rather than from
    MEDIA.tsv, so this does not depend on C21 having passed first.

    tools/media.py sheets rebuilds them."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    try:
        import media
    except ImportError as e:
        return ["tools/media.py could not be imported: %s" % e]
    out = []
    folders = sorted(d for d in os.listdir(ROOT)
                     if re.match(r"^\d\d_", d) and os.path.isdir(os.path.join(ROOT, d))
                     and d not in MEDIA_SKIP)
    for d in folders:
        want_from = media.sheet_inputs(d)
        sheet = os.path.join(ROOT, d, SHEET)
        if len(want_from) < 2:
            if os.path.exists(sheet):
                out.append("%s/%s has no folder of images behind it any more" % (d, SHEET))
            continue
        if not os.path.exists(sheet):
            out.append("%s/ has %d images and no %s" % (d, len(want_from), SHEET))
            continue
        got = sheet_digest(sheet)
        if got is None:
            out.append("%s/%s carries no build digest; rebuild it" % (d, SHEET))
        elif got != media.sheet_digest(d):
            out.append("%s/%s is stale: the folder has changed since it was built" % (d, SHEET))
    return out


@check("C23", "tHHMM tokens are times the file actually carries")
def c23():
    """NAMING.txt says the token is the moment the file was made, and a token is
    only worth anything if that is enforceable. Left alone it becomes decoration:
    a file gets renamed, someone types a plausible four digits, and from then on
    the archive says a thing happened at a time it did not.

    Two timestamps are legitimate. "captured" is when the shutter opened.
    "made" is when this version was written, and is the right one for a frame
    that was drawn on afterwards. Anything else is invented."""
    if not os.path.exists(os.path.join(ROOT, "MEDIA.tsv")): return []
    out = []
    for line in read("MEDIA.tsv").split("\n"):
        if not line or line.startswith("#") or line.startswith("path\t"): continue
        r = dict(zip(MEDIA_COLUMNS, line.split("\t")))
        m = re.search(r"_t(\d{2})(\d{2})\.[a-z0-9]+$", r["path"])
        if not m: continue
        token = m.group(1) + ":" + m.group(2)
        stamps = [t[11:16] for t in (r.get("captured", ""), r.get("made", "")) if t]
        if not stamps:
            out.append("%s carries a time token but no timestamp of any kind" % r["path"])
        elif token not in stamps:
            out.append("%s says t%s%s; the file says %s"
                       % (r["path"], m.group(1), m.group(2), " and ".join(stamps)))
    return out


@check("C24", "every numbered folder explains itself")
def c24():
    """Four of these folders went the whole life of the project with no apparatus
    file at all, 04_plant-room among them, which is the one nearly every claim in
    the survey rests on. Thirty-three photographs and nothing saying what they
    were, which was better, or what the gap at 28 meant.

    A folder of evidence with no note beside it is a folder only its author can
    use, and only for as long as they remember. This is the check that stops the
    next folder arriving the same way."""
    out = []
    for d in sorted(os.listdir(ROOT)):
        if not re.match(r"^\d\d_", d) or not os.path.isdir(os.path.join(ROOT, d)):
            continue
        docs = [f for f in os.listdir(os.path.join(ROOT, d))
                if APPARATUS.match(f) and f.lower().endswith(".txt")]
        if not docs:
            out.append("%s/ has no apparatus file. Add a READ-ME.txt saying what is in "
                       "it, what it is good for, and what it must not be used for" % d)
    return out


@check("C25", "every key in the legend is drawn on the diagram")
def c25():
    """The survey's opening paragraph promises "Every key is drawn as a circle, on
    the drawing and in the text alike". It was not true: M, N, 1, 3, 4 and 7 lived
    in the legend and the prose and appeared nowhere on the picture, and nobody
    noticed until a reader asked why valve 7 was missing.

    A key defined in the legend but absent from the drawing is the worst kind of
    gap, because the legend is what tells you the drawing is complete."""
    s = survey()
    lg = re.search(r'<h4>The letters, as the sheets number them</h4>([\s\S]*?)</dl>', s)
    if not lg:
        return ["could not find the legend block that defines the keys"]
    keys = set()
    for dt in re.findall(r"<dt>([\s\S]*?)</dt>", lg.group(1)):
        keys.update(re.findall(r"<code>([A-Z0-9]{1,2})</code>", dt))
    if not keys:
        return ["the legend defines no keys at all"]
    m = re.search(r'<svg viewBox="0 0 1560 2370"[\s\S]*?</svg>', s)
    if not m:
        return ["could not find the schematic svg"]
    svg = m.group(0)
    # a badge is a circle in the valve or unsure colour with its letter beside it
    drawn = set(re.findall(
        r'<circle[^>]*stroke="var\(--(?:valve|unsure)\)"[^>]*/>\s*<text[^>]*>([A-Z0-9]{1,2})</text>', svg))
    out = ["%s is defined in the legend but has no badge on the diagram" % k
           for k in sorted(keys - drawn)]
    # the other direction matters just as much: a badge on the picture that the
    # legend never defines is a key the reader cannot look up. 5 was one.
    out += ["%s is drawn on the diagram but the legend never defines it" % k
            for k in sorted(drawn - keys)]
    return out


def main(argv):
    verbose = "-v" in argv
    want = [a.upper() for a in argv if re.match(r"^[Cc]\d+$", a)]
    fails = 0
    print("checking %s\n" % ROOT)
    for cid, title, fn in results:
        if want and cid not in want: continue
        try:
            problems = fn()
        except Exception as e:
            problems = ["the check itself failed: %s: %s" % (type(e).__name__, e)]
        notes = [p for p in problems if p.startswith("NOTE ")]
        hard = [p for p in problems if not p.startswith("NOTE ")]
        if hard:
            fails += 1
            print("  FAIL  %-4s %s" % (cid, title))
            for p in hard: print("          %s" % p)
        else:
            if verbose or notes: print("  ok    %-4s %s" % (cid, title))
        for p in notes: print("          %s" % p[5:])
    print()
    print("  %d check(s) failed" % fails if fails else "  all checks pass")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
