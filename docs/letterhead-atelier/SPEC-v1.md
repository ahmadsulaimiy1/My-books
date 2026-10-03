# letterhead v1.0 — the locked specification

**الإمام أحمد بن إبراهيم السليمي (آل سلام)** · PERSONAL OFFICE · IMAM AHMAD IBROHIM SULAIMIY · ĀL-ES-SALAM

> GENERATED FILE — rewritten by `tools/verify-v1.py --spec`.
> Every value below is read back out of the stylesheets by
> `python3 tools/verify-v1.py`, which fails by name if one moves.

## THE SHEET

| | value in source |
|---|---|
| Trim | `width:210mm; height:297mm` |
| Page box | `@page{ size:A4; margin:0; }` |
| Left axis — every block | `.register{ position:absolute; top:107.4mm; left:24mm; right:48mm;` |
| Writing measure | `.field{ position:absolute; top:147mm; left:24mm; right:48mm; bottom:52mm;` |

## THE PLATE

| | value in source |
|---|---|
| Head depth 56mm, pier at 172mm | `.plate     { clip-path:polygon(0 0,210mm 0,210mm 297mm,172mm 297mm,172mm 56mm,0 56mm);` |
| Gold keyline — lower silhouette only, 0.55mm proud | `.plate-gold{ clip-path:polygon(0 0,210mm 0,210mm 297mm,172mm 297mm,172mm 56.55mm,0 56.55mm); }` |
| Continuation pier — same 38mm | `.cont-plate{ position:absolute; top:0; right:0; bottom:0; width:38mm;` |

## THE BINDING EDGE — nine members, total 7.87mm from x=172mm

| | value in source |
|---|---|
| Assembly origin and width | `.edge{ position:absolute; top:0; bottom:0; left:172mm; width:7.87mm;` |
| 1 · crevice + lit arris  .55 | `.edge-arris{ position:absolute; top:56mm; bottom:0; left:-.20mm; width:.55mm;` |
| 2 · SILL, lit            .86 | `.edge-sill { left:.35mm;  width:.86mm;` |
| 3 · near wall, cut       .19 | `.edge-cut  { left:1.21mm; width:.19mm;` |
| 4 · GOLD RAIL, proud    3.40 | `.edge-rail { left:1.40mm; width:3.40mm;` |
| 5 · return, lit chamfer  .35 | `.edge-ret  { left:4.80mm; width:.35mm;` |
| 6 · PLATINUM, recessed  2.20 | `.edge-plat { left:5.15mm; width:2.20mm;` |
| 7 · far wall, lit        .30 | `.edge-wall { left:7.35mm; width:.30mm;` |
| 8 · cut line             .22 | `.edge-rule { left:7.65mm; width:.22mm; background:#020814; }` |

## THE SEAL — 46mm, centred (139, 56), 10mm clear on every side

| | value in source |
|---|---|
| Medallion | `.medallion{ position:absolute; left:116mm; top:33mm; width:46mm; height:46mm;` |
| Bezel — steel ring | `.med-steel{ position:absolute; inset:1.5mm;` |
| Field | `.med-field{ position:absolute; inset:2.6mm;` |
| Inner hairline ring | `.med-hair { position:absolute; inset:4.4mm;` |
| Mark, 19mm, clear inside | `.med-mark { position:absolute; left:50%; top:50%;` |
| Latin wordmark held OFF the clear zone | `font-size:13.6pt;   letter-spacing:.06em;` |

## THE RED CHANNEL — the binding section turned 90°

| | value in source |
|---|---|
| Stainless wall, above, shaded  .50 | `.redch-steel{ position:absolute; left:0; right:38mm; top:94.5mm; height:.5mm;` |
| Red channel                   5.60 | `.redch      { position:absolute; left:0; right:38mm; top:95mm; height:5.6mm;` |
| Gold wall, below, lit          .62 | `.redch-gold { position:absolute; left:0; right:38mm; top:100.6mm; height:.62mm;` |

## TYPOGRAPHY — four voices, one fount per script per layer

| | value in source |
|---|---|
| Arabic identity · Reem Kufi 600 19pt | `font-weight:600; font-size:19pt;` |
| Latin identity · Playfair Display 700 13.6pt | `.ident-name{ font-family:"Playfair Display",serif; font-weight:700;` |
| Arabic document · Scheherazade New 13.4pt / 1.78 | `.letter{ font-family:"Scheherazade New",serif; font-size:13.4pt; line-height:1.78;` |
| Latin document · EB Garamond | `.letter .lat{ font-family:"EB Garamond",serif;` |
| Instrument · Inter | `.foot .contact{ font:400 6.2pt/1 "Inter",sans-serif;` |
| Amiri is OUT of the build | `"Scheherazade New","family=Scheherazade+New:wght@400","arabic", 400` |

## PALETTE

| | value in source |
|---|---|
| Sapphire, deepest | `--sapphire-950:#020B1E;` |
| Sapphire, ground | `--sapphire-800:#082349;` |
| Sapphire, lit | `--sapphire-600:#11418F;` |
| RED — the principal red, and it is red | `--red-700:#C8102E;` |
| Pearl | `--pearl:#FBF9F5;` |
| Ink | `--ink:#121826;` |
| Gold — rich ramp, for members that carry weight | `--foil-gold-rich:linear-gradient(104deg,` |
| Platinum — cooler and a stop darker than the stainless | `--foil-plat:linear-gradient(104deg,` |
| Stainless — the diamond ramp, white at 72% | `--foil-steel:linear-gradient(104deg,` |

## What is NOT frozen

The stationery is a template, so the **content** of a letter is free:
the addressee, the reference, the date, the subject, the body and the
signature blocks all change per letter and are not part of v1.

Everything else is. A change to any table above is a change to the
**design**, and belongs in v2 — bump `VERSION` in `tools/verify-v1.py`,
update the constant, re-seal with `--seal`, and tag.
