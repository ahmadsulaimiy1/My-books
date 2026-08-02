/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    // Add real image domains here once a CMS/asset host is chosen.
    // Using picsum.photos only as a placeholder source during design phase.
    remotePatterns: [
      { protocol: 'https', hostname: 'picsum.photos' }
    ]
  },
  // i18n handled via a custom LanguageProvider (React Context) rather than
  // Next.js built-in i18n routing, since the design uses a client-side
  // instant toggle (no page reload / no /en /ar route prefixes).

  // --- Migration bridge -----------------------------------------------
  // The homepage ("/") is a real, componentized Next.js route
  // (src/app/page.jsx). Every other page currently exists as a complete,
  // already-working static HTML file (self-contained CSS/JS, same design
  // system) and has NOT yet been converted into React components — see
  // /docs/MIGRATION.md for why, and for the conversion checklist.
  //
  // These rewrites give each one a clean URL without needing conversion
  // first. Nothing here is faked or hidden: visiting /about literally
  // serves /public/legacy/about.html as a static file. `beforeFiles` is
  // required so these rewrites are checked before Next.js's own routing,
  // in case a real page.jsx is later added at the same path during
  // conversion — it will then correctly take over from the rewrite.
  async rewrites() {
    return {
      beforeFiles: [
        { source: '/about', destination: '/legacy/about.html' },
        { source: '/founders-welcome', destination: '/legacy/founders-welcome.html' },
        { source: '/vision-mission-values', destination: '/legacy/vision-mission-values.html' },
        { source: '/governance', destination: '/legacy/governance.html' },
        { source: '/academic-structure', destination: '/legacy/academic-structure.html' },
        { source: '/graduate-designations-apgdm', destination: '/legacy/graduate-designations-apgdm.html' },
        { source: '/institute-professional-studies', destination: '/legacy/institute-professional-studies.html' },
        { source: '/admissions', destination: '/legacy/admissions.html' },
        { source: '/tuition-scholarships', destination: '/legacy/tuition-scholarships.html' },
        { source: '/digital-campus', destination: '/legacy/digital-campus.html' },
        { source: '/student-portal', destination: '/legacy/student-portal.html' },
        { source: '/lecturer-portal', destination: '/legacy/lecturer-portal.html' },
        { source: '/staff-portal', destination: '/legacy/staff-portal.html' },
        { source: '/administrator-portal', destination: '/legacy/administrator-portal.html' },
        { source: '/digital-library', destination: '/legacy/digital-library.html' },
        { source: '/research-innovation', destination: '/legacy/research-innovation.html' },
        { source: '/alumni-careers', destination: '/legacy/alumni-careers.html' },
        { source: '/news-media-communications', destination: '/legacy/news-media-communications.html' },
        { source: '/albalagh-connect', destination: '/legacy/albalagh-connect.html' },
        { source: '/student-life-campus-organisations', destination: '/legacy/student-life-campus-organisations.html' },
      ],
    };
  },
};

module.exports = nextConfig;
