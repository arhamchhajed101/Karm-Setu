import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import type { ActiveTab } from './components/Navbar';
import { CustomerView } from './views/CustomerView';
import { WorkerView } from './views/WorkerView';
import { CooperativeAdminView } from './views/CooperativeAdminView';
import { AnalyticsView } from './views/AnalyticsView';
import { InstitutionalView } from './views/InstitutionalView';
import { Logo } from './components/Logo';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('customer');
  const [currentUserRole, setCurrentUserRole] = useState<string>('customer');

  return (
    <div className="min-h-screen flex flex-col bg-slate-50/50 text-slate-900 font-sans">
      {/* Navigation Header */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        currentUserRole={currentUserRole}
        setCurrentUserRole={setCurrentUserRole}
      />

      {/* Main Content Area */}
      <main className="flex-1">
        {activeTab === 'customer' && <CustomerView />}
        {activeTab === 'worker' && <WorkerView />}
        {activeTab === 'cooperative' && <CooperativeAdminView />}
        {activeTab === 'analytics' && <AnalyticsView />}
        {activeTab === 'institutional' && <InstitutionalView />}
      </main>

      {/* Sober Institutional Footer */}
      <footer className="bg-white border-t border-slate-200 mt-12 py-8 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Logo size="sm" showTagline={false} />
            <span className="text-slate-400">|</span>
            <span>Smart India Hackathon (SIH 2026) Prototype</span>
          </div>

          <div className="flex flex-wrap items-center gap-6 text-slate-600">
            <span>Ministry of Cooperation NCD Dataset</span>
            <span>•</span>
            <span>e-Shram Social Security Framework</span>
            <span>•</span>
            <span>Delhi Police Verification Guidelines</span>
          </div>

          <div className="text-slate-400 text-[11px]">
            Cooperative-Owned Platform Architecture • FastAPI + React
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
