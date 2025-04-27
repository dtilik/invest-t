import React, { ReactNode } from 'react';
import Header from './Header';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-8">
        {children}
      </main>
      <footer className="bg-gray-800 text-center text-white py-4">
        <p className="text-sm">Tinkoff Trading Bot UI &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}
