'use client';

/*
  PortalShell
  -----------
  Shared sidebar + topbar layout for every role's portal (Student, Faculty,
  Staff, Admin, Applicant, Parent). One shell, one set of styles, so every
  portal screen feels like the same platform instead of five separate
  builds — see the "unified ecosystem" goal in
  /albalagh-lms-portal-scoping.md.

  Usage:
    <PortalShell role="student" active="dashboard" title="Dashboard">
      ...page content...
    </PortalShell>
*/

import { useState } from 'react';
import Link from 'next/link';
import PreviewBanner from './PreviewBanner';

const NAV_BY_ROLE = {
  student: [
    { key: 'dashboard', label: 'Dashboard', href: '/portal/student' },
    { key: 'courses', label: 'My Courses', href: '/portal/student/courses' },
    { key: 'assignments', label: 'Assignments', href: '/portal/student/assignments' },
    { key: 'quizzes', label: 'Quizzes', href: '/portal/student/quizzes' },
    { key: 'results', label: 'Results', href: '/portal/student/results' },
    { key: 'timetable', label: 'Timetable', href: '/portal/student/timetable' },
    { key: 'attendance', label: 'Attendance', href: '/portal/student/attendance' },
    { key: 'library', label: 'Library', href: '/portal/library' },
    { key: 'messages', label: 'Messages', href: '/portal/student/messages' },
    { key: 'notifications', label: 'Notifications', href: '/portal/student/notifications' },
    { key: 'profile', label: 'Profile', href: '/portal/student/profile' },
    { key: 'settings', label: 'Settings', href: '/portal/student/settings' },
  ],
  faculty: [
    { key: 'dashboard', label: 'Dashboard', href: '/portal/faculty' },
    { key: 'courses', label: 'My Courses', href: '/portal/faculty/courses' },
    { key: 'gradebook', label: 'Gradebook', href: '/portal/faculty/gradebook' },
    { key: 'attendance', label: 'Attendance', href: '/portal/faculty/attendance' },
    { key: 'messages', label: 'Messages', href: '/portal/faculty/messages' },
    { key: 'profile', label: 'Profile', href: '/portal/faculty/profile' },
  ],
  staff: [
    { key: 'dashboard', label: 'Dashboard', href: '/portal/staff' },
    { key: 'admissions', label: 'Admissions', href: '/portal/staff/admissions' },
    { key: 'finance', label: 'Finance', href: '/portal/staff/finance' },
    { key: 'students', label: 'Students', href: '/portal/staff/students' },
    { key: 'profile', label: 'Profile', href: '/portal/staff/profile' },
  ],
  admin: [
    { key: 'dashboard', label: 'Dashboard', href: '/portal/admin' },
    { key: 'users', label: 'Users & Roles', href: '/portal/admin/users' },
    { key: 'academic', label: 'Academic', href: '/portal/admin/academic' },
  ],
  applicant: [
    { key: 'dashboard', label: 'Application Status', href: '/portal/applicant' },
  ],
  parent: [
    { key: 'dashboard', label: 'Overview', href: '/portal/parent' },
  ],
};

const ROLE_LABEL = {
  student: 'Student Portal',
  faculty: 'Faculty Portal',
  staff: 'Staff Portal',
  admin: 'Administrator Portal',
  applicant: 'Applicant Portal',
  parent: 'Parent Portal',
};

export default function PortalShell({ role, active, title, children }) {
  const [navOpen, setNavOpen] = useState(false);
  const items = NAV_BY_ROLE[role] ?? [];

  return (
    <div className="shell">
      <PreviewBanner />

      <header className="topbar">
        <div className="topbar-inner">
          <button
            className="nav-toggle"
            aria-label="Toggle navigation"
            aria-expanded={navOpen}
            onClick={() => setNavOpen((v) => !v)}
            type="button"
          >
            ☰
          </button>
          <Link href="/" className="brand">
            <BrandMark />
            <span>Albalagh</span>
          </Link>
          <span className="role-label">{ROLE_LABEL[role] ?? 'Portal'}</span>
          <Link href="/" className="exit-link">
            Exit to public site
          </Link>
        </div>
      </header>

      <div className="layout">
        <nav className={`sidebar ${navOpen ? 'open' : ''}`} aria-label="Portal navigation">
          {items.map((item) => (
            <Link
              key={item.key}
              href={item.href}
              className={item.key === active ? 'active' : ''}
              onClick={() => setNavOpen(false)}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <main className="content">
          {title && <h1 className="page-title">{title}</h1>}
          {children}
        </main>
      </div>

      <style jsx>{`
        .shell { min-height: 100vh; display: flex; flex-direction: column; background: var(--manuscript); }
        .topbar { background: var(--navy-dark); border-bottom: 1px solid var(--border-dark); }
        .topbar-inner { max-width: 1440px; margin: 0 auto; padding: 0 20px; height: 64px; display: flex; align-items: center; gap: 16px; }
        .nav-toggle { display: none; background: none; border: none; color: #fff; font-size: 20px; cursor: pointer; padding: 4px; }
        .brand { display: flex; align-items: center; gap: 8px; color: #fff; font-family: 'Fraunces', serif; font-size: 17px; font-weight: 600; }
        .role-label { color: var(--gold-light); font-size: 13px; font-weight: 600; border-inline-start: 1px solid var(--border-dark); padding-inline-start: 16px; }
        .exit-link { margin-inline-start: auto; color: #C7CEDC; font-size: 13px; }
        .exit-link:hover { color: var(--gold-light); }

        .layout { flex: 1; display: flex; max-width: 1440px; margin: 0 auto; width: 100%; }
        .sidebar { width: 240px; flex-shrink: 0; background: var(--surface); border-inline-end: 1px solid var(--border); padding: 24px 12px; display: flex; flex-direction: column; gap: 2px; }
        .sidebar a { padding: 10px 14px; border-radius: var(--radius-sm); font-size: 14px; font-weight: 500; color: var(--ink-muted); }
        .sidebar a:hover { background: var(--manuscript); color: var(--navy); }
        .sidebar a.active { background: var(--navy); color: #fff; }

        .content { flex: 1; padding: 32px 28px 64px; min-width: 0; }
        .page-title { font-family: 'Fraunces', serif; font-size: 26px; color: var(--navy); margin: 0 0 24px; }

        @media (max-width: 860px) {
          .nav-toggle { display: block; }
          .role-label { display: none; }
          .sidebar {
            position: fixed; top: 96px; bottom: 0; inset-inline-start: 0; z-index: 90;
            width: 260px; transform: translateX(-100%); transition: transform 0.2s ease;
            box-shadow: var(--shadow-3); overflow-y: auto;
          }
          :global([dir='rtl']) .sidebar { transform: translateX(100%); }
          .sidebar.open { transform: translateX(0); }
          .content { padding: 24px 16px 48px; }
        }
        @media (prefers-reduced-motion: reduce) {
          .sidebar { transition: none; }
        }
      `}</style>
    </div>
  );
}

function BrandMark() {
  return (
    <svg viewBox="0 0 48 48" width="26" height="26" fill="none" aria-hidden="true">
      <path
        d="M24 4 L30 14 L42 14 L33 22 L37 34 L24 27 L11 34 L15 22 L6 14 L18 14 Z"
        stroke="var(--gold)"
        strokeWidth="1.8"
        fill="none"
      />
    </svg>
  );
}
