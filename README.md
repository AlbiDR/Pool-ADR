# Pool plant room

A working survey of one residential pool installation: the plant room, the
balance tank, the equipment, the chemicals, and how to run it.

Compiled from photographs of the rooms, from the four printed sheets kept in
the plant room, and from the makers' own manuals. Every statement in it is
labelled with where it came from.

## Start here

**[Open the survey](https://albidr.github.io/Pool-ADR/)**

<p align="center">
  <a href="https://albidr.github.io/Pool-ADR/"><img src="qr-survey.png" alt="QR code linking to the survey" width="340" height="340"></a>
</p>

<p align="center">
  <code>albidr.github.io/Pool-ADR</code><br>
  <sub>Print this and put it on the plant room wall. It always resolves to the current version.</sub>
</p>

One self-contained HTML page. No internet needed once it has loaded, no linked
files, every photograph embedded inside it. It prints properly if you want a
copy on the wall down there, and it is worth having one: the plant room is
below ground, where a phone may have no signal at the moment you most need it.

Four things it does that a printout cannot. **Tap any circled letter or number**
and it tells you what that valve is without scrolling back to the legend, then
steps you through every place the document mentions it; the digits carry two
meanings in this installation, a valve and a Kripsol lever position, and it
shows both rather than guessing. **Press `/`** to search it. **Every photograph
in the archive is in it**, as an index you can tap to enlarge, so the page
answers "which picture was that?" with nothing else to hand. And it follows your
**light or dark** setting, or whichever you pick. With scripting off it is still
the same document, top to bottom.

## What is in here

| | |
|---|---|
| `00_inbox/` | Staging. New files land here as they come off the phone and are filed from there. |
| `01_survey/` | The deliverable: the survey as HTML and PDF, plus the diagram as a PNG. |
| `02_printed-sheets/` | The four printed pages kept in the room. The procedures section is transcribed from these. |
| `03_nameplates/` | The plates and labels every specification rests on. |
| `04_plant-room/` | 33 photographs, in the order they were taken. The evidence nearly every claim rests on. |
| `05_balance-room/` | The balance tank and the hatch that reaches it, plus what the coloured marks on photograph 04 mean. |
| `06_drawings/` | Dimensioned sketches and the scaled plan of both rooms. |
| `07_video/` | Two 360 degree pans and one floor-level survey. |
| `08_panoramas/` | Straightened wall views reprojected from the photosphere, safe to count from. Its `READ-ME.txt` says why the earlier stitched versions were deleted. |
| `09_manuals/` | The makers' own manuals, with the official link for each and the key figures found. |
| `10_products/` | Every chemical on the shelf, photographed with its label, plus a catalogue and a symptom-to-action guide. |
| `11_scan/` | A 3D scan of the plant room, and the plan derived from it. |
| [`LOG.txt`](LOG.txt) | What was actually done and when: every switch, dose, backwash and reading. The survey describes the installation; this records its operation. |
| [`MEDIA.tsv`](MEDIA.tsv) | One row for every media file: what it shows, its size, its dimensions, when it was taken, and its `sha256`. The one place a file's description lives. |
| [`CHANGELOG.txt`](CHANGELOG.txt) | What was done to the **archive**, and why. `LOG.txt` is the pool; this is the filing. |

Every numbered folder carries its own `READ-ME.txt` saying what is in it, what
it is good for, and what it must not be used for. Read that before the pictures.
Each also carries a `CONTACT-SHEET.jpg`: every image in the folder, numbered, at
thumbnail size. Open that first. It is a few hundred kilobytes against tens of
megabytes of originals, and it answers "which one do I want?" without opening
anything.

## Two things worth knowing before you use any of it

**Not every wide image can be trusted.** An early stitch of the manifold wall
drew six drops where there are four, and it did not look wrong. Every wide
image kept here is now a reprojection of a single photosphere instead, which
cannot invent geometry because there is no stitching in it. The stitches were
deleted; `08_panoramas/READ-ME.txt` records what they were and why they went.

**Where a maker's manual contradicts the printed sheets, this follows the
manual and says so.** The clearest case is the filter gauge: the sheet says
"about 1 bar", but Kripsol's own manual gives 0.5 to 0.7 bar as normal running
and 1.0 as the point at which you stop and backwash.

## How it is named, and how to find anything

Every file follows one rule, set out in [NAMING.txt](NAMING.txt): an index,
what the file shows, an optional note on how it differs from its neighbour,
then a marked technical token. A name in capitals is apparatus rather than
evidence, takes no index, and describes the folder it sits in.

What a file actually **shows** is not in its name, because a name is a handle
and stretching it into a description produces filenames nobody can type. That
lives in [MEDIA.tsv](MEDIA.tsv), one line per file:

```bash
python3 tools/media.py show 04_plant-room
```

Measured dimensions for both rooms and what follows from them are in
[DIMENSIONS.txt](DIMENSIONS.txt).

## Adding or changing media

```bash
python3 tools/media.py scan      # rewrite MEDIA.tsv, keeping the captions
python3 tools/media.py sheets    # rebuild the contact sheets
python3 tools/check.py           # C21, C22 and C23 will tell you if you forgot
```

`scan` computes everything except the caption, which it carries forward, and
lists any file still missing one. Write that line and the checker goes quiet.

## What is still open

The survey has a section listing it: what has not been measured, what has not
been tested, and what nobody can measure without finding out. Nothing there is
known and merely unrecorded.

## Regenerating the PDF and the diagram

Both are tracked, so a fresh clone has them. They are generated from the HTML,
so after editing the survey:

```bash
python3 tools/rebuild.py
```

That runs Chrome, rewrites both, and refreshes the source hashes in
`01_survey/DERIVED.txt` so the checker agrees. `C18` fails if you forget.

## Keeping it consistent

This survey states the same fact in several files at once, which is good for
reading it and bad for editing it. One command checks the lot:

```bash
python3 tools/check.py
```

Twenty-three checks, standard library only (one, the near-duplicate
scan, uses Pillow when it is available and reports itself skipped when it is not). Section numbering, the nav, internal links,
the folder table against the folders on disk, file references, offline
self-containment, punctuation, superseded wording, the canonical numbers in
[FACTS.txt](FACTS.txt), naming, stated counts, whether the PDF and the
diagram still match the HTML they came from, near-duplicate images,
GitHub's size limits, the activity log's ordering, the media manifest against
the files on disk, whether each contact sheet still shows its whole folder, and
whether every time token in a file name is a time that file actually carries.
Every one of them is a mistake that actually happened here.

[MAINTENANCE.md](MAINTENANCE.md) explains how to do the usual things without
causing drift, and `python3 tools/selftest.py` breaks the repository
twenty-three ways to prove the checks still detect anything.

## A disclaimer, because this is public

This is a private record of one particular installation, written by its owner
for their own use. It is **not professional advice**, it has not been verified
by a physical inspection or against an installation drawing, and the printed
sheets it draws on are a household reference rather than a specification.

It describes handling concentrated sulphuric acid and chlorine donors, which
release chlorine gas on contact with each other. If you are working on your own
pool, use your own equipment's manuals and your own judgement.
