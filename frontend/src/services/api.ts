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

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: 'Network error occurred' }));
    throw new Error(errorBody.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
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
