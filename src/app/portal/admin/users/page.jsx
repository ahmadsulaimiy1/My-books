import { getUsers, getRoleOptions } from '@/lib/services/adminService';
import UsersView from './UsersView';

export const metadata = {
  title: 'Users & Roles — Administrator Preview | Albalagh Global',
  description: 'Frontend preview of the Administrator user and role management screen in the Albalagh Global Administrator Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function UsersPage() {
  const [users, roleOptions] = await Promise.all([getUsers(), getRoleOptions()]);
  return <UsersView users={users} roleOptions={roleOptions} />;
}
