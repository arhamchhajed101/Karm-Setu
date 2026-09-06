# Import Base and all models here so that Alembic and Base.metadata have a complete model inventory
from app.db.session import Base
from app.models.user import User, UserRole
from app.models.cooperative import Cooperative
from app.models.worker import Worker
from app.models.service import Service
from app.models.customer import Customer
from app.models.job import Job, JobStatus, PaymentStatus
from app.models.allocation import AllocationScore
from app.models.settlement import CooperativeSettlement
from app.models.welfare import WelfareRecord
from app.models.analytics import DemandObservation, Forecast
from app.models.institutional import InstitutionalProject
from app.models.review import Review
from app.models.audit import AuditLog
