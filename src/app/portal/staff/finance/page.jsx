import FinanceView from './FinanceView';

export const metadata = {
  title: 'Finance — Staff Preview | Albalagh Global',
  description: 'Frontend preview of the Staff fee ledger in the Albalagh Global Staff Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function FinancePage() {
  return <FinanceView />;
}
