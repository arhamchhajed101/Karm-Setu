from fastapi.testclient import TestClient


def test_demand_forecast_endpoint(client: TestClient):
    res = client.get("/api/v1/analytics/forecast?zone=Central%20Delhi&category=Plumbing&days_ahead=7")
    assert res.status_code == 200
    data = res.json()
    assert data["zone"] == "Central Delhi"
    assert data["service_category"] == "Plumbing"
    assert "daily_forecast" in data
    assert len(data["daily_forecast"]) == 7
    assert data["total_projected_demand_7d"] > 0
    assert data["capacity_status"] in ["DEFICIT", "BALANCED", "SURPLUS"]
    assert "recommendation" in data

    # Check forecast point attributes
    pt = data["daily_forecast"][0]
    assert "predicted_demand" in pt
    assert "confidence_low" in pt
    assert "confidence_high" in pt
    assert pt["confidence_low"] <= pt["predicted_demand"] <= pt["confidence_high"]


def test_skill_gaps_detection(client: TestClient):
    res = client.get("/api/v1/analytics/skill-gaps?zone=Central%20Delhi")
    assert res.status_code == 200
    gaps = res.json()
    assert isinstance(gaps, list)
    for g in gaps:
        assert "service_category" in g
        assert "deficit_count" in g
        assert "severity" in g
        assert "action_item" in g


def test_heatmap_data(client: TestClient):
    res = client.get("/api/v1/analytics/heatmap")
    assert res.status_code == 200
    pts = res.json()
    assert len(pts) >= 5
    for p in pts:
        assert "zone" in p
        assert "latitude" in p
        assert "longitude" in p
        assert "intensity" in p
        assert 0.0 <= p["intensity"] <= 1.0


def test_cooperative_utilization_metrics(client: TestClient):
    res = client.get("/api/v1/analytics/utilization/1")
    assert res.status_code == 200
    data = res.json()
    assert data["cooperative_id"] == 1
    assert "average_utilization_rate" in data
    assert "fairness_gini_coefficient" in data
    assert 0.0 <= data["fairness_gini_coefficient"] <= 1.0
