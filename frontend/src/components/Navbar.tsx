import React, { useEffect } from 'react';
import { Logo } from './Logo';
import { api, setStoredToken } from '../services/api';
import { User, Users, Briefcase, BarChart3, Building2 } from 'lucide-react';

export type ActiveTab = 'customer' | 'worker' | 'cooperative' | 'analytics' | 'institutional';

interface NavbarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  currentUserRole: string;
  setCurrentUserRole: (role: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  currentUserRole,
  setCurrentUserRole,
}) => {

  // Quick switch between demo personas
  const handleRoleChange = async (role: string) => {
    setCurrentUserRole(role);
    try {
      let email = 'customer@karmsetu.in';
      if (role === 'worker') email = 'worker@karmsetu.in';
      if (role === 'cooperative_admin') email = 'admin@karmsetu.in';
      if (role === 'supervisor') email = 'supervisor@karmsetu.in';

      const res = await api.login(email, 'Password123!');
      setStoredToken(res.access_token);

      // Match tab to role
      if (role === 'customer') setActiveTab('customer');
      if (role === 'worker') setActiveTab('worker');
      if (role === 'cooperative_admin') setActiveTab('cooperative');
      if (role === 'supervisor') setActiveTab('institutional');
    } catch (err) {
      console.error('Role switch error', err);
    }
  };

  useEffect(() => {
    // Initial login as customer or coop admin
    handleRoleChange(currentUserRole);
  }, []);

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
      {/* Top sober institutional bar */}
      <div className="bg-slate-50 border-b border-slate-200/80 px-4 sm:px-8 py-1.5 text-xs text-slate-600 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
          <span className="font-semibold text-slate-700">SIH 2026 Initiative</span>
          <span className="text-slate-300">|</span>
          <span className="hidden md:inline text-slate-600">
            Ministry of Cooperation • National Labour Cooperative Federation of India (NLCF)
          </span>
        </div>

        {/* Demo Fast Role Switcher */}
        <div className="flex items-center gap-1.5">
          <span className="text-slate-500 font-medium">Demo Persona:</span>
          <div className="inline-flex rounded-md border border-slate-300 p-0.5 bg-white shadow-xs">
            <button
              onClick={() => handleRoleChange('customer')}
              className={`px-2 py-0.5 rounded text-xs font-medium transition-colors ${
                currentUserRole === 'customer' ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100'
              }`}
            >
              Customer
            </button>
            <button
              onClick={() => handleRoleChange('worker')}
              className={`px-2 py-0.5 rounded text-xs font-medium transition-colors ${
                currentUserRole === 'worker' ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100'
              }`}
            >
              Worker
            </button>
            <button
              onClick={() => handleRoleChange('cooperative_admin')}
              className={`px-2 py-0.5 rounded text-xs font-medium transition-colors ${
                currentUserRole === 'cooperative_admin' ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100'
              }`}
            >
              Coop Admin
            </button>
            <button
              onClick={() => handleRoleChange('supervisor')}
              className={`px-2 py-0.5 rounded text-xs font-medium transition-colors ${
                currentUserRole === 'supervisor' ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100'
              }`}
            >
              Supervisor
            </button>
          </div>
        </div>
      </div>

      {/* Main navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        <Logo size="md" />

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 overflow-x-auto pb-1 sm:pb-0">
          <button
            onClick={() => setActiveTab('customer')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'customer'
                ? 'bg-amber-50 text-amber-900 border border-amber-300 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <User className="w-4 h-4 text-amber-700" />
            <span>Service Booking</span>
          </button>

          <button
            onClick={() => setActiveTab('worker')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'worker'
                ? 'bg-amber-50 text-amber-900 border border-amber-300 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <Briefcase className="w-4 h-4 text-amber-700" />
            <span>Worker Profile</span>
          </button>

          <button
            onClick={() => setActiveTab('cooperative')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'cooperative'
                ? 'bg-amber-50 text-amber-900 border border-amber-300 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <Users className="w-4 h-4 text-amber-700" />
            <span>Cooperative Operating System</span>
          </button>

          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'analytics'
                ? 'bg-amber-50 text-amber-900 border border-amber-300 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <BarChart3 className="w-4 h-4 text-amber-700" />
            <span>Demand Analytics</span>
          </button>

          <button
            onClick={() => setActiveTab('institutional')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'institutional'
                ? 'bg-amber-50 text-amber-900 border border-amber-300 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <Building2 className="w-4 h-4 text-amber-700" />
            <span>Institutional Projects</span>
          </button>
        </nav>
      </div>
    </header>
  );
};
