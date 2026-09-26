"""The author's colophon on the fronts of the covers, in his own words (Bible, ch. 25 §14 ي): one source for the
three editions, never shortened on a front."""

BY = "تأليف الفقير إلى ربه"
AUTHOR_NAME = "أبي عبد الله جلال الدين أحمد بن إبراهيم السليمي"
AUTHOR_LINES = ("أبي عبد الله جلال الدين", "أحمد بن إبراهيم السليمي")   # the same words, broken as a colophon breaks them
PRAYER = "غفر الله له ولوالديه وللمسلمين"

assert " ".join(AUTHOR_LINES) == AUTHOR_NAME
