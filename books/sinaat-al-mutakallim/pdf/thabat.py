#!/usr/bin/env python3
"""ثبت المصادر of a volume: every source its notes cite, with the edition the book uses (Bible, chs. 45, 74, 112و).

The degree of each book is read from the quotation ledger (التحقيق/سجل-النقول.tsv), from the rows of the volume itself.
The sources are the titles the Master Bibliography marks as cited in the volume (its field «المجلدات», set when the
volume's notes are set), completed by the few the base does not hold (OUTSIDE). The edition is the base's catalogue
record, or, where that record is open or is not the edition cited, the edition read on the book's card or on the scan
of the print (EDITION). No thabat holds a book its notes do not cite, and no cited book is left out: a title the
volume cites whose edition is still open stops the build. Arabic sources are ordered by the name the author is known
by, the article set aside; foreign sources follow, by surname.

    python3 thabat.py [N]     writes the thabat of volume N (the first by default) where that volume keeps it
"""
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "book" / "_production" / "المصادر" / "قاعدة-المصادر.tsv"
sys.path.insert(0, str(HERE))
from paths import OPENING  # noqa: E402
from volumes import ORD, vol_folder  # noqa: E402


def volume_name(n):
    return "المجلد " + ORD[n - 1]


def out_of(n):
    """Where a volume keeps its thabat: the first beside the opening's appendix, the others among their closings; the
    thabat of the whole series («all», الثبت الجامع) closes the eleventh as its «المصادر والمراجع» (Bible, ch. 111 §4)."""
    if n == "all":
        return vol_folder(11) / "الخواتيم" / "المصادر-والمراجع.md"
    return OPENING / "91-ثبت-المصادر.md" if n == 1 else vol_folder(n) / "الخواتيم" / "ثبت-المصادر.md"


# where the base's catalogue record is open, or is not the edition the notes cite: the edition as read on its card
# or on its scan
EDITION = [
    ("مجمع الملك فهد لطباعة المصحف الشريف", "مصحف المدينة النبوية", "برواية حفص عن عاصم، المدينة المنورة"),
    ("الجاحظ", "البيان والتبيين", "تحقيق عبد السلام محمد هارون، مكتبة الخانجي، القاهرة"),
    ("الشافعي", "الرسالة", "تحقيق وشرح أحمد محمد شاكر، مصطفى البابي الحلبي وأولاده، مصر، الأولى، ١٣٥٨هـ / ١٩٤٠م"),
    ("الغزالي", "المستصفى", "ومعه فواتح الرحموت، تقديم وضبط وتعليق إبراهيم محمد رمضان، دار الأرقم بن أبي الأرقم، بيروت"),
    ("الشاطبي", "المقاصد الشافية في شرح الخلاصة الكافية", "تحقيق مجموعة من المحقّقين (والجزء الثامن بتحقيق محمد إبراهيم البنّا)، معهد البحوث العلمية وإحياء التراث الإسلامي، جامعة أم القرى، مكة المكرمة، الأولى، ١٤٢٨هـ / ٢٠٠٧م، ١٠ أجزاء"),
    ("ابن هشام", "شرح شذور الذهب", "ومعه منتهى الأرب لمحمد محيي الدين عبد الحميد، دار الطلائع، القاهرة، رقم الإيداع ١٣٦٣٤/٢٠٠٤"),
    ("الشاطبي", "الموافقات", "تحقيق أبي عبيدة مشهور بن حسن آل سلمان، دار ابن عفان، الأولى، ١٤١٧هـ / ١٩٩٧م"),
    ("ابن فارس", "الصاحبي في فقه اللغة العربية ومسائلها وسنن العرب في كلامها", "محمد علي بيضون، الأولى، ١٤١٨هـ / ١٩٩٧م"),
    ("الزركلي", "الأعلام", "دار العلم للملايين، بيروت، الخامسة عشرة، ٢٠٠٢م"),
    ("ضياء الدين ابن الأثير", "المثل السائر في أدب الكاتب والشاعر", "تحقيق أحمد الحوفي وبدوي طبانة، دار نهضة مصر، القاهرة، ٤ أجزاء"),
    ("السعيد محمد بدوي", "مستويات العربية المعاصرة في مصر: بحثٌ في علاقة اللغة بالحضارة", "دار المعارف، القاهرة، ١٩٧٣م"),
    ("الذهبي", "سير أعلام النبلاء", "أشرف على تحقيقه شعيب الأرنؤوط، مؤسسة الرسالة، بيروت، الثانية، ١٤٠٢هـ / ١٩٨٢م، ٢٥ جزءًا"),
    ("ابن جني", "الخصائص", "تحقيق محمد علي النجار، دار الكتب المصرية، القسم الأدبي؛ المكتبة العلمية، ٣ أجزاء"),
    ("عبد القاهر الجرجاني", "دلائل الإعجاز", "تحقيق محمود محمد شاكر أبو فهر، مكتبة الخانجي، القاهرة، رقم الإيداع ١١٨٨٩/٢٠٠٠"),
    ("الخطيب القزويني", "الإيضاح في علوم البلاغة", "تحقيق محمد عبد المنعم خفاجي، المكتبة الأزهرية للتراث، القاهرة، الثالثة، ١٤١٣هـ / ١٩٩٣م"),
    ("أبو هلال العسكري", "كتاب الصناعتين: الكتابة والشعر", "تحقيق علي محمد البجاوي ومحمد أبو الفضل إبراهيم، دار إحياء الكتب العربية (عيسى البابي الحلبي وشركاه)، القاهرة، الأولى، ١٣٧١هـ / ١٩٥٢م"),
    ("ابن تيمية", "اقتضاء الصراط المستقيم", "تحقيق ناصر عبد الكريم العقل، مكتبة الرشد، الرياض، مجلّدان"),
    ("ابن خلكان", "وفيات الأعيان", "تحقيق إحسان عباس، دار صادر، بيروت، ٧ أجزاء"),
    ("الجاحظ", "الحيوان", "تحقيق وشرح عبد السلام محمد هارون، مصطفى البابي الحلبي وأولاده، مصر، الثانية، ١٣٨٥هـ / ١٩٦٥م"),
    ("الميداني", "مجمع الأمثال", "تحقيق محمد محيي الدين عبد الحميد، مطبعة السنة المحمدية، القاهرة، ١٣٧٤هـ / ١٩٥٥م"),
    ("ابن قتيبة", "عيون الأخبار", "دار الكتب المصرية، القاهرة، ١٣٤٣هـ / ١٩٢٥م"),
    ("الشريف الجرجاني", "التعريفات", "مصطفى البابي الحلبي وأولاده، مصر، ١٣٥٧هـ / ١٩٣٨م"),
    ("ابن جماعة", "تذكرة السامع والمتكلم في أدب العالم والمتعلم", "دائرة المعارف العثمانية، حيدر آباد الدكن، ١٣٥٣هـ"),
    ("أبو نعيم الأصبهاني", "حلية الأولياء وطبقات الأصفياء", "مكتبة الخانجي ومطبعة السعادة، القاهرة، الأولى، ١٣٥٧هـ / ١٩٣٨م، ١٠ أجزاء"),
    ("السخاوي", "المقاصد الحسنة في بيان كثير من الأحاديث المشتهرة على الألسنة", "دار الميمنة، دمشق، ومكتبة الميمنة المدنية، المدينة المنورة، الأولى، ١٤٣٩هـ / ٢٠١٧م، ٥ مجلدات، لكلٍّ محقّقه"),
    ("ابن كثير", "تفسير القرآن العظيم", "تحقيق مصطفى السيد محمد وآخرين، مؤسسة قرطبة ومكتبة أولاد الشيخ للتراث، الجيزة، الأولى، ١٤٢١هـ / ٢٠٠٠م"),
    ("ابن جني", "سر صناعة الإعراب", "دراسة وتحقيق حسن هنداوي، دار القلم، دمشق، الثانية، ١٤١٣هـ / ١٩٩٣م"),
    ("الخليل بن أحمد", "كتاب العين", "تحقيق مهدي المخزومي وإبراهيم السامرائي، سلسلة المعاجم والفهارس"),
    ("إبراهيم أنيس", "الأصوات اللغوية", "مكتبة الأنجلو المصرية، الخامسة، ١٩٧٥م"),
    ("كمال بشر", "علم الأصوات", "دار غريب للطباعة والنشر والتوزيع، القاهرة، ٢٠٠٠م"),
    ("تمام حسان", "اللغة العربية معناها ومبناها", "دار الثقافة، الدار البيضاء، ١٩٩٤م"),
    ("البخاري", "الأدب المفرد", "تحقيق محمد فؤاد عبد الباقي، دار البشائر الإسلامية، بيروت، الثالثة، ١٤٠٩هـ / ١٩٨٩م"),
    # the editions read on the title pages of the scans the ledger's rows were matched on (round-1 and round-2 batches)
    ("أبو بكر ابن الأنباري", "شرح القصائد السبع الطوال الجاهليات", "تحقيق عبد السلام محمد هارون، دار المعارف، القاهرة [سلسلة ذخائر العرب (٣٥)]، الخامسة"),
    ("الطبري", "جامع البيان عن تأويل آي القرآن", "تحقيق عبد الله بن عبد المحسن التركي، دار هجر للطباعة والنشر والتوزيع والإعلان - القاهرة، مصر، الأولى، ١٤٢٢هـ / ٢٠٠١م، ٢٦ جزءًا"),
    ("القرطبي", "الجامع لأحكام القرآن", "دار الكتب المصرية، القاهرة، الطبعة الثانية، في مصوّرة الهيئة المصرية العامة للكتاب (الطبعة الثالثة مصوّرةً عن الثانية بترقيمها)، ١٩٨٧م، ٢٠ جزءًا"),
    ("الألباني", "صحيح سنن أبي داود", "مكتبة المعارف للنشر والتوزيع، الرياض، الأولى للطبعة الجديدة، ١٤١٩هـ / ١٩٩٨م، ٣ مجلدات"),
    ("ابن عبد البر", "جامع بيان العلم وفضله", "تحقيق أبو الأشبال الزهيري، دار ابن الجوزي، السعودية، الأولى، ١٤١٤هـ / ١٩٩٤م، جزآن"),
    ("ابن حجر", "فتح الباري بشرح صحيح البخاري", "المكتبة السلفية، القاهرة، بترقيم محمد فؤاد عبد الباقي، ١٣ جزءًا"),
    ("ابن خلدون", "المقدمة", "والمقدمة جزؤه الأول، ضبط المتن ووضع الحواشي والفهارس خليل شحادة، مراجعة سهيل زكار، دار الفكر، بيروت، الأولى، ١٤٠١هـ / ١٩٨١م، ٨ أجزاء"),
]
# an edition kept per base row where two rows share an author and short title (the Sahihs and their comparison editions)
BY_ROW = {
    "مص-٠٣١": "السلطانية، بالمطبعة الكبرى الأميرية، ببولاق مصر، ١٣١١هـ، بأمر السلطان عبد الحميد الثاني، ٩ أجزاء؛ وأرقام الأحاديث بترقيم "
              "محمد فؤاد عبد الباقي، كما في مصوّرتها عن دار طوق النجاة، بعناية محمد زهير بن ناصر الناصر، ط١",
    # the title page of the copy every volume was matched on (archive.org saheeh_moslem_Abdulbaqy; مصوّرات/…/H1/muslim_title.jpg)
    "مص-٠٣٣": "تحقيق محمد فؤاد عبد الباقي، مطبعة دار إحياء الكتب العربية، فيصل عيسى البابي الحلبي، القاهرة، ٥ أجزاء",
    "مص-٠٣٥": "تحقيق محمد محيي الدين عبد الحميد، المكتبة العصرية، صيدا – بيروت، ٤ أجزاء",
}
MUSLIM_REPRINT = "؛ وقُرئ بعضه في مصوّرة طبعة عيسى البابي الحلبي وشركاه: دار الحديث، القاهرة، الأولى، ١٤١٢هـ / ١٩٩١م"
# what a volume (or «all») cites differently from the rest: (volume, author, short title) -> (title, edition)
SIBAWAYH_SEEN = ("الكتاب", "تحقيق عبد السلام محمد هارون، عالم الكتب، بيروت، الثالثة، ١٤٠٣هـ / ١٩٨٣م؛ وترقيمها ترقيم طبعة مكتبة "
                 "الخانجي، القاهرة، الثالثة، ١٤٠٨هـ / ١٩٨٨م، ٤ أجزاء")
IDAH_BOTH = ("الإيضاح في علوم البلاغة", "تحقيق محمد عبد المنعم خفاجي، المكتبة الأزهرية للتراث، القاهرة، الثالثة، ١٤١٣هـ / ١٩٩٣م؛ "
             "وشرحه وتعليقه وتنقيحه في طبعة دار الكتاب اللبناني ومكتبة المدرسة، بيروت، السادسة، ١٤٠٥هـ / ١٩٨٥م")
JAHIZ_7 = ("البيان والتبيين", "تحقيق وشرح عبد السلام محمد هارون، مكتبة الخانجي، القاهرة، السابعة، ١٤١٨هـ / ١٩٩٨م")
PER_VOLUME = {
    (3, "ابن خلدون", "المقدمة"): ("المقدمة (الجزء الأول من تاريخ ابن خلدون)", "ضبط المتن خليل شحادة، مراجعة سهيل زكار، دار الفكر، بيروت، الأولى، ١٤٠١هـ / ١٩٨١م"),
    (2, "سيبويه", "الكتاب"): SIBAWAYH_SEEN, (3, "سيبويه", "الكتاب"): SIBAWAYH_SEEN, ("all", "سيبويه", "الكتاب"): SIBAWAYH_SEEN,
    (4, "الخطيب القزويني", "الإيضاح في علوم البلاغة"): ("الإيضاح في علوم البلاغة", "شرح وتعليق وتنقيح محمد عبد المنعم خفاجي، دار الكتاب "
                                                         "اللبناني ومكتبة المدرسة، بيروت، السادسة، ١٤٠٥هـ / ١٩٨٥م"),
    (3, "الخطيب القزويني", "الإيضاح في علوم البلاغة"): IDAH_BOTH, ("all", "الخطيب القزويني", "الإيضاح في علوم البلاغة"): IDAH_BOTH,
    (3, "القرطبي", "الجامع لأحكام القرآن"): ("الجامع لأحكام القرآن", "دار الكتب المصرية، القاهرة، الثانية، ١٣٨٤هـ / ١٩٦٤م، ٢٠ جزءًا (في ١٠ مجلدات)؛ "
                                                "والهيئة المصرية العامة للكتاب، الثالثة مصوّرة عن الثانية بترقيمها، ١٩٨٧م"),
    (8, "الجاحظ", "البيان والتبيين"): JAHIZ_7, (10, "الجاحظ", "البيان والتبيين"): JAHIZ_7,
}
# Ibn Khaldun: the work matched is the History, the Muqaddima its first part (F114, F216)
TITLE = {("ابن خلدون", "المقدمة"): "تاريخ ابن خلدون (العبر وديوان المبتدأ والخبر)"}
# al-Tirmidhi: each part has its own editor and printing (title pages in the ledger); a volume names the parts its notes cite
TIRMIDHI_PART = {3: "الجزء الثالث بتحقيق محمد فؤاد عبد الباقي، ط٢، ١٣٨٨هـ / ١٩٦٨م",
                 4: "الجزء الرابع بتحقيق إبراهيم عطوة عوض، ط١، ١٣٨٢هـ / ١٩٦٢م (وترقيمه في ط٢، ١٣٩٥هـ / ١٩٧٥م نفسه)",
                 5: "الجزء الخامس بتحقيق إبراهيم عطوة عوض، ط٢، ١٣٩٥هـ / ١٩٧٥م"}
TIRMIDHI_PARTS = {1: (4,), 3: (3,), 4: (3, 5), 6: (3, 4, 5), 8: (3, 5), 9: (5,), 10: (3,), "all": (3, 4, 5)}


def tirmidhi(n):
    return "شركة مكتبة ومطبعة مصطفى البابي الحلبي وأولاده، مصر؛ " + "؛ و".join(TIRMIDHI_PART[k] for k in TIRMIDHI_PARTS[n])
# sources the notes cite that the base does not hold (an article, a collection of records): (volumes, author, title,
# edition); to be entered in the base when it is next revised
OUTSIDE = [
    (("الثاني",), "برجشتراسر", "التطور النحوي للغة العربية", "أخرجه وصحّحه وعلّق عليه رمضان عبد التواب، مكتبة الخانجي، القاهرة، ودار الرفاعي، الرياض، ١٤٠٢هـ / ١٩٨٢م"),
    (("الأول",), "العقاد، عباس محمود", "«الحروف اللاتينية»", "مجلة الرسالة، القاهرة، السنة الثانية عشرة، العدد ٥٨٥، ١٨ سبتمبر ١٩٤٤م، ص٧٦١ وما بعدها"),
    (("الرابع",), "النويري", "نهاية الأرب في فنون الأدب", "دار الكتب المصرية، القاهرة"),
    (("الرابع",), "ابن حجة الحموي", "خزانة الأدب وغاية الأرب", "شرح عصام شعيتو، دار ومكتبة الهلال، بيروت، الأولى، ١٩٨٧م"),
    (("العاشر",), "الثعالبي", "خاص الخاص", "عني بتصحيحه محمود السمكري، مطبعة السعادة، القاهرة، الأولى، ١٣٢٦هـ"),
    (("السابع", "الثامن"), "ساجقلي زاده", "الرسالة الولدية في آداب البحث والمناظرة", "المطبعة الجمالية، مصر، الأولى، ١٣٢٩هـ"),
    (("السادس", "السابع"), "البيهقي", "مناقب الشافعي", "تحقيق السيد أحمد صقر، جزآن"),
    (("السادس",), "ابن المقفع", "الأدب الكبير", "تحقيق أحمد زكي باشا، جمعية العروة الوثقى، مطبعة مدرسة محمد علي الصناعية، الإسكندرية، الأولى، ١٣٣٠هـ / ١٩١٢م"),
    (("السادس", "الثامن"), "ابن نجيم", "الأشباه والنظائر على مذهب أبي حنيفة النعمان", "دار الكتب العلمية، بيروت، ١٤١٩هـ"),
    (("الثامن",), "النووي", "المجموع شرح المهذب", "تحقيق محمد نجيب المطيعي، مكتبة الإرشاد، جدة"),
    (("الثامن",), "النووي", "تهذيب الأسماء واللغات", "إدارة الطباعة المنيرية، القاهرة"),
    (("الرابع",), "الألباني", "إرواء الغليل في تخريج أحاديث منار السبيل", "إشراف محمد زهير الشاويش، المكتب الإسلامي، بيروت، الأولى، ١٣٩٩هـ / ١٩٧٩م"),
    (("الأول",), "ثعلب", "شرح شعر زهير بن أبي سلمى", "تحقيق فخر الدين قباوة، مكتبة هارون الرشيد، دمشق، الثالثة، ١٤٢٨هـ / ٢٠٠٨م"),
    (("الأول",), "عاتق بن غيث البلادي", "الأدب الشعبي في الحجاز", "دار مكة، مكة المكرمة، الثانية، ١٤٠٢هـ / ١٩٨٢م"),
    (("الثاني",), "ابن الجزري", "المقدمة فيما يجب على قارئ القرآن أن يعلمه", "عن نسخة عليها خط الناظم، تحقيق محمد خليل الزروق، دار الساقية، بنغازي، الأولى، ٢٠٠٧م"),
    (("الثاني",), "أبو بكر ابن الأنباري", "إيضاح الوقف والابتداء في كتاب الله عز وجل", "تحقيق محيي الدين عبد الرحمن رمضان، مجمع اللغة العربية بدمشق، ١٣٩١هـ / ١٩٧١م"),
    (("الرابع",), "المتنبي", "ديوان أبي الطيب المتنبي", "وفي أثناء متنه شرح الواحدي، نشره فريدرخ ديتريصي، برلين، ١٨٦١م"),
    # sources of notes added in the final editorial round (edition as the note gives it, from the copy it was read in)
    (("السادس",), "ابن حجر", "بلوغ المرام", "تحقيق ماهر ياسين الفحل، دار القبس، الرياض، الأولى، ١٤٣٥هـ / ٢٠١٤م"),
    (("العاشر",), "ابن حجر", "تقريب التهذيب", "تحقيق محمد عوامة، دار الرشيد، سوريا، الأولى، ١٤٠٦هـ / ١٩٨٦م"),
    (("العاشر",), "السخاوي", "المقاصد الحسنة", "تحقيق محمد عثمان الخشت، دار الكتاب العربي، بيروت، الأولى، ١٤٠٥هـ / ١٩٨٥م"),
    (("الثامن",), "تقي الدين السبكي", "قضاء الأرب في أسئلة حلب", "تحقيق محمد عالم عبد المجيد الأفغاني، المكتبة التجارية، مكة المكرمة، ١٤٠٩هـ"),
]
# the foreign sources as the thabat sets them: those the base holds, by the base's title; then those it does not
FOREIGN = {
    "The Significance of Learner's Errors": ("Corder, S. P.", '"The Significance of Learner\'s Errors."', "*IRAL: International Review of Applied Linguistics in Language Teaching* 5, no. 4 (1967): 161–170."),
    "Interaction Ritual: Essays on Face-to-Face Behavior": ("Goffman, Erving", '"On Face-Work: An Analysis of Ritual Elements in Social Interaction."', "*Psychiatry* 18, no. 3 (1955): 213–231. Reprinted in *Interaction Ritual: Essays on Face-to-Face Behaviour*, 5–45. Harmondsworth: Penguin University Books, 1972."),
    "A Simplest Systematics for the Organization of Turn-Taking for Conversation": ("Sacks, Harvey, Emanuel A. Schegloff, and Gail Jefferson", '"A Simplest Systematics for the Organization of Turn-Taking for Conversation."', "*Language* 50, no. 4 (1974): 696–735. Variant version in J. Schenkein (ed.), *Studies in the Organization of Conversational Interaction*, 7–55. New York: Academic Press, 1978."),
    "The Role of Deliberate Practice in the Acquisition of Expert Performance": ("Ericsson, K. Anders, Ralf Th. Krampe, and Clemens Tesch-Römer", '"The Role of Deliberate Practice in the Acquisition of Expert Performance."', "*Psychological Review* 100, no. 3 (1993): 363–406."),
    "Diglossia": ("Ferguson, Charles A.", '"Diglossia."', "*Word* 15, no. 2 (1959): 325–340."),
    "On Communicative Competence": ("Hymes, Dell", '"On Communicative Competence."', "In J. B. Pride and J. Holmes (eds.), *Sociolinguistics: Selected Readings*. Harmondsworth: Penguin, 1972."),
    "What Is Educated Spoken Arabic?": ("Mitchell, T. F.", '"What Is Educated Spoken Arabic?"', "*International Journal of the Sociology of Language* 61 (1986): 7–32."),
    "How to Do Things with Words": ("Austin, J. L.", "*How to Do Things with Words.*", "Edited by J. O. Urmson. Oxford: Clarendon Press, 1962."),
    "Logic and Conversation": ("Grice, H. P.", '"Logic and Conversation."', "In P. Cole and J. L. Morgan (eds.), *Syntax and Semantics*, vol. 3: *Speech Acts*, 41–58. New York: Academic Press, 1975."),
    "A Synopsis of Linguistic Theory, 1930–1955": ("Firth, J. R.", '"A Synopsis of Linguistic Theory, 1930–1955."', "In *Studies in Linguistic Analysis*. Oxford: Basil Blackwell, 1962."),
    "Shadowing Procedures in Teaching and Their Future": ("Hamada, Yo", '"Shadowing Procedures in Teaching and Their Future."', "*The Language Teacher* 45, no. 6 (2021): 32–35. doi:10.37546/JALTTLT45.6-3."),
}
FOREIGN_OUTSIDE = [
    # WALS / PHOIBLE (online; no pages)
    (("الثاني", "الحادي عشر"), "Maddieson, Ian", '"Presence of Uncommon Consonants."', "In Matthew S. Dryer and Martin Haspelmath (eds.), *The World Atlas of Language Structures Online*, ch. 19. v2020.4. Zenodo, doi:10.5281/zenodo.13950591. https://wals.info/chapter/19 (accessed 25 Sept. 2026)."),
    (("الثالث",), "Dahl, Östen, and Viveka Velupillai", '"The Past Tense."', "In Matthew S. Dryer and Martin Haspelmath (eds.), *The World Atlas of Language Structures Online*, ch. 66. v2020.4. Zenodo, doi:10.5281/zenodo.13950591. https://wals.info/chapter/66 (accessed 25 Sept. 2026)."),
    (("الثالث",), "Dryer, Matthew S.", '"Order of Subject, Object and Verb."', "In Matthew S. Dryer and Martin Haspelmath (eds.), *The World Atlas of Language Structures Online*, ch. 81. v2020.4. Zenodo, doi:10.5281/zenodo.13950591. https://wals.info/chapter/81 (accessed 25 Sept. 2026)."),
    (("الثالث",), "Dryer, Matthew S.", '"Expression of Pronominal Subjects."', "In Matthew S. Dryer and Martin Haspelmath (eds.), *The World Atlas of Language Structures Online*, ch. 101. v2020.4. Zenodo, doi:10.5281/zenodo.13950591. https://wals.info/chapter/101 (accessed 25 Sept. 2026)."),
    (("الحادي عشر",), "Haspelmath, Martin", '"Occurrence of Nominal Plurality."', "In Matthew S. Dryer and Martin Haspelmath (eds.), *The World Atlas of Language Structures Online*, ch. 34. v2020.4. Zenodo, doi:10.5281/zenodo.13950591. https://wals.info/chapter/34 (accessed 25 Sept. 2026)."),
    (("الحادي عشر",), "Moran, Steven, and Daniel McCloy (eds.)", "*PHOIBLE 2.0.*", "Jena: Max Planck Institute for the Science of Human History, 2019. https://phoible.org (accessed 25 Sept. 2026)."),
    # books and articles
    (("الثاني", "الثالث"), "Robinson, Charles Henry", "*Dictionary of the Hausa Language.* Vol. 1: *Hausa–English*.", "3rd ed. Cambridge: Cambridge University Press, 1913."),
    (("الثالث",), "Leslau, Charlotte, and Wolf Leslau (comp.)", "*African Proverbs.*", "Mount Vernon, N.Y.: Peter Pauper Press, 1962."),
    (("الثالث",), "Clark, Herbert H., and Jean E. Fox Tree", '"Using *uh* and *um* in Spontaneous Speaking."', "*Cognition* 84 (2002): 73–111."),
    (("الرابع",), "Ong, Walter J.", "*Orality and Literacy: The Technologizing of the Word.*", "London and New York: Routledge, 2002. First published 1982. Cited in the pagination of its e-book (Taylor & Francis e-Library, 2005)."),
    (("الرابع",), "Bus, Adriana G., Marinus H. van IJzendoorn, and Anthony D. Pellegrini", '"Joint Book Reading Makes for Success in Learning to Read: A Meta-Analysis on Intergenerational Transmission of Literacy."', "*Review of Educational Research* 65, no. 1 (1995): 1–21."),
    (("الرابع", "الثامن"), "Murdock, Bennet B.", '"The Serial Position Effect of Free Recall."', "*Journal of Experimental Psychology* 64, no. 5 (1962): 482–488."),
    (("الرابع", "الثامن"), "Unsworth, Nash, Gene A. Brewer, and Gregory J. Spillers", '"Inter- and Intra-Individual Variation in Immediate Free Recall: An Examination of Serial Position Functions and Recall Initiation Strategies."', "*Memory* 19, no. 1 (2011): 67–82."),
    (("الخامس", "السادس", "السابع"), "Rogers, Carl R., and Richard E. Farson", "*Active Listening.*", "Chicago: Industrial Relations Center, University of Chicago, 1957. Read in the excerpt published by Gordon Training International, 2007."),
    (("السادس",), "Carnegie, Dale", "*How to Win Friends and Influence People.*", "First published 1936. 11th Indian ed. Bombay: D. B. Taraporevala Sons & Co., 1943."),
    (("السادس",), "Mehrabian, Albert, and Morton Wiener", '"Decoding of Inconsistent Communications."', "*Journal of Personality and Social Psychology* 6, no. 1 (1967): 109–114."),
    (("السادس",), "Mehrabian, Albert, and Susan R. Ferris", '"Inference of Attitudes from Nonverbal Communication in Two Channels."', "*Journal of Consulting Psychology* 31, no. 3 (1967): 248–252."),
    (("السادس",), "Mehrabian, Albert", '"\'Silent Messages\' – Description and Ordering Information."', "Web page. http://www.kaaj.com/psych/smorder.html (accessed 25 Sept. 2026)."),
    (("السادس",), "Ekman, Paul, Richard J. Davidson, and Wallace V. Friesen", '"The Duchenne Smile: Emotional Expression and Brain Physiology II."', "*Journal of Personality and Social Psychology* 58, no. 2 (1990): 342–353."),
    (("السادس",), "Krumhuber, Eva G., and Antony S. R. Manstead", '"Can Duchenne Smiles Be Feigned? New Evidence on Felt and False Smiles."', "*Emotion* 9, no. 6 (2009): 807–820."),
    (("السادس",), "Malinowski, B.", '"The Problem of Meaning in Primitive Languages."', "Supplement I in C. K. Ogden and I. A. Richards, *The Meaning of Meaning*, 296–336. 7th ed. New York: Harcourt, Brace; London: Kegan Paul, 1945. First published 1923."),
    (("السادس",), "Bell, Allan", '"Language Style as Audience Design."', "*Language in Society* 13, no. 2 (1984): 145–204."),
    (("السابع",), "Kamins, Melissa L., and Carol S. Dweck", '"Person versus Process Praise and Criticism: Implications for Contingent Self-Worth and Coping."', "*Developmental Psychology* 35, no. 3 (1999): 835–847."),
    (("السابع",), "Hamblin, C. L.", "*Fallacies.*", "London: Methuen, 1970."),
    (("السابع",), "Hansen, Hans", '"Fallacies."', "In Edward N. Zalta and Uri Nodelman (eds.), *The Stanford Encyclopedia of Philosophy* (Fall 2024 Edition). https://plato.stanford.edu/archives/fall2024/entries/fallacies/."),
    (("السابع",), "Aristotle", "*Rhetorica.*", "Translated by W. Rhys Roberts. In W. D. Ross (ed.), *The Works of Aristotle*, vol. 11. Oxford: Clarendon Press, 1924."),
    (("السابع",), "Toulmin, Stephen E.", "*The Uses of Argument.*", "Updated ed. Cambridge: Cambridge University Press, 2003. First published 1958."),
    (("الثامن",), "Wilson, Karen, and James H. Korn", '"Attention during Lectures: Beyond Ten Minutes."', "*Teaching of Psychology* 34, no. 2 (2007): 85–89."),
    (("التاسع",), "Development Dimensions International (DDI)", '"STAR Method for Interviewing and Feedback."', "Web page. https://www.ddi.com/solutions/behavioral-interviewing/star-method (accessed 26 Sept. 2026)."),
    (("التاسع",), "Janis, Irving L.", "*Victims of Groupthink: A Psychological Study of Foreign-Policy Decisions and Fiascoes.*", "Boston: Houghton Mifflin, 1972."),
    (("العاشر",), "Shure Incorporated", "*Microphone Techniques for Live Sound Reinforcement.*", "Shure, 2014."),
    (("الأول",), "Sharp, H. (ed.)", "*Selections from Educational Records, Part I: 1781–1839.*", "Calcutta: Superintendent Government Printing, 1920. (Macaulay's Minute, 2 February 1835; Lord Bentinck's Resolution, 7 March 1835.)"),
    (("الأول",), "Spitta-Bey, Wilhelm", "*Grammatik des arabischen Vulgärdialectes von Aegypten.*", "Leipzig: J. C. Hinrichs, 1880."),
    (("الأول",), "Wensinck, A. J., et al.", "*Concordance et indices de la tradition musulmane.*", "Leiden: E. J. Brill."),
]


def counted(m):
    """«٢٦ أجزاء» → «٢٦ جزءًا»: the noun after a number in the form the number asks for."""
    n = int(m.group(1).translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")))
    sing, plur = ("جزء", "أجزاء") if m.group(2).startswith(("أجزاء", "جزء")) else ("مجلد", "مجلدات")
    if n == 1:
        return f"{sing} واحد"
    if n == 2:
        return "جزآن" if sing == "جزء" else "مجلدان"
    r = n % 100
    if n >= 100 and r == 0:
        return f"{m.group(1)} {sing}"
    if 3 <= r <= 10:
        return f"{m.group(1)} {plur}"
    return f"{m.group(1)} {sing}ًا"


def tidy(ed):
    """A catalogue card is not a bibliography entry: drop its bookkeeping and keep publisher, place, edition, year, parts."""
    ed = re.sub(r"\s*\((?:متسلسلة الترقيم|الأخير فهارس|آخر ٢ فهارس|الثامن فهارس|[٠-٩]+ والفهارس|وأعادوا طباعتها بالتصوير مِرار|الأولى لدار ابن حزم)\)", "", ed)
    ed = re.sub(r"\s*\([^()]*بحسب بطاقة الشاملة\)", "", ed)   # catalogue bookkeeping is not part of an entry
    ed = re.sub(r"الجزء: [٠-٩]+ - الطبعة: [٠-٩]+، [٠-٩]+،\s*", "", ed)
    ed = re.sub(r"مجموعة محققين\s*وهم:\s*،", "مجموعة من المحققين،", ed).replace("وهم:،", "،").replace("مجموعة محققين،", "مجموعة من المحققين،").replace("٢. أجزاء", "٢ أجزاء").replace(" م.،", " م،")
    ed = re.sub(r"،\s*٢ (?:أجزاء|جزءان)", "، جزآن", ed)
    # a count that already names its noun takes no second «أجزاء» («٢٠ جزءا (في ١٠ مجلدات) أجزاء»)
    ed = re.sub(r"([٠-٩]+ (?:جزءًا|جزءا|أجزاء|مجلدات|مجلدًا)(?: \([^)]*\))?) أجزاء", r"\1", ed)
    # the counted noun agrees with its number: ٣–١٠ أجزاء، ١١–٩٩ جزءًا، المئة جزء (Bible, ch. 05)
    ed = re.sub(r"(?<![٠-٩])([٠-٩]+) (أجزاء|جزءًا|جزءا|مجلدات|مجلدًا|مجلدا)(?![\u0600-\u06FF])", counted, ed)
    ed = re.sub(r"،(?=[^\s])", "، ", ed)
    # the date pair in the imprint's own form, «١٤١٣هـ / ١٩٩٣م», its era letters never apart from their years
    ed = re.sub(r"([٠-٩]+)\s*هـ\s*[-–/]\s*([٠-٩]+)\s*مـ?(?=[\s،.]|$)", "\\1هـ\u00A0/\u00A0\\2م", ed)
    ed = re.sub(r"([٠-٩]+)\s+(هـ|م)(?=[\s،.]|$)", r"\1\2", ed)
    ed = re.sub(r"\s+-\s+(?=لبنان)", "\u00A0- ", ed)
    ed = re.sub(r"\s+-\s+(?=القاهرة)", "، ", ed)    # a catalogue's Latin hyphen between publisher and city
    return re.sub(r"[ \t\n]+", " ", ed).strip(" ،.")


DEGREE = {"print": "طوبق على المطبوع", "digital": "على نسخةٍ رقمية", "general": "إحالةٌ عامّة"}
LEDGER = HERE.parent / "book" / "_production" / "التحقيق" / "سجل-النقول.tsv"
# foreign sources that are publications online only (a database, an encyclopaedia, a web page): never «طوبق على المطبوع»
ONLINE = ("World Atlas", "PHOIBLE", "Stanford Encyclopedia", "Web page")
# the Qur'an was set from the Uthmani text of two digital services; the second editions of the Sahihs and of Abu
# Dawud were used for comparison and grading only
OVERRIDE = {"مصحف المدينة النبوية": "digital"}
BY_EDITION = {("صحيح البخاري", "التأصيل"): "digital", ("صحيح مسلم", "ذهني"): "digital", ("سنن أبي داود", "الأرنؤوط"): "digital"}
# quotations a volume takes whose ledger row is still to be written (the batch reports name the scan or copy they were
# matched on); used only while the volume's own ledger holds no row for the book: (volume, author) -> degree
PENDING = {
    (1, "أبو بكر ابن الأنباري"): "print",    # Zuhayr's closing note, pp. 289–290 seen on scan 3855pdf_202001 (F111, R002)
    (9, "الترمذي"): "print",                 # no. 3433, print-matched at 5/494 (rows م٤-٠١١، م٨-٠١٤; F022, F032)
    (8, "أبو نعيم الأصبهاني"): "print",      # Hilya 9/118, scan D2/227 and its title page (F011)
    (8, "النووي، المجموع شرح المهذب"): "print",  # al-Majmu' 1/54, scan D2/308 (F011)
    (8, "الألباني، صحيح سنن أبي داود"): "print",  # 3/189 and 3/193–194 and the title page seen (F001, F008)
    (4, "السخاوي"): "print",
    (8, "السخاوي"): "digital",               # al-Maqasid 1/390–391, Maymana ed., on Shamela 1266 (F409)
    (10, "السخاوي"): "digital",              # al-Maqasid, al-Khisht ed., p. 332 no. 455, on Shamela (F044)
    (10, "ابن حجر"): "digital",              # Taqrib, ed. Awwama, p. 460 no. 5617, on Shamela (F398)
    (6, "ابن حجر، بلوغ المرام"): "digital",  # Bulugh al-Maram no. 935, ed. al-Fahl, p. 361, on Shamela 17757 (F304)                 # al-Maqasid 3/372, Maymana ed., matched on the print scan (F247)
    (4, "المتنبي"): "print",                 # Dieterici's Berlin 1861 edition, p. 548 seen on archive.org 3190pdf_202001 (round 2, V4)
}
EDITIONS = {}
_ROWS = None


def norm(x):
    x = re.sub(r"[\u064B-\u0652\u0640]", "", x or "")
    return re.sub(r"\s+", " ", x.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")).strip()


def ledger_rows(n):
    """The ledger's rows of volume n (all volumes for «all»), Qur'an set aside: (who, source, state, note)."""
    global _ROWS
    if _ROWS is None:
        with open(LEDGER, encoding="utf-8") as fh:
            _ROWS = [r for r in csv.DictReader(fh, delimiter="\t") if r["النوع"] != "قرآن"]
    AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    pre = None if n == "all" else "م" + str(n).translate(AR) + "-"
    return [r for r in _ROWS if pre is None or r["الرقم"].startswith(pre)]


def on_print(r):
    """A row matched on the print: «متحقّق» (only the print makes it so), or a matched row the ledger notes as seen on the scan."""
    return r["الحالة"].startswith("متحقّق") or "طوبق على مصوّرة المطبوع" in r["ملاحظات"]


def heads(title):
    t = norm(re.sub(r"^كتاب ", "", title.split(":")[0].split("(")[0].strip()))
    return " ".join(t.split()[:2])


def matches(author, title, r, others):
    """Whether ledger row r takes its quotation from this book: its title in the row's source, or its author named
    there when he has no other book in the list."""
    src, who = norm(r["المصدر الأوّلي"]), norm(r["المؤلف أو الراوي"])
    name = norm(author.split("،")[0])
    h = heads(title)
    if len(h.split()) > 1 or len(h) > 6:
        if re.search(r"(^|[\s،؛:(«])و?" + re.escape(h), src):
            return True
    if others:            # an author with more than one book in this list is matched by title only
        return False
    if re.search(r"[A-Za-z]", author):
        surname = author.split(",")[0].strip()
        return surname in r["المؤلف أو الراوي"] or surname in r["المصدر الأوّلي"] or f"{surname} (ed" in r["الطبعة"]
    parts = [norm(x) for x in re.split(r"[؛،:]", r["المؤلف أو الراوي"] + "؛" + r["المصدر الأوّلي"])]
    return any(x == name or (len(name) > 4 and x.endswith(" " + name)) or (len(x) > 4 and name.endswith(x) and " " in name) for x in parts)


def degree(author, title, edition="", n="all", others=False):
    """How far the book was used in volume n, from the ledger's own rows of that volume: matched on the scan of the
    print, matched on a digital copy, or cited in general (named, or its meaning given, with no quotation in the ledger)."""
    if title in OVERRIDE:
        return OVERRIDE[title]
    for (t, mark), deg in BY_EDITION.items():
        if t == title and mark in edition:
            return deg
    found = [r for r in ledger_rows(n) if matches(author, title, r, others)]
    if found:
        if any(on_print(r) for r in found):
            return "print"
        if any("نسخةٍ رقمية" in r["ملاحظات"] for r in found):
            return "digital"
        return "general"
    if n != "all" and same_page_seen(author, title, n, others):
        return "print"
    for (k, who), deg in PENDING.items():
        if (k == n or n == "all") and (who == author or who == f"{author}، {short(title)}"):
            return deg
    return "general"


_NOTES = {}


def notes_of(n):
    """The footnote lines of volume n (its source lists set aside)."""
    if n not in _NOTES:
        from volumes import vol_folder
        _NOTES[n] = [ln for f in sorted(vol_folder(n).rglob("*.md")) if "ثبت" not in f.name and "المصادر-والمراجع" not in f.name
                     for ln in f.read_text(encoding="utf-8").splitlines() if ln.startswith("[^")]
    return _NOTES[n]


def same_page_seen(author, title, n, others):
    """A volume whose ledger has no row for a book still quotes it on the print when one of its own notes cites the book at
    a page another volume's row matched on the scan of that print (the same passage, the same page)."""
    seen = [r for r in ledger_rows("all") if on_print(r) and matches(author, title, r, True)]   # by title alone
    h = norm(short(title)).split()[0] if not re.search(r"[A-Za-z]", author) else author.split(",")[0]
    for r in seen:
        part = re.sub(r"[^٠-٩]", "", r["الجزء"]) if re.fullmatch(r"\s*[٠-٩]+\s*", r["الجزء"]) else ""
        for pg in re.findall(r"[٠-٩]+(?:–[٠-٩]+)?", r["الصفحة"]):
            cite = f"{part}/{pg}" if part else f"ص{pg}"
            if any(h in norm(ln) and cite in ln for ln in notes_of(n)):
                return True
    return False


def foreign_degree(a, t, e, n):
    if any(x in t + " " + e for x in ONLINE):
        return "general"
    return degree(a, t, e, n)


def key(name):
    n = re.sub(r"^(ال|ابن |أبو |أبي |ضياء الدين |الخطيب |عبد القاهر )", "", name.strip())
    return re.sub(r"^ال", "", n)


def short(title):
    return re.sub(r"^كتاب ", "", title.split(":")[0].split("(")[0].strip())


def edition_for(author, title):
    """The EDITION entry for a base title: the same book (short title) by the same author."""
    for a, t, e in EDITION:
        same_book = short(t) == short(title) or short(title).startswith(short(t)) or short(t).startswith(short(title))
        if same_book and (a.split("،")[0] in author or author in a):
            return a, t, e
    return None


def cited(n):
    """The base's titles the notes of volume n cite (n = «all»: of any volume)."""
    names = {volume_name(k) for k in range(1, 12)} if n == "all" else {volume_name(n)}
    with open(BASE, encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh, delimiter="\t") if names & {v.strip() for v in r["المجلدات"].split("،")}]


def volumes_of(r):
    """«١، ٣، ٦»: the volumes whose notes cite a title of the base."""
    AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    ks = [k for k in range(1, 12) if volume_name(k) in [v.strip() for v in r["المجلدات"].split("،")]]
    return "، ".join(str(k).translate(AR) for k in ks)


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    n = "all" if arg == "all" else int(arg)
    if n == 11:   # the eleventh has no thabat of its own: it closes with the series thabat (Bible, ch. 111 §4)
        raise SystemExit("volume 11 keeps the series thabat («المصادر والمراجع»): python3 thabat.py all")
    ords = set(ORD) if n == "all" else {ORD[n - 1]}
    where = {}                                          # (author, title) -> the volumes that cite it (for «all»)
    rows, foreign, open_ = {}, [], []
    muslim_reprint = any("مسلم" in r["المؤلف أو الراوي"] and "دار الحديث" in r["الطبعة"] for r in ledger_rows(n))
    for r in cited(n):
        author, title = r["المؤلف"], r["العنوان"]
        if not re.search(r"[\u0600-\u06FF]", author):   # a Latin name, accents included
            if title not in FOREIGN:
                open_.append(f"{author}, {title}: no form in FOREIGN")
                continue
            foreign.append(FOREIGN[title])
            continue
        e = edition_for(author, title)
        if r["الرقم"] in BY_ROW:
            ed = BY_ROW[r["الرقم"]] + (MUSLIM_REPRINT if r["الرقم"] == "مص-٠٣٣" and muslim_reprint else "")
        elif e:
            author, ed = e[0], e[2]
        else:
            ed = re.sub(r"\s*\[ت [^\]]*\]", "", r["الطبعة (من سجلّ فهرسة)"]).replace("&lt;i&gt;", "").replace("&lt;/i&gt;", "")
            if "تُحدَّد" in ed:
                open_.append(f"{r['الرقم']} {author}، {title}: the edition is still open")
                continue
        shown = re.sub(r"\s*\((طوق النجاة|دار التأصيل|ترقيم عبد الباقي|الطبعة التركية|ت\. [^)]*|تاريخ ابن خلدون، ج١|الجواب الكافي|رواية حفص)[^)]*\)", "", e[1] if e else title).strip()
        base_short = short(shown)
        if author == "الترمذي":
            shown, ed = "الجامع الصحيح وهو سنن الترمذي", tirmidhi(n)
        shown = TITLE.get((author, base_short), shown)
        if (n, author, base_short) in PER_VOLUME:
            shown, ed = PER_VOLUME[(n, author, base_short)]
        rows[(author, r["العنوان"])] = (author, shown, tidy(ed), base_short)
        where[(author, r["العنوان"])] = volumes_of(r)
    label = "الثبت الجامع" if n == "all" else volume_name(n)
    if open_:
        raise SystemExit("the thabat of " + label + " cannot be set:\n  " + "\n  ".join(open_))
    for vols, a, t, e in OUTSIDE:
        if ords & set(vols):
            rows[(a, t)] = (a, t, tidy(e), short(t))
            where[(a, t)] = "، ".join(str(ORD.index(v) + 1).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")) for v in vols)
    foreign += [(a, t, e) for vols, a, t, e in FOREIGN_OUTSIDE if ords & set(vols)]
    if not rows and not foreign:
        raise SystemExit(label + ": the base marks no title as cited in its notes")
    ar = sorted(rows.values(), key=lambda x: (key(x[0]), x[1]))
    EDITIONS.update({(a, t): e for a, t, e, _ in ar})
    names = [a.split("،")[0].strip() for a, _, _, _ in ar]
    vols = {(x[0], x[1]): where.get(k, "") for k, x in rows.items()}
    tail = (lambda a, t: f' <span class="vols">(المجلد {vols[(a, t)]})</span>' if n == "all" and vols.get((a, t)) else "")
    ar = [(a, t, e + f'. <span class="deg">{DEGREE[degree(a, b, e, n, names.count(a.split("،")[0].strip()) > 1 and a not in ("البخاري", "مسلم", "أبو داود"))]}</span>' + tail(a, t))
          for a, t, e, b in ar]
    if n == "all":
        head = ["# المصادر والمراجع", "", "<!-- sub: الثبت الجامع: ما أُحيل إليه في حواشي المجلدات الأحد عشر، بالطبعة التي أُحيل إليها -->", "",
                "هذا ثبتُ السلسلة كلها: كل كتابٍ أُحيل إليه في حاشيةٍ من حواشي مجلداتها، بالطبعة التي أُحيل إليها، وبعده أرقام "
                "المجلدات التي أُحيل إليه فيها. ولكل مجلدٍ ثبتُه في آخره.", ""]
    else:
        head = ["## ثبت المصادر" if n == 1 else "# ثبت المصادر", "",
                "<!-- sub: ما أُحيل إليه في حواشي هذا المجلد، بالطبعة التي أُحيل إليها -->", ""]
    md = head + [
          "رُتّبت المصادر العربية على شهرة مؤلّفيها، من غير اعتدادٍ بـ«ال» و«ابن» و«أبي» في أولها، ثم المصادر الأجنبية على أسماء عائلات مؤلّفيها. "
          "وحيث ذُكر للكتاب طبعتان فالأولى للإحالة والثانية للمقابلة.",
          "وليست المصادر كلّها على درجةٍ واحدة من الاستعمال، فبُيّنت درجة كلٍّ منها في آخره: «طوبق على المطبوع» لما رُئي النقل منه "
          "في صفحته من مصوّرة الطبعة المذكورة؛ و«على نسخةٍ رقمية» لما طوبق على نسخةٍ رقميةٍ لتلك الطبعة ولم تُرَ صفحته المطبوعة؛ "
          "و«إحالةٌ عامّة» لما أُحيل إليه بلا نقلٍ منصوص، أو حُكي معناه.", "", "### المصادر العربية", ""]
    md += [f"- **{a}**، {t}، {e}" for a, t, e in ar]
    md += ["", "### المصادر الأجنبية", ""]
    md += [f"- {a.rstrip('.')}. {t} {e} <span class=\"deg\">{DEGREE[foreign_degree(a, t, e, n)]}</span>" for a, t, e in sorted(foreign)]
    out = out_of(n)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(label + ":", out.relative_to(HERE.parent), len(ar), "Arabic,", len(foreign), "foreign")


if __name__ == "__main__":
    main()
