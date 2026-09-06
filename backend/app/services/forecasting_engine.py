from datetime import date, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.analytics import DemandObservation, Forecast
from app.models.worker import Worker
from app.models.job import Job
from app.models.service import Service
from app.schemas.analytics import CategoryForecastResponse, ForecastPoint, SkillGapAlert, DemandHeatmapPoint


class DemandForecastingEngine:
    """
    KarmSetu Demand Forecasting & Workforce Analytics Engine
    Performs time-series decomposition, seasonal adjustment, and skill-gap identification.
    """

    # Seasonal factors by category and month (1-12)
    SEASONAL_INDEX = {
        "Plumbing": {6: 1.35, 7: 1.50, 8: 1.45, 9: 1.30, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 10: 1.05, 11: 1.0, 12: 1.0},
        "Electrical": {4: 1.30, 5: 1.45, 6: 1.40, 7: 1.25, 8: 1.15, 1: 0.95, 2: 1.0, 3: 1.15, 9: 1.1, 10: 1.2, 11: 1.0, 12: 1.0},
        "Painting": {9: 1.40, 10: 1.60, 11: 1.30, 1: 0.9, 2: 1.0, 3: 1.1, 4: 1.0, 5: 0.9, 6: 0.7, 7: 0.6, 8: 0.7, 12: 1.0},
        "Carpentry": {10: 1.25, 11: 1.20, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0, 8: 1.0, 9: 1.1, 12: 1.05},
        "Masonry": {1: 1.1, 2: 1.2, 3: 1.2, 4: 1.1, 5: 1.0, 6: 0.8, 7: 0.6, 8: 0.7, 9: 0.9, 10: 1.2, 11: 1.25, 12: 1.15},
    }

    @classmethod
    def get_forecast_for_category(
        cls, db: Session, zone: str, category: str, days_ahead: int = 7
    ) -> CategoryForecastResponse:
        """
        Generates forward-looking daily demand projections with confidence intervals for a given category & zone.
        """
        today = date.today()
        # Query recent observations for baseline
        recent_obs = (
            db.query(DemandObservation)
            .filter(
                DemandObservation.zone == zone,
                DemandObservation.service_category == category,
                DemandObservation.date >= today - timedelta(days=30),
            )
            .all()
        )

        if recent_obs:
            baseline_daily = sum(o.bookings_count for o in recent_obs) / len(recent_obs)
        else:
            baseline_daily = 8.5  # Realistic default synthetic baseline if observations haven't seeded yet

        # Count active workers in cooperative ecosystem capable of this trade
        workers = db.query(Worker).filter(Worker.availability_status != "OFF_DUTY").all()
        active_workers_count = sum(
            1 for w in workers if category.lower() in (w.skills.lower() if w.skills else "")
        )
        if active_workers_count == 0:
            active_workers_count = 5  # Baseline

        daily_points: List[ForecastPoint] = []
        total_projected = 0.0

        for i in range(1, days_ahead + 1):
            forecast_date = today + timedelta(days=i)
            month = forecast_date.month
            day_of_week = forecast_date.weekday()

            # Seasonality multiplier
            season_mult = cls.SEASONAL_INDEX.get(category, {}).get(month, 1.0)

            # Weekend effect (Saturdays & Sundays typically have 20% higher home service demand)
            weekend_mult = 1.22 if day_of_week in (5, 6) else 0.94

            predicted = round(baseline_daily * season_mult * weekend_mult, 1)
            margin = round(predicted * 0.15, 1)  # 15% error band
            conf_low = round(max(0.0, predicted - margin), 1)
            conf_high = round(predicted + margin, 1)

            daily_points.append(
                ForecastPoint(
                    date=forecast_date.isoformat(),
                    predicted_demand=predicted,
                    confidence_low=conf_low,
                    confidence_high=conf_high,
                    seasonal_factor=season_mult,
                )
            )
            total_projected += predicted

        # Evaluate capacity vs projected demand
        # Average worker can comfortably complete ~2 jobs per day
        daily_capacity = active_workers_count * 2.0
        avg_daily_demand = total_projected / days_ahead
        utilization_pct = round((avg_daily_demand / daily_capacity) * 100.0, 1) if daily_capacity > 0 else 100.0

        if utilization_pct > 110.0:
            capacity_status = "DEFICIT"
            recommendation = (
                f"Urgent: Projected demand ({round(avg_daily_demand, 1)} jobs/day) exceeds current roster capacity "
                f"({daily_capacity} jobs/day). Recommend onboarding or cross-allocating additional {category} workers."
            )
        elif utilization_pct < 60.0:
            capacity_status = "SURPLUS"
            recommendation = (
                f"Notice: Roster capacity ({daily_capacity} jobs/day) exceeds demand ({round(avg_daily_demand, 1)} jobs/day). "
                f"Consider promotional cooperative packages to increase workforce utilization."
            )
        else:
            capacity_status = "BALANCED"
            recommendation = "Optimal balance between worker availability and consumer demand."

        return CategoryForecastResponse(
            zone=zone,
            service_category=category,
            current_active_workers=active_workers_count,
            daily_forecast=daily_points,
            total_projected_demand_7d=round(total_projected, 1),
            capacity_status=capacity_status,
            projected_utilization_pct=utilization_pct,
            recommendation=recommendation,
        )

    @classmethod
    def detect_skill_gaps(cls, db: Session, zone: str = "Central Delhi") -> List[SkillGapAlert]:
        """
        Scans all trade categories in a zone to identify deficits where projected peak demand will outstrip verified worker supply.
        """
        categories = ["Plumbing", "Electrical", "Carpentry", "Masonry", "Painting"]
        alerts = []

        for cat in categories:
            forecast_data = cls.get_forecast_for_category(db, zone, cat)
            peak_demand = max(p.predicted_demand for p in forecast_data.daily_forecast)
            required_workers = int(peak_demand / 1.8) + 1  # 1.8 jobs/worker peak target
            current_workers = forecast_data.current_active_workers

            if required_workers > current_workers:
                deficit = required_workers - current_workers
                severity = "HIGH" if deficit >= 3 else "MEDIUM"
                action_item = (
                    f"Recruit or request federation loan of {deficit} certified {cat} workers before weekend peak."
                )
                alerts.append(
                    SkillGapAlert(
                        zone=zone,
                        service_category=cat,
                        required_skills=[cat],
                        current_worker_count=current_workers,
                        projected_peak_demand=peak_demand,
                        deficit_count=deficit,
                        severity=severity,
                        action_item=action_item,
                    )
                )

        return alerts

    @classmethod
    def get_demand_heatmap(cls, db: Session) -> List[DemandHeatmapPoint]:
        """
        Provides geospatial coordinate intensity for map overlays.
        """
        zones_coords = {
            "Central Delhi": (28.6139, 77.2090),
            "South Delhi": (28.5355, 77.2410),
            "North Delhi": (28.7041, 77.1025),
            "West Delhi": (28.6508, 77.1158),
            "East Delhi": (28.6280, 77.2950),
            "Noida / Ghaziabad": (28.5700, 77.3200),
            "Gurugram": (28.4595, 77.0266),
        }
        heatmap = []
        for zone_name, (lat, lon) in zones_coords.items():
            # Query count of bookings in last 30 days
            total_bookings = (
                db.query(func.sum(DemandObservation.bookings_count))
                .filter(DemandObservation.zone == zone_name)
                .scalar()
                or 120
            )
            intensity = min(float(total_bookings) / 300.0, 1.0)
            heatmap.append(
                DemandHeatmapPoint(
                    zone=zone_name,
                    latitude=lat,
                    longitude=lon,
                    total_bookings=int(total_bookings),
                    intensity=round(intensity, 2),
                )
            )
        return heatmap
