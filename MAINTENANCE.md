# Keeping this repository honest

One command. Run it after any edit, before any commit:

```bash
python3 tools/check.py
```

No installation, python3 and the standard library. The one exception is the
near-duplicate scan, which uses Pillow when it is installed and reports itself
skipped when it is not; nothing else needs it. It exits non-zero if
anything is wrong and prints the file and the reason.

## Why there is a checker at all

This survey deliberately says the same thing in more than one place. The plant
room area is in the title block, in `DIMENSIONS.txt`, and in the reasoning about
storing acid in a confined space. That repetition is good for whoever is reading
it at seven in the evening with wet hands, and bad for whoever is editing it,
because changing one copy leaves the others quietly wrong.

Every check below is a mistake that actually happened while this document was
being written. They are not hypothetical.

| | What it catches | The time it bit |
|---|---|---|
| `C1` | Unbalanced braces in the survey stylesheet | A stray `}` glued itself to the next selector and Chrome discarded the whole rule. 120 valve badges rendered as plain text and nothing looked broken. |
| `C2` | A key CSS rule going missing | Same incident, from the other direction. |
| `C3` | Section numbers not running 1..n in document order | Sections were reordered and the numbers stayed put. |
| `C4` | Nav entries that point at nothing, or in the wrong order | |
| `C5` | Internal links with no target | |
| `C6` | The folder table disagreeing with the folders on disk | `10_products/` was listed after `11_scan/`. |
| `C7` | Prose naming a file that does not exist | Four panorama files were deleted; three documents still pointed at them. |
| `C8` | The survey reaching out to the network | It has to work in a basement with no signal. Every image is a `data:` URI and it must stay that way. |
| `C9` | Em dashes, en dashes, curly quotes, emoji | |
| `C10` | Attribution to anyone other than you | |
| `C11` | A superseded statement coming back | An earlier version of this survey put the tank at 7.5 percent and called it "correctly sized". It is 5.1 percent, and adequate rather than generous. |
| `C12` | A canonical number changed in one file only | |
| `C13` | Prose citing a section by number | Renumbering broke six cross-references at once. The rule now is to cite sections by name. |
| `C14` | File names outside the convention in `NAMING.txt` | |
| `C15` | The published URL differing between files | |
| `C16` | Files over GitHub's size limits | 100 MB is a hard refusal, 50 MB a warning, 1 GB the site cap. |
| `C17` | A count stated in prose drifting from the folder | The README says "34 photographs". Add one and that sentence is wrong, and nothing else will tell you. |
| `C18` | The PDF or the diagram no longer matching the HTML | Both are generated from the survey. Editing it invalidates them, and neither looks wrong afterwards. The hashes are in `01_survey/DERIVED.txt`. |
| `C20` | The activity log out of order, or using an invented category | Caught two ordering slips within a minute of being written, both mine. |
| `C19` | Two frames of the same thing filed as two photographs | Photographs 27 and 28 were shot in the same second and differed only by camera shake. They were not byte-identical, so an exact-hash audit walked past them. This one compares what the pictures look like. |

## Proving the checks still work

```bash
python3 tools/selftest.py
```

It breaks the repository twenty ways, once per check, confirms each break is
caught, and puts everything back. It refuses to run on a dirty tree, so a crash
cannot cost you work.

This is not ceremony. When it was first run, two checks passed on a repository
that was genuinely broken: `C2` was satisfied by `h4 code{` standing in for the
rule it was meant to be guarding, and `C15` only asked whether the right URL was
present, not whether a wrong one was sitting beside it. A check that has never
failed is indistinguishable from a check that cannot fail.

## Doing the usual things

**Changing a number.** Edit it in `FACTS.txt` first. Run the checker. It names
every file still carrying the old value. Fix those, run again.

**Correcting something the survey got wrong.** Say so in the text rather than
editing the mistake out. The house style is "An earlier version of this document
said X; that was my inference and it was wrong." Then add the old wording to the
`NEVER` list in `FACTS.txt` with `|| unless: an earlier version`, which lets the
correction stand while failing on any fresh assertion of the mistake.

**Adding a photograph.** Drop it in `00_inbox/`, which is gitignored so nothing
half-filed reaches the repository. File it under the right numbered folder using
the next free index, following `NAMING.txt`. Indices are permanent and
append-only: a gap means something was deleted, never that something is missing.

**Deleting a file.** `git rm` it, then run the checker. `C7` finds every document
that still refers to it. Record the deletion in that folder's `READ-ME.txt`
rather than letting the index gap go unexplained.

**Adding a section to the survey.** Add the `<section id="...">`, give its
heading a `<span class="n">&#167;X</span>`, add the nav entry in the same
position, then renumber:

```bash
python3 - <<'PY'
import re
p = "01_survey/pool-plant-room-survey.html"
s = open(p, encoding="utf-8").read()
n = [0]
def bump(m):
    n[0] += 1
    return '<span class="n">&#167;%d</span>' % n[0]
s = re.sub(r'<span class="n">&#167;(?:\d+|X)</span>', bump, s)
open(p, "w", encoding="utf-8").write(s)
print("renumbered %d sections" % n[0])
PY
python3 tools/check.py
```

Cross-references in prose name the section rather than its number, so
renumbering cannot break them. `C13` enforces that.

**After editing the survey.** The PDF and the diagram PNG are built from it and
are now wrong.

```bash
python3 tools/rebuild.py
python3 tools/check.py
```

`rebuild.py` runs Chrome for both, then refreshes the source hashes in
`01_survey/DERIVED.txt`. The hashes cover the source, not the output, so an edit
to the water chemistry does not falsely flag the diagram, and a real edit to the
diagram cannot slip past because a file happened to be touched.

**Regenerating the QR code.** Only needed if the published URL changes.

```bash
python3 -m venv /tmp/qrenv && /tmp/qrenv/bin/pip install segno
/tmp/qrenv/bin/python - <<'PY'
import segno
URL = "https://albidr.github.io/Pool-ADR/"
q = segno.make(URL, error="H")
q.save("qr-survey.png", scale=24, border=4, dark="#1B2124", light="#FFFFFF")
PY
```

The SVG in the survey title block is inline, so it has to be rebuilt the same
way and pasted in. Keep it dark on white whatever happens: a colour-inverted QR
code will not scan on a good number of phones, which is why it carries its own
white plate instead of using the page background.

## Logging what you do

`LOG.txt` is the operational record: every switch of the reintegro or the pump,
every dose, every backwash with the gauge reading after it, every level taken
with a tape. Newest at the top, one line each, always with the number in it.

It exists because on 2026-09-08 nobody could answer "how long has the reintegro
actually run?" The information had never been written down, only said out loud,
and two wrong estimates were built on the gap before it was noticed. A fill that
was paused twice looks identical in hindsight to one that ran straight through.

## The three rules underneath all of this

1. **One fact, one home.** `FACTS.txt` holds the numbers. Everything else quotes
   them.
2. **Cite by name, never by number.** Numbers move. Names do not.
3. **Corrections stay visible.** The document records what it used to say and why
   that was wrong. That history is the reason it can be trusted, and `C11` is
   what stops it from being silently undone.
