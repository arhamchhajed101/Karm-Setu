from fastapi.testclient import TestClient


def test_evaluate_allocation_scoring(client: TestClient):
    # Authenticate as admin
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@karmsetu.in", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Find a job to evaluate (e.g. job 1)
    eval_res = client.post("/api/v1/allocation/evaluate/1", headers=headers)
    assert eval_res.status_code == 200
    data = eval_res.json()

    assert "candidates" in data
    assert "total_eligible_workers" in data
    assert data["total_eligible_workers"] > 0

    top_candidate = data["candidates"][0]
    assert "scores" in top_candidate
    assert "narrative_explanation" in top_candidate
    
    scores = top_candidate["scores"]
    assert "skill_score" in scores
    assert "availability_score" in scores
    assert "distance_score" in scores
    assert "reliability_score" in scores
    assert "workload_score" in scores
    assert "fairness_score" in scores
    assert "total_score" in scores

    # Verify score bounds
    assert 0 <= scores["skill_score"] <= 30
    assert 0 <= scores["availability_score"] <= 20
    assert 0 <= scores["distance_score"] <= 15
    assert 0 <= scores["reliability_score"] <= 15
    assert 0 <= scores["workload_score"] <= 10
    assert 0 <= scores["fairness_score"] <= 10
    assert 0 <= scores["total_score"] <= 100

    # Ensure candidates are sorted descending by total_score
    all_scores = [c["scores"]["total_score"] for c in data["candidates"]]
    assert all_scores == sorted(all_scores, reverse=True)


def test_auto_assign_job(client: TestClient):
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@karmsetu.in", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Auto assign a pending job (e.g. KS-DEMO-001 which is in REQUESTED state)
    # Let's list jobs to find a REQUESTED job
    jobs_res = client.get("/api/v1/jobs?status=REQUESTED", headers=headers)
    jobs = jobs_res.json()
    if jobs:
        target_job_id = jobs[0]["id"]
        assign_res = client.post(f"/api/v1/allocation/auto-assign/{target_job_id}", headers=headers)
        assert assign_res.status_code == 200
        assign_data = assign_res.json()
        assert assign_data["status"] == "ASSIGNED"
        assert assign_data["assigned_worker_id"] is not None
        assert "narrative_explanation" in assign_data
