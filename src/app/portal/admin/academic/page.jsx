import { getProgrammes, getCreditUnitPolicy } from '@/lib/services/adminService';
import AcademicView from './AcademicView';

export const metadata = {
  title: 'Academic — Administrator Preview | Albalagh Global',
  description: 'Frontend preview of the Administrator programme and course management overview in the Albalagh Global Administrator Portal.',
  robots: { index: false, follow: false },
};

export default async function AcademicPage() {
  const [programmes, creditUnitPolicy] = await Promise.all([getProgrammes(), getCreditUnitPolicy()]);
  return <AcademicView programmes={programmes} creditUnitPolicy={creditUnitPolicy} />;
}
