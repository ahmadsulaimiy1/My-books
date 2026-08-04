import { getLedger, getFeeTypes } from '@/lib/services/staffService';
import FinanceView from './FinanceView';

export const metadata = {
  title: 'Finance — Staff Preview | Albalagh Global',
  description: 'Frontend preview of the Staff fee ledger in the Albalagh Global Staff Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function FinancePage() {
  const [ledger, feeTypes] = await Promise.all([getLedger(), getFeeTypes()]);
  return <FinanceView ledger={ledger} feeTypes={feeTypes} />;
}
