from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date

from app.db.session import Base


class DemandObservation(Base):
    __tablename__ = "demand_observations"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    zone = Column(String, nullable=False, index=True)  # e.g., "North Delhi", "South Delhi", "West Delhi", "East Delhi", "Central"
    service_category = Column(String, nullable=False, index=True)  # "Plumbing", "Electrical", etc.
    
    bookings_count = Column(Integer, default=0, nullable=False)
    completed_count = Column(Integer, default=0, nullable=False)
    cancellations_count = Column(Integer, default=0, nullable=False)
    
    avg_price = Column(Float, default=0.0)
    lead_time_hours = Column(Float, default=2.5)  # Average time from booking to arrival


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    zone = Column(String, nullable=False, index=True)
    service_category = Column(String, nullable=False, index=True)
    forecast_period = Column(String, nullable=False)  # e.g., "7_DAYS", "30_DAYS", "2026-W37"
    
    predicted_demand = Column(Float, nullable=False)
    confidence_interval_low = Column(Float, nullable=False)
    confidence_interval_high = Column(Float, nullable=False)
    seasonal_factor = Column(Float, default=1.0)  # e.g. 1.35 for monsoon plumbing surge
    
    historical_avg = Column(Float, default=0.0)
    trend_percentage = Column(Float, default=0.0)
    
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
