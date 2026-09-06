from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient


def test_job_price_estimate(client: TestClient):
    req_data = {
        "service_id": 1,
        "latitude": 28.6139,
        "longitude": 77.2090,
        "is_emergency": False,
    }
    res = client.post("/api/v1/jobs/estimate", json=req_data)
    assert res.status_code == 200
    data = res.json()
    assert "estimated_total" in data
    assert data["travel_fee"] == 50.0
    assert data["emergency_surge"] == 0.0
    assert data["estimated_total"] == data["base_price"] + 50.0


def test_job_booking_and_settlement_lifecycle(client: TestClient):
    # 1. Login as customer
    login_cust = client.post(
        "/api/v1/auth/login",
        json={"email": "customer@karmsetu.in", "password": "Password123!"},
    )
    cust_token = login_cust.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # 2. Create a job booking
    now = datetime.now(timezone.utc)
    job_payload = {
        "service_id": 1,
        "slot_start": (now + timedelta(hours=2)).isoformat(),
        "slot_end": (now + timedelta(hours=3)).isoformat(),
        "address": "45 Barakhamba Road, Connaught Place, New Delhi",
        "latitude": 28.6300,
        "longitude": 77.2200,
        "is_emergency": False,
        "customer_notes": "Main tap leaking heavily in bathroom.",
        "payment_method": "ONLINE_SIMULATED",
    }
    create_res = client.post("/api/v1/jobs", json=job_payload, headers=cust_headers)
    assert create_res.status_code == 201
    job = create_res.json()
    job_id = job["id"]
    assert job["status"] == "REQUESTED"
    assert job["booking_ref"].startswith("KS-")

    # 3. Login as admin & auto-assign
    login_admin = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@karmsetu.in", "password": "Password123!"},
    )
    admin_token = login_admin.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    assign_res = client.post(f"/api/v1/allocation/auto-assign/{job_id}", headers=admin_headers)
    assert assign_res.status_code == 200

    # 4. Progress job status: ACCEPTED -> IN_PROGRESS -> COMPLETED
    step1 = client.patch(
        f"/api/v1/jobs/{job_id}/status",
        json={"status": "ACCEPTED", "notes": "Worker confirmed ETA 15 mins"},
        headers=admin_headers,
    )
    assert step1.status_code == 200
    assert step1.json()["status"] == "ACCEPTED"

    step2 = client.patch(
        f"/api/v1/jobs/{job_id}/status",
        json={"status": "IN_PROGRESS"},
        headers=admin_headers,
    )
    assert step2.status_code == 200
    assert step2.json()["status"] == "IN_PROGRESS"

    step3 = client.patch(
        f"/api/v1/jobs/{job_id}/status",
        json={"status": "COMPLETED", "final_price": 350.0},
        headers=admin_headers,
    )
    assert step3.status_code == 200
    assert step3.json()["status"] == "COMPLETED"

    # 5. Simulate payment & verify ledger distribution
    sim_res = client.post(
        "/api/v1/settlements/simulate-payment",
        json={"job_id": job_id, "payment_method": "ONLINE_SIMULATED", "amount": 350.0, "simulate_status": "PAID"},
        headers=cust_headers,
    )
    assert sim_res.status_code == 200
    settlement = sim_res.json()
    assert settlement["gross_amount"] == 350.0
    # 15% coop = 52.5, 5% welfare = 17.5, 80% worker = 280.0
    assert settlement["cooperative_amount"] == 52.5
    assert settlement["welfare_amount"] == 17.5
    assert settlement["worker_amount"] == 280.0
    assert settlement["settlement_status"] == "SETTLED"
