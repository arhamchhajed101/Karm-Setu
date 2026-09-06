import random
import json
import uuid
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.cooperative import Cooperative
from app.models.worker import Worker
from app.models.service import Service
from app.models.customer import Customer
from app.models.job import Job, JobStatus, PaymentStatus
from app.models.settlement import CooperativeSettlement
from app.models.welfare import WelfareRecord
from app.models.analytics import DemandObservation, Forecast
from app.models.institutional import InstitutionalProject
from app.models.review import Review
from app.models.allocation import AllocationScore
from app.services.allocation_engine import SmartFairAllocationEngine

# Constants for realistic Indian data generation
COOPERATIVES_DATA = [
    {
        "name": "Delhi Labour & Construction Workers Cooperative Society Ltd.",
        "registration_id": "DL-COOP-2018-0492",
        "state": "Delhi",
        "district": "Central Delhi",
        "address": "42, Shramik Bhavan, Daryaganj, New Delhi",
        "pin_code": "110002",
        "contact_phone": "+91-11-23278901",
        "contact_email": "central@delhishramik.coop",
        "type": "Labour Contract Society",
        "categories": ["Plumbing", "Electrical", "Masonry", "Welding"],
        "commission_rate": 0.15,
        "welfare_contribution_rate": 0.05,
    },
    {
        "name": "South Delhi Shramik Seva Sahakari Samiti",
        "registration_id": "DL-COOP-2020-1184",
        "state": "Delhi",
        "district": "South Delhi",
        "address": "B-18, Okhla Industrial Area Phase-II, New Delhi",
        "pin_code": "110020",
        "contact_phone": "+91-11-41657890",
        "contact_email": "south@delhishramik.coop",
        "type": "Skilled Trades Cooperative",
        "categories": ["Electrical", "Carpentry", "Painting", "HVAC"],
        "commission_rate": 0.14,
        "welfare_contribution_rate": 0.05,
    },
    {
        "name": "NCR Urban Infrastructure & Artisan Society",
        "registration_id": "UP-COOP-2019-3382",
        "state": "Uttar Pradesh",
        "district": "Noida / Ghaziabad",
        "address": "Plot 7, Sector 62, Noida",
        "pin_code": "201309",
        "contact_phone": "+91-120-2401928",
        "contact_email": "contact@ncricoop.in",
        "type": "Multi-Purpose Labour Society",
        "categories": ["Plumbing", "Painting", "Deep Cleaning", "Masonry"],
        "commission_rate": 0.15,
        "welfare_contribution_rate": 0.06,
    },
    {
        "name": "Gurugram Facility & Skilled Artisan Cooperative",
        "registration_id": "HR-COOP-2021-0945",
        "state": "Haryana",
        "district": "Gurugram",
        "address": "Auto Market Complex, Sector 14, Gurugram",
        "pin_code": "122001",
        "contact_phone": "+91-124-4289012",
        "contact_email": "info@gurugramartisan.coop",
        "type": "Labour Cooperative Society",
        "categories": ["Carpentry", "Electrical", "Plumbing", "HVAC"],
        "commission_rate": 0.15,
        "welfare_contribution_rate": 0.05,
    },
    {
        "name": "Jaipur Shilpkar & Shram Sahakari Sangh",
        "registration_id": "RJ-COOP-2017-0231",
        "state": "Rajasthan",
        "district": "Jaipur",
        "address": "MI Road, Near Ajmeri Gate, Jaipur",
        "pin_code": "302001",
        "contact_phone": "+91-141-2365901",
        "contact_email": "jaipurshilp@rajasthancoop.org",
        "type": "Heritage Artisan & Labour Society",
        "categories": ["Masonry", "Carpentry", "Painting", "Stone Work"],
        "commission_rate": 0.12,
        "welfare_contribution_rate": 0.05,
    },
]

SERVICES_CATALOGUE = [
    # Plumbing
    {"category": "Plumbing", "name": "Pipe Leakage & Tap Repair", "pricing_model": "FIXED", "base_price": 299.0, "duration": 45, "skills": ["Plumbing"]},
    {"category": "Plumbing", "name": "Bathroom Sanitary Fitting & Installation", "pricing_model": "FIXED", "base_price": 649.0, "duration": 90, "skills": ["Plumbing", "Sanitary"]},
    {"category": "Plumbing", "name": "Overhead Water Tank Cleaning & Inspection", "pricing_model": "FIXED", "base_price": 899.0, "duration": 120, "skills": ["Plumbing", "Water Systems"]},
    {"category": "Plumbing", "name": "Drainage Unclogging & Jetting", "pricing_model": "INSPECTION_DIAGNOSTIC", "base_price": 499.0, "duration": 60, "skills": ["Plumbing", "Drainage"]},
    
    # Electrical
    {"category": "Electrical", "name": "Switchboard & Wiring Short Circuit Repair", "pricing_model": "FIXED", "base_price": 349.0, "duration": 60, "skills": ["Electrical"]},
    {"category": "Electrical", "name": "Ceiling Fan & Exhaust Fan Installation", "pricing_model": "FIXED", "base_price": 249.0, "duration": 40, "skills": ["Electrical"]},
    {"category": "Electrical", "name": "Inverter / Battery Setup & Diagnostics", "pricing_model": "INSPECTION_DIAGNOSTIC", "base_price": 499.0, "duration": 60, "skills": ["Electrical", "Power Backup"]},
    {"category": "Electrical", "name": "MCB & Main Distribution Box Upgrade", "pricing_model": "FIXED", "base_price": 799.0, "duration": 90, "skills": ["Electrical"]},
    
    # Carpentry
    {"category": "Carpentry", "name": "Door Lock & Handle Replacement", "pricing_model": "FIXED", "base_price": 299.0, "duration": 45, "skills": ["Carpentry"]},
    {"category": "Carpentry", "name": "Modular Furniture Assembly & Repair", "pricing_model": "HOURLY", "base_price": 450.0, "duration": 120, "skills": ["Carpentry", "Assembly"]},
    {"category": "Carpentry", "name": "Wooden Window Frame & Hinge Restoration", "pricing_model": "FIXED", "base_price": 599.0, "duration": 90, "skills": ["Carpentry"]},
    
    # Masonry & Construction
    {"category": "Masonry", "name": "Wall Plastering & Crack Repair", "pricing_model": "FIXED", "base_price": 750.0, "duration": 150, "skills": ["Masonry", "Plastering"]},
    {"category": "Masonry", "name": "Floor Tile Replacement & Grouting", "pricing_model": "FIXED", "base_price": 899.0, "duration": 180, "skills": ["Masonry", "Tiling"]},
    {"category": "Masonry", "name": "Brickwork Wall Repair & Minor Masonry", "pricing_model": "HOURLY", "base_price": 500.0, "duration": 180, "skills": ["Masonry"]},
    
    # Painting
    {"category": "Painting", "name": "Single Room Wall Emulsion Painting", "pricing_model": "FIXED", "base_price": 1499.0, "duration": 240, "skills": ["Painting"]},
    {"category": "Painting", "name": "Waterproofing & Anti-Damp Wall Treatment", "pricing_model": "FIXED", "base_price": 1899.0, "duration": 180, "skills": ["Painting", "Waterproofing"]},
    {"category": "Painting", "name": "Wood Polish & Metal Enamel Coating", "pricing_model": "FIXED", "base_price": 999.0, "duration": 120, "skills": ["Painting", "Polishing"]},
    
    # Welding & Metalwork
    {"category": "Welding", "name": "Iron Gate & Grille Welding Repair", "pricing_model": "FIXED", "base_price": 599.0, "duration": 60, "skills": ["Welding"]},
    {"category": "Welding", "name": "Balcony Safety Railing Fabrication", "pricing_model": "HOURLY", "base_price": 600.0, "duration": 180, "skills": ["Welding", "Fabrication"]},
]

FIRST_NAMES = [
    "Ramesh", "Suresh", "Manoj", "Dinesh", "Rajesh", "Prakash", "Sunil", "Anil", "Vikram",
    "Ajay", "Vijay", "Mukesh", "Naresh", "Santosh", "Ashok", "Kishan", "Radhey", "Bablu",
    "Deepak", "Amit", "Vinod", "Govind", "Harish", "Satish", "Mohan", "Gopal", "Pappu",
    "Jitendra", "Dharmendra", "Mahesh", "Sanjay", "Raju", "Chandan", "Suraj", "Pankaj"
]

LAST_NAMES = [
    "Kumar", "Sharma", "Verma", "Singh", "Yadav", "Gupta", "Mishra", "Pandey", "Chauhan",
    "Thakur", "Rathore", "Maurya", "Paswan", "Lal", "Rawat", "Prasad", "Shah", "Kanojia",
    "Choudhary", "Giri", "Bind", "Soni", "Nayak", "Joshi", "Bhardwaj"
]

DELHI_COORDS = [
    (28.6139, 77.2090, "Connaught Place, Central Delhi"),
    (28.6508, 77.1158, "Rajouri Garden, West Delhi"),
    (28.5355, 77.2410, "Kalkaji, South Delhi"),
    (28.7041, 77.1025, "Rohini, North Delhi"),
    (28.6280, 77.2950, "Laxmi Nagar, East Delhi"),
    (28.4595, 77.0266, "DLF Phase 3, Gurugram"),
    (28.5700, 77.3200, "Sector 18, Noida"),
    (28.6692, 77.4538, "Kavi Nagar, Ghaziabad"),
]


def seed_database():
    print("[INFO] Initializing KarmSetu Database & Tables...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).count() > 50:
            print("[INFO] Database already contains seeded data. Skipping.")
            return

        print("[USER] Creating Core Demo Users for all 4 Roles...")
        default_pw = get_password_hash("Password123!")

        # 1. Admin User
        admin_user = User(
            email="admin@karmsetu.in",
            hashed_password=default_pw,
            full_name="Rajiv Shrivastava",
            phone="+91-9811002233",
            role=UserRole.COOPERATIVE_ADMIN,
            is_active=True,
        )
        db.add(admin_user)

        # 2. Worker User
        worker_user = User(
            email="worker@karmsetu.in",
            hashed_password=default_pw,
            full_name="Ramesh Kumar",
            phone="+91-9876543210",
            role=UserRole.WORKER,
            is_active=True,
        )
        db.add(worker_user)

        # 3. Customer User
        customer_user = User(
            email="customer@karmsetu.in",
            hashed_password=default_pw,
            full_name="Ananya Mehra",
            phone="+91-9988776655",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        db.add(customer_user)

        # 4. Supervisor User
        supervisor_user = User(
            email="supervisor@karmsetu.in",
            hashed_password=default_pw,
            full_name="Vikramaditya Rao",
            phone="+91-9123456789",
            role=UserRole.SUPERVISOR,
            is_active=True,
        )
        db.add(supervisor_user)
        db.commit()

        # Seed Customer Profile
        customer_profile = Customer(
            user_id=customer_user.id,
            name="Ananya Mehra",
            phone="+91-9988776655",
            email="customer@karmsetu.in",
            address="Apartment 402, Lotus Towers, Vasant Kunj, New Delhi",
            city="Delhi",
            latitude=28.5244,
            longitude=77.1587,
        )
        db.add(customer_profile)

        print("[COOP] Creating 5 Labour Cooperatives...")
        cooperatives = []
        for c_data in COOPERATIVES_DATA:
            coop = Cooperative(
                name=c_data["name"],
                registration_id=c_data["registration_id"],
                state=c_data["state"],
                district=c_data["district"],
                address=c_data["address"],
                pin_code=c_data["pin_code"],
                contact_phone=c_data["contact_phone"],
                contact_email=c_data["contact_email"],
                type=c_data["type"],
                verification_status="VERIFIED",
                service_categories=json.dumps(c_data["categories"]),
                commission_rate=c_data["commission_rate"],
                welfare_contribution_rate=c_data["welfare_contribution_rate"],
                total_members=0,
                total_jobs_completed=0,
                welfare_fund_pool=45200.0,
            )
            db.add(coop)
            cooperatives.append(coop)
        db.commit()

        print("[SERVICE] Creating 20+ Service Offerings across Cooperatives...")
        services = []
        for coop in cooperatives:
            for s_item in SERVICES_CATALOGUE:
                s = Service(
                    cooperative_id=coop.id,
                    category=s_item["category"],
                    name=s_item["name"],
                    description=f"Professional cooperative-verified {s_item['category'].lower()} service backed by {coop.name}.",
                    pricing_model=s_item["pricing_model"],
                    base_price=s_item["base_price"],
                    estimated_duration_minutes=s_item["duration"],
                    emergency_multiplier=1.25,
                    required_skills=json.dumps(s_item["skills"]),
                    is_active=True,
                )
                db.add(s)
                services.append(s)
        db.commit()

        print("[WORKER] Creating 210+ Verified Cooperative Workers...")
        all_skills_pool = ["Plumbing", "Electrical", "Carpentry", "Masonry", "Painting", "Welding", "Sanitary", "Waterproofing"]
        workers: list[Worker] = []

        # First worker is our default test worker
        worker_profile_1 = Worker(
            user_id=worker_user.id,
            cooperative_id=cooperatives[0].id,
            name="Ramesh Kumar",
            phone="+91-9876543210",
            photo_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
            skills=json.dumps(["Plumbing", "Sanitary", "Pipe Fitting"]),
            experience_years=8,
            certificates=json.dumps([
                {"name": "ITI National Trade Certificate - Plumber", "issuer": "NCVT India", "year": 2018},
                {"name": "Delhi Police Citizen Verification Reference", "ref_id": "DP-VR-2023-88219", "year": 2023},
            ]),
            verification_status="VERIFIED",
            verification_ref_id="DP-VR-2023-88219",
            police_station_jurisdiction="Daryaganj PS, Central Delhi",
            rating=4.92,
            total_jobs=148,
            weekly_jobs_count=3,
            reliability_score=0.98,
            availability_status="AVAILABLE",
            latitude=28.6139,
            longitude=77.2090,
            address="Connaught Place, New Delhi",
            welfare_status="ACTIVE",
            total_earnings=88400.0,
            welfare_balance=4420.0,
        )
        db.add(worker_profile_1)
        workers.append(worker_profile_1)

        # Generate 210 additional workers
        for i in range(2, 215):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            w_name = f"{first} {last}"
            w_phone = f"+91-{random.randint(9100000000, 9999999999)}"
            coop = random.choice(cooperatives)

            # Assign 1-3 skills
            num_skills = random.choice([1, 2, 2, 3])
            w_skills = random.sample(all_skills_pool, num_skills)

            loc = random.choice(DELHI_COORDS)
            lat_jitter = loc[0] + random.uniform(-0.04, 0.04)
            lon_jitter = loc[1] + random.uniform(-0.04, 0.04)

            exp = random.randint(2, 16)
            rating = round(random.uniform(4.35, 4.98), 2)
            tot_jobs = random.randint(15, 260)
            weekly = random.randint(0, 7)
            reliability = round(random.uniform(0.91, 0.99), 2)
            avail = random.choices(["AVAILABLE", "BUSY", "OFF_DUTY"], weights=[75, 20, 5])[0]
            welf_stat = random.choices(["ACTIVE", "EXPIRING_SOON", "PENDING"], weights=[80, 15, 5])[0]

            certs = [
                {"name": f"ITI Certificate in {w_skills[0]}", "issuer": "Directorate General of Training", "year": 2020},
                {"name": "Skill India Assessment Certificate", "issuer": "NSDC", "year": 2022}
            ]

            # Create User for worker
            u = User(
                email=f"worker_{i}_{first.lower()}@karmsetu.in",
                hashed_password=default_pw,
                full_name=w_name,
                phone=w_phone,
                role=UserRole.WORKER,
                is_active=True,
            )
            db.add(u)
            db.flush()

            w = Worker(
                user_id=u.id,
                cooperative_id=coop.id,
                name=w_name,
                phone=w_phone,
                photo_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={w_name.replace(' ', '')}",
                skills=json.dumps(w_skills),
                experience_years=exp,
                certificates=json.dumps(certs),
                verification_status="VERIFIED",
                verification_ref_id=f"DP-VR-{random.randint(2022, 2026)}-{random.randint(10000, 99999)}",
                police_station_jurisdiction=loc[2].split(",")[0] + " PS",
                rating=rating,
                total_jobs=tot_jobs,
                weekly_jobs_count=weekly,
                reliability_score=reliability,
                availability_status=avail,
                latitude=round(lat_jitter, 4),
                longitude=round(lon_jitter, 4),
                address=loc[2],
                welfare_status=welf_stat,
                total_earnings=round(tot_jobs * random.uniform(400.0, 750.0), 2),
                welfare_balance=round(tot_jobs * 25.0, 2),
            )
            db.add(w)
            workers.append(w)
            coop.total_members = (coop.total_members or 0) + 1

        db.commit()

        print("[WELFARE] Seeding Welfare Records & e-Shram Insurance Policies...")
        welfare_schemes = [
            ("e-Shram Pradhan Mantri Shram Yogi Maandhan (PM-SYM)", 3000.0, 100.0),
            ("Pradhan Mantri Suraksha Bima Yojana (PMSBY Accident)", 200000.0, 20.0),
            ("Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY Life)", 200000.0, 436.0),
            ("State Construction Workers Welfare Board Card", 50000.0, 50.0),
        ]

        today = date.today()
        for w in workers:
            scheme = random.choice(welfare_schemes)
            is_expiring = (w.welfare_status == "EXPIRING_SOON")
            end_d = today + timedelta(days=random.randint(5, 25)) if is_expiring else today + timedelta(days=random.randint(60, 340))
            start_d = end_d - timedelta(days=365)

            rec = WelfareRecord(
                worker_id=w.id,
                cooperative_id=w.cooperative_id,
                scheme_name=scheme[0],
                policy_number=f"IN-WLF-{random.randint(100000, 999999)}",
                status="EXPIRING_SOON" if is_expiring else "ACTIVE",
                coverage_amount=scheme[1],
                annual_premium=scheme[2],
                start_date=start_d,
                end_date=end_d,
                contribution_status="UP_TO_DATE",
                last_contribution_date=today - timedelta(days=random.randint(10, 45)),
                total_welfare_contributed=w.welfare_balance or 0.0,
            )
            db.add(rec)
        db.commit()

        print("[FORECAST] Seeding 180 Days of Historical Demand Observations for Forecasting...")
        zones = ["Central Delhi", "South Delhi", "North Delhi", "West Delhi", "East Delhi", "Noida / Ghaziabad", "Gurugram"]
        categories = ["Plumbing", "Electrical", "Carpentry", "Masonry", "Painting"]

        start_hist_date = today - timedelta(days=180)
        curr = start_hist_date
        while curr <= today:
            month = curr.month
            day_of_week = curr.weekday()
            weekend_boost = 1.25 if day_of_week in (5, 6) else 1.0

            for z in zones:
                for cat in categories:
                    # Apply seasonal simulation
                    season_mult = 1.0
                    if cat == "Plumbing" and month in (7, 8, 9):  # Monsoon plumbing surge
                        season_mult = 1.45
                    elif cat == "Electrical" and month in (5, 6, 7):  # Summer electrical surge
                        season_mult = 1.40
                    elif cat == "Painting" and month in (9, 10, 11):  # Festive pre-Diwali painting
                        season_mult = 1.55

                    base_daily = random.randint(4, 12)
                    bookings = int(base_daily * season_mult * weekend_boost)
                    cancellations = int(bookings * random.uniform(0.02, 0.07))
                    completed = max(0, bookings - cancellations)
                    avg_p = round(random.uniform(450.0, 950.0), 2)

                    obs = DemandObservation(
                        date=curr,
                        zone=z,
                        service_category=cat,
                        bookings_count=bookings,
                        completed_count=completed,
                        cancellations_count=cancellations,
                        avg_price=avg_p,
                        lead_time_hours=round(random.uniform(1.2, 3.5), 1),
                    )
                    db.add(obs)

            curr += timedelta(days=1)
        db.commit()

        print("[JOBS] Seeding 1,050+ Historical Jobs, Settlements, and Customer Reviews...")
        # Create 15 synthetic customers
        synth_customers = [customer_profile]
        for c_idx in range(1, 15):
            c_u = User(
                email=f"customer_{c_idx}@example.com",
                hashed_password=default_pw,
                full_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                phone=f"+91-{random.randint(9000000000, 9999999999)}",
                role=UserRole.CUSTOMER,
                is_active=True,
            )
            db.add(c_u)
            db.flush()
            c_p = Customer(
                user_id=c_u.id,
                name=c_u.full_name,
                phone=c_u.phone,
                email=c_u.email,
                address=random.choice(DELHI_COORDS)[2],
                city="Delhi",
                latitude=random.choice(DELHI_COORDS)[0],
                longitude=random.choice(DELHI_COORDS)[1],
            )
            db.add(c_p)
            synth_customers.append(c_p)
        db.commit()

        # Generate 1,050 jobs over past 180 days
        for j_idx in range(1, 1051):
            cust = random.choice(synth_customers)
            srv = random.choice(services)
            coop = db.query(Cooperative).filter(Cooperative.id == srv.cooperative_id).first()
            days_ago = random.randint(1, 180)
            job_date = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(1, 12))

            # Pick an eligible worker from this cooperative
            eligible_workers = [
                w for w in workers if w.cooperative_id == coop.id
            ]
            assigned_w = random.choice(eligible_workers) if eligible_workers else random.choice(workers)

            price = srv.base_price + 50.0  # Base + travel
            ref = f"KS-{job_date.year}-{j_idx:05d}"

            # Most historical jobs are COMPLETED
            status_choice = JobStatus.COMPLETED
            pay_status = PaymentStatus.SETTLED

            job = Job(
                booking_ref=ref,
                customer_id=cust.id,
                service_id=srv.id,
                cooperative_id=coop.id,
                assigned_worker_id=assigned_w.id,
                status=status_choice,
                slot_start=job_date,
                slot_end=job_date + timedelta(minutes=srv.estimated_duration_minutes),
                address=cust.address or "Vasant Kunj, New Delhi",
                latitude=cust.latitude,
                longitude=cust.longitude,
                is_emergency=(random.random() < 0.15),
                price_estimate=price,
                final_price=price,
                payment_status=pay_status,
                payment_method=random.choice(["ONLINE_SIMULATED", "CASH_ON_DELIVERY", "DIRECT_UPI"]),
                customer_notes="Please arrive promptly and bring standard tools.",
                supervisor_verified=(random.random() < 0.20),
                created_at=job_date - timedelta(hours=3),
                assigned_at=job_date - timedelta(hours=2),
                accepted_at=job_date - timedelta(hours=1),
                started_at=job_date,
                completed_at=job_date + timedelta(minutes=srv.estimated_duration_minutes),
            )
            db.add(job)
            db.flush()

            # Create settlement ledger record
            comm = round(price * coop.commission_rate, 2)
            welf = round(price * coop.welfare_contribution_rate, 2)
            w_share = round(price - comm - welf, 2)

            settlement = CooperativeSettlement(
                job_id=job.id,
                cooperative_id=coop.id,
                worker_id=assigned_w.id,
                gross_amount=price,
                worker_amount=w_share,
                cooperative_amount=comm,
                welfare_amount=welf,
                adjustment_amount=0.0,
                payment_method=job.payment_method,
                payment_status="PAID",
                settlement_status="SETTLED",
                settled_at=job.completed_at,
            )
            db.add(settlement)

            # Generate customer review for 40% of jobs
            if random.random() < 0.40:
                review_rating = random.choices([5.0, 4.5, 4.0, 3.5], weights=[60, 25, 10, 5])[0]
                rev = Review(
                    job_id=job.id,
                    customer_id=cust.id,
                    worker_id=assigned_w.id,
                    rating=review_rating,
                    comment=random.choice([
                        "Excellent work, highly professional and punctual.",
                        "Very cooperative worker, resolved the issue quickly.",
                        "Great cooperative platform, transparent pricing.",
                        "Neat and clean work, explained everything well.",
                    ]),
                    tags=json.dumps(["Punctual", "Skilled", "Verified"]),
                    created_at=job.completed_at + timedelta(minutes=15),
                )
                db.add(rev)

            if j_idx % 200 == 0:
                db.commit()
                print(f"  ...seeded {j_idx} jobs")

        db.commit()

        # Seed 5 active pending/in-progress jobs for live demoing right now
        print("[LIVE] Creating 5 Active Live Jobs for instant dashboard testing...")
        active_states = [JobStatus.REQUESTED, JobStatus.ASSIGNED, JobStatus.ACCEPTED, JobStatus.IN_PROGRESS]
        for a_idx, st in enumerate(active_states, start=1):
            srv = random.choice(services)
            coop = db.query(Cooperative).filter(Cooperative.id == srv.cooperative_id).first()
            live_job = Job(
                booking_ref=f"KS-DEMO-{a_idx:03d}",
                customer_id=customer_profile.id,
                service_id=srv.id,
                cooperative_id=coop.id,
                assigned_worker_id=worker_profile_1.id if st != JobStatus.REQUESTED else None,
                status=st,
                slot_start=datetime.now(timezone.utc) + timedelta(hours=a_idx),
                slot_end=datetime.now(timezone.utc) + timedelta(hours=a_idx + 1),
                address="Sector 14, Gurugram, Haryana",
                latitude=28.4595,
                longitude=77.0266,
                is_emergency=(a_idx == 1),
                price_estimate=srv.base_price + 50.0,
                payment_status=PaymentStatus.PENDING,
                payment_method="ONLINE_SIMULATED",
                customer_notes="Demo active job for SIH live evaluation.",
                created_at=datetime.now(timezone.utc),
            )
            db.add(live_job)
        db.commit()

        print("[PROJECTS] Seeding 3 Institutional Multi-Worker Projects (P1)...")
        institutional_contracts = [
            {
                "client": "CPWD (Central Public Works Dept) New Delhi",
                "title": "Government Quarters Electrification & Sanitary Renovation",
                "description": "Comprehensive electrical rewiring and sanitary plumbing overhaul for 40 residential staff quarters at Daryaganj.",
                "headcount": 18,
                "skills": {"Electrician": 8, "Plumber": 6, "Mason": 4},
                "budget": 450000.0,
                "duration_days": 45,
                "status": "ACTIVE",
                "progress": 42.0,
            },
            {
                "client": "Delhi Metro Rail Corporation (DMRC)",
                "title": "Metro Station Concourse Tiling & Structural Maintenance",
                "description": "Floor tiling replacement, anti-skid re-grouting, and masonry structural repair across 3 interchange metro stations.",
                "headcount": 24,
                "skills": {"Mason": 14, "Painter": 6, "Welder": 4},
                "budget": 780000.0,
                "duration_days": 60,
                "status": "ACTIVE",
                "progress": 65.0,
            },
            {
                "client": "Apollo Indraprastha Hospital Complex",
                "title": "Annual Facility Deep Sanitation & Minor Carpentry Framework",
                "description": "Preventive maintenance, door closure repairs, and emergency plumbing standby teams.",
                "headcount": 12,
                "skills": {"Carpenter": 5, "Plumber": 4, "Electrician": 3},
                "budget": 320000.0,
                "duration_days": 90,
                "status": "PLANNED",
                "progress": 10.0,
            },
        ]

        for p_data in institutional_contracts:
            project = InstitutionalProject(
                client_name=p_data["client"],
                title=p_data["title"],
                description=p_data["description"],
                cooperative_id=cooperatives[0].id,
                supervisor_id=supervisor_user.id,
                required_headcount=p_data["headcount"],
                skills_breakdown=json.dumps(p_data["skills"]),
                assigned_workers=json.dumps([w.id for w in workers[:p_data["headcount"]]]),
                start_date=today - timedelta(days=15),
                end_date=today + timedelta(days=p_data["duration_days"]),
                budget=p_data["budget"],
                amount_disbursed=round(p_data["budget"] * (p_data["progress"] / 100.0), 2),
                status=p_data["status"],
                progress_percentage=p_data["progress"],
                milestones=json.dumps([
                    {"title": "Phase 1: Diagnostic Survey & Material Procurement", "completed": True},
                    {"title": "Phase 2: Core Mechanical & Electrical Overhaul", "completed": p_data["progress"] > 40},
                    {"title": "Phase 3: Final Quality Inspection & Supervisor Handover", "completed": False},
                ]),
            )
            db.add(project)
        db.commit()

        print("\n[SUCCESS] KarmSetu Database Seeding Successfully Completed!")
        print("---------------------------------------------------------------")
        print("[CREDENTIALS] Test Credentials for Demo & Antigravity Validation:")
        print("  Cooperative Admin:  admin@karmsetu.in      | Password123!")
        print("  Worker:             worker@karmsetu.in     | Password123!")
        print("  Customer:           customer@karmsetu.in   | Password123!")
        print("  Supervisor:         supervisor@karmsetu.in | Password123!")
        print("---------------------------------------------------------------")
        print(f"[STATS] 5 Cooperatives | {len(workers)} Workers | {len(services)} Services | 1,050+ Historical Jobs")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seeding error: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
