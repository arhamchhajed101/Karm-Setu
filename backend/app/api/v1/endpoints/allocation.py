import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.models.job import Job, JobStatus
from app.models.worker import Worker
from app.models.service import Service
from app.models.allocation import AllocationScore
from app.schemas.allocation import (
    AllocationEvaluateResponse,
    AllocationCandidate,
    ScoreBreakdown,
    ManualAssignRequest,
    AutoAssignResponse,
)
from app.services.allocation_engine import SmartFairAllocationEngine
from app.services.audit_service import AuditService

router = APIRouter()


@router.post("/evaluate/{job_id}", response_model=AllocationEvaluateResponse)
def evaluate_job_allocation(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates all cooperative workers for a job using the explainable multi-factor scoring engine:
    - Skill Match (30%)
    - Slot Availability (20%)
    - Distance Proximity (15%)
    - Reliability & Trust (15%)
    - Workload / Fatigue Avoidance (10%)
    - Fairness / Utilization Equalization (10%)
    
    Returns explainable AI scoring breakdown and narrative justification for each candidate.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    service = db.query(Service).filter(Service.id == job.service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    # Fetch all workers in the serving cooperative
    workers = db.query(Worker).filter(Worker.cooperative_id == job.cooperative_id).all()
    if not workers:
        # If no workers in this cooperative, try all active workers as federation fallback
        workers = db.query(Worker).all()

    ranked = SmartFairAllocationEngine.rank_candidates_for_job(workers, job, service)

    # Delete previous non-assigned evaluations for this job to keep ledger clean
    db.query(AllocationScore).filter(
        AllocationScore.job_id == job.id, AllocationScore.is_assigned == False
    ).delete()

    candidate_responses: List[AllocationCandidate] = []
    top_worker_id = None
    top_worker_name = None
    top_reason = None

    for idx, c in enumerate(ranked):
        w: Worker = c["worker"]
        scores = c["scores"]
        narrative = c["narrative"]

        if idx == 0:
            top_worker_id = w.id
            top_worker_name = w.name
            top_reason = narrative

        # Save allocation evaluation snapshot
        alloc_record = AllocationScore(
            job_id=job.id,
            worker_id=w.id,
            skill_score=scores["skill_score"],
            availability_score=scores["availability_score"],
            distance_score=scores["distance_score"],
            reliability_score=scores["reliability_score"],
            workload_score=scores["workload_score"],
            fairness_score=scores["fairness_score"],
            total_score=scores["total_score"],
            is_assigned=False,
            explanation=narrative,
            evaluated_at=datetime.now(timezone.utc),
        )
        db.add(alloc_record)

        candidate_responses.append(
            AllocationCandidate(
                worker_id=w.id,
                worker_name=w.name,
                worker_phone=w.phone,
                photo_url=w.photo_url,
                rating=w.rating,
                verification_status=w.verification_status,
                distance_km=scores.get("distance_km", 0.0),
                weekly_jobs=w.weekly_jobs_count or 0,
                scores=ScoreBreakdown(
                    skill_score=scores["skill_score"],
                    availability_score=scores["availability_score"],
                    distance_score=scores["distance_score"],
                    reliability_score=scores["reliability_score"],
                    workload_score=scores["workload_score"],
                    fairness_score=scores["fairness_score"],
                    total_score=scores["total_score"],
                ),
                narrative_explanation=narrative,
            )
        )

    db.commit()

    return AllocationEvaluateResponse(
        job_id=job.id,
        booking_ref=job.booking_ref,
        service_name=service.name,
        service_category=service.category,
        job_location={"address": job.address, "latitude": job.latitude, "longitude": job.longitude},
        candidates=candidate_responses,
        recommended_worker_id=top_worker_id,
        recommended_worker_name=top_worker_name,
        top_recommendation_reason=top_reason,
        total_eligible_workers=len(candidate_responses),
        evaluated_at=datetime.now(timezone.utc),
    )


@router.post("/auto-assign/{job_id}", response_model=AutoAssignResponse)
def auto_assign_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COOPERATIVE_ADMIN, UserRole.SUPERVISOR))
):
    """
    Automatically selects the top-scoring candidate from the explainable allocation engine and assigns the job.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.status not in [JobStatus.REQUESTED, JobStatus.ASSIGNED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot assign job in status: {job.status.value}"
        )

    service = db.query(Service).filter(Service.id == job.service_id).first()
    workers = db.query(Worker).filter(Worker.cooperative_id == job.cooperative_id).all()
    if not workers:
        workers = db.query(Worker).all()

    ranked = SmartFairAllocationEngine.rank_candidates_for_job(workers, job, service)
    if not ranked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No eligible workers found matching the skill and availability constraints."
        )

    top_choice = ranked[0]
    assigned_worker: Worker = top_choice["worker"]

    job.assigned_worker_id = assigned_worker.id
    job.status = JobStatus.ASSIGNED
    job.assigned_at = datetime.now(timezone.utc)
    assigned_worker.availability_status = "BUSY"

    # Mark corresponding allocation score as assigned
    alloc_entry = (
        db.query(AllocationScore)
        .filter(AllocationScore.job_id == job.id, AllocationScore.worker_id == assigned_worker.id)
        .first()
    )
    if alloc_entry:
        alloc_entry.is_assigned = True
    else:
        scores = top_choice["scores"]
        alloc_entry = AllocationScore(
            job_id=job.id,
            worker_id=assigned_worker.id,
            skill_score=scores["skill_score"],
            availability_score=scores["availability_score"],
            distance_score=scores["distance_score"],
            reliability_score=scores["reliability_score"],
            workload_score=scores["workload_score"],
            fairness_score=scores["fairness_score"],
            total_score=scores["total_score"],
            is_assigned=True,
            explanation=top_choice["narrative"],
            evaluated_at=datetime.now(timezone.utc),
        )
        db.add(alloc_entry)

    db.commit()
    db.refresh(job)

    AuditService.log_event(
        db,
        entity_type="ALLOCATION",
        entity_id=job.id,
        action="AUTO_ASSIGNED",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        details={
            "worker_id": assigned_worker.id,
            "worker_name": assigned_worker.name,
            "total_score": top_choice["total_score"],
            "explanation": top_choice["narrative"],
        }
    )

    return AutoAssignResponse(
        job_id=job.id,
        booking_ref=job.booking_ref,
        assigned_worker_id=assigned_worker.id,
        assigned_worker_name=assigned_worker.name,
        assigned_worker_phone=assigned_worker.phone,
        total_score=top_choice["total_score"],
        narrative_explanation=top_choice["narrative"],
        status=job.status.value,
    )


@router.post("/manual-assign/{job_id}", response_model=AutoAssignResponse)
def manual_assign_job(
    job_id: int,
    assign_req: ManualAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COOPERATIVE_ADMIN, UserRole.SUPERVISOR))
):
    """
    Allows cooperative coordinator to manually override allocation and assign a specific worker.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    worker = db.query(Worker).filter(Worker.id == assign_req.worker_id).first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")

    service = db.query(Service).filter(Service.id == job.service_id).first()
    total_score, scores, narrative = SmartFairAllocationEngine.evaluate_worker(worker, job, service)

    job.assigned_worker_id = worker.id
    job.status = JobStatus.ASSIGNED
    job.assigned_at = datetime.now(timezone.utc)
    worker.availability_status = "BUSY"

    notes = assign_req.coordinator_notes or "Coordinator manual override"
    explanation_str = f"Manual Assignment by Coordinator ({current_user.full_name}): {notes}. Evaluation: {narrative}"

    alloc_entry = AllocationScore(
        job_id=job.id,
        worker_id=worker.id,
        skill_score=scores.get("skill_score", 20.0),
        availability_score=scores.get("availability_score", 20.0),
        distance_score=scores.get("distance_score", 10.0),
        reliability_score=scores.get("reliability_score", 10.0),
        workload_score=scores.get("workload_score", 5.0),
        fairness_score=scores.get("fairness_score", 5.0),
        total_score=total_score,
        is_assigned=True,
        explanation=explanation_str,
        evaluated_at=datetime.now(timezone.utc),
    )
    db.add(alloc_entry)
    db.commit()
    db.refresh(job)

    AuditService.log_event(
        db,
        entity_type="ALLOCATION",
        entity_id=job.id,
        action="MANUAL_ASSIGNED",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        details={"worker_id": worker.id, "worker_name": worker.name, "notes": notes}
    )

    return AutoAssignResponse(
        job_id=job.id,
        booking_ref=job.booking_ref,
        assigned_worker_id=worker.id,
        assigned_worker_name=worker.name,
        assigned_worker_phone=worker.phone,
        total_score=total_score,
        narrative_explanation=explanation_str,
        status=job.status.value,
    )
