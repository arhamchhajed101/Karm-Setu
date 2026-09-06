import json
import math
from typing import List, Tuple, Optional
from datetime import datetime

from app.models.worker import Worker
from app.models.job import Job
from app.models.service import Service


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two GPS coordinates in kilometers."""
    r = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 2)


class SmartFairAllocationEngine:
    """
    KarmSetu Explainable Smart Fair Allocation Engine
    Complies strictly with PRD Section 3.2:
    - 30% Skill Match
    - 20% Availability / Slot Fit
    - 15% Distance / Travel
    - 15% Reliability / Trust
    - 10% Current Workload
    - 10% Fairness / Utilization Adjustment
    """

    @classmethod
    def evaluate_worker(
        cls, worker: Worker, job: Job, service: Service
    ) -> Tuple[float, dict, str]:
        """
        Evaluates a single worker against a job.
        Returns: (total_score, scores_dict, narrative_explanation)
        """
        # Parse skills and certificates
        try:
            worker_skills = json.loads(worker.skills) if isinstance(worker.skills, str) else (worker.skills or [])
        except Exception:
            worker_skills = []

        try:
            worker_certs = json.loads(worker.certificates) if isinstance(worker.certificates, str) else (worker.certificates or [])
        except Exception:
            worker_certs = []

        try:
            required_skills = json.loads(service.required_skills) if isinstance(service.required_skills, str) else (service.required_skills or [])
        except Exception:
            required_skills = []

        # 1. HARD SAFETY & ELIGIBILITY CONSTRAINTS
        if worker.availability_status == "OFF_DUTY":
            return (0.0, {}, "Ineligible: Worker is currently off-duty.")
        
        # Check if worker satisfies required skill (case-insensitive)
        worker_skills_lower = [s.lower() for s in worker_skills]
        if required_skills:
            has_mandatory_skill = any(req.lower() in worker_skills_lower for req in required_skills)
            if not has_mandatory_skill:
                return (0.0, {}, f"Ineligible: Missing mandatory skill {required_skills}.")

        # 2. FACTOR 1: SKILL MATCH (30 Points Max)
        # Base trade match: 20 points
        skill_score = 20.0
        # Experience bonus: 1 pt per year up to 5 pts
        exp_bonus = min(float(worker.experience_years or 1), 5.0)
        skill_score += exp_bonus
        # Certification bonus: up to 5 pts
        cert_bonus = min(len(worker_certs) * 2.5, 5.0)
        skill_score += cert_bonus
        skill_score = min(skill_score, 30.0)

        # 3. FACTOR 2: AVAILABILITY & SLOT FIT (20 Points Max)
        if worker.availability_status == "AVAILABLE":
            avail_score = 20.0
        elif worker.availability_status == "BUSY":
            avail_score = 6.0
        else:
            avail_score = 0.0

        # 4. FACTOR 3: DISTANCE & TRAVEL PROXIMITY (15 Points Max)
        dist_km = haversine_distance(job.latitude, job.longitude, worker.latitude, worker.longitude)
        if dist_km <= 3.0:
            dist_score = 15.0
        elif dist_km <= 10.0:
            # Linear decay from 15 to 8
            dist_score = 15.0 - ((dist_km - 3.0) / 7.0) * 7.0
        elif dist_km <= 25.0:
            # Linear decay from 8 to 3
            dist_score = 8.0 - ((dist_km - 10.0) / 15.0) * 5.0
        else:
            dist_score = 1.0
        dist_score = round(max(dist_score, 1.0), 2)

        # 5. FACTOR 4: RELIABILITY & TRUST (15 Points Max)
        # Rating (10 points max): worker.rating / 5.0 * 10
        norm_rating = (worker.rating / 5.0) * 10.0
        # Reliability completion metric (3 points max): reliability_score * 3
        norm_rel = worker.reliability_score * 3.0
        # Verified trust credential bonus (2 points)
        verify_bonus = 2.0 if worker.verification_status == "VERIFIED" else 0.5
        rel_score = round(min(norm_rating + norm_rel + verify_bonus, 15.0), 2)

        # 6. FACTOR 5: CURRENT WORKLOAD / FATIGUE AVOIDANCE (10 Points Max)
        # Prefer workers with manageable weekly volume to prevent burnout and service degradation
        weekly = worker.weekly_jobs_count or 0
        if weekly <= 2:
            workload_score = 10.0
        elif weekly <= 5:
            workload_score = 8.0
        elif weekly <= 8:
            workload_score = 5.0
        elif weekly <= 12:
            workload_score = 3.0
        else:
            workload_score = 1.0

        # 7. FACTOR 6: FAIRNESS & COOPERATIVE UTILIZATION EQUALIZATION (10 Points Max)
        # Distributes income equitably across cooperative roster when quality is assured
        if weekly <= 2 and worker.rating >= 4.0:
            fairness_score = 10.0
            fairness_desc = "High underutilization priority (+10.0 pts boost to balance cooperative income)"
        elif weekly <= 4 and worker.rating >= 4.0:
            fairness_score = 7.0
            fairness_desc = "Moderate underutilization priority (+7.0 pts boost)"
        elif weekly <= 7:
            fairness_score = 4.0
            fairness_desc = "Balanced workload (+4.0 pts)"
        else:
            fairness_score = 1.0
            fairness_desc = "Worker near target capacity (+1.0 pt)"

        # TOTAL WEIGHTED SCORE (Max 100.0)
        total_score = round(
            skill_score + avail_score + dist_score + rel_score + workload_score + fairness_score, 2
        )

        scores = {
            "skill_score": round(skill_score, 2),
            "availability_score": round(avail_score, 2),
            "distance_score": round(dist_score, 2),
            "reliability_score": round(rel_score, 2),
            "workload_score": round(workload_score, 2),
            "fairness_score": round(fairness_score, 2),
            "total_score": total_score,
            "distance_km": dist_km,
        }

        narrative = (
            f"Candidate {worker.name} scored {total_score}/100. "
            f"Skill Match: {round(skill_score, 1)}/30 ({worker.experience_years} yrs exp, {len(worker_certs)} certs). "
            f"Distance: {dist_km} km away ({round(dist_score, 1)}/15). "
            f"Trust: {worker.rating}★ rating ({round(rel_score, 1)}/15, status: {worker.verification_status}). "
            f"Fairness Adjustment: {fairness_desc} ({weekly} jobs completed this week)."
        )

        return (total_score, scores, narrative)

    @classmethod
    def rank_candidates_for_job(
        cls, workers: List[Worker], job: Job, service: Service
    ) -> List[dict]:
        """
        Ranks all eligible cooperative workers by explainable allocation score.
        Returns sorted list of candidate breakdowns.
        """
        candidates = []
        for worker in workers:
            total_score, scores, narrative = cls.evaluate_worker(worker, job, service)
            if total_score > 0.0:  # Passed hard safety & skill constraints
                candidates.append({
                    "worker": worker,
                    "total_score": total_score,
                    "scores": scores,
                    "narrative": narrative,
                    "distance_km": scores.get("distance_km", 0.0),
                })

        # Sort descending by total score
        candidates.sort(key=lambda x: x["total_score"], reverse=True)
        return candidates
