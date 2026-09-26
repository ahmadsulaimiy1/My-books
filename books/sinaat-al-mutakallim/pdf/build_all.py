#!/usr/bin/env python3
"""Build the series, rebuilding only what changed, then check everything.

Each volume has a fingerprint: the hash of its source files, the series-wide sources it prints (front matter,
the sources base, the registers the indexes read) and every tool under pdf/. A volume is rebuilt only when its
fingerprint differs from the one recorded at its last good build (book/_production/الإخراج/بصمات-البناء.json).
Nothing is skipped on the checking side: the covers are regenerated from the final page counts, and preflight
runs on all eleven volumes every time.

    python3 pdf/build_all.py            build what changed, four at a time, then covers, proofs, preflight
    python3 pdf/build_all.py --all      rebuild every volume regardless of its fingerprint
    python3 pdf/build_all.py --lanes 2  fewer volumes at once
"""
import glob
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOK = ROOT / "book"
sys.path.insert(0, str(HERE))
from volumes import VOLUMES, unit_files  # noqa: E402

FP = BOOK / "_production" / "الإخراج" / "بصمات-البناء.json"
SHARED = [BOOK / "_production" / "المصادر" / "قاعدة-المصادر.tsv", BOOK / "_production" / "التحقيق" / "سجل-الأعلام.tsv",
          BOOK / "_production" / "التحقيق" / "سجل-المصطلحات.tsv", BOOK / "_production" / "الإخراج" / "فواصل-الصفحات.json"]


def fingerprint(n):
    h = hashlib.sha256()
    files = [f for u in VOLUMES[n - 1]["units"] for f in unit_files(n, u)]
    files += sorted((BOOK / f"المجلد-{'الأول'}").rglob("*.md")) if n == 1 else []
    files += sorted(HERE.glob("*.py")) + [f for f in SHARED if f.exists()]
    for f in sorted(set(files)):
        if f.exists():
            h.update(str(f.relative_to(ROOT)).encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def pdf_of(n):
    hits = glob.glob(str(ROOT / f"Volume-{n:02d}_*_Final-Proof.pdf"))
    return hits[0] if hits else None


def build(n):
    for _ in range(3):                        # a stranded heading is recorded and the volume set again
        r = subprocess.run([sys.executable, str(HERE / "volume.py"), str(n)], capture_output=True, text=True)
        if r.returncode:
            return n, False, r.stdout[-400:] + r.stderr[-400:]
        # preflight reports the stranded headings (its cover check may fail until the covers are redrawn below)
        subprocess.run([sys.executable, str(HERE / "preflight.py"), str(n)], capture_output=True, text=True)
        fb = subprocess.run([sys.executable, str(HERE / "fixbreaks.py"), str(n)], capture_output=True, text=True)
        if "added []" in fb.stdout:
            break
    return n, True, ""


def main(argv):
    lanes = int(argv[argv.index("--lanes") + 1]) if "--lanes" in argv else 4
    old = json.loads(FP.read_text()) if FP.exists() else {}
    now = {str(n): fingerprint(n) for n in range(1, 12)}
    todo = [n for n in range(1, 12) if "--all" in argv or old.get(str(n)) != now[str(n)] or not pdf_of(n)]
    print("to build:", todo or "nothing (all volumes current)")
    ok = dict(old)
    with ThreadPoolExecutor(lanes) as ex:
        for n, good, err in ex.map(build, todo):
            print(f"volume {n}: {'built' if good else 'FAILED'} {err}")
            if good:
                ok[str(n)] = fingerprint(n)       # after the build: fixbreaks may have added page breaks
    FP.write_text(json.dumps(ok, indent=1))
    subprocess.run([sys.executable, str(HERE / "covers.py")], check=True)
    proofs = subprocess.Popen([sys.executable, str(HERE / "cover_proofs.py")], stdout=subprocess.DEVNULL)
    with ThreadPoolExecutor(lanes) as ex:
        res = list(ex.map(lambda n: (n, subprocess.run([sys.executable, str(HERE / "preflight.py"), str(n)],
                                                        capture_output=True, text=True).returncode), range(1, 12)))
    proofs.wait()
    failed = [n for n, rc in res if rc]
    print("preflight:", "all eleven pass" if not failed else f"FAILED in {failed}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
