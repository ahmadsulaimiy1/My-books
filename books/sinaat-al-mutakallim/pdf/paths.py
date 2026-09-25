"""Where the tools find the manuscript (Bible, ch. 112d). One place, so that no tool writes the structure twice."""
from volumes import BOOK, vol_folder

VOL1 = vol_folder(1)
OPENING = VOL1 / "الافتتاحية"
AUTHOR_WORD = VOL1 / "00-كلمة-المؤلف.md"
INTRO = VOL1 / "المدخل"
CLOSING = vol_folder(10) / "الخاتمة" / "00-خاتمة-الكتاب.md"
GLOSSARY = vol_folder(11) / "الخواتيم" / "المسرد.md"
PRODUCTION = BOOK / "_production"
