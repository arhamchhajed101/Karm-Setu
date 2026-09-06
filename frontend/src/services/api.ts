/**
 * KarmSetu API Service Client
 * Connects frontend to the FastAPI backend running on port 8000 (via Vite proxy /api/v1)
 */

const rawApiUrl = import.meta.env.VITE_API_URL || '';
const formattedApiUrl = (rawApiUrl.startsWith('http://') || rawApiUrl.startsWith('https://') || rawApiUrl === '')
  ? rawApiUrl
  : `https://${rawApiUrl}`;

const API_BASE = formattedApiUrl ? `${formattedApiUrl.replace(/\/$/, '')}/api/v1` : '/api/v1';

export interface User {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  role: 'customer' | 'worker' | 'cooperative_admin' | 'supervisor';
  worker_profile?: any;
  customer_profile?: any;
}

export interface Cooperative {
  id: number;
  name: string;
  registration_id: string;
  state: string;
  district: string;
  address?: string;
  contact_phone?: string;
  contact_email?: string;
  type: string;
  verification_status: string;
  service_categories: string[];
  commission_rate: number;
  welfare_contribution_rate: number;
  total_members: number;
  total_jobs_completed: number;
  welfare_fund_pool: number;
}

export interface ServiceItem {
  id: number;
  cooperative_id: number;
  cooperative_name?: string;
  category: string;
  name: string;
  description?: string;
  pricing_model: string;
  base_price: number;
  estimated_duration_minutes: number;
  emergency_multiplier: number;
  required_skills: string[];
}

export interface WorkerItem {
  id: number;
  user_id: number;
  cooperative_id: number;
  cooperative_name?: string;
  name: string;
  phone: string;
  photo_url?: string;
  skills: string[];
  experience_years: number;
  certificates: any[];
  verification_status: string;
  verification_ref_id?: string;
  rating: number;
  total_jobs: number;
  weekly_jobs_count: number;
  reliability_score: number;
  availability_status: 'AVAILABLE' | 'BUSY' | 'OFF_DUTY';
  latitude: number;
  longitude: number;
  address?: string;
  welfare_status: string;
  total_earnings: number;
  welfare_balance: number;
}

export interface JobItem {
  id: number;
  booking_ref: string;
  customer_id: number;
  customer_name?: string;
  customer_phone?: string;
  service_id: number;
  service_name?: string;
  service_category?: string;
  cooperative_id: number;
  cooperative_name?: string;
  assigned_worker_id?: number;
  assigned_worker_name?: string;
  assigned_worker_phone?: string;
  status: 'REQUESTED' | 'ASSIGNED' | 'ACCEPTED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  slot_start: string;
  slot_end: string;
  address: string;
  latitude: number;
  longitude: number;
  is_emergency: boolean;
  price_estimate: number;
  final_price?: number;
  payment_status: string;
  payment_method: string;
  customer_notes?: string;
  worker_notes?: string;
  supervisor_verified: boolean;
  created_at: string;
}

export interface AllocationCandidate {
  worker_id: number;
  worker_name: string;
  worker_phone: string;
  photo_url?: string;
  rating: number;
  verification_status: string;
  distance_km: number;
  weekly_jobs: number;
  scores: {
    skill_score: number;
    availability_score: number;
    distance_score: number;
    reliability_score: number;
    workload_score: number;
    fairness_score: number;
    total_score: number;
  };
  narrative_explanation: string;
}

export interface AllocationEvaluation {
  job_id: number;
  booking_ref: string;
  service_name: string;
  service_category: string;
  candidates: AllocationCandidate[];
  recommended_worker_id?: number;
  recommended_worker_name?: number;
  top_recommendation_reason?: string;
  total_eligible_workers: number;
}

export interface ForecastResponse {
  zone: string;
  service_category: string;
  current_active_workers: number;
  daily_forecast: {
    date: string;
    predicted_demand: number;
    confidence_low: number;
    confidence_high: number;
    seasonal_factor: number;
  }[];
  total_projected_demand_7d: number;
  capacity_status: 'DEFICIT' | 'BALANCED' | 'SURPLUS';
  projected_utilization_pct: number;
  recommendation: string;
}

export interface InstitutionalProject {
  id: number;
  client_name: string;
  title: string;
  description?: string;
  cooperative_id: number;
  cooperative_name?: string;
  supervisor_id?: number;
  supervisor_name?: string;
  required_headcount: number;
  skills_breakdown: Record<string, number>;
  assigned_workers: number[];
  start_date: string;
  end_date: string;
  budget: number;
  amount_disbursed: number;
  status: string;
  progress_percentage: number;
  milestones: { title: string; completed: boolean }[];
}

import {
  MOCK_COOPERATIVES,
  MOCK_SERVICES,
  MOCK_WORKERS,
  MOCK_JOBS,
  MOCK_ALLOCATION_EVALUATION,
  MOCK_FORECAST,
  MOCK_PROJECTS,
} from './mockData';

// In-memory state for interactive mutations when backend is offline
let stateJobs = [...MOCK_JOBS];
let stateWorkers = [...MOCK_WORKERS];

function getMockFallback<T>(endpoint: string, options: RequestInit = {}): T {
  console.info(`[KarmSetu GitHub Pages Mode] Serving local simulation for: ${endpoint}`);
  const method = (options.method || 'GET').toUpperCase();
  let body: any = {};
  try {
    if (options.body) body = JSON.parse(options.body as string);
  } catch (e) {
    body = {};
  }

  // Auth
  if (endpoint.startsWith('/auth/login')) {
    const email = body.email || 'customer@karmsetu.in';
    let role = 'customer';
    let full_name = 'Vikram Malhotra';
    if (email.includes('admin')) { role = 'cooperative_admin'; full_name = 'Anil Sharma (Society Secretary)'; }
    else if (email.includes('worker')) { role = 'worker'; full_name = 'Ramesh Kumar Verma'; }
    else if (email.includes('supervisor')) { role = 'supervisor'; full_name = 'Rajesh Tyagi (Govt Inspector)'; }
    return { access_token: 'mock-jwt-token-karmsetu', token_type: 'bearer', user_id: 1, role, full_name } as unknown as T;
  }
  if (endpoint.startsWith('/auth/me')) {
    const role = localStorage.getItem('karmsetu_demo_role') || 'customer';
    return {
      id: 1,
      email: `${role}@karmsetu.in`,
      full_name: role === 'cooperative_admin' ? 'Anil Sharma (Coop Admin)' : role === 'worker' ? 'Ramesh Kumar Verma' : 'Vikram Malhotra',
      role,
      worker_profile: role === 'worker' ? stateWorkers[0] : undefined,
    } as unknown as T;
  }

  // Cooperatives
  if (endpoint === '/cooperatives') return MOCK_COOPERATIVES as unknown as T;
  if (endpoint.includes('/kpis')) {
    return {
      total_workers: 64,
      active_today: 42,
      completed_jobs: 412,
      total_revenue: 284500,
      welfare_pool: 42675,
      fairness_index: '0.89 / 1.0 (Optimal)',
      avg_hourly_earnings: 320,
    } as unknown as T;
  }
  if (endpoint.includes('/roster')) return stateWorkers as unknown as T;

  // Services & Estimates
  if (endpoint.startsWith('/services')) return MOCK_SERVICES as unknown as T;
  if (endpoint.startsWith('/jobs/estimate')) {
    const service = MOCK_SERVICES.find(s => s.id === body.service_id) || MOCK_SERVICES[0];
    const base = service.base_price;
    const travel = 50;
    const mult = body.is_emergency ? (service.emergency_multiplier || 1.4) : 1.0;
    const est = Math.round((base + travel) * mult);
    return {
      service_id: service.id,
      service_name: service.name,
      base_price: base,
      travel_fee: travel,
      emergency_surcharge: body.is_emergency ? Math.round(base * (mult - 1)) : 0,
      estimated_total: est,
      cooperative_share: Math.round(est * 0.15),
      worker_share: Math.round(est * 0.80),
      welfare_share: Math.round(est * 0.05),
    } as unknown as T;
  }

  // Workers
  if (endpoint.startsWith('/workers') && endpoint.includes('/availability')) {
    const id = parseInt(endpoint.split('/')[2]);
    const worker = stateWorkers.find(w => w.id === id) || stateWorkers[0];
    worker.availability_status = body.availability_status || 'AVAILABLE';
    return worker as unknown as T;
  }
  if (endpoint.startsWith('/workers') && endpoint.includes('/earnings')) {
    return {
      total_earnings: 48600,
      weekly_earnings: 5800,
      welfare_balance: 14200,
      settlement_count: 142,
      schemes: [
        { name: 'PM Shram Yogi Maan-Dhan (PM-SYM)', status: 'ACTIVE', monthly_contribution: 100 },
        { name: 'Pradhan Mantri Suraksha Bima Yojana (PMSBY)', status: 'ACTIVE', sum_insured: 200000 },
      ],
    } as unknown as T;
  }
  if (endpoint.startsWith('/workers')) return stateWorkers as unknown as T;

  // Jobs
  if (endpoint.startsWith('/jobs') && method === 'POST' && !endpoint.includes('status') && !endpoint.includes('supervisor-verify')) {
    const newJob: JobItem = {
      id: 100 + stateJobs.length + 1,
      booking_ref: `KS-JOB-2026-0${900 + stateJobs.length}`,
      customer_id: 3,
      customer_name: 'Vikram Malhotra',
      customer_phone: '+91 98111 22334',
      service_id: body.service_id || 1,
      service_name: (MOCK_SERVICES.find(s => s.id === body.service_id)?.name) || 'Service Request',
      service_category: (MOCK_SERVICES.find(s => s.id === body.service_id)?.category) || 'General',
      cooperative_id: 1,
      cooperative_name: 'Delhi Labour & Construction Cooperative Society',
      status: 'REQUESTED',
      slot_start: body.slot_start || new Date().toISOString(),
      slot_end: body.slot_end || new Date(Date.now() + 7200000).toISOString(),
      address: body.address || 'Central Delhi',
      latitude: body.latitude || 28.6139,
      longitude: body.longitude || 77.2090,
      is_emergency: !!body.is_emergency,
      price_estimate: 549.0,
      payment_status: 'PENDING',
      payment_method: body.payment_method || 'UPI',
      customer_notes: body.customer_notes || 'Booked via KarmSetu web portal',
      supervisor_verified: false,
      created_at: new Date().toISOString(),
    };
    stateJobs = [newJob, ...stateJobs];
    return newJob as unknown as T;
  }
  if (endpoint.includes('/status')) {
    const parts = endpoint.split('/');
    const jobId = parseInt(parts[2]);
    const job = stateJobs.find(j => j.id === jobId);
    if (job) {
      job.status = body.status as any;
      if (body.final_price) job.final_price = body.final_price;
      return job as unknown as T;
    }
  }
  if (endpoint.includes('/supervisor-verify')) {
    const parts = endpoint.split('/');
    const jobId = parseInt(parts[2]);
    const job = stateJobs.find(j => j.id === jobId);
    if (job) {
      job.supervisor_verified = true;
      return job as unknown as T;
    }
  }
  if (endpoint.startsWith('/jobs')) return stateJobs as unknown as T;

  // Allocation
  if (endpoint.startsWith('/allocation/evaluate')) return MOCK_ALLOCATION_EVALUATION as unknown as T;
  if (endpoint.startsWith('/allocation/auto-assign')) {
    const parts = endpoint.split('/');
    const jobId = parseInt(parts[3]);
    const job = stateJobs.find(j => j.id === jobId);
    if (job) {
      job.status = 'ASSIGNED';
      job.assigned_worker_id = 3;
      job.assigned_worker_name = 'Mohd. Imran Qureshi';
      job.assigned_worker_phone = '+91 98188 45678';
    }
    return { success: true, message: 'Worker auto-assigned based on explainable 6-dimension scoring' } as unknown as T;
  }
  if (endpoint.startsWith('/allocation/manual-assign')) {
    const parts = endpoint.split('/');
    const jobId = parseInt(parts[3]);
    const job = stateJobs.find(j => j.id === jobId);
    if (job) {
      job.status = 'ASSIGNED';
      const w = stateWorkers.find(wk => wk.id === body.worker_id) || stateWorkers[0];
      job.assigned_worker_id = w.id;
      job.assigned_worker_name = w.name;
      job.assigned_worker_phone = w.phone;
    }
    return { success: true, message: 'Worker manually assigned by coordinator' } as unknown as T;
  }

  // Settlements
  if (endpoint.startsWith('/settlements/simulate-payment')) {
    return { success: true, payment_id: 'TXN-SIM-2026-9901', status: 'PAID' } as unknown as T;
  }
  if (endpoint.startsWith('/settlements/cooperative')) {
    return {
      total_gross: 284500,
      worker_disbursed: 227600,
      cooperative_retained: 42675,
      welfare_pool_funded: 14225,
      settlement_count: 412,
    } as unknown as T;
  }
  if (endpoint.startsWith('/settlements')) {
    return [
      { id: 1, booking_ref: 'KS-JOB-2026-0888', gross_amount: 850, worker_amount: 680, coop_amount: 127.5, welfare_amount: 42.5, status: 'SETTLED', created_at: new Date(Date.now() - 86400000).toISOString() },
      { id: 2, booking_ref: 'KS-JOB-2026-0889', gross_amount: 499, worker_amount: 399.2, coop_amount: 74.85, welfare_amount: 24.95, status: 'SETTLED', created_at: new Date(Date.now() - 172800000).toISOString() },
    ] as unknown as T;
  }

  // Welfare
  if (endpoint.startsWith('/welfare/worker')) {
    return {
      worker_id: 1,
      eshram_id: 'UAN-9921-4829-1029',
      welfare_balance: 14200,
      schemes: [
        { name: 'PM Shram Yogi Maan-Dhan', policy_no: 'PMSYM-2023-88192', status: 'ACTIVE', renewal_date: '2026-11-30' },
        { name: 'Pradhan Mantri Suraksha Bima Yojana', policy_no: 'PMSBY-2024-55102', status: 'ACTIVE', renewal_date: '2026-05-31' },
      ],
    } as unknown as T;
  }
  if (endpoint.startsWith('/welfare/alerts')) {
    return [
      { id: 1, worker_name: 'Ramesh Kumar Verma', scheme: 'PMSBY Insurance Renewal', message: 'Annual accident insurance premium deduction due in 18 days', urgency: 'MEDIUM' },
      { id: 2, worker_name: 'Suresh Chandra Sharma', scheme: 'State BOCW Card', message: 'Triennial biometric verification window open at District Welfare Office', urgency: 'LOW' },
    ] as unknown as T;
  }

  // Analytics
  if (endpoint.startsWith('/analytics/forecast')) return MOCK_FORECAST as unknown as T;
  if (endpoint.startsWith('/analytics/skill-gaps')) {
    return [
      {
        zone: 'Central Delhi',
        service_category: 'Plumbing',
        required_skills: ['Pipe Fitting', 'Drainage Cleansing'],
        current_worker_count: 18,
        projected_peak_demand: 24,
        deficit_count: 6,
        severity: 'HIGH',
        action_item: 'Activate off-duty standby roster and invite cross-cooperative roster sharing.',
      },
      {
        zone: 'Central Delhi',
        service_category: 'Carpentry',
        required_skills: ['Joinery', 'Locksmithing'],
        current_worker_count: 12,
        projected_peak_demand: 14,
        deficit_count: 2,
        severity: 'MEDIUM',
        action_item: 'Schedule apprenticeship transition for junior artisans before weekend peak.',
      },
      {
        zone: 'Central Delhi',
        service_category: 'Electrical',
        required_skills: ['Wiring', 'Safety Compliance'],
        current_worker_count: 26,
        projected_peak_demand: 22,
        deficit_count: 0,
        severity: 'LOW',
        action_item: 'Supply is balanced with healthy reserve capacity.',
      },
    ] as unknown as T;
  }
  if (endpoint.startsWith('/analytics/heatmap')) {
    return [
      { zone: 'Connaught Place', latitude: 28.6315, longitude: 77.2167, total_bookings: 184, intensity: 0.95 },
      { zone: 'Defence Colony', latitude: 28.5729, longitude: 77.2304, total_bookings: 142, intensity: 0.78 },
      { zone: 'Saket District Centre', latitude: 28.5244, longitude: 77.2066, total_bookings: 126, intensity: 0.72 },
      { zone: 'Karol Bagh Market', latitude: 28.6514, longitude: 77.1907, total_bookings: 110, intensity: 0.65 },
      { zone: 'Janakpuri West', latitude: 28.6280, longitude: 77.0800, total_bookings: 96, intensity: 0.58 },
    ] as unknown as T;
  }
  if (endpoint.startsWith('/analytics/utilization')) {
    return {
      cooperative_id: 1,
      average_utilization_rate: 3.4,
      fairness_gini_coefficient: 0.21,
      overworked_workers_count: 2,
      underutilized_workers_count: 5,
      optimal_workers_count: 57,
      utilization_distribution: [
        { bracket: '0-2 jobs/wk', worker_count: 5 },
        { bracket: '3-5 jobs/wk', worker_count: 57 },
        { bracket: '6+ jobs/wk', worker_count: 2 },
      ],
    } as unknown as T;
  }

  // Institutional
  if (endpoint.startsWith('/institutional/projects')) return MOCK_PROJECTS as unknown as T;

  return {} as unknown as T;
}

// Token storage helper
export const getStoredToken = () => localStorage.getItem('karmsetu_token');
export const setStoredToken = (token: string) => localStorage.setItem('karmsetu_token', token);
export const removeStoredToken = () => localStorage.removeItem('karmsetu_token');

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      return getMockFallback<T>(endpoint, options);
    }

    return await response.json();
  } catch (error) {
    return getMockFallback<T>(endpoint, options);
  }
}

export const api = {
  // Authentication
  login: (email: string, password: string = 'Password123!') =>
    request<{ access_token: string; token_type: string; user_id: number; role: string; full_name: string }>(
      '/auth/login',
      { method: 'POST', body: JSON.stringify({ email, password }) }
    ),

  getMe: () => request<User>('/auth/me'),

  // Cooperatives
  getCooperatives: () => request<Cooperative[]>('/cooperatives'),
  getCooperativeKPIs: (id: number) => request<any>(`/cooperatives/${id}/kpis`),
  getCooperativeRoster: (id: number) => request<any[]>(`/cooperatives/${id}/roster`),

  // Services
  getServices: (category?: string) =>
    request<ServiceItem[]>(`/services${category ? `?category=${encodeURIComponent(category)}` : ''}`),
  
  getEstimate: (service_id: number, lat: number = 28.6139, lon: number = 77.2090, is_emergency: boolean = false) =>
    request<any>('/jobs/estimate', {
      method: 'POST',
      body: JSON.stringify({ service_id, latitude: lat, longitude: lon, is_emergency }),
    }),

  // Workers
  getWorkers: (coopId?: number) =>
    request<WorkerItem[]>(`/workers${coopId ? `?cooperative_id=${coopId}` : ''}`),
  
  updateWorkerAvailability: (id: number, status: 'AVAILABLE' | 'BUSY' | 'OFF_DUTY') =>
    request<WorkerItem>(`/workers/${id}/availability`, {
      method: 'PATCH',
      body: JSON.stringify({ availability_status: status }),
    }),

  getWorkerEarnings: (id: number) => request<any>(`/workers/${id}/earnings`),

  // Jobs
  getJobs: (status?: string, coopId?: number) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (coopId) params.append('cooperative_id', coopId.toString());
    return request<JobItem[]>(`/jobs?${params.toString()}`);
  },

  createJob: (jobData: {
    service_id: number;
    slot_start: string;
    slot_end: string;
    address: string;
    latitude: number;
    longitude: number;
    is_emergency: boolean;
    customer_notes?: string;
    payment_method?: string;
  }) =>
    request<JobItem>('/jobs', {
      method: 'POST',
      body: JSON.stringify(jobData),
    }),

  updateJobStatus: (id: number, status: string, notes?: string, final_price?: number) =>
    request<JobItem>(`/jobs/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, notes, final_price }),
    }),

  supervisorVerifyJob: (id: number) =>
    request<JobItem>(`/jobs/${id}/supervisor-verify`, { method: 'POST' }),

  // Smart Allocation
  evaluateAllocation: (jobId: number) =>
    request<AllocationEvaluation>(`/allocation/evaluate/${jobId}`, { method: 'POST' }),

  autoAssignJob: (jobId: number) =>
    request<any>(`/allocation/auto-assign/${jobId}`, { method: 'POST' }),

  manualAssignJob: (jobId: number, workerId: number, notes?: string) =>
    request<any>(`/allocation/manual-assign/${jobId}`, {
      method: 'POST',
      body: JSON.stringify({ worker_id: workerId, coordinator_notes: notes }),
    }),

  // Settlements & Payments
  getSettlements: () => request<any[]>('/settlements'),
  simulatePayment: (jobId: number, amount: number, method: string = 'ONLINE_SIMULATED') =>
    request<any>('/settlements/simulate-payment', {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId, amount, payment_method: method, simulate_status: 'PAID' }),
    }),
  getSettlementSummary: (coopId: number) =>
    request<any>(`/settlements/cooperative/${coopId}/summary`),

  // Welfare & Insurance
  getWorkerWelfare: (workerId: number) =>
    request<any>(`/welfare/worker/${workerId}`),
  getWelfareAlerts: () => request<any[]>('/welfare/alerts'),

  // Analytics & Forecasting
  getDemandForecast: (zone: string = 'Central Delhi', category: string = 'Plumbing', days: number = 7) =>
    request<ForecastResponse>(`/analytics/forecast?zone=${encodeURIComponent(zone)}&category=${encodeURIComponent(category)}&days_ahead=${days}`),
  getSkillGaps: (zone: string = 'Central Delhi') =>
    request<any[]>(`/analytics/skill-gaps?zone=${encodeURIComponent(zone)}`),
  getHeatmap: () => request<any[]>('/analytics/heatmap'),
  getUtilization: (coopId: number = 1) =>
    request<any>(`/analytics/utilization/${coopId}`),

  // Institutional
  getProjects: () => request<InstitutionalProject[]>('/institutional/projects'),
  getProject: (id: number) => request<InstitutionalProject>(`/institutional/projects/${id}`),
};
