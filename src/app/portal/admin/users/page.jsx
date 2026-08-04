import UsersView from './UsersView';

export const metadata = {
  title: 'Users & Roles — Administrator Preview | Albalagh Global',
  description: 'Frontend preview of the Administrator user and role management screen in the Albalagh Global Administrator Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function UsersPage() {
  return <UsersView />;
}
