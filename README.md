# Pool plant room

A working survey of one residential pool installation: the plant room, the
balance tank, the equipment, the chemicals, and how to run it.

Compiled from photographs of the rooms, from the four printed sheets kept in
the plant room, and from the makers' own manuals. Every statement in it is
labelled with where it came from.

## Start here

**[Open the survey](https://albidr.github.io/Pool-ADR/)**

One self-contained HTML page. No internet needed once it has loaded, no linked
files, every photograph embedded inside it. It prints properly if you want a
copy on the wall down there, and it is worth having one: the plant room is
below ground, where a phone may have no signal at the moment you most need it.

## What is in here

| | |
|---|---|
| `00_inbox/` | Staging. New files land here as they come off the phone and are filed from there. |
| `01_survey/` | The deliverable: the survey as HTML and PDF, plus the diagram as a PNG. |
| `02_printed-sheets/` | The four printed pages kept in the room. The procedures section is transcribed from these. |
| `03_nameplates/` | The plates and labels every specification rests on. |
| `04_plant-room/` | 34 photographs, in the order they were taken. |
| `05_balance-room/` | The balance tank and the hatch that reaches it, plus what the coloured marks on photograph 04 mean. |
| `06_drawings/` | Dimensioned sketches and the scaled plan of both rooms. |
| `07_video/` | Two 360 degree pans and one floor-level survey. |
| `08_panoramas/` | Wide images of two kinds, and **the distinction matters** — read its `READ-ME.txt` before using either. |
| `09_manuals/` | The makers' own manuals, with the official link for each and the key figures found. |
| `10_products/` | Every chemical on the shelf, photographed with its label, plus a catalogue and a symptom-to-action guide. |
| `11_scan/` | A 3D scan of the plant room, and the plan derived from it. |

## Two things worth knowing before you use any of it

**Not every wide image can be trusted.** `08_panoramas/` holds both stitched
images and reprojections of a single photosphere. An early stitch of the
manifold wall drew six drops where there are four, and it did not look wrong.
The reprojections cannot do that, because there is no stitching in them. The
folder's `READ-ME.txt` says which is which and why.

**Where a maker's manual contradicts the printed sheets, this follows the
manual and says so.** The clearest case is the filter gauge: the sheet says
"about 1 bar", but Kripsol's own manual gives 0.5 to 0.7 bar as normal running
and 1.0 as the point at which you stop and backwash.

## How it is named

Every file follows one rule, set out in [NAMING.txt](NAMING.txt): an index,
what the file shows, an optional note on how it differs from its neighbour,
then a marked technical token. Measured dimensions for both rooms and what
follows from them are in [DIMENSIONS.txt](DIMENSIONS.txt).

## What is still open

The survey has a section listing it: what has not been measured, what has not
been tested, and what nobody can measure without finding out. Nothing there is
known and merely unrecorded.

## Regenerating the PDF and the diagram

Both are tracked, so a fresh clone has them. They are generated from the HTML,
so after editing the survey, rebuild them with:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=35000 \
  --print-to-pdf="01_survey/pool-plant-room-survey.pdf" \
  "file://$PWD/01_survey/pool-plant-room-survey.html"
```

## A disclaimer, because this is public

This is a private record of one particular installation, written by its owner
for their own use. It is **not professional advice**, it has not been verified
by a physical inspection or against an installation drawing, and the printed
sheets it draws on are a household reference rather than a specification.

It describes handling concentrated sulphuric acid and chlorine donors, which
release chlorine gas on contact with each other. If you are working on your own
pool, use your own equipment's manuals and your own judgement.
