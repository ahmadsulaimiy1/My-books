#!/usr/bin/env python3
"""
Assemble the Digital Campus costing paper on the atelier stationery.

ONE SOURCE, ONE DOCUMENT, AND THE PAGINATION IS MEASURED RATHER THAN GUESSED.
The sheet clips at 210x297 and says nothing when it does, so a long paper laid
out by hand loses its last paragraph silently. This script therefore runs in
three passes:

  1  GALLEY    every block is emitted once into a single 138mm column
  2  MEASURE   Chromium renders the galley and reports each block's height
  3  IMPRESS   the blocks are packed into sheets against the real field extents

Pass 2 is the reason the paper is correct rather than approximately correct. A
section head is never left at the foot of a sheet, because a head is marked
keep-with-next and is carried forward with the block it introduces.

THE LETTERHEAD IS NOT REBUILT HERE. The plate, the nine-member binding
section, the medallion, the pier, the red channel, the foot and the security
layers are the atelier's own, loaded from ../letterhead-atelier/assets and
emitted by the same constructions. Only three things on the stationery are
addressed by this document: the red channel's legend, the register, and the
writing field.

    python3 tools/build-paper.py          build and paginate
    python3 tools/build-paper.py --pdf    build, then print to PDF
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
AT   = "../letterhead-atelier/assets"            # the stationery, unchanged
def _find(*cands):
    return next((p for p in cands if os.path.exists(p)), None)

# TWO BINARIES, FOR TWO JOBS. --dump-dom is old-headless only, and old headless
# has been removed from the full Chrome binary; chrome-headless-shell is the
# standalone implementation that still carries it. The PDF is printed from the
# full binary, because that is the pipeline the stationery's embedded faces
# were verified against.
SHELL  = _find("/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",
               "/usr/bin/chromium-headless-shell")
CHROME = _find("/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
               "/opt/pw-browsers/chromium/chrome-linux/chrome",
               "/usr/bin/chromium", "/usr/bin/google-chrome") or SHELL

MM = 96 / 25.4                                   # CSS px per mm at 96dpi

# ── the file ────────────────────────────────────────────────────────────────
# The reference, the addressee and the Hijri equivalent are the paper's own
# metadata rather than the source's — the source paper carries none. They are
# stated in ONE place so the school can correct them in one edit.
REF        = "PO/SHRS/2026/09/0021"
DATE_AR    = "١٤ ربيع الآخر ١٤٤٨هـ"
DATE_EN    = "28 September 2026"
DATE_SUB   = "الموافق ٢٨ سبتمبر ٢٠٢٦م"
TO_NAME    = "Sultan Hanafi Royal Schools"
TO_ROLE    = "The Proprietor and Management"
CLASS_EN   = "Confidential — institutional"
SUBJECT    = "Digital Campus — engineering requirement, implementation routes and costing basis"

NAME_AR  = "الإمام أحمد بن إبراهيم السليمي"
HOUSE_AR = "(آل سلام)"
SCOPE_AR = "للتطوير الأكاديمي والدعوة الإسلامية والعلاقات الدولية والشؤون الأهلية الخاصة"

# ══ THE STATIONERY — the atelier's constructions, called not copied ════════
GUIL = '''      <svg class="fill" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <defs>
          <pattern id="guil" width="44" height="17" patternUnits="userSpaceOnUse">
            <g fill="none" stroke="#E4CC8A" stroke-width=".38">
              <path d="M0 8.5 C 5.5 1, 16.5 1, 22 8.5 S 38.5 16, 44 8.5"/>
              <path d="M0 8.5 C 5.5 16, 16.5 16, 22 8.5 S 38.5 1, 44 8.5"/>
            </g>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#guil)"/>
      </svg>'''

def medallion(cls="medallion"):
    return f'''  <div class="{cls} gold-block">
    <div class="med-steel steel-block"></div>
    <div class="med-field field-sapphire">
      <div class="med-hair"></div>
      <img class="med-mark" src="{AT}/insignia-foil.png"
           alt="Insignia of the Personal Office">
    </div>
  </div>
'''

def edge(full=False):
    a = " edge-arris--full" if full else ""
    return f'''  <div class="edge-arris{a}"></div>
  <div class="edge">
    <i class="edge-sill"></i>
    <i class="edge-cut"></i>
    <i class="edge-rail gold-block gold-block--rich"></i>
    <i class="edge-ret"></i>
    <i class="edge-plat plat-block"></i>
    <i class="edge-wall"></i>
    <i class="edge-rule"></i>
  </div>
'''

def pier():
    return f'''  <span class="vert pier-en gold-type gold-type--dark">IMAM AHMAD IBROHIM SULAIMIY</span>
  <span class="vert pier-sub">PERSONAL OFFICE &nbsp;·&nbsp; ĀL-ES-SALAM</span>

  <div class="verify">
    <div class="frame gold-block"><img src="{AT}/qr-office.png"
         alt="Scan for the office contact card"></div>
    <div class="serial">{REF}</div>
  </div>
'''

def plate():
    return f'''  <!-- ══ ONE MILLED PLATE: head across the sheet, pier down the binding edge ══ -->
  <div class="plate-gold gold-block"></div>
  <div class="plate field-sapphire">
    <div class="plate-guil">
{GUIL}
    </div>
  </div>
{edge()}{pier()}'''

def head():
    """The masthead, unaltered. Only the red channel's legend is this paper's:
    a costing paper is not official correspondence and must not claim to be."""
    return f'''
  <div class="office gold-type gold-type--dark">المكتب الخاص</div>
  <h1 class="name">{NAME_AR}</h1>
  <div class="house gold-type gold-type--dark">{HOUSE_AR}</div>
  <div class="name-rule gold-block gold-block--dark"></div>
  <p class="scope-ar">{SCOPE_AR}</p>

  <div class="ident">
    <div class="ident-rule"></div>
    <div class="ident-office">PERSONAL OFFICE</div>
    <div class="ident-name letterpress">IMAM AHMAD IBROHIM SULAIMIY</div>
    <div class="ident-house">ĀL · ES · SALAM</div>
    <div class="scope-en">Academic Development<i></i>Islamic Da&lsquo;wah<i></i>International Relations<i></i>Private &amp; Civic Affairs</div>
  </div>

  <!-- ══ THE RED CHANNEL — the binding section turned through 90° ══ -->
  <div class="redch-steel steel-block steel-block--dark"></div>
  <div class="redch field-red"></div>
  <div class="redch-in">
    <span class="en">COSTING &amp; IMPLEMENTATION PAPER</span>
    <span class="ar">ورقة تقدير وتنفيذ</span>
  </div>
  <div class="redch-gold gold-block gold-block--rich"></div>
'''

def register():
    return f'''
  <div class="reg2">
    <div class="reg2-pair">
      <div class="reg2-to">
        <span class="k">Prepared for</span>
        <div class="nm">{TO_NAME}</div>
        <div class="ro">{TO_ROLE}</div>
      </div>
      <div class="reg2-file">
        <div class="r2"><span class="k">Reference</span><span class="v ref">{REF}</span></div>
        <div class="r2"><span class="k">Date</span><span class="v ara">{DATE_AR}<span class="sub2">{DATE_EN}</span></span></div>
      </div>
    </div>
    <div class="reg2-hair gold-block"></div>
    <div class="reg2-sub"><span class="k">Subject</span><span class="s">{SUBJECT}</span></div>
  </div>
'''

SECURITY = f'''
  <svg class="latent" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <g fill="none" stroke="#6B7080" stroke-width="0.5" opacity="0.18">
      <circle cx="200" cy="200" r="190"/><circle cx="200" cy="200" r="152"/>
      <circle cx="200" cy="200" r="107"/><circle cx="200" cy="200" r="76"/>
      <rect x="65.5" y="65.5" width="269" height="269"/>
      <rect x="65.5" y="65.5" width="269" height="269" transform="rotate(45 200 200)"/>
      <rect x="105" y="105" width="190" height="190" transform="rotate(22.5 200 200)"/>
      <path d="M10 200 H390 M200 10 V390 M66 66 L334 334 M334 66 L66 334"/>
    </g>
  </svg>
'''
WATERMARK = f'''  <span class="watermark"><img src="{AT}/insignia-deboss.png" alt="" aria-hidden="true"></span>
'''

def foot(fa, fe):
    # The classification replaces the contact block on a confidential paper:
    # the pier already carries the office, and a costing document's foot has
    # one thing to say about itself.
    strip = ("المكتب الخاص · الإمام أحمد بن إبراهيم السليمي (آل سلام) · "
             "DIGITAL CAMPUS · ENGINEERING & OPERATIONAL SERVICES · ") * 5
    return f'''
  <div class="microtext">{strip}</div>
  <div class="foot-rule gold-block"></div>
  <div class="foot">
    <span class="contact">CONFIDENTIAL<i></i>INSTITUTIONAL COSTING DOCUMENT</span>
    <span class="folio"><span class="ar">{fa}</span><span class="sep">·</span>{fe}</span>
  </div>
'''

def cont_head(sec_label):
    return f'''
  <div class="cont-plate field-sapphire"><div class="plate-guil">
{GUIL}
  </div></div>
{edge(full=True)}{pier()}
{medallion("cont-med medallion")}
  <div class="cont-ref">REF. <span class="ref">{REF}</span><br><span class="k">DIGITAL CAMPUS &nbsp;·&nbsp; COSTING PAPER</span><span class="sec">{sec_label}</span></div>
  <div class="cont-head">
    <div class="cont-name letterpress">{NAME_AR} {HOUSE_AR}</div>
  </div>
  <div class="cont-rule gold-block"></div>
'''

AR_NUM = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
def folio(page, total):
    return (f"صفحة {str(page).translate(AR_NUM)} من {str(total).translate(AR_NUM)}",
            f"PAGE {page} OF {total}")

HEAD = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="{at}/letterhead-typography.css">
<link rel="stylesheet" href="{at}/materials.css">
<link rel="stylesheet" href="{at}/atelier.css">
<link rel="stylesheet" href="assets/paper.css">
</head>
<body>
'''

# ══════════════════════════════════════════════════════════════════════════════
#  THE DOCUMENT
#
#  Every block below is traceable to the source paper. Where the source hedges,
#  this paper hedges in the same place and in the same direction: a capability
#  the source calls potential is marked PROPOSED here and is never written as
#  though it were delivered. Nothing is asserted about any external vendor's
#  pricing, licensing or terms, because the source asserts nothing about them.
#
#  Two glyphs the Latin cut on this stationery does not carry are deliberately
#  absent from the copy: the approximation sign and the arrow. "Approximately"
#  is set as a word, and every flow on the sheet is drawn rather than typed.
# ══════════════════════════════════════════════════════════════════════════════
BLOCKS = []

def B(html, keep=False):
    """keep=True binds this block to the one after it, so a section head is
    never orphaned at the foot of a sheet."""
    BLOCKS.append({"html": html.strip(), "keep": keep})

SEC = {"n": 0, "label": ""}
def section(ar, title, run=None):
    """run= a short form for the running head, where the full title would
    crowd the Arabic name across the top of the continuation sheet."""
    SEC["n"] += 1
    SEC["label"] = f'{SEC["n"]:02d} &nbsp;·&nbsp; {run or title}'
    BLOCKS.append({"html": f'''<div class="head" data-sec="{SEC['label']}">
  <div class="rail"><span class="n">SECTION {SEC['n']:02d}</span></div>
  <div class="t">{title}<span class="ar">{ar}</span></div>
</div>'''.strip(), "keep": True})

def P(*paras, cls="blk"):
    B(f'<div class="{cls}">' + "".join(f"<p>{p}</p>" for p in paras) + "</div>")

def note(key, *paras, imp=False):
    k = "note note--imp" if imp else "note"
    B(f'<div class="{k}"><div class="nk">{key}</div>'
      + "".join(f"<p>{p}</p>" for p in paras) + "</div>")

def kicker(text):
    """A standing label belongs to what follows it; on its own at the foot of a
    sheet it is a fault."""
    B(f'<div class="kicker">{text}</div>', keep=True)

def points(items, cls="pts"):
    B(f'<ul class="{cls}">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>")

MK_NOW  = '<span class="mk mk--now">In place · under refinement</span>'
MK_PROP = '<span class="mk mk--prop">Proposed · subject to approval</span>'

def table(heads, rows, full=True, widths=None):
    w = widths or []
    th = "".join(
        f'<th{" class=r" if h.startswith("^") else ""}'
        f'{f" style=width:{w[i]}" if i < len(w) and w[i] else ""}>{h.lstrip("^")}</th>'
        for i, h in enumerate(heads))
    tr = ""
    for r in rows:
        if r and r[0] == "GRP":
            tr += f'<tr class="grp"><td colspan="{len(heads)}">{r[1]}</td></tr>'
            continue
        tr += "<tr>" + "".join(
            f'<td class="{"k" if i == 0 else ""}{" r" if c.startswith("^") else ""}">'
            f'{c.lstrip("^")}</td>' for i, c in enumerate(r)) + "</tr>"
    B(f'<table class="tbl{" full" if full else ""}"><thead><tr>{th}</tr></thead>'
      f'<tbody>{tr}</tbody></table>')

# ── SHEET ONE · the opening statement ───────────────────────────────────────
B('''<div class="lede blk--tight">
  <div class="kicker">EXECUTIVE SYNTHESIS</div>
  <p>Sultan Hanafi Royal Schools is in the course of bringing a substantial part of its
  academic, administrative, communication and student-facing processes into a single
  institutional environment. That environment is referred to throughout this paper as
  the Digital Campus.</p>
  <p>A considerable part of it has already been established. The requirement that remains
  is not principally the creation of further pages or features: it is the integration,
  refinement, hardening and operational stabilisation of the services through which the
  school will hold its records and run its workflows, credentials and communication.</p>
  <p>Two legitimate routes remain open for completing it. This paper sets out both, with
  the derivation of every figure shown, so that the decision can be taken on the
  institution&rsquo;s own grounds.</p>
</div>''')

B('''<div class="summary full">
  <div class="row">
    <div class="l"><div class="t">Route 1 &nbsp;·&nbsp; Third-party platforms</div>
      <div class="d">Acquisition and integration of selected external services.</div></div>
    <div class="a"><span class="fig fig--lg">$4,148</span>
      <span class="q">Indicative aggregate</span></div>
  </div>
  <div class="row">
    <div class="l"><div class="t">Route 2 &nbsp;·&nbsp; Continued in-house development</div>
      <div class="d">220 to 250 engineering sessions at $25, $30 and $35, by character of work.</div></div>
    <div class="a"><span class="fig fig--lg">$5,500 &ndash; $8,750</span>
      <span class="q">Planning envelope</span></div>
  </div>
</div>''')

# ── 01 ──────────────────────────────────────────────────────────────────────
section("كيف تُقرأ هذه الورقة", "How this paper is to be read")
B('''<div class="conv">
  <div class="d"><span class="k">Status</span>
    <p>Two marks are used throughout. <b>In place &middot; under refinement</b> means
    established on the existing platform, in use or in active refinement.
    <b>Proposed &middot; subject to approval</b> means a capability direction the platform
    is designed to admit, which has not been implemented and is not asserted to exist.
    A row carrying no mark is descriptive. This paper does not assert that any individual
    item is complete.</p></div>
  <div class="d"><span class="k">Figures</span>
    <p>Every figure appears with the arithmetic that produces it. The range in Section 08
    is a planning envelope, not an invoice, and not an assertion that every session within
    it will be required. Amounts are in United States dollars.</p></div>
  <div class="d"><span class="k">Basis</span>
    <p>The rates are structured around the direct operational and engineering requirement
    associated with the remaining work &mdash; its nature, complexity and technical intensity
    &mdash; rather than introducing a separate margin into the stated figures. Section 08
    shows the derivation in full; Section 14 sets out what is recharged on actual usage and
    what is not.</p></div>
  <div class="d"><span class="k">Decision</span>
    <p>Nothing in this paper commits the school to either route, and neither route is
    recommended in preference to the other. Section 15 states the position.</p></div>
</div>''')

# ── 02 ──────────────────────────────────────────────────────────────────────
section("الحرم الرقمي كطبقة مؤسسية", "The Digital Campus as an institutional layer",
        run="The Digital Campus as a layer")
P("The term is used here in a specific sense. It does not mean a collection of digital "
  "tools each performing one task. It means a single institutional layer in which the "
  "school&rsquo;s records, workflows and services resolve against one authoritative source.",
  "The practical consequence is that a student exists once. The same record carries "
  "enrolment, academic progress, results, credentials and correspondence history. A result "
  "approved in the academic workflow is the result a certificate is generated from, and the "
  "result a verification enquiry resolves against. An announcement issued to a class is "
  "addressed to the roll the academic workflow already maintains.",
  "This is why the engineering effort described below accumulates rather than dissipates. "
  "Work on the credential layer did not have to re-establish who the students are; work on "
  "communication did not have to re-establish which classes exist. Each completed component "
  "becomes part of the ground the next one stands on &mdash; and it is also why the work "
  "that remains is weighted toward integration and stabilisation rather than toward new "
  "features.", cls="blk--tight")

B('''<div class="full"><div class="track">
  <div class="st"><span>Student record</span></div>
  <div class="st"><span>Academic workflow</span></div>
  <div class="st"><span>Result</span></div>
  <div class="st"><span>Certificate</span></div>
  <div class="st"><span>Verification</span></div>
  <div class="st"><span>Communication</span></div>
  <div class="st"><span>Student &amp; parent access</span></div>
  <div class="st"><span>Administrative record</span></div>
</div>
<div class="track-key">The connected chain the platform is being built to carry. Each
station is the same institutional record at a further stage, not a separate system holding
its own copy of it. Not every station is operational; Section 11 states the position of each.</div></div>''')

table(["Institutional area", "What it covers", "Status"],
 [["Academic and administrative workflows",
   "Structured digital processes for selected institutional operations.", MK_NOW],
  ["Credential infrastructure",
   "Certificate generation, unique references and verification-oriented workflows.", MK_NOW],
  ["Communication infrastructure",
   "A central communication layer able to support role-based and targeted institutional "
   "communication.", MK_NOW],
  ["Management visibility",
   "Structured dashboards and operational views intended to improve institutional awareness.", MK_NOW],
  ["Shared Digital Campus foundation",
   "The common environment within which further institutional services can be progressively "
   "integrated.", MK_NOW]],
 widths=["46mm", None, "30mm"])

# ── 03 ──────────────────────────────────────────────────────────────────────
section("ما تم إنشاؤه بالفعل", "What has already been established")
P("The current development direction has established a substantial digital foundation. The "
  "architecture matters more than any individual screen: it allows functions that would "
  "otherwise sit in separate systems to be brought progressively into one institutional "
  "environment, which reduces fragmentation and gives any future expansion a defined place "
  "to attach to.",
  "The remaining work is accordingly concerned with bringing critical components to a stable, "
  "integrated and fully operational standard, rather than with establishing the foundation "
  "itself. Two parts of that foundation account for a large share of what the school will "
  "notice in use, and they are set out next, in Sections 04 and 05, before the remaining "
  "engineering requirement is stated.")
note("INSTITUTIONAL PRINCIPLE",
 "The objective is not to add more digital functions. It is to establish, progressively, a "
 "coherent institutional system in which records, workflows, credentials, communication and "
 "selected services operate together under the school&rsquo;s own digital direction.")

# ── 04 ──────────────────────────────────────────────────────────────────────
section("بنية الشهادات", "Credential infrastructure &mdash; the Certificate Generation Room",
        run="The Certificate Generation Room")
P("The Certificate Generation Room is not a page that produces certificates. It is the "
  "credential layer of the Digital Campus: the point at which an institutional record "
  "becomes a formal, referenced and verifiable institutional output, and at which the school "
  "retains its own record of having issued it.",
  "The distinction is administrative rather than technical. A document generator produces a "
  "file. A credential infrastructure produces an <i>issued credential</i> &mdash; carrying a "
  "unique institutional reference, a verification path, and a retained record against which "
  "a later enquiry, whether from a parent, an employer, another institution or the school&rsquo;s "
  "own registry, can be resolved. The second is what allows the school to answer for a "
  "document years after issuing it.",
  "The intended lifecycle runs as follows.", cls="blk--tight")

B('''<ol class="chain full">
  <li><div class="st">Record</div><div class="sd">The student&rsquo;s academic record, held once
    in the Digital Campus rather than re-entered for each document produced from it.</div></li>
  <li><div class="st">Authorisation</div><div class="sd">The result or award is approved within
    the academic workflow. Nothing can be generated from a record that has not been
    authorised.</div></li>
  <li><div class="st">Certificate generation</div><div class="sd">The certificate is produced
    from the authorised record, so the document and the record cannot diverge.</div></li>
  <li><div class="st">Unique reference</div><div class="sd">Each issued credential carries an
    institutional reference, with a QR link to it where that has been implemented.</div></li>
  <li><div class="st">Verification</div><div class="sd">The reference resolves against the
    issuing record rather than against the document presented &mdash; which is what makes a
    reply authoritative instead of a comparison between two pieces of paper.</div></li>
  <li><div class="st">Validation</div><div class="sd">An authorised or public check can confirm
    that the credential was issued by the school and remains current.</div></li>
  <li><div class="st">Permanent record</div><div class="sd">The issue is retained
    institutionally. This is the step that makes controlled re-issuance possible, as distinct
    from simply printing the document again.</div></li>
</ol>''')

kicker("POTENTIAL EXTENSIONS &nbsp;·&nbsp; SUBJECT TO APPROVAL AND IMPLEMENTATION")
points([
 "<b>Duplicate certificate requests</b> and controlled re-issuance workflows, resolved against "
 "the retained record of issue.",
 "<b>Credential verification services</b> for external parties enquiring about a document "
 "presented to them.",
 "<b>Transcript and academic-record requests</b> for selected records.",
 "<b>Public or authorised verification pages</b>, according to what the school decides may be "
 "confirmed openly and what requires authorisation.",
 "<b>Additional credential types</b> as the institution&rsquo;s requirements expand."])
note("IMPORTANT DISTINCTION",
 "The credential infrastructure described here is an institutional capability that can be "
 "expanded progressively. The availability of any particular automated or chargeable service "
 "within it would depend on its subsequent implementation and on the school&rsquo;s approved "
 "administrative arrangements. Nothing in this section asserts that an extension listed above "
 "is in operation.")

# ── 05 ──────────────────────────────────────────────────────────────────────
section("قناة الاتصال المؤسسي", "The Communication Channel")
P("The Communication Channel is likewise not a chat feature. It is intended as the "
  "institution&rsquo;s communication layer: one place through which the school addresses its "
  "constituencies, with the addressing done by institutional role rather than by maintaining "
  "a separate contact list for every relationship.",
  "Its significance is that communication resolves against the same records as everything "
  "else. A notice to a class, a result notification to a parent, a staff circular and an "
  "administrative reply are all addressed from the institutional roll, and all leave a "
  "retained communication history. The communication layer itself is established and under "
  "refinement; the operating scope below is the direction it is designed to admit, item by "
  "item, as each is implemented and approved.", cls="blk--tight")

table(["Operating scope", "Institutional purpose", "Status"],
 [["Administration to student",
   "Direct institutional communication addressed from the student roll.", MK_PROP],
  ["Administration to parent or guardian",
   "Communication with the authorised adult recorded against the student.", MK_PROP],
  ["Management and staff",
   "Internal circulation to management and to academic and administrative staff.", MK_PROP],
  ["Targeted announcements",
   "Communication addressed to a defined group &mdash; a class, a year, a programme, a "
   "staff function &mdash; rather than to everyone.", MK_PROP]],
 widths=["44mm", None, "30mm"])
table(["Operating scope (continued)", "Institutional purpose", "Status"],
 [
  ["Institutional notices",
   "Controlled distribution of formal notices, with the distribution itself recorded.", MK_PROP],
  ["Role-based access",
   "What a user may send, and to whom, determined by their institutional role.", MK_PROP],
  ["Communication history",
   "A retained record of what was sent, to whom and when, available to authorised users.", MK_PROP],
  ["Integration with other workflows",
   "Communication raised by an academic or administrative process rather than composed "
   "separately from it.", MK_PROP]],
 widths=["44mm", None, "30mm"])

# ── 06 ──────────────────────────────────────────────────────────────────────
section("ما بقي من العمل الهندسي", "The remaining engineering requirement")
P("The remaining work is expected to centre on nine areas. None of them is the creation of a "
  "new subsystem. All of them are the work of making existing subsystems correct, connected, "
  "secure and operationally dependable &mdash; which is the part of a platform&rsquo;s "
  "development that is least visible from outside it and most consequential in use.")
table(["Engineering area", "What the work consists of"],
 [["System and service integration",
   "Connecting the relevant Digital Campus components so that they resolve against one "
   "another rather than operating in parallel."],
  ["MCP configuration and engineering",
   "Configuration and engineering of the model-context tooling used within the development "
   "workflow, where the work requires it."],
  ["Certificate and verification workflows",
   "Refinement and operational validation of the credential lifecycle set out in Section 04."],
  ["Communication infrastructure",
   "Refinement of the communication layer, and its integration with institutional roles and "
   "workflows."],
  ["Database and workflow refinement",
   "Improving the consistency and operational reliability of the stored records and of the "
   "processes that act on them."],
  ["Permissions and access control",
   "Defining and enforcing what each institutional role may see and may do, across the "
   "relevant services."]],
 widths=["50mm", None])
table(["Engineering area (continued)", "What the work consists of"],
 [
  ["Security hardening and validation",
   "Hardening, testing and validation to bring the platform to a production-ready standard."],
  ["Performance and difficult debugging",
   "Performance optimisation, and the diagnosis of faults that cross more than one component."],
  ["Deployment and documentation",
   "Deployment, documentation and final operational refinement."]],
 widths=["50mm", None])

# ── 07 ──────────────────────────────────────────────────────────────────────
section("جلسة العمل الهندسي", "The engineering session, and why the rates differ",
        run="The engineering session")
P("For the remaining work, effort is expressed in engineering sessions rather than in billed "
  "hours. The reason is practical. The work listed in Section 06 is not uniform: an afternoon "
  "spent tracing a permissions fault across three components and an afternoon spent writing "
  "documentation are both an afternoon, and they are not the same piece of engineering. An "
  "hourly unit records the duration and discards the distinction.",
  "An engineering session is a defined unit of engineering workload within the continuing "
  "development cycle. In practice a session typically occupies about 60 to 120 minutes of "
  "continuous work, the longer figure where the task involves integration, configuration, "
  "debugging, testing or operational refinement that cannot sensibly be interrupted part-way. "
  "A single session may combine implementation, integration, configuration, debugging, "
  "testing, validation, security refinement, deployment preparation, documentation and "
  "operational stabilisation. What makes it one session is that it completes one unit of "
  "work &mdash; not that it occupies one hour.",
  "The rate is then set by the character of the work rather than by its duration. Three rates "
  "are used.", cls="blk--tight")

table(["^Rate", "Engineering character", "Typical work at this rate"],
 [['^<span class="fig">$25</span>', "Standard engineering",
   "Routine configuration; standard integration; database and workflow refinement; "
   "documentation; straightforward testing."],
  ['^<span class="fig">$30</span>', "Intermediate engineering",
   "Multi-system integration; permissions and workflow logic; debugging; validation; "
   "cross-component refinement."],
  ['^<span class="fig">$35</span>', "Advanced and critical engineering",
   "Complex integration; security hardening; production configuration; performance "
   "optimisation; difficult debugging; stabilisation of critical workflows."]],
 widths=["16mm", "40mm", None])
note("RATE BASIS",
 "The $25, $30 and $35 structure is the engineering service rate applicable to this project. "
 "It is not an official Anthropic, MCP or external vendor tariff, and no external vendor&rsquo;s "
 "pricing is asserted anywhere in this paper. What underlying operational resources are "
 "consumed during the work, and how they are treated, is a separate matter and is set out in "
 "Section 14.")

# ── 08 ──────────────────────────────────────────────────────────────────────
section("كيف استُخلص التقدير", "How the estimate is derived")
P("The estimate has two inputs and no others: the volume of sessions that remain, and the mix "
  "of rates across them. Both are stated below, and the arithmetic is shown in full so that "
  "the range can be checked rather than accepted.",
  "The remaining volume is assessed at approximately 220 to 250 sessions across the nine "
  "areas in Section 06. Multiplying each volume by each rate gives the following, in United "
  "States dollars.", cls="blk--tight")

B('''<div class="full"><table class="mtx">
  <thead><tr>
    <th class="c">Sessions</th>
    <th>$25<span class="s">Standard</span></th>
    <th>$30<span class="s">Intermediate</span></th>
    <th>$35<span class="s">Advanced</span></th>
  </tr></thead>
  <tbody>
    <tr><td class="c">220 sessions</td><td class="x">$5,500</td><td>$6,600</td><td>$7,700</td></tr>
    <tr><td class="c">235 sessions</td><td>$5,875</td><td>$7,050</td><td>$8,225</td></tr>
    <tr><td class="c">250 sessions</td><td>$6,250</td><td>$7,500</td><td class="x">$8,750</td></tr>
  </tbody>
</table>
<div class="mtx-key">The planning envelope runs between the two figures set in weight:
220 &times; $25 = $5,500 at one corner, and 250 &times; $35 = $8,750 at the other. The middle
row is the arithmetic midpoint of the volume, shown so that the interior of the range is
visible and not merely implied.</div></div>''')

P("Those two corners are the arithmetic extremes, and neither is expected. $5,500 assumes "
  "that 220 sessions prove sufficient <i>and</i> that every one of them is standard work; "
  "$8,750 assumes 250 sessions of which every one is advanced or critical. Section 06 "
  "contains both documentation and security hardening, so the mix will fall between them.",
  "To show what a realistic middle looks like without presenting it as a forecast:")
B('''<div class="work full">
  <div class="e">235 sessions &nbsp;·&nbsp; 50% standard, 30% intermediate, 20% advanced<br>
  (0.50 &times; $25) + (0.30 &times; $30) + (0.20 &times; $35) = $28.50 per session<br>
  235 &times; $28.50 = <span class="fig">$6,697.50</span></div>
  <div class="c">ILLUSTRATIVE ONLY &nbsp;·&nbsp; NOT A FORECAST AND NOT A QUOTED FIGURE</div>
</div>''')
note("COST CONTROL",
 "The range is a transparent planning envelope, not an assertion that every session within it "
 "will be required. Allocation should follow the work actually undertaken, at the rate "
 "applicable to its character; the blended figure above is shown to make the interior of the "
 "range legible, not to propose a price.")

# ── 09 ──────────────────────────────────────────────────────────────────────
section("مسارا التنفيذ", "The two implementation routes")
P("The school can reach the required capability through external platforms, through continued "
  "in-house development, or through a selected combination of the two. Both routes are "
  "legitimate. They differ less in what the school will be able to do next year than in what "
  "the school owns at the end of it.")
table(["Implementation route", "Basis", "^Estimated cost"],
 [["Route 1 &mdash; Third-party platforms",
   "External platforms and services providing selected capabilities, integrated into the "
   "Digital Campus.",
   '^<span class="fig">$4,148</span><br><span class="mk mk--prop" style="text-align:right">'
   'Indicative</span>'],
  ["Route 2 &mdash; Continued in-house development",
   "Remaining engineering sessions: configuration, integration, testing, hardening and "
   "operational refinement.",
   '^<span class="fig">$5,500 &ndash; $8,750</span><br>'
   '<span class="mk mk--prop" style="text-align:right">Planning envelope</span>']],
 widths=["48mm", None, "34mm"])

note("READING THE TWO FIGURES",
 "The two amounts are not the same kind of figure and should not be read as a straight price "
 "comparison. The approximately $4,148 under Route 1 is an aggregate for acquiring and "
 "integrating external services; whether and how often it recurs depends on the licensing "
 "basis of each service selected, which this paper does not assert and which would need to be "
 "established from the providers&rsquo; own terms. The $5,500 to $8,750 under Route 2 is a "
 "one-time engineering allocation, at the end of which the capability is held by the school. "
 "A comparison over more than a single year would require the licensing terms of the specific "
 "products in hand.")

B('''<div class="routes full">
  <div class="route">
    <div class="rn">Route 1</div>
    <div class="rt">Third-party platforms</div>
    <span class="rf">Approximately $4,148</span>
    <div class="sh">Considerations in favour</div>
    <ul>
      <li>Established functionality is available without every underlying service having to
        be built.</li>
      <li>Adoption can be quicker where a mature product closely matches the requirement.</li>
      <li>The internal development requirement is correspondingly reduced.</li>
      <li>Maintenance and support of the acquired capability rest with the provider.</li>
    </ul>
    <div class="sh sh--w">Considerations to weigh</div>
    <ul>
      <li>The school remains dependent on the provider for that capability.</li>
      <li>Licensing, subscription and renewal terms continue to apply.</li>
      <li>Feature direction is set by the provider rather than by the school.</li>
      <li>Integration is constrained to what the product exposes.</li>
      <li>Control over the direction of future development is correspondingly reduced.</li>
    </ul>
  </div>
  <div class="route">
    <div class="rn">Route 2</div>
    <div class="rt">Continued in-house development</div>
    <span class="rf">$5,500 &ndash; $8,750</span>
    <div class="sh">Considerations in favour</div>
    <ul>
      <li><b>Ownership.</b> The resulting platform is held by the school.</li>
      <li><b>Integration.</b> New services are designed against records the school already
        holds, rather than alongside them.</li>
      <li><b>School-specific workflows.</b> The institution&rsquo;s own processes can be
        accommodated as they are.</li>
      <li><b>Customisation.</b> Requirements for which no external product is an exact fit can
        be met directly.</li>
      <li><b>Extensibility.</b> Later capabilities build on the same foundation.</li>
      <li><b>Consolidation.</b> Separate processes can be brought progressively into one
        environment.</li>
      <li><b>Control.</b> The direction of future development remains with the institution.</li>
      <li><b>Continuity.</b> Institutional rules and workflows are represented in the platform
        rather than in disconnected tools.</li>
    </ul>
    <div class="sh sh--w">Considerations to weigh</div>
    <ul>
      <li>The engineering work has to be performed, and it is the larger of the two figures.</li>
      <li>Delivery depends on continuing engineering capacity being available.</li>
      <li>The school carries responsibility for the maintenance and operational continuity of
        what it owns.</li>
      <li>Capability arrives as the work is completed rather than on acquisition.</li>
    </ul>
  </div>
</div>''')
# ── 10 ──────────────────────────────────────────────────────────────────────
section("ما يتركه الإنفاق بعده", "What the expenditure leaves behind")
P("The principal distinction between the routes is not the amount spent. It is what the "
  "expenditure leaves behind as institutional capability.",
  "Under continued in-house development the school accumulates an integrated digital asset "
  "shaped around its own operating structure. Each completed component can become part of the "
  "foundation for the next, which allows the value of earlier engineering to extend forward "
  "rather than being spent once. The alternative to that property is not cheaper work; it is "
  "the repeated acquisition of disconnected solutions, each of which has to be integrated "
  "again against records it did not originate.")
table(["Value area", "Institutional significance"],
 [["Institutional ownership",
   "The school&rsquo;s digital environment remains aligned with its own workflows and its own "
   "development direction."],
  ["Deeper integration",
   "New services are designed around the existing Digital Campus rather than operating as "
   "isolated products beside it."],
  ["Customisation",
   "Institution-specific requirements can be incorporated where an external product would not "
   "be an exact fit."],
  ["Extensibility",
   "The platform becomes a base for further academic, administrative and student-facing "
   "services."],
  ["Progressive consolidation",
   "Separate processes can be brought gradually into a more coherent institutional "
   "environment."],
  ["Institutional continuity",
   "School-specific rules, structures and workflows are reflected in the platform rather than "
   "remaining dependent on disconnected tools or on individual working practice."]],
 widths=["44mm", None])

B('''<div class="nest full">
  <div class="lay">
    <span class="lk">Extensions</span>
    <div class="lv">Verification &nbsp;·&nbsp; Document and record requests &nbsp;·&nbsp;
      Specialised digital services &nbsp;·&nbsp; Future integrations</div>
    <div class="lay">
      <span class="lk">Services</span>
      <div class="lv">Student &nbsp;·&nbsp; Parent and guardian &nbsp;·&nbsp; Staff
        &nbsp;·&nbsp; Admissions &nbsp;·&nbsp; Online programmes</div>
      <div class="lay">
        <span class="lk">Workflows</span>
        <div class="lv">Academic &nbsp;·&nbsp; Administration &nbsp;·&nbsp; Credentials
          &nbsp;·&nbsp; Communication</div>
        <div class="lay lay--core">
          <span class="lk">Core</span>
          <div class="lv">Institutional records and identity</div>
        </div>
      </div>
    </div>
  </div>
</div>''')
P("The model is not aspirational architecture. It is a statement of <i>where a new service "
  "attaches</i>: at the services or extensions layer, against records and workflows that "
  "already exist. That is the whole practical difference between extending a platform and "
  "procuring another one.")

# ── 11 ──────────────────────────────────────────────────────────────────────
section("ما تحصل عليه المدرسة", "What the school obtains, by area")
P("The following is a structured view of what the Digital Campus can support as development "
  "continues, set out by institutional area. The marks distinguish what is established or "
  "under refinement from what is a capability direction. These are capability directions, not "
  "claims that every item is already operational.")
B('''<div class="legend full">
  <div class="i">''' + MK_NOW + '''<div class="d">Established on the existing platform, in use
    or in active refinement.</div></div>
  <div class="i">''' + MK_PROP + '''<div class="d">A direction the platform is designed to
    admit; not implemented, and not asserted to exist.</div></div>
</div>''')
REG_HEAD = ["Area", "What it covers", "Status"]
REG_W    = ["44mm", None, "30mm"]
table(REG_HEAD,
 [["GRP", "Academic"],
  ["Student records", "The authoritative record of each student, held once.", MK_NOW],
  ["Academic workflows", "Structured digital processes for selected academic operations.", MK_NOW],
  ["Results", "Result entry, approval and selected result and document services.", MK_NOW],
  ["Attendance", "Attendance capture against the academic roll.", MK_PROP],
  ["Progression", "Progression tracking between stages and programmes.", MK_PROP],
  ["Academic reporting", "Structured reporting drawn from the academic records.", MK_PROP]],
 widths=REG_W)
table(REG_HEAD,
 [["GRP", "Administration"],
  ["Document management", "Institutional documents held and retrievable within the platform.", MK_NOW],
  ["Permissions", "Role-based access control across the relevant institutional roles.", MK_NOW],
  ["Administrative processes", "Selected administrative operations carried as digital workflows.", MK_NOW],
  ["Admissions and applications", "Digital application and admission processes.", MK_PROP],
  ["Staff workflows", "Structured processes for staff-facing administrative work.", MK_PROP]],
 widths=REG_W)
table(REG_HEAD,
 [["GRP", "Credentials"],
  ["Certificate generation", "Certificates produced from the authorised record.", MK_NOW],
  ["Unique references", "An institutional reference carried by each issued credential.", MK_NOW],
  ["Verification and validation", "Resolution of a reference against the issuing record.", MK_NOW],
  ["Credential records", "A retained institutional record of what has been issued.", MK_PROP],
  ["Document requests", "Requests for duplicates, transcripts and selected records.", MK_PROP],
  ["Controlled re-issuance", "Re-issuance resolved against the retained record of issue.", MK_PROP],
  ["External verification", "Confirmation to an external party of a credential presented to it.", MK_PROP]],
 widths=REG_W)
table(REG_HEAD,
 [["GRP", "Communication"],
  ["Communication layer", "A central layer addressing users by institutional role.", MK_NOW],
  ["Students, parents, staff", "Communication with each constituency from the institutional roll.", MK_PROP],
  ["Targeted communication", "Addressing a defined group rather than the whole institution.", MK_PROP],
  ["Communication history", "A retained record of institutional communication.", MK_PROP]],
 widths=REG_W)
table(REG_HEAD,
 [["GRP", "Management"],
  ["Dashboards and views", "Operational views intended to improve institutional awareness.", MK_NOW],
  ["Operational indicators", "Indicators drawn from the operating records themselves.", MK_PROP],
  ["Structured reporting", "Reporting for institutional oversight across selected areas.", MK_PROP]],
 widths=REG_W)
table(REG_HEAD,
 [["GRP", "Student services"],
  ["Student profiles", "A student-facing view of the record the institution holds.", MK_PROP],
  ["Authorised parent access", "Access for the authorised adult recorded against the student.", MK_PROP],
  ["Service requests", "Requests for documents and selected institutional services.", MK_PROP]],
 widths=REG_W)
table(REG_HEAD,
 [["GRP", "Online and distance education"],
  ["Programme foundation", "A foundation for selected online programmes and learning services.", MK_PROP],
  ["Digital academic delivery", "Delivery and administration of selected programmes digitally.", MK_PROP],
  ["GRP", "Institutional service layer"],
  ["Common environment", "The shared environment through which further school-specific "
   "services can be introduced progressively.", MK_NOW]],
 widths=REG_W)

# ── 12 ──────────────────────────────────────────────────────────────────────
section("ما يتغير عمليًّا", "What changes in practice")
P("The benefits below are stated as consequences rather than as qualities. Each is a change "
  "in how a specific piece of institutional work is done, and each is traceable to a part of "
  "the architecture described above.")
kicker("DIRECT CONSEQUENCES")
points([
 "A result approved once does not have to be re-entered to produce a certificate, and does "
 "not have to be looked up again to answer a verification enquiry. The three are the same "
 "record at three stages.",
 "A credential enquiry is answered from the issuing record rather than from the document "
 "presented, which is what makes the reply authoritative rather than a comparison between two "
 "pieces of paper.",
 "A notice addressed to a class is addressed to the roll the academic workflow already "
 "maintains, so no separate distribution list has to be kept current alongside it.",
 "A request for a duplicate document resolves against a retained record of issue, which is "
 "what allows re-issuance to be <i>controlled</i> rather than simply repeated "
 "<i>(proposed &middot; subject to approval)</i>.",
 "Records that were retrievable only by the person who filed them become retrievable by any "
 "authorised user, within the permissions set for their role.",
 "Management views are drawn from the operating records themselves rather than compiled "
 "separately, so they report the position rather than a summary of it.",
 "The same foundation carries additional programmes, services or user groups without a second "
 "environment having to be established beside it."])
kicker("INDIRECT AND LONGER-TERM CONSEQUENCES")
points([
 "Fewer disconnected processes make the institutional environment easier to administer and "
 "easier to hand over &mdash; which matters at a change of staff more than at any other time.",
 "School-specific rules and structures become represented in the platform as development "
 "continues, rather than residing in the working practice of particular individuals.",
 "A new operational requirement can be met by extending an existing foundation rather than by "
 "procuring and integrating a further system.",
 "Services can be added progressively without the environment having to be rebuilt around them.",
 "The accumulated platform is capability that can continue to be developed, rather than a "
 "purchased function of fixed scope."], cls="pts pts--sapphire")

# ── 13 ──────────────────────────────────────────────────────────────────────
section("الاستدامة التشغيلية", "Operational sustainability and controlled service recharge",
        run="Operational sustainability")
P("A connected Digital Campus can, subject to institutional approval and to appropriate "
  "financial arrangements, support selected service-based mechanisms that contribute toward "
  "its continuing operational requirements. The point is not that services should be "
  "monetised. It is that the platform provides a technically controlled and administratively "
  "auditable way to structure a charge where the institution decides that one is appropriate.",
  "One such mechanism would be controlled digital service access. A controlled digital "
  "service-access mechanism may, subject to institutional approval, be structured around "
  "modest service recharges for selected services: a student or an authorised parent or "
  "guardian could load a designated recharge amount in order to obtain a specified service, "
  "with the corresponding funds credited directly to the school&rsquo;s designated account "
  "under its approved administrative and financial structure.")
note("IMPORTANT", 
 "This is a potential service model. It is not a statement that every student must pay to "
 "view results, and it is not proposed as a condition of access to academic information. "
 "Whether to implement such a mechanism at all, which services it would apply to, the "
 "amounts, the eligibility, the exemptions, the financial treatment and the administrative "
 "controls would each be matters for the institution to determine and approve.", imp=True)
kicker("SERVICES THAT COULD, WHERE APPROVED, BE STRUCTURED IN THIS WAY")
points([
 "Result-access services for a specified result or digital result statement.",
 "Duplicate certificate and duplicate document requests.",
 "Credential verification services for external parties.",
 "Transcript and selected academic-record requests.",
 "Selected application and administrative services.",
 "Online programme and specialised digital academic access.",
 "Examination-related digital services.",
 "Other digital services as the institution may approve."])
P("The strategic significance is narrow, and worth stating plainly rather than overstating. "
  "Where the institution approves such arrangements, selected service activity could "
  "contribute toward the platform&rsquo;s own maintenance, development and future expansion. "
  "A platform that meets part of its recurring operational requirement from the services it "
  "provides is a different financial proposition from one that does not &mdash; but only to "
  "the extent, and in the form, that the institution chooses to implement.")

# ── 14 ──────────────────────────────────────────────────────────────────────
section("أساس الاستهلاك التشغيلي", "Operational usage and the resource basis")
P("Two things are measured separately in this paper, and conflating them is the commonest way "
  "a costing of this kind becomes unreadable.",
  "<b>The engineering session is the workload unit.</b> It expresses the engineering effort "
  "&mdash; implementation, integration, configuration, debugging, testing, validation, "
  "security refinement, deployment preparation, documentation and operational stabilisation "
  "&mdash; and it is what the rates in Section 07 are applied to.",
  "<b>The underlying operational resources are a separate matter.</b> Developing, integrating "
  "and testing a platform of this kind consumes real service and tooling resources during the "
  "work itself. Those are consumed according to what the work actually requires and are "
  "recharged on the basis of actual usage. They are not estimated inside the session rate, "
  "and no margin is applied to them. The session rate does not stand in for them, and they do "
  "not vary with it.",
  "This is why the costing considers more than the visible implementation tasks. The "
  "engineering activity required to configure, test, refine and stabilise a system is the "
  "larger part of bringing it to an operational standard, and the session is a practical unit "
  "for representing that continuing workload while keeping the figure tied to the character "
  "of the work rather than to the clock.")

# ── 15 ──────────────────────────────────────────────────────────────────────
section("الموقف الإداري", "Administrative position")
P("Both implementation routes remain available, and this paper does not recommend one over the "
  "other. Third-party integration can introduce established capabilities into the Digital "
  "Campus under a defined external product relationship, and may be the appropriate direction "
  "where the school prefers an existing service, where speed of adoption matters, or where a "
  "capability would be disproportionate to build internally.",
  "Continued in-house development directs the remaining expenditure into a platform the "
  "school holds, and its value accumulates through the platform itself: each completed "
  "component can become part of the foundation for the next. Where the facts support "
  "additional institutional value from that route &mdash; ownership, depth of integration, "
  "customisation, extensibility, continuity and control of future direction &mdash; this "
  "paper has set it out, in Sections 09 and 10, together with what the route requires in "
  "return.",
  "The appropriate direction remains an administrative decision for Sultan Hanafi Royal "
  "Schools, taking into account its priorities, its existing arrangements, its preferred "
  "operating model, its technical requirements and its longer-term institutional objectives.")
note("COMPLETION AND OPERATIONAL MATURITY",
 "The objective of the continuing work is to bring the existing infrastructure to a stable, "
 "integrated and fully operational standard, with the principal components working together "
 "as part of the Digital Campus. The final allocation may be settled within the stated range "
 "according to the actual volume of remaining engineering work and the rate applicable to its "
 "character.")

B(f'''<div class="sign">
  <div class="s1">
    <div class="sp"><img src="{AT}/signature-imam.png"
         alt="Signature of Imam Ahmad Ibrohim Sulaimiy"></div>
    <div class="rule gold-block"></div>
    <div class="nm">Imam Ahmad Ibrohim Sulaimiy</div>
    <div class="ar">الإمام أحمد بن إبراهيم السليمي (آل سلام)</div>
    <div class="ro">For: Digital Transformation &amp; ICT<br>Sultan Hanafi Royal Schools</div>
  </div>
  <div class="s2">
    <div class="rule--f"></div>
    <div class="ro">For institutional approval</div>
    <div class="bl"><i></i>Name and designation<i></i>Date</div>
  </div>
</div>''')

# ══════════════════════════════════════════════════════════════════════════════
#  PASS 1 · THE GALLEY, and PASS 2 · THE MEASUREMENT
#
#  The galley is the whole document in one 138mm column with no sheet around
#  it. Chromium renders it, a script writes each block's top and bottom back
#  into the DOM, and --dump-dom hands the numbers to this script. Advance is
#  taken as the distance between successive block tops, so collapsed margins
#  are measured rather than modelled.
# ══════════════════════════════════════════════════════════════════════════════
GALLEY_JS = '''
<script>
// MEASURE AFTER THE FACES ARE APPLIED, NOT AFTER THE DOM IS PARSED. Every face
// on this stationery is an embedded WOFF2 with font-display:block, so a script
// that runs at parse time measures the fallback and reports heights that are
// wrong by centimetres over a long document. document.fonts.ready is the only
// correct moment, and virtual time lets it settle before --dump-dom reads back.
document.fonts.ready.then(function(){
  var g = document.getElementById('g'), k = g.children, out = [];
  for (var i = 0; i < k.length; i++){
    var r = k[i].getBoundingClientRect();
    out.push([Math.round(r.top*100)/100, Math.round(r.bottom*100)/100]);
  }
  var pre = document.createElement('pre');
  pre.id = 'measurements';
  pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
});
</script>
'''

def write_galley(path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEAD.format(title="galley — measurement only", at=AT))
        f.write('<div style="padding:20mm;background:#FBF9F5">\n')
        f.write('<div class="paper galley" id="g">\n')
        for b in BLOCKS:
            f.write(b["html"] + "\n")
        f.write('</div>\n</div>\n')
        f.write(GALLEY_JS)
        f.write("</body>\n</html>\n")

def measure(galley_path):
    if not SHELL:
        raise SystemExit("no chrome-headless-shell found — cannot measure the galley")
    out = subprocess.run(
        [SHELL, "--disable-gpu", "--no-sandbox",
         "--virtual-time-budget=12000", "--run-all-compositor-stages-before-draw",
         "--dump-dom", "file://" + os.path.abspath(galley_path)],
        capture_output=True, text=True, timeout=180).stdout
    m = re.search(r'<pre id="measurements">(.*?)</pre>', out, re.S)
    if not m:
        raise SystemExit("the galley did not report measurements — check the render")
    rects = json.loads(m.group(1))
    if len(rects) != len(BLOCKS):
        raise SystemExit(f"measured {len(rects)} blocks, expected {len(BLOCKS)}")
    for i, b in enumerate(BLOCKS):
        b["h"] = rects[i][1] - rects[i][0]
        b["adv"] = (rects[i+1][0] - rects[i][0]) if i + 1 < len(rects) else b["h"]
    return BLOCKS

# ══════════════════════════════════════════════════════════════════════════════
#  PASS 3 · THE IMPRESSION
#
#  Sheet one opens at 152mm, clear of the register, and closes at 25mm: 120mm
#  field. Every sheet after it opens at 44mm, 8mm clear of the continuation
#  rule, and closes at the same place: 229mm. A block is placed if its own
#  height fits; the sheet then advances by the block's advance, so the trailing
#  margin of a sheet's last block costs nothing.
# ══════════════════════════════════════════════════════════════════════════════
CAP_FIRST = (297 - 152 - 25) * MM
CAP_CONT  = (297 -  43 - 25) * MM

def paginate():
    sheets, cur, y = [], [], 0.0
    cap = CAP_FIRST
    i = 0
    while i < len(BLOCKS):
        b = BLOCKS[i]
        need = b["h"]
        if b["keep"] and i + 1 < len(BLOCKS):           # a head and its first block
            need = b["adv"] + BLOCKS[i+1]["h"]
        if cur and y + need > cap + 0.5:
            sheets.append(cur); cur, y, cap = [], 0.0, CAP_CONT
            continue
        if not cur and need > cap + 0.5:
            raise SystemExit(f"block {i} is {need/MM:.1f}mm and will not fit a "
                             f"{cap/MM:.0f}mm field — split it in the source")
        cur.append(b); y += b["adv"]; i += 1
    if cur:
        sheets.append(cur)
    return sheets

def heads_in(blocks):
    """Every section label that begins on this sheet, in order."""
    return [m.group(1) for m in
            (re.search(r'data-sec="([^"]*)"', b["html"]) for b in blocks) if m]

def main():
    # THE GALLEY MUST SIT WHERE THE DOCUMENT SITS. Every stylesheet on this
    # sheet is linked relatively; a galley written into tools/ resolves none of
    # them, renders unstyled, and reports heights that are wrong by a third.
    galley = os.path.join(ROOT, ".galley.html")
    write_galley(galley)
    measure(galley)
    sheets = paginate()
    total = len(sheets)
    os.remove(galley)                 # a measuring instrument, not an artefact

    parts = [HEAD.format(title="Digital Campus — Costing & Implementation Paper", at=AT)]
    carried = ""                      # the section the NEXT sheet opens inside
    for n, blocks in enumerate(sheets, 1):
        fa, fe = folio(n, total)
        running = carried
        hs = heads_in(blocks)
        if hs:
            carried = hs[-1]
        body = "\n".join(b["html"] for b in blocks)
        if n == 1:
            parts.append('<div class="sheet">\n' + plate() + medallion() + head()
                + register() + SECURITY
                + '  <div class="field field--open">\n    <div class="paper">\n'
                + body + '\n    </div>\n  </div>\n'
                + foot(fa, fe) + '\n</div>\n')
        else:
            # the security layers are carried only where there is open ground
            # for them: the final sheet, which closes on the signature
            sec = (SECURITY + WATERMARK) if n == total else ""
            parts.append('<div class="sheet">\n' + cont_head(running or hs[0] if hs else running) + sec
                + '  <div class="field field--paper">\n    <div class="paper">\n'
                + body + '\n    </div>\n  </div>\n'
                + foot(fa, fe) + '\n</div>\n')
    parts.append("</body>\n</html>\n")

    dest = os.path.join(ROOT, "digital-campus-paper.html")
    open(dest, "w", encoding="utf-8").write("\n".join(parts))
    for n, blocks in enumerate(sheets, 1):
        used = sum(b["adv"] for b in blocks) - (blocks[-1]["adv"] - blocks[-1]["h"])
        cap = CAP_FIRST if n == 1 else CAP_CONT
        print(f"  sheet {n:2d}  {len(blocks):2d} blocks  {used/MM:6.1f} / {cap/MM:.0f} mm"
              f"  {used/cap*100:5.1f}%")
        if "--map" in sys.argv:
            for b in blocks:
                t = " ".join(re.sub("<[^>]+>", " ", b["html"]).split())[:62]
                print(f"            {b['h']/MM:6.1f}mm  {t}")
    print(f"\n{len(BLOCKS)} blocks → {total} sheets → {dest}")

    if "--pdf" in sys.argv:
        pdf = os.path.join(ROOT, "print", "digital-campus-paper.pdf")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--virtual-time-budget=20000", "--run-all-compositor-stages-before-draw",
            "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
            "file://" + os.path.abspath(dest)], check=True, capture_output=True, timeout=300)
        print(pdf)

if __name__ == "__main__":
    main()
