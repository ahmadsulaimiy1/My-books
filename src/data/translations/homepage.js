// Homepage translation dictionary.
// Consumed via <LanguageProvider dict={homepageDict}> — see src/app/page.jsx.
// Each key maps to { en, ar }. Missing Arabic entries fall back to English
// automatically (see LanguageContext.t()), so this can be filled in
// incrementally without ever breaking the page.

const homepageDict = {
  heroEyebrow: { en: 'Albalagh Global', ar: 'البلاغ العالمية' },
  heroTitle: {
    en: 'Islamic Sciences and Modern Civilization, for a Connected World',
    ar: 'العلوم الإسلامية والحضارة الحديثة، لعالم مترابط',
  },
  heroLead: {
    en: 'A bilingual, online-first college combining classical Islamic scholarship with the technical and professional skills of the modern world.',
    ar: 'كلية إلكترونية ثنائية اللغة تجمع بين العلم الشرعي الكلاسيكي والمهارات التقنية والمهنية للعالم الحديث.',
  },
  heroCta1: { en: 'Apply Now', ar: 'قدّم الآن' },
  heroCta2: { en: 'Explore Programmes', ar: 'استكشف البرامج' },

  whyEyebrow: { en: 'Why Albalagh', ar: 'لماذا البلاغ' },
  whyTitle: { en: 'Built for serious students, from day one', ar: 'مصممة لطلاب جادين، منذ اليوم الأول' },
  why1Title: { en: 'Bilingual by Design', ar: 'ثنائية اللغة بالتصميم' },
  why1Body: { en: 'Every programme, every page, in English and Arabic.', ar: 'كل برنامج وكل صفحة، بالإنجليزية والعربية.' },
  why2Title: { en: 'Islamic Ethics at the Core', ar: 'الأخلاق الإسلامية في الجوهر' },
  why2Body: { en: 'Academic excellence grounded in Islamic values, not separate from them.', ar: 'تميز أكاديمي متجذر في القيم الإسلامية، لا منفصل عنها.' },
  why3Title: { en: 'Modern Technical Skills', ar: 'مهارات تقنية حديثة' },
  why3Body: { en: 'AI, software, media, and business skills built into every School.', ar: 'مهارات الذكاء الاصطناعي والبرمجيات والإعلام والأعمال مدمجة في كل كلية.' },
  why4Title: { en: 'Flexible Online Delivery', ar: 'تقديم إلكتروني مرن' },
  why4Body: { en: 'Live and recorded classes, built around real students\u2019 schedules.', ar: 'دروس مباشرة ومسجلة، مبنية حول جداول الطلاب الحقيقية.' },

  schoolsEyebrow: { en: 'Four Schools', ar: 'أربع كليات' },
  schoolsTitle: { en: 'Choose your path', ar: 'اختر مسارك' },
  s1: { en: 'School of Islamic Sciences', ar: 'كلية العلوم الإسلامية' },
  s2: { en: 'School of Media, Journalism & Digital Communication', ar: 'كلية الإعلام والصحافة والاتصال الرقمي' },
  s3: { en: 'School of AI, Innovation & Technology', ar: 'كلية الذكاء الاصطناعي والابتكار والتقنية' },
  s4: { en: 'School of Business, Entrepreneurship & Financial Management', ar: 'كلية الأعمال وريادة الأعمال والإدارة المالية' },
  learnMore: { en: 'Learn More', ar: 'اعرف المزيد' },

  ctaTitle: { en: 'Ready to begin your journey?', ar: 'مستعد لبدء رحلتك؟' },
  ctaBody: { en: 'Applications are open. Explore admission routes and apply today.', ar: 'باب التقديم مفتوح. استكشف مسارات القبول وقدّم اليوم.' },
  ctaBtn: { en: 'Start Your Application', ar: 'ابدأ طلبك' },

  contactHeading: { en: 'Get in Touch', ar: 'تواصل معنا' },
  contactBody: { en: 'Questions about programmes or admissions? Reach out any time.', ar: 'أسئلة حول البرامج أو القبول؟ تواصل معنا في أي وقت.' },
};

export default homepageDict;
