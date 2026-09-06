import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { ForecastResponse } from '../services/api';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import { BarChart3, TrendingUp, CheckCircle2 } from 'lucide-react';

export const AnalyticsView: React.FC = () => {
  const [zone, setZone] = useState<string>('Central Delhi');
  const [category, setCategory] = useState<string>('Plumbing');
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [skillGaps, setSkillGaps] = useState<any[]>([]);
  const [heatmap, setHeatmap] = useState<any[]>([]);
  const [utilization, setUtilization] = useState<any>(null);

  const zones = [
    'Central Delhi',
    'South Delhi',
    'North Delhi',
    'West Delhi',
    'East Delhi',
    'Noida / Ghaziabad',
    'Gurugram',
  ];

  const categories = ['Plumbing', 'Electrical', 'Carpentry', 'Masonry', 'Painting'];

  const loadAnalytics = async () => {
    try {
      const fData = await api.getDemandForecast(zone, category, 7);
      setForecast(fData);
      const gData = await api.getSkillGaps(zone);
      setSkillGaps(gData);
      const hData = await api.getHeatmap();
      setHeatmap(hData);
      const uData = await api.getUtilization(1);
      setUtilization(uData);
    } catch (err) {
      console.error('Failed loading analytics', err);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, [zone, category]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8 space-y-8">
      {/* Analytics Header */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold mb-2">
              <BarChart3 className="w-3.5 h-3.5" />
              Workforce Intelligence Layer (PRD Section 3)
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Predictive Demand & Skill-Gap Analytics
            </h1>
            <p className="text-sm text-slate-600 mt-1 max-w-2xl">
              Time-series forecasting with seasonal indices (monsoon plumbing surges, summer HVAC spikes) to eliminate idle capacity and preempt trade shortages.
            </p>
          </div>

          {/* Filter Dropdowns */}
          <div className="flex flex-wrap items-center gap-2">
            <div>
              <label className="text-[10px] font-bold text-slate-500 block uppercase">Zone / District</label>
              <select
                value={zone}
                onChange={e => setZone(e.target.value)}
                className="bg-white border border-slate-300 rounded px-3 py-1.5 text-xs font-semibold text-slate-800 focus:outline-none focus:border-slate-800"
              >
                {zones.map(z => (
                  <option key={z} value={z}>{z}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[10px] font-bold text-slate-500 block uppercase">Trade Category</label>
              <select
                value={category}
                onChange={e => setCategory(e.target.value)}
                className="bg-white border border-slate-300 rounded px-3 py-1.5 text-xs font-semibold text-slate-800 focus:outline-none focus:border-slate-800"
              >
                {categories.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Utilization & Fairness metrics bar */}
        {utilization && (
          <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-slate-400 block text-[11px]">Fairness Gini Index</span>
              <strong className="text-emerald-700 text-sm font-mono">{utilization.fairness_gini_coefficient}</strong>
              <span className="text-[10px] text-slate-500 block">Low inequality</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[11px]">Average Utilization</span>
              <strong className="text-slate-900 text-sm">{utilization.average_utilization_rate} jobs/wk</strong>
            </div>
            <div>
              <span className="text-slate-400 block text-[11px]">Underutilized Members</span>
              <strong className="text-amber-700 text-sm">{utilization.underutilized_workers_count} workers</strong>
              <span className="text-[10px] text-slate-500 block">Given priority boost</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[11px]">Optimal Workload</span>
              <strong className="text-slate-900 text-sm">{utilization.optimal_workers_count} workers</strong>
            </div>
          </div>
        )}
      </div>

      {/* Forecast Chart & Capacity Status */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              7-Day Projected Service Demand ({category} in {zone})
            </h2>
            <p className="text-xs text-slate-500">
              Deterministic time-series model with upper and lower 95% confidence intervals
            </p>
          </div>

          {forecast && (
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                forecast.capacity_status === 'DEFICIT' ? 'bg-red-100 text-red-800' :
                forecast.capacity_status === 'SURPLUS' ? 'bg-amber-100 text-amber-800' :
                'bg-emerald-100 text-emerald-800'
              }`}>
                Capacity: {forecast.capacity_status}
              </span>
              <span className="text-xs text-slate-600">
                {forecast.projected_utilization_pct}% Projected Utilization
              </span>
            </div>
          )}
        </div>

        {/* Recommendation alert */}
        {forecast && (
          <div className="bg-slate-50 border border-slate-200 rounded p-3 text-xs text-slate-700 flex items-start gap-2.5">
            <TrendingUp className="w-4 h-4 text-slate-600 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-900">Operational Recommendation:</strong> {forecast.recommendation}
            </div>
          </div>
        )}

        {/* Recharts Area Chart */}
        <div className="h-72 w-full pt-2">
          {forecast ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={forecast.daily_forecast} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorDemand" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#d97706" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#d97706" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', borderRadius: '6px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Area type="monotone" dataKey="confidence_high" stroke="#94a3b8" strokeDasharray="3 3" fillOpacity={0} name="Confidence High (95%)" />
                <Area type="monotone" dataKey="predicted_demand" stroke="#b45309" strokeWidth={2.5} fill="url(#colorDemand)" name="Predicted Bookings" />
                <Area type="monotone" dataKey="confidence_low" stroke="#94a3b8" strokeDasharray="3 3" fillOpacity={0} name="Confidence Low (95%)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-400 text-xs">
              Loading forecast chart...
            </div>
          )}
        </div>
      </div>

      {/* Two Column Layout: Trade Deficit Alerts & Geospatial Density Heatmap */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Skill Gap & Shortage Warnings (6 cols) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">
              Trade Deficits & Skill Gap Alerts
            </h2>
            <span className="text-xs text-red-700 font-semibold">{skillGaps.length} Action Items</span>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs space-y-3">
            <p className="text-xs text-slate-500">
              Scans all trade categories in {zone} where upcoming peak demand exceeds verified supply.
            </p>

            {skillGaps.length === 0 ? (
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded text-emerald-800 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>All trade skills have sufficient roster supply for projected demand.</span>
              </div>
            ) : (
              <div className="space-y-2.5">
                {skillGaps.map((gap, idx) => (
                  <div key={idx} className="border border-red-200 bg-red-50/40 rounded p-3 text-xs space-y-1.5">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-red-900 text-sm">{gap.service_category} Deficit</span>
                      <span className="px-2 py-0.5 rounded bg-red-100 text-red-800 text-[10px] font-bold">
                        {gap.severity} PRIORITY
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-600 flex justify-between">
                      <span>Current Workers: <strong>{gap.current_worker_count}</strong></span>
                      <span>Peak Demand: <strong>{gap.projected_peak_demand} jobs/day</strong></span>
                      <span className="text-red-700 font-bold">Deficit: -{gap.deficit_count}</span>
                    </div>

                    <p className="text-[11px] text-slate-700 bg-white p-2 rounded border border-red-100 font-medium">
                      💡 {gap.action_item}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Geospatial Booking Density Heatmap (6 cols) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">
              Geospatial Demand Heatmap Density
            </h2>
            <span className="text-xs text-slate-500">Delhi NCR Grid</span>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-xs">
            <table className="w-full text-left border-collapse text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">District / Zone</th>
                  <th className="py-2.5 px-3">Coordinates</th>
                  <th className="py-2.5 px-3 text-right">30-Day Bookings</th>
                  <th className="py-2.5 px-3 text-right">Density Index</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {heatmap.map((pt, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-semibold text-slate-900">
                      {pt.zone}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-500">
                      {pt.latitude.toFixed(3)}, {pt.longitude.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3 text-right font-medium text-slate-800">
                      {pt.total_bookings}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <div className="inline-flex items-center gap-1.5">
                        <div className="w-16 bg-slate-100 h-2 rounded-full overflow-hidden">
                          <div
                            className="bg-amber-600 h-full rounded-full"
                            style={{ width: `${Math.min(pt.intensity * 100, 100)}%` }}
                          />
                        </div>
                        <span className="text-[10px] font-bold text-slate-700">{pt.intensity.toFixed(2)}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
