'use client';

import { useState, useEffect } from 'react';
import { listAccounts, createAccount, Account, ApiResponse } from '@/lib/api';
import Layout from '@/components/ui/Layout';
import AccountList from '@/components/accounts/AccountList';

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [creatingAccount, setCreatingAccount] = useState<boolean>(false);
  const [createResponse, setCreateResponse] = useState<ApiResponse | null>(null);

  // Fetch accounts on page load
  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listAccounts();
      setAccounts(data);
    } catch (err) {
      setError('Failed to load accounts. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAccount = async () => {
    setCreatingAccount(true);
    setCreateResponse(null);
    try {
      const response = await createAccount();
      setCreateResponse(response);
      
      // If account was created successfully, refresh the list
      if (response.status === 'created' && response.account_id) {
        fetchAccounts();
      }
    } catch (err) {
      setError('Failed to create account. Please try again.');
      console.error(err);
    } finally {
      setCreatingAccount(false);
    }
  };

  const getResponseNotification = () => {
    if (!createResponse) return null;

    if (createResponse.status === 'created') {
      return (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Success! </strong>
          <span className="block sm:inline">New account created with ID: {createResponse.account_id}</span>
        </div>
      );
    } else if (createResponse.status === 'info') {
      return (
        <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Information: </strong>
          <span className="block sm:inline">{createResponse.message}</span>
        </div>
      );
    } else if (createResponse.status === 'error') {
      return (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{createResponse.message}</span>
        </div>
      );
    }
    
    return null;
  };

  return (
    <Layout>
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Account Management</h1>
        <button
          onClick={handleCreateAccount}
          disabled={creatingAccount}
          className={`bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded inline-flex items-center ${
            creatingAccount ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {creatingAccount ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creating...
            </>
          ) : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create New Account
            </>
          )}
        </button>
      </div>

      {getResponseNotification()}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center p-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
        </div>
      ) : (
        <AccountList accounts={accounts} onRefresh={fetchAccounts} />
      )}
    </Layout>
  );
}
