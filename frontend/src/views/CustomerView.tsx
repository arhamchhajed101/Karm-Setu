import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { ServiceItem, JobItem } from '../services/api';
import { ShieldCheck, Clock, CheckCircle2, ChevronRight, CreditCard } from 'lucide-react';

export const CustomerView: React.FC = () => {
  const [services, setServices] = useState<ServiceItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedService, setSelectedService] = useState<ServiceItem | null>(null);
  const [myBookings, setMyBookings] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [bookingSuccess, setBookingSuccess] = useState<string | null>(null);

  // Booking Form State
  const [address, setAddress] = useState<string>('Flat 304, Green Valley Apts, Daryaganj, New Delhi');
  const [slotDate, setSlotDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [slotTime, setSlotTime] = useState<string>('14:00');
  const [isEmergency, setIsEmergency] = useState<boolean>(false);
  const [customerNotes, setCustomerNotes] = useState<string>('');
  const [paymentMethod] = useState<string>('ONLINE_SIMULATED');

  // Load services and bookings
  const loadData = async () => {
    try {
      setLoading(true);
      const srvData = await api.getServices();
      setServices(srvData);
      if (srvData.length > 0 && !selectedService) {
        setSelectedService(srvData[0]);
      }
      const jobs = await api.getJobs();
      setMyBookings(jobs.slice(0, 10));
    } catch (err) {
      console.error('Error fetching services', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const categories = ['All', 'Plumbing', 'Electrical', 'Carpentry', 'Masonry', 'Painting', 'Welding'];

  const filteredServices = selectedCategory === 'All'
    ? services
    : services.filter(s => s.category.toLowerCase() === selectedCategory.toLowerCase());

  // Transparent calculation
  const travelFee = 50.0;
  const basePrice = selectedService ? selectedService.base_price : 0;
  const emergencySurge = isEmergency && selectedService ? Math.round(basePrice * (selectedService.emergency_multiplier - 1.0)) : 0;
  const estimatedTotal = basePrice + travelFee + emergencySurge;

  const handleCreateBooking = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedService) return;

    try {
      const slotStart = new Date(`${slotDate}T${slotTime}:00Z`).toISOString();
      const slotEnd = new Date(new Date(slotStart).getTime() + (selectedService.estimated_duration_minutes * 60000)).toISOString();

      const newJob = await api.createJob({
        service_id: selectedService.id,
        slot_start: slotStart,
        slot_end: slotEnd,
        address,
        latitude: 28.6139,
        longitude: 77.2090,
        is_emergency: isEmergency,
        customer_notes: customerNotes,
        payment_method: paymentMethod,
      });

      setBookingSuccess(`Booking confirmed! Reference: ${newJob.booking_ref}. The cooperative allocation engine is assigning a verified worker.`);
      setCustomerNotes('');
      loadData();
    } catch (err: any) {
      alert(`Booking failed: ${err.message}`);
    }
  };

  const handleSimulatePayment = async (jobId: number, amount: number) => {
    try {
      await api.simulatePayment(jobId, amount, 'ONLINE_SIMULATED');
      alert(`Payment of ₹${amount} simulated successfully! Revenue ledger disbursed to worker, cooperative, and welfare fund.`);
      loadData();
    } catch (err: any) {
      alert(`Payment error: ${err.message}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8 space-y-8">
      {/* Sober Header Banner */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold mb-2">
              <ShieldCheck className="w-3.5 h-3.5" />
              Verified Cooperative Network
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Book Skilled Labour Services
            </h1>
            <p className="text-sm text-slate-600 mt-1 max-w-2xl">
              All services are delivered by members of certified labour cooperatives. Transparent pricing, verified identity credentials, and social security-backed workforce.
            </p>
          </div>

          <div className="flex items-center gap-6 border-t md:border-t-0 md:border-l border-slate-200 pt-4 md:pt-0 md:pl-6 text-xs text-slate-600">
            <div>
              <div className="font-semibold text-slate-900 text-base">47,182+</div>
              <div>Registered Coops</div>
            </div>
            <div>
              <div className="font-semibold text-slate-900 text-base">₹50</div>
              <div>Standard Travel Fee</div>
            </div>
            <div>
              <div className="font-semibold text-emerald-700 text-base">100%</div>
              <div>Audited Ledger</div>
            </div>
          </div>
        </div>
      </div>

      {bookingSuccess && (
        <div className="bg-emerald-50 border border-emerald-300 rounded-lg p-4 flex items-start gap-3 text-emerald-900 text-sm">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium">{bookingSuccess}</p>
          </div>
          <button onClick={() => setBookingSuccess(null)} className="text-emerald-700 font-bold hover:text-emerald-900 text-xs">
            Dismiss
          </button>
        </div>
      )}

      {/* Main Booking Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Catalogue & Category Filter (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Category Tabs */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3.5 py-1.5 rounded-md text-xs font-semibold whitespace-nowrap transition-colors ${
                  selectedCategory === cat
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Service Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {loading ? (
              <div className="col-span-2 p-8 text-center text-slate-400 text-xs bg-white rounded-lg border border-slate-200">
                Loading cooperative service catalogue...
              </div>
            ) : (
              filteredServices.map(srv => {
                const isSelected = selectedService?.id === srv.id;
                return (
                  <div
                    key={srv.id}
                    onClick={() => setSelectedService(srv)}
                    className={`cursor-pointer rounded-lg p-4 border transition-all ${
                      isSelected
                        ? 'bg-amber-50/50 border-amber-500 shadow-sm ring-1 ring-amber-400/50'
                        : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/60'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                        {srv.category}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded bg-slate-100 font-medium text-slate-700">
                        {srv.pricing_model === 'FIXED' ? 'Fixed Fee' : srv.pricing_model === 'HOURLY' ? 'Hourly' : 'Diagnostic'}
                      </span>
                    </div>

                    <h3 className="font-semibold text-slate-900 text-sm mt-1">
                      {srv.name}
                    </h3>

                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                      {srv.description}
                    </p>

                    <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-100 text-xs">
                      <div className="flex items-center gap-1 text-slate-500">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{srv.estimated_duration_minutes} mins</span>
                      </div>
                      <div className="font-bold text-slate-900 text-base">
                        ₹{srv.base_price}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: Transparent Upfront Estimate & Booking Form (5 cols) */}
        <div className="lg:col-span-5">
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-xs sticky top-24 space-y-6">
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Service Order & Transparent Estimate
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Full breakdown before booking. No surge hidden charges.
              </p>
            </div>

            {selectedService ? (
              <form onSubmit={handleCreateBooking} className="space-y-4 text-xs">
                {/* Selected service summary */}
                <div className="bg-slate-50 p-3 rounded-md border border-slate-200 flex justify-between items-center">
                  <div>
                    <span className="text-slate-500 text-[11px] block">{selectedService.category}</span>
                    <span className="font-semibold text-slate-800">{selectedService.name}</span>
                  </div>
                  <span className="font-bold text-slate-900 text-sm">₹{selectedService.base_price}</span>
                </div>

                {/* Date and Time Slot */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Date</label>
                    <input
                      type="date"
                      value={slotDate}
                      onChange={e => setSlotDate(e.target.value)}
                      className="w-full border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800 focus:outline-none focus:border-slate-800"
                      required
                    />
                  </div>
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Time Slot</label>
                    <select
                      value={slotTime}
                      onChange={e => setSlotTime(e.target.value)}
                      className="w-full border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800 focus:outline-none focus:border-slate-800"
                    >
                      <option value="09:00">09:00 AM - 10:00 AM</option>
                      <option value="11:00">11:00 AM - 12:00 PM</option>
                      <option value="14:00">02:00 PM - 03:00 PM</option>
                      <option value="16:00">04:00 PM - 05:00 PM</option>
                      <option value="18:00">06:00 PM - 07:00 PM</option>
                    </select>
                  </div>
                </div>

                {/* Service Address */}
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Service Address / Landmark</label>
                  <input
                    type="text"
                    value={address}
                    onChange={e => setAddress(e.target.value)}
                    placeholder="House / Flat No, Street, Landmark"
                    className="w-full border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800 focus:outline-none focus:border-slate-800"
                    required
                  />
                </div>

                {/* Priority Dispatch Toggle */}
                <div className="flex items-center gap-2 p-2.5 rounded border border-slate-200 bg-slate-50">
                  <input
                    type="checkbox"
                    id="emergency"
                    checked={isEmergency}
                    onChange={e => setIsEmergency(e.target.checked)}
                    className="rounded border-slate-300 text-amber-600 focus:ring-0"
                  />
                  <label htmlFor="emergency" className="text-slate-700 cursor-pointer select-none">
                    <span className="font-semibold text-slate-900 block">Emergency Priority Dispatch</span>
                    <span className="text-[11px] text-slate-500">Allocates nearest worker with priority guarantee (+25% surge)</span>
                  </label>
                </div>

                {/* Specific instructions */}
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Special Notes for Worker (Optional)</label>
                  <textarea
                    rows={2}
                    value={customerNotes}
                    onChange={e => setCustomerNotes(e.target.value)}
                    placeholder="E.g., Bring heavy pipe wrench, ring bell twice..."
                    className="w-full border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800 focus:outline-none focus:border-slate-800"
                  />
                </div>

                {/* Transparent Price Breakdown */}
                <div className="border-t border-slate-200 pt-3 space-y-1.5 text-xs text-slate-600">
                  <div className="flex justify-between">
                    <span>Base Service Price:</span>
                    <span className="font-medium text-slate-900">₹{basePrice.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Cooperative Standard Travel Fee:</span>
                    <span className="font-medium text-slate-900">₹{travelFee.toFixed(2)}</span>
                  </div>
                  {isEmergency && (
                    <div className="flex justify-between text-amber-800">
                      <span>Emergency Surge (25%):</span>
                      <span className="font-medium">₹{emergencySurge.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm font-bold text-slate-900 pt-2 border-t border-slate-200">
                    <span>Total Estimate:</span>
                    <span>₹{estimatedTotal.toFixed(2)}</span>
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white rounded-md font-semibold text-sm transition-colors shadow-xs flex items-center justify-center gap-2"
                >
                  <span>Confirm Booking</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </form>
            ) : (
              <p className="text-slate-500 text-xs">Please select a service from the catalogue.</p>
            )}
          </div>
        </div>
      </div>

      {/* Active Customer Bookings & Live Timeline */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-xs space-y-4">
        <h2 className="text-base font-bold text-slate-900">
          Your Bookings & State Machine Tracking
        </h2>
        <p className="text-xs text-slate-500">
          Track lifecycle progress (`REQUESTED` → `ASSIGNED` → `ACCEPTED` → `IN_PROGRESS` → `COMPLETED`)
        </p>

        <div className="divide-y divide-slate-100">
          {myBookings.map(job => (
            <div key={job.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-900 text-sm font-mono">{job.booking_ref}</span>
                  <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                    job.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' :
                    job.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' :
                    job.status === 'ACCEPTED' ? 'bg-purple-100 text-purple-800' :
                    job.status === 'ASSIGNED' ? 'bg-amber-100 text-amber-800' :
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

                <div className="text-xs text-slate-600">
                  <span className="font-semibold text-slate-800">{job.service_name}</span> • {job.address}
                </div>

                <div className="text-[11px] text-slate-500 flex items-center gap-3">
                  <span>Slot: {new Date(job.slot_start).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</span>
                  {job.assigned_worker_name && (
                    <span>Assigned Worker: <strong className="text-slate-700">{job.assigned_worker_name}</strong></span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-xs text-slate-500">Total Price</div>
                  <div className="font-bold text-slate-900 text-sm">₹{job.final_price || job.price_estimate}</div>
                </div>

                {job.status === 'COMPLETED' && job.payment_status === 'PENDING' && (
                  <button
                    onClick={() => handleSimulatePayment(job.id, job.final_price || job.price_estimate)}
                    className="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded text-xs font-semibold flex items-center gap-1.5 shadow-xs"
                  >
                    <CreditCard className="w-3.5 h-3.5" />
                    <span>Pay ₹{job.final_price || job.price_estimate} (Simulate)</span>
                  </button>
                )}

                {job.payment_status === 'SETTLED' && (
                  <span className="px-2.5 py-1 rounded bg-slate-100 text-slate-700 text-xs font-medium">
                    ✓ Paid & Settled
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
