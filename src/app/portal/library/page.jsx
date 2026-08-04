import { getLibraryItems } from '@/lib/services/libraryService';
import LibraryView from './LibraryView';

export const metadata = {
  title: 'Library — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Portal library catalogue, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function LibraryPage() {
  const items = await getLibraryItems();
  return <LibraryView items={items} />;
}
