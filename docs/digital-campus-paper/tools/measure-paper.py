#!/usr/bin/env python3
"""
Verify the impression. THE SHEET CLIPS AND SAYS NOTHING WHEN IT DOES.

.sheet is 210x297 with overflow:hidden, so a paragraph pushed past the foot
does not warn, does not reflow and does not appear — it simply is not there.
A long paper laid out against a fixed field has to be measured after it is
built, in the document that will actually be printed, or it cannot be trusted.

This checks, for every sheet:

  · the writing field's content does not pass the field's own lower edge;
  · nothing in the field reaches the microtext, the foot rule or the folio;
  · on sheet one, the register closes above the field rather than into it;
  · nothing crosses the binding section at 172mm or leaves the trim.

    python3 tools/measure-paper.py              check digital-campus-paper.html
    python3 tools/measure-paper.py FILE.html
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHELL = next((p for p in (
    "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",
    "/usr/bin/chromium-headless-shell") if os.path.exists(p)), None)

PROBE = '''
<script>
document.fonts.ready.then(function(){
  var MM = 96/25.4, out = [];
  document.querySelectorAll('.sheet').forEach(function(sh, i){
    var s = sh.getBoundingClientRect();
    var mm = function(v){ return Math.round((v - s.top)/MM*10)/10; };
    var mx = function(v){ return Math.round((v - s.left)/MM*10)/10; };
    var f  = sh.querySelector('.field');
    var pr = f ? f.querySelector('.paper') : null;
    var kids = pr ? pr.children : [];
    var last = kids.length ? kids[kids.length-1].getBoundingClientRect() : null;
    var reg  = sh.querySelector('.reg2');
    var over = 0, wide = 0;
    sh.querySelectorAll('.paper > *').forEach(function(e){
      var r = e.getBoundingClientRect();
      if (mm(r.bottom) > 272.1) over++;
      if (mx(r.right) > 162.1 || mx(r.left) < 23.9) wide++;
    });
    out.push({
      sheet: i+1,
      fieldTop:    f ? mm(f.getBoundingClientRect().top)    : null,
      fieldBottom: f ? mm(f.getBoundingClientRect().bottom) : null,
      contentBottom: last ? mm(last.bottom) : null,
      regBottom: reg ? mm(reg.getBoundingClientRect().bottom) : null,
      past: over, wide: wide, blocks: kids.length
    });
  });
  var p = document.createElement('pre'); p.id = 'report';
  p.textContent = JSON.stringify(out); document.body.appendChild(p);
});
</script>
'''

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "digital-campus-paper.html")
    probe = os.path.join(ROOT, ".probe.html")
    html = open(src, encoding="utf-8").read()
    open(probe, "w", encoding="utf-8").write(html.replace("</body>", PROBE + "</body>"))
    out = subprocess.run([SHELL, "--disable-gpu", "--no-sandbox",
        "--virtual-time-budget=20000", "--dump-dom", "file://" + probe],
        capture_output=True, text=True, timeout=300).stdout
    os.remove(probe)
    m = re.search(r'<pre id="report">(.*?)</pre>', out, re.S)
    if not m:
        raise SystemExit("the probe did not report — the document failed to render")
    rows, bad = json.loads(m.group(1)), 0

    print(f"{'sheet':>5} {'field':>14} {'content ends':>13} {'slack':>7}   notes")
    for r in rows:
        slack = (r["fieldBottom"] - r["contentBottom"]) if r["contentBottom"] else None
        n = []
        if r["past"]:  n.append(f"{r['past']} block(s) past the foot"); bad += 1
        if r["wide"]:  n.append(f"{r['wide']} block(s) outside the measure"); bad += 1
        if slack is not None and slack < -0.5:
            n.append(f"overset by {-slack:.1f}mm"); bad += 1
        if r["regBottom"] and r["fieldTop"] and r["regBottom"] > r["fieldTop"] + .1:
            n.append(f"register runs {r['regBottom']-r['fieldTop']:.1f}mm into the field"); bad += 1
        print(f"{r['sheet']:>5} {r['fieldTop']:>6.1f}–{r['fieldBottom']:<7.1f}"
              f"{r['contentBottom']:>13.1f}{slack:>7.1f}   {'; '.join(n) or 'ok'}")

    print()
    if bad:
        print(f"FAIL — {bad} fault(s). The sheet clips silently; fix these before printing.")
        sys.exit(1)
    print(f"ok — {len(rows)} sheets, every field within its own extent.")

if __name__ == "__main__":
    main()
