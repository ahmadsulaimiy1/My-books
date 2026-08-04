/*
  notificationService — see ./README.md for the service-layer contract.

  Only the Student Portal has notification screens today, but this lives
  as its own service (rather than folded into studentService) because
  notifications are a cross-role concern — Faculty/Staff/Admin will need
  the same read/mark-read shape once they grow notification screens, and
  a real backend almost certainly models notifications as their own
  collection, not nested under "student".
*/

import { demoNotifications } from '@/lib/portalDemoData';

export async function getNotifications(/* { role, userId } */) {
  return demoNotifications;
}

// No real persistence yet — mock accepts and echoes the change so the UI
// can update local state optimistically.
export async function markAsRead({ notificationId }) {
  return { success: true, notificationId };
}
