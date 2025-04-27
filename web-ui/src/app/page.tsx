'use client';

import { useState } from 'react';
import Link from 'next/link';
import Layout from '@/components/ui/Layout';

export default function Home() {
  const [botStatus, setBotStatus] = useState('idle');

  return (
    <Layout>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Overview Card */}
        <div className="md:col-span-2 lg:col-span-3 bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Trading Bot Dashboard</h2>
          <p className="text-gray-600">
            Welcome to your Tinkoff Trading Bot dashboard. Manage your accounts, view trades, and monitor performance.
          </p>
          <div className="mt-4 flex space-x-4">
            <Link 
              href="/accounts" 
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md inline-flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 mr-2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Z" />
              </svg>
              Manage Accounts
            </Link>
          </div>
        </div>
        
        {/* Account Summary Card */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Account Summary</h3>
            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">Sandbox</span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Total Accounts</p>
              <p className="text-2xl font-semibold">--</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Active Accounts</p>
              <p className="text-2xl font-semibold">--</p>
            </div>
          </div>
          <div className="mt-4">
            <Link 
              href="/accounts" 
              className="text-sm text-blue-600 hover:text-blue-800 inline-flex items-center"
            >
              View details
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </div>
        
        {/* Bot Status Card */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Bot Status</h3>
            <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${
              botStatus === 'running' ? 'bg-green-100 text-green-800' : 
              botStatus === 'error' ? 'bg-red-100 text-red-800' : 
              'bg-yellow-100 text-yellow-800'
            }`}>
              {botStatus === 'running' ? 'Running' : 
               botStatus === 'error' ? 'Error' : 'Idle'}
            </span>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Your trading bot is currently {botStatus === 'running' ? 'running and actively trading' : 
                                           botStatus === 'error' ? 'experiencing issues' : 'idle'}.
          </p>
          <button 
            className={`w-full ${botStatus === 'running' 
              ? 'bg-red-600 hover:bg-red-700' 
              : 'bg-green-600 hover:bg-green-700'} text-white px-4 py-2 rounded-md`}
            onClick={() => setBotStatus(botStatus === 'running' ? 'idle' : 'running')}
          >
            {botStatus === 'running' ? 'Stop Bot' : 'Start Bot'}
          </button>
        </div>
        
        {/* Recent Activity Card */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            <p className="text-gray-500 text-sm italic">No recent activity</p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
