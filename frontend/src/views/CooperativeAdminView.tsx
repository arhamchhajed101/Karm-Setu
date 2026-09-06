import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Cooperative, JobItem, WorkerItem, AllocationEvaluation } from '../services/api';
import { CheckCircle2, Sparkles } from 'lucide-react';

export const CooperativeAdminView: React.FC = () => {
  const [cooperative, setCooperative] = useState<Cooperative | null>(null);
  const [kpis, setKpis] = useState<any>(null);
  const [roster, setRoster] = useState<WorkerItem[]>([]);
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [settlements, setSettlements] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Allocation Modal State
  const [evaluatingJob, setEvaluatingJob] = useState<JobItem | null>(null);
  const [allocationResult, setAllocationResult] = useState<AllocationEvaluation | null>(null);
  const [evaluating, setEvaluating] = useState<boolean>(false);
  const [assignSuccess, setAssignSuccess] = useState<string | null>(null);

  const loadCoopData = async () => {
    try {
      setLoading(true);
      const coops = await api.getCooperatives();
      if (coops.length > 0) {
        const c = coops[0]; // Delhi Labour Cooperative
        setCooperative(c);
        const kpiData = await api.getCooperativeKPIs(c.id);
        setKpis(kpiData);
        const rData = await api.getWorkers(c.id);
        setRoster(rData);
        const jData = await api.getJobs(undefined, c.id);
        setJobs(jData.slice(0, 15));
        const sData = await api.getSettlements();
        setSettlements(sData.slice(0, 10));
      }
    } catch (err) {
      console.error('Failed loading coop data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCoopData();
  }, []);

  const handleOpenAllocation = async (job: JobItem) => {
    setEvaluatingJob(job);
    setEvaluating(true);
    setAssignSuccess(null);
    try {
      const evaluation = await api.evaluateAllocation(job.id);
      setAllocationResult(evaluation);
    } catch (err: any) {
      alert(`Evaluation failed: ${err.message}`);
    } finally {
      setEvaluating(false);
    }
  };

  const handleAutoAssign = async (jobId: number) => {
    try {
      const res = await api.autoAssignJob(jobId);
      setAssignSuccess(`Assigned to ${res.assigned_worker_name} (Score: ${res.total_score}/100)!`);
      loadCoopData();
    } catch (err: any) {
      alert(`Auto-assign failed: ${err.message}`);
    }
  };

  const handleManualAssign = async (jobId: number, workerId: number) => {
    try {
      const res = await api.manualAssignJob(jobId, workerId, 'Coordinator Manual Selection');
      setAssignSuccess(`Manually assigned to ${res.assigned_worker_name}!`);
      loadCoopData();
    } catch (err: any) {
      alert(`Manual assign failed: ${err.message}`);
    }
  };

  if (loading || !cooperative) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-12 text-center text-slate-500">
        Loading cooperative operations dashboard...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8 space-y-8">
      {/* Cooperative Identity & Executive Banner */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                Reg: {cooperative.registration_id}
              </span>
              <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-xs font-semibold">
                {cooperative.verification_status}
              </span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight mt-1">
              {cooperative.name}
            </h1>
            <p className="text-xs text-slate-600 mt-1">
              Jurisdiction: {cooperative.district}, {cooperative.state} • Operational Pool Retention: {(cooperative.commission_rate * 100).toFixed(0)}% • Welfare Rate: {(cooperative.welfare_contribution_rate * 100).toFixed(0)}%
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right text-xs">
              <div className="text-slate-500">Welfare Pool Reserve</div>
              <div className="text-lg font-bold text-emerald-700">₹{(kpis?.total_welfare_pool || 45200).toLocaleString()}</div>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <div className="text-xs font-medium text-slate-500">Total Workforce Roster</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">{kpis?.total_workers || roster.length}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">{kpis?.active_available_workers || 140} Available on Duty</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <div className="text-xs font-medium text-slate-500">Active Service Jobs</div>
          <div className="text-2xl font-bold text-amber-700 mt-1">{kpis?.active_jobs_count || 4}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Pending Dispatch & In-Flight</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <div className="text-xs font-medium text-slate-500">Jobs Completed</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">{kpis?.total_jobs_completed || 1050}</div>
          <div className="text-[11px] text-emerald-600 mt-0.5 font-medium">98.2% Completion Rate</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <div className="text-xs font-medium text-slate-500">Average Worker Rating</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">★ {kpis?.average_worker_rating || 4.85}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Verified Police Badged</div>
        </div>
      </div>

      {/* Section: Live Job Queue & Smart Allocation Engine */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Demand Queue & Smart Allocation Engine
            </h2>
            <p className="text-xs text-slate-500">
              Evaluate eligible cooperative workers using transparent multi-factor scoring (PRD Section 3.2).
            </p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded bg-slate-100 font-medium text-slate-700">
            {jobs.length} Jobs
          </span>
        </div>

        <div className="divide-y divide-slate-100">
          {jobs.map(job => (
            <div key={job.id} className="py-3.5 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-slate-900 text-xs">{job.booking_ref}</span>
                  <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                    job.status === 'REQUESTED' ? 'bg-amber-100 text-amber-800' :
                    job.status === 'ASSIGNED' ? 'bg-blue-100 text-blue-800' :
                    job.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' :
                    'bg-slate-100 text-slate-700'
                  }`}>
                    {job.status}
                  </span>
                  {job.is_emergency && (
                    <span className="px-1.5 py-0.5 rounded bg-red-100 text-red-800 text-[10px] font-semibold">
                      EMERGENCY
                    </span>
                  )}
                </div>

                <div className="text-xs font-medium text-slate-800">
                  {job.service_name} • {job.address}
                </div>

                <div className="text-[11px] text-slate-500">
                  Customer: {job.customer_name || 'Ananya Mehra'} • Estimate: ₹{job.price_estimate}
                  {job.assigned_worker_name && (
                    <span className="ml-2 text-slate-700 font-semibold">• Worker: {job.assigned_worker_name}</span>
                  )}
                </div>
              </div>

              <div>
                <button
                  onClick={() => handleOpenAllocation(job)}
                  className="px-3.5 py-1.5 rounded bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold flex items-center gap-1.5 shadow-xs transition-colors"
                >
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  <span>{job.status === 'REQUESTED' ? 'Evaluate & Assign' : 'Inspect Allocation'}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Allocation Inspector Modal / Panel */}
      {evaluatingJob && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white border border-slate-300 rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-200 flex items-start justify-between bg-slate-50">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold bg-white px-2 py-0.5 rounded border border-slate-300 text-slate-900">
                    {evaluatingJob.booking_ref}
                  </span>
                  <span className="text-xs text-slate-500">Smart Fair Allocation Engine (PRD 3.2)</span>
                </div>
                <h3 className="text-lg font-bold text-slate-900 mt-1">
                  Worker Matching: {evaluatingJob.service_name}
                </h3>
                <p className="text-xs text-slate-600 mt-0.5">
                  Location: {evaluatingJob.address}
                </p>
              </div>

              <button
                onClick={() => setEvaluatingJob(null)}
                className="text-slate-400 hover:text-slate-700 font-bold p-1 text-lg"
              >
                ✕
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto space-y-6 text-xs">
              {evaluating ? (
                <div className="py-12 text-center text-slate-500">
                  Computing 6-factor deterministic scoring and explainability justifications...
                </div>
              ) : allocationResult ? (
                <>
                  {/* Top Recommendation Banner */}
                  <div className="bg-amber-50 border border-amber-300 rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-amber-700" />
                        <span className="font-bold text-amber-950 text-sm">
                          Top Match: {allocationResult.recommended_worker_name}
                        </span>
                      </div>
                      {evaluatingJob.status === 'REQUESTED' && (
                        <button
                          onClick={() => handleAutoAssign(evaluatingJob.id)}
                          className="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded font-bold text-xs shadow-xs"
                        >
                          Auto-Assign Best Candidate
                        </button>
                      )}
                    </div>
                    <p className="text-amber-900 leading-relaxed text-[11px]">
                      {allocationResult.top_recommendation_reason}
                    </p>
                  </div>

                  {assignSuccess && (
                    <div className="bg-emerald-50 border border-emerald-300 text-emerald-900 p-3 rounded font-medium">
                      ✓ {assignSuccess}
                    </div>
                  )}

                  {/* Criteria Formula Legend */}
                  <div className="grid grid-cols-2 sm:grid-cols-6 gap-2 text-[10px] text-slate-600 bg-slate-50 p-3 rounded border border-slate-200">
                    <div><strong>Skill:</strong> 30% weight</div>
                    <div><strong>Availability:</strong> 20% weight</div>
                    <div><strong>Distance:</strong> 15% weight</div>
                    <div><strong>Reliability:</strong> 15% weight</div>
                    <div><strong>Workload:</strong> 10% weight</div>
                    <div><strong>Fairness:</strong> 10% boost</div>
                  </div>

                  {/* Candidate Ranking Table */}
                  <div className="border border-slate-200 rounded-lg overflow-hidden">
                    <table className="w-full text-left border-collapse">
                      <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[10px] tracking-wider">
                        <tr>
                          <th className="py-2.5 px-3">Rank & Candidate</th>
                          <th className="py-2.5 px-3">Distance</th>
                          <th className="py-2.5 px-3">Skill (30)</th>
                          <th className="py-2.5 px-3">Trust (15)</th>
                          <th className="py-2.5 px-3">Fairness (10)</th>
                          <th className="py-2.5 px-3 font-bold text-slate-900">Total (100)</th>
                          <th className="py-2.5 px-3 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {allocationResult.candidates.map((cand, idx) => (
                          <tr key={cand.worker_id} className={idx === 0 ? 'bg-amber-50/40' : 'hover:bg-slate-50'}>
                            <td className="py-3 px-3">
                              <div className="font-semibold text-slate-900">
                                #{idx + 1} {cand.worker_name}
                              </div>
                              <div className="text-[10px] text-slate-500">
                                {cand.worker_phone} • {cand.weekly_jobs} jobs this wk
                              </div>
                            </td>
                            <td className="py-3 px-3 text-slate-600">{cand.distance_km} km</td>
                            <td className="py-3 px-3">{cand.scores.skill_score}/30</td>
                            <td className="py-3 px-3">{cand.scores.reliability_score}/15</td>
                            <td className="py-3 px-3 text-amber-800 font-semibold">+{cand.scores.fairness_score}</td>
                            <td className="py-3 px-3 font-bold text-slate-900 text-sm">
                              {cand.scores.total_score}
                            </td>
                            <td className="py-3 px-3 text-right">
                              {evaluatingJob.status === 'REQUESTED' ? (
                                <button
                                  onClick={() => handleManualAssign(evaluatingJob.id, cand.worker_id)}
                                  className="px-2.5 py-1 rounded border border-slate-300 hover:bg-slate-100 font-medium text-[11px] text-slate-700"
                                >
                                  Assign
                                </button>
                              ) : (
                                <span className="text-[11px] text-slate-400">Assigned</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              ) : null}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end">
              <button
                onClick={() => setEvaluatingJob(null)}
                className="px-4 py-1.5 rounded bg-slate-200 hover:bg-slate-300 font-semibold text-xs text-slate-800"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Two Column Layout: Worker Roster & Financial Settlements Ledger */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Worker Roster Table (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">
              Cooperative Worker Roster ({roster.length})
            </h2>
            <span className="text-xs text-slate-500">Verified Delhi Police Registry</span>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-xs">
            <div className="overflow-x-auto max-h-96 overflow-y-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[10px] tracking-wider sticky top-0">
                  <tr>
                    <th className="py-2.5 px-3">Worker</th>
                    <th className="py-2.5 px-3">Trades</th>
                    <th className="py-2.5 px-3">Rating</th>
                    <th className="py-2.5 px-3">Wk Jobs</th>
                    <th className="py-2.5 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {roster.slice(0, 15).map(w => (
                    <tr key={w.id} className="hover:bg-slate-50">
                      <td className="py-2.5 px-3">
                        <div className="font-semibold text-slate-900">{w.name}</div>
                        <div className="text-[10px] text-slate-500 font-mono">{w.phone}</div>
                      </td>
                      <td className="py-2.5 px-3">
                        <div className="flex flex-wrap gap-1">
                          {w.skills.map(s => (
                            <span key={s} className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px]">
                              {s}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="py-2.5 px-3 font-semibold text-amber-800">
                        ★ {w.rating.toFixed(1)}
                      </td>
                      <td className="py-2.5 px-3 text-slate-700 font-medium">
                        {w.weekly_jobs_count}
                      </td>
                      <td className="py-2.5 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          w.availability_status === 'AVAILABLE' ? 'bg-emerald-100 text-emerald-800' :
                          w.availability_status === 'BUSY' ? 'bg-amber-100 text-amber-800' :
                          'bg-slate-100 text-slate-700'
                        }`}>
                          {w.availability_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Column: Financial Settlements Ledger (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">
              Settlements & Welfare Ledger
            </h2>
            <span className="text-xs text-emerald-700 font-semibold">80 / 15 / 5 Rule</span>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs space-y-3">
            <p className="text-xs text-slate-500">
              Automated breakdown of gross revenue disbursed to worker earnings, cooperative pool, and welfare fund.
            </p>

            <div className="space-y-2.5 max-h-80 overflow-y-auto">
              {settlements.map(s => (
                <div key={s.id} className="border border-slate-200 rounded p-3 text-xs space-y-1 bg-slate-50/50">
                  <div className="flex justify-between items-center">
                    <span className="font-mono font-bold text-slate-900 text-[11px]">{s.booking_ref}</span>
                    <span className="font-bold text-slate-900">₹{s.gross_amount}</span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-[10px] text-slate-600 pt-1 border-t border-slate-200">
                    <div>
                      <span className="text-slate-400 block">Worker (80%)</span>
                      <strong className="text-slate-900">₹{s.worker_amount}</strong>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Coop (15%)</span>
                      <strong className="text-slate-900">₹{s.cooperative_amount}</strong>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Welfare (5%)</span>
                      <strong className="text-emerald-700">₹{s.welfare_amount}</strong>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
