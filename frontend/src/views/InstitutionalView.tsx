import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { InstitutionalProject } from '../services/api';
import { Building2, Users, Clock, CheckSquare } from 'lucide-react';

export const InstitutionalView: React.FC = () => {
  const [projects, setProjects] = useState<InstitutionalProject[]>([]);
  const [selectedProject, setSelectedProject] = useState<InstitutionalProject | null>(null);

  const loadProjects = async () => {
    try {
      const pData = await api.getProjects();
      setProjects(pData);
      if (pData.length > 0 && !selectedProject) {
        setSelectedProject(pData[0]);
      }
    } catch (err) {
      console.error('Error fetching institutional projects', err);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8 space-y-8">
      {/* Institutional Header */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold mb-2">
              <Building2 className="w-3.5 h-3.5" />
              Public Procurement & Enterprise Contracts (PRD Section 4 P1)
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Institutional Multi-Worker Operations
            </h1>
            <p className="text-sm text-slate-600 mt-1 max-w-2xl">
              Cooperative workforce deployment for government infrastructure, metro systems, universities, and commercial facility management contracts.
            </p>
          </div>

          <div className="flex items-center gap-4 border-t md:border-t-0 md:border-l border-slate-200 pt-4 md:pt-0 md:pl-6 text-xs text-slate-600">
            <div>
              <div className="font-semibold text-slate-900 text-base">{projects.length}</div>
              <div>Active Contracts</div>
            </div>
            <div>
              <div className="font-semibold text-slate-900 text-base">₹15.5 Lakhs</div>
              <div>Contract Portfolio</div>
            </div>
          </div>
        </div>
      </div>

      {/* Projects Grid & Details */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Project Cards List (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <h2 className="text-base font-bold text-slate-900">Enterprise Projects</h2>

          <div className="space-y-3">
            {projects.map(p => {
              const isSelected = selectedProject?.id === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => setSelectedProject(p)}
                  className={`cursor-pointer border rounded-lg p-4 transition-all ${
                    isSelected
                      ? 'bg-amber-50/50 border-amber-500 shadow-xs ring-1 ring-amber-400/50'
                      : 'bg-white border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                      {p.client_name}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      p.status === 'ACTIVE' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {p.status}
                    </span>
                  </div>

                  <h3 className="font-semibold text-slate-900 text-sm mt-1">
                    {p.title}
                  </h3>

                  <div className="mt-3 flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 pt-2.5">
                    <div className="flex items-center gap-1">
                      <Users className="w-3.5 h-3.5" />
                      <span>{p.required_headcount} Workers Required</span>
                    </div>
                    <div className="font-bold text-slate-900">
                      ₹{p.budget.toLocaleString()}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Project Milestones, Team Allocation & Supervisor Inspection (7 cols) */}
        <div className="lg:col-span-7">
          {selectedProject ? (
            <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-xs space-y-6">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    {selectedProject.client_name}
                  </span>
                  <span className="font-mono text-xs text-slate-400">
                    ID: PRJ-2026-{selectedProject.id}
                  </span>
                </div>
                <h2 className="text-lg font-bold text-slate-900 mt-1">
                  {selectedProject.title}
                </h2>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  {selectedProject.description}
                </p>
              </div>

              {/* Progress & Commercials */}
              <div className="grid grid-cols-3 gap-3 bg-slate-50 p-3.5 rounded border border-slate-200 text-xs">
                <div>
                  <span className="text-slate-400 block text-[11px]">Total Budget</span>
                  <strong className="text-slate-900 text-sm">₹{selectedProject.budget.toLocaleString()}</strong>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Disbursed</span>
                  <strong className="text-slate-900 text-sm">₹{selectedProject.amount_disbursed.toLocaleString()}</strong>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Execution Progress</span>
                  <strong className="text-emerald-700 text-sm">{selectedProject.progress_percentage}%</strong>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-[11px] font-semibold text-slate-600">
                  <span>Contract Completion</span>
                  <span>{selectedProject.progress_percentage}%</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                  <div
                    className="bg-emerald-600 h-full rounded-full transition-all"
                    style={{ width: `${selectedProject.progress_percentage}%` }}
                  />
                </div>
              </div>

              {/* Trade Skills Breakdown */}
              <div className="space-y-2 text-xs">
                <h3 className="font-bold text-slate-900">Workforce Headcount Breakdown</h3>
                <div className="grid grid-cols-3 gap-2">
                  {Object.entries(selectedProject.skills_breakdown).map(([skill, count]) => (
                    <div key={skill} className="p-2.5 rounded border border-slate-200 bg-white flex justify-between items-center">
                      <span className="font-medium text-slate-700">{skill}</span>
                      <span className="font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded text-xs">
                        {count} workers
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Milestones & Supervisor Sign-off */}
              <div className="space-y-3 text-xs border-t border-slate-100 pt-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-slate-900">Supervisor Inspection Milestones</h3>
                  <span className="text-slate-500 text-[11px]">Supervisor: Vikramaditya Rao</span>
                </div>

                <div className="space-y-2">
                  {selectedProject.milestones.map((m, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 rounded border border-slate-200 bg-slate-50/50">
                      <div className="flex items-center gap-2">
                        {m.completed ? (
                          <CheckSquare className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                        ) : (
                          <Clock className="w-4 h-4 text-slate-400 flex-shrink-0" />
                        )}
                        <span className={m.completed ? 'font-medium text-slate-800' : 'text-slate-600'}>
                          {m.title}
                        </span>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        m.completed ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'
                      }`}>
                        {m.completed ? 'Verified' : 'Pending Inspection'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-xs">Select a contract from the list to view details.</p>
          )}
        </div>
      </div>
    </div>
  );
};
