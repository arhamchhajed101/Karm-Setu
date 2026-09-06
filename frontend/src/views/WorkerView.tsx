import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { WorkerItem, JobItem } from '../services/api';
import { ShieldCheck, Clock, MapPin, CheckCircle2, Play, CheckSquare, Award, AlertCircle, Wallet, Shield } from 'lucide-react';

export const WorkerView: React.FC = () => {
  const [worker, setWorker] = useState<WorkerItem | null>(null);
  const [assignedJobs, setAssignedJobs] = useState<JobItem[]>([]);
  const [welfareData, setWelfareData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadWorkerData = async () => {
    try {
      setLoading(true);
      // Fetch default worker (Ramesh Kumar, ID 1)
      const workers = await api.getWorkers();
      if (workers.length > 0) {
        const w = workers[0];
        setWorker(w);

        // Fetch worker welfare profile
        const welf = await api.getWorkerWelfare(w.id);
        setWelfareData(welf);

        // Fetch jobs assigned to this worker
        const jobs = await api.getJobs();
        const myJobs = jobs.filter(j => j.assigned_worker_id === w.id || j.status === 'ASSIGNED');
        setAssignedJobs(myJobs);
      }
    } catch (err) {
      console.error('Error fetching worker details', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkerData();
  }, []);

  const handleToggleAvailability = async (status: 'AVAILABLE' | 'BUSY' | 'OFF_DUTY') => {
    if (!worker) return;
    try {
      const updated = await api.updateWorkerAvailability(worker.id, status);
      setWorker(updated);
    } catch (err: any) {
      alert(`Could not update availability: ${err.message}`);
    }
  };

  const handleJobAction = async (jobId: number, nextStatus: string) => {
    try {
      await api.updateJobStatus(jobId, nextStatus);
      loadWorkerData();
    } catch (err: any) {
      alert(`Action failed: ${err.message}`);
    }
  };

  if (loading || !worker) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-12 text-center text-slate-500">
        Loading worker profile...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8 space-y-8">
      {/* Worker Identity & Status Header */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center text-2xl font-bold text-slate-700">
              {worker.name.split(' ').map(n => n[0]).join('')}
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-slate-900">{worker.name}</h1>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-xs font-semibold">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  Verified Member
                </span>
              </div>

              <div className="text-xs text-slate-600 mt-1 flex flex-wrap items-center gap-3">
                <span>Cooperative: <strong>{worker.cooperative_name || 'Delhi Labour Cooperative'}</strong></span>
                <span>•</span>
                <span>Phone: {worker.phone}</span>
                <span>•</span>
                <span>Police Ref: <code className="bg-slate-100 px-1 py-0.5 rounded">{worker.verification_ref_id || 'DP-VR-2023-88219'}</code></span>
              </div>

              <div className="flex items-center gap-1.5 mt-2">
                {worker.skills.map(s => (
                  <span key={s} className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px] font-medium">
                    {s}
                  </span>
                ))}
                <span className="text-xs text-amber-700 font-semibold ml-2">
                  ★ {worker.rating.toFixed(2)} rating
                </span>
              </div>
            </div>
          </div>

          {/* Availability Switcher */}
          <div className="border-t md:border-t-0 md:border-l border-slate-200 pt-4 md:pt-0 md:pl-6 flex flex-col items-start md:items-end gap-2">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Shift Availability
            </div>
            <div className="inline-flex rounded-md border border-slate-300 p-1 bg-slate-50 shadow-xs">
              <button
                onClick={() => handleToggleAvailability('AVAILABLE')}
                className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
                  worker.availability_status === 'AVAILABLE'
                    ? 'bg-emerald-700 text-white shadow-xs'
                    : 'text-slate-600 hover:bg-slate-200'
                }`}
              >
                ● Available for Jobs
              </button>
              <button
                onClick={() => handleToggleAvailability('BUSY')}
                className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
                  worker.availability_status === 'BUSY'
                    ? 'bg-amber-600 text-white shadow-xs'
                    : 'text-slate-600 hover:bg-slate-200'
                }`}
              >
                ● On Site / Busy
              </button>
              <button
                onClick={() => handleToggleAvailability('OFF_DUTY')}
                className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
                  worker.availability_status === 'OFF_DUTY'
                    ? 'bg-slate-700 text-white shadow-xs'
                    : 'text-slate-600 hover:bg-slate-200'
                }`}
              >
                ● Off Duty
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Overview Cards: Financials & Welfare Fund */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Total Disbursed Earnings</span>
            <Wallet className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">
            ₹{worker.total_earnings.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Direct to Bank/Cash reconciliations</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Worker Social Security Pool</span>
            <Shield className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-emerald-700 mt-2">
            ₹{worker.welfare_balance.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">5% contribution saved from every job</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Weekly Workload</span>
            <Clock className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">
            {worker.weekly_jobs_count} Jobs
          </div>
          <div className="text-[11px] text-emerald-600 mt-1 font-medium">Balanced / Optimal capacity</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Historical Completion</span>
            <Award className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">
            {worker.total_jobs} Completed
          </div>
          <div className="text-[11px] text-slate-500 mt-1">98% Reliability Trust metric</div>
        </div>
      </div>

      {/* Two Column Layout: Assigned Jobs & Social Security Schemes */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Assigned Active Jobs (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">
              Assigned Job Queue & Work Execution
            </h2>
            <span className="text-xs text-slate-500">{assignedJobs.length} Jobs in Queue</span>
          </div>

          {assignedJobs.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-lg p-8 text-center text-slate-500 text-xs">
              No active jobs currently in your queue. You are ready for automated allocation dispatch!
            </div>
          ) : (
            <div className="space-y-3">
              {assignedJobs.map(job => (
                <div key={job.id} className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900 text-sm font-mono">{job.booking_ref}</span>
                        <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                          job.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' :
                          job.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' :
                          job.status === 'ACCEPTED' ? 'bg-purple-100 text-purple-800' :
                          'bg-amber-100 text-amber-800'
                        }`}>
                          {job.status}
                        </span>
                      </div>
                      <h3 className="font-semibold text-slate-800 text-sm mt-1">{job.service_name}</h3>
                    </div>

                    <div className="text-right">
                      <div className="text-xs text-slate-500">Gross Price</div>
                      <div className="font-bold text-slate-900 text-base">₹{job.final_price || job.price_estimate}</div>
                    </div>
                  </div>

                  <div className="text-xs text-slate-600 space-y-1 bg-slate-50 p-2.5 rounded border border-slate-100">
                    <div className="flex items-center gap-1.5 text-slate-700">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span>{job.address}</span>
                    </div>
                    {job.customer_notes && (
                      <div className="text-slate-500 text-[11px]">
                        <strong>Customer note:</strong> {job.customer_notes}
                      </div>
                    )}
                  </div>

                  {/* Actions for Worker */}
                  <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                    {job.status === 'ASSIGNED' && (
                      <button
                        onClick={() => handleJobAction(job.id, 'ACCEPTED')}
                        className="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded text-xs font-semibold flex items-center gap-1 shadow-xs"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Accept Job</span>
                      </button>
                    )}

                    {job.status === 'ACCEPTED' && (
                      <button
                        onClick={() => handleJobAction(job.id, 'IN_PROGRESS')}
                        className="px-3.5 py-1.5 bg-blue-700 hover:bg-blue-800 text-white rounded text-xs font-semibold flex items-center gap-1 shadow-xs"
                      >
                        <Play className="w-3.5 h-3.5" />
                        <span>Start Work (At Site)</span>
                      </button>
                    )}

                    {job.status === 'IN_PROGRESS' && (
                      <button
                        onClick={() => handleJobAction(job.id, 'COMPLETED')}
                        className="px-3.5 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded text-xs font-semibold flex items-center gap-1 shadow-xs"
                      >
                        <CheckSquare className="w-3.5 h-3.5" />
                        <span>Mark Job Completed</span>
                      </button>
                    )}

                    {job.status === 'COMPLETED' && (
                      <span className="text-xs font-medium text-emerald-800 flex items-center gap-1">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        Job Completed & Reconciled
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Social Security & e-Shram Insurance Portfolio (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">
              e-Shram & Welfare Portfolio
            </h2>
            <span className="text-xs text-emerald-700 font-semibold">Active Coverage</span>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs space-y-4">
            <p className="text-xs text-slate-500">
              Government and cooperative-backed social security policies linked to this worker ID.
            </p>

            {welfareData?.records?.map((rec: any) => (
              <div key={rec.id} className="border border-slate-200 rounded-md p-3.5 space-y-2 text-xs">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="font-semibold text-slate-900 block">{rec.scheme_name}</span>
                    <span className="text-slate-500 font-mono text-[11px]">Policy: {rec.policy_number}</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    rec.status === 'ACTIVE' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                  }`}>
                    {rec.status}
                  </span>
                </div>

                <div className="flex justify-between items-center text-slate-600 pt-2 border-t border-slate-100 text-[11px]">
                  <span>Coverage: <strong>₹{rec.coverage_amount.toLocaleString()}</strong></span>
                  <span>Expires: {rec.end_date}</span>
                </div>
              </div>
            ))}

            {welfareData?.alerts?.length > 0 && (
              <div className="bg-amber-50 border border-amber-300 rounded-md p-3 space-y-1.5 text-xs text-amber-900">
                <div className="flex items-center gap-1.5 font-bold">
                  <AlertCircle className="w-4 h-4 text-amber-700" />
                  <span>Renewal Notice</span>
                </div>
                {welfareData.alerts.map((al: any, idx: number) => (
                  <p key={idx} className="text-[11px] text-amber-800">{al.message}</p>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
