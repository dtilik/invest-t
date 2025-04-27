import { useState } from 'react';
import { Account } from '@/lib/api';

interface AccountListProps {
  accounts: Account[];
  onRefresh: () => void;
}

export default function AccountList({ accounts, onRefresh }: AccountListProps) {
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACCOUNT_STATUS_OPEN':
        return 'bg-green-100 text-green-800';
      case 'ACCOUNT_STATUS_CLOSED':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <div className="flex justify-between items-center px-6 py-4 border-b">
        <h2 className="text-xl font-semibold text-gray-800">Your Accounts</h2>
        <button
          onClick={onRefresh}
          className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4 mr-1">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
          </svg>
          Refresh
        </button>
      </div>

      {accounts.length === 0 ? (
        <div className="p-6 text-center text-gray-500">
          No accounts found. Create a new account to get started.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Account ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Opened Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {accounts.map((account) => (
                <tr key={account.id} className={selectedAccount === account.id ? 'bg-blue-50' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{account.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{account.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{account.type}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(account.status)}`}>
                      {account.status.replace('ACCOUNT_STATUS_', '')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatDate(account.opened_date)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button 
                      onClick={() => setSelectedAccount(account.id)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Select
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {selectedAccount && (
        <div className="p-4 bg-gray-50 border-t">
          <p className="text-sm text-gray-700">Account {selectedAccount} selected</p>
        </div>
      )}
    </div>
  );
}
