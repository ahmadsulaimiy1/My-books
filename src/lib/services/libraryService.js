/*
  libraryService — see ./README.md for the service-layer contract.
  Shared across roles (src/app/portal/library/page.jsx).
*/

import { demoLibrary } from '@/lib/portalDemoData';

export async function getLibraryItems(/* { courseId } */) {
  return demoLibrary;
}
