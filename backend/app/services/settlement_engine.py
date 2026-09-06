from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus, PaymentStatus
from app.models.cooperative import Cooperative
from app.models.worker import Worker
from app.models.settlement import CooperativeSettlement


class SettlementEngine:
    """
    KarmSetu Cooperative Financial Settlement Engine
    Enforces transparent revenue distribution according to cooperative rules:
    - Worker Disbursement (~80%)
    - Cooperative Operating Pool (~15%)
    - Worker Social Security / Welfare Fund (~5%)
    """

    @classmethod
    def calculate_breakdown(
        cls, gross_amount: float, commission_rate: float = 0.15, welfare_rate: float = 0.05, adjustment: float = 0.0
    ) -> dict:
        cooperative_amount = round(gross_amount * commission_rate, 2)
        welfare_amount = round(gross_amount * welfare_rate, 2)
        worker_amount = round(gross_amount - cooperative_amount - welfare_amount + adjustment, 2)
        return {
            "gross_amount": gross_amount,
            "worker_amount": worker_amount,
            "cooperative_amount": cooperative_amount,
            "welfare_amount": welfare_amount,
            "adjustment_amount": adjustment,
        }

    @classmethod
    def process_job_settlement(
        cls,
        db: Session,
        job: Job,
        payment_method: str = "ONLINE_SIMULATED",
        adjustment: float = 0.0,
        notes: str = None
    ) -> CooperativeSettlement:
        """
        Creates or updates settlement ledger entry for a completed job and updates worker & cooperative balances.
        """
        if not job.assigned_worker_id:
            raise ValueError("Cannot settle a job without an assigned worker.")

        cooperative = db.query(Cooperative).filter(Cooperative.id == job.cooperative_id).first()
        worker = db.query(Worker).filter(Worker.id == job.assigned_worker_id).first()

        gross = job.final_price if (job.final_price is not None and job.final_price > 0) else job.price_estimate
        comm_rate = cooperative.commission_rate if cooperative else 0.15
        welf_rate = cooperative.welfare_contribution_rate if cooperative else 0.05

        calc = cls.calculate_breakdown(gross, comm_rate, welf_rate, adjustment)

        # Check if settlement already exists for this job
        settlement = db.query(CooperativeSettlement).filter(CooperativeSettlement.job_id == job.id).first()
        if not settlement:
            settlement = CooperativeSettlement(
                job_id=job.id,
                cooperative_id=job.cooperative_id,
                worker_id=job.assigned_worker_id,
                gross_amount=calc["gross_amount"],
                worker_amount=calc["worker_amount"],
                cooperative_amount=calc["cooperative_amount"],
                welfare_amount=calc["welfare_amount"],
                adjustment_amount=calc["adjustment_amount"],
                payment_method=payment_method,
                payment_status="PAID",
                settlement_status="SETTLED",
                notes=notes or f"Automated settlement for {job.booking_ref}",
                settled_at=datetime.now(timezone.utc)
            )
            db.add(settlement)
        else:
            settlement.gross_amount = calc["gross_amount"]
            settlement.worker_amount = calc["worker_amount"]
            settlement.cooperative_amount = calc["cooperative_amount"]
            settlement.welfare_amount = calc["welfare_amount"]
            settlement.adjustment_amount = calc["adjustment_amount"]
            settlement.payment_status = "PAID"
            settlement.settlement_status = "SETTLED"
            settlement.settled_at = datetime.now(timezone.utc)

        # Update worker balances and metrics
        if worker:
            worker.total_earnings = round((worker.total_earnings or 0.0) + calc["worker_amount"], 2)
            worker.welfare_balance = round((worker.welfare_balance or 0.0) + calc["welfare_amount"], 2)
            worker.total_jobs = (worker.total_jobs or 0) + 1
            worker.weekly_jobs_count = (worker.weekly_jobs_count or 0) + 1
            worker.availability_status = "AVAILABLE"  # Released back to pool

        # Update cooperative welfare fund pool
        if cooperative:
            cooperative.welfare_fund_pool = round(
                (cooperative.welfare_fund_pool or 0.0) + calc["welfare_amount"], 2
            )
            cooperative.total_jobs_completed = (cooperative.total_jobs_completed or 0) + 1

        # Mark job as settled
        job.payment_status = PaymentStatus.SETTLED
        job.status = JobStatus.COMPLETED
        if not job.completed_at:
            job.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(settlement)
        return settlement
