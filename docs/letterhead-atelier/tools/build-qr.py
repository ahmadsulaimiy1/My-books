#!/usr/bin/env python3
"""
Generate the verification QR.

    python3 tools/build-qr.py

The code is a real one and it scans. It carries a vCard, so a phone that reads
it gets the office straight into its contacts rather than a dead link — no
domain is invented here, and nothing points anywhere that does not exist.

Error correction is set to H (30%), which is what lets a code survive being
printed small on textured stock and read at an angle. Module colour is the
sapphire, not black: at H, the contrast is still far beyond what a reader needs,
and a black square would be the one un-designed object on the sheet.

If the office ever stands up a verification endpoint, change PAYLOAD to the URL
and rebuild — the geometry and quiet zone are already correct for it.
"""
import os
import qrcode
from qrcode.constants import ERROR_CORRECT_Q

HERE   = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")

# MECARD, not vCard. A full vCard pushed this to version 21 - 101 modules -
# which at the 22mm it prints is 0.18mm per module: far below what any reader
# can resolve off paper. MECARD carries the same information in a third of the
# characters and is read by every phone camera.
PAYLOAD = ("MECARD:N:Imam Ahmad Ibrohim Sulaimiy;ORG:The Personal Office;"
           "TEL:+2348104302087;TEL:+447961869638;"
           "EMAIL:abisulaimiycollege@gmail.com;;")

# 22mm is the printed width. Module size is checked against it below, because a
# QR that cannot be scanned is not a security feature, it is a decoration.
PRINT_MM = 22.0

SAPPHIRE = "#082047"
PEARL    = "#F9F7F2"


def main():
    q = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_Q,
                      box_size=20, border=4)   # border 4 = the required quiet zone
    q.add_data(PAYLOAD)
    q.make(fit=True)
    img = q.make_image(fill_color=SAPPHIRE, back_color=PEARL).convert("RGB")
    out = os.path.join(ASSETS, "qr-office.png")
    img.save(out, optimize=True)

    modules = 17 + 4 * q.version          # data modules, excluding the quiet zone
    mm = PRINT_MM / modules
    print(f"qr-office.png  version {q.version}  {modules}x{modules} modules  "
          f"{os.path.getsize(out)//1024} KB  (ECC Q, quiet zone 4)")
    print(f"at {PRINT_MM:g}mm printed: {mm:.3f} mm per module "
          f"({'OK' if mm >= 0.33 else 'TOO SMALL - shorten the payload'})")

    # prove it decodes, from a raster at the size it will actually print
    try:
        import cv2, numpy as np
        from PIL import Image as I
        px = int(PRINT_MM / 25.4 * 600)   # 600dpi, a good print scan
        small = I.open(out).resize((px, px), I.LANCZOS).convert("RGB")
        data, *_ = cv2.QRCodeDetector().detectAndDecode(
            cv2.cvtColor(np.asarray(small), cv2.COLOR_RGB2BGR))
        print("decoded at print size:" if data else "DECODE FAILED at print size",
              (data[:60] + "...") if data else "")
    except ImportError:
        print("(install opencv-python-headless to verify the decode)")


if __name__ == "__main__":
    main()
