"""The series' page (Bible, ch. 112ك): 17 × 24 cm for all eleven volumes, the established format of the Arabic
scholarly book. The text block keeps its measure of 122 mm, so the type, the tables and the dialogues keep their
proportions; the page is shorter and its margins narrower, and the text reflows into it."""

W, H = 170.0, 240.0          # the trimmed page, mm
TOP, SIDE, BOTTOM = 22.0, 24.0, 28.0
TEXT_W = W - 2 * SIDE         # 122 mm
TEXT_H = H - TOP - BOTTOM     # 190 mm
BAND = 80.0                   # the sapphire band over a chapter's first page
FIRST = BAND + 12.0           # where the text of a chapter's first page begins
