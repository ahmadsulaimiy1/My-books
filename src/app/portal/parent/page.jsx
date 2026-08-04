import { getParentProfile, getLinkedStudentOverview } from '@/lib/services/parentService';
import ParentOverviewView from './ParentOverviewView';

export const metadata = {
  title: 'Overview — Parent Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Parent Portal overview screen, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function ParentOverviewPage() {
  const [parent, overview] = await Promise.all([getParentProfile(), getLinkedStudentOverview()]);
  return <ParentOverviewView parent={parent} overview={overview} />;
}
