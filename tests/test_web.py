"""Tests for the Flask web application."""

import json
import pytest
from src.variant_classifier.web.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestIndexPage:
    def test_index_loads(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"ACMG/AMP" in response.data

    def test_index_has_checkboxes(self, client):
        response = client.get("/")
        assert b"PVS1" in response.data
        assert b"BA1" in response.data


class TestClassifyAPI:
    def test_classify_basic(self, client):
        response = client.post(
            "/api/classify",
            data=json.dumps({"codes": ["PVS1", "PS1"]}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["classification"] == "Pathogenic"
        assert data["total_points"] == 12

    def test_classify_vus(self, client):
        response = client.post(
            "/api/classify",
            data=json.dumps({"codes": ["PM2", "PP3"]}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        assert data["classification"] == "VUS (Uncertain Significance)"
        assert data["total_points"] == 3

    def test_classify_missing_codes(self, client):
        response = client.post(
            "/api/classify",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_classify_invalid_code(self, client):
        response = client.post(
            "/api/classify",
            data=json.dumps({"codes": ["FAKE"]}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_classify_codes_not_list(self, client):
        response = client.post(
            "/api/classify",
            data=json.dumps({"codes": "PVS1"}),
            content_type="application/json",
        )
        assert response.status_code == 400


class TestAdviseAPI:
    def test_advise_basic(self, client):
        response = client.post(
            "/api/advise",
            data=json.dumps({"codes": ["PM2", "PP3"]}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["current_classification"] == "VUS (Uncertain Significance)"
        assert len(data["upgrades"]) > 0
        assert len(data["downgrades"]) > 0

    def test_advise_has_options(self, client):
        response = client.post(
            "/api/advise",
            data=json.dumps({"codes": ["PM2", "PP3"]}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        lp_upgrade = next(u for u in data["upgrades"] if u["target_short"] == "LP")
        assert len(lp_upgrade["options"]) > 0
        assert "codes" in lp_upgrade["options"][0]
        assert "descriptions" in lp_upgrade["options"][0]
        assert "points" in lp_upgrade["options"][0]

    def test_advise_missing_codes(self, client):
        response = client.post(
            "/api/advise",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_advise_returns_points_breakdown(self, client):
        response = client.post(
            "/api/advise",
            data=json.dumps({"codes": ["PM2", "PP3", "BP1"]}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        assert data["pathogenic_points"] == 3  # PM2(2) + PP3(1)
        assert data["benign_points"] == -1     # BP1(-1)
        assert data["total_points"] == 2

    def test_advise_invalid_code(self, client):
        response = client.post(
            "/api/advise",
            data=json.dumps({"codes": ["FAKE"]}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_advise_codes_not_list(self, client):
        response = client.post(
            "/api/advise",
            data=json.dumps({"codes": "PVS1"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_advise_duplicate_code(self, client):
        response = client.post(
            "/api/advise",
            data=json.dumps({"codes": ["PVS1", "PVS1"]}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Duplicate" in data["error"]

    def test_advise_max_codes_parameter(self, client):
        response = client.post(
            "/api/advise",
            data=json.dumps({"codes": ["PM2"], "max_codes": 2}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_advise_max_codes_too_high(self, client):
        response = client.post(
            "/api/advise",
            data=json.dumps({"codes": ["PM2"], "max_codes": 99}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_advise_max_codes_zero(self, client):
        response = client.post(
            "/api/advise",
            data=json.dumps({"codes": ["PM2"], "max_codes": 0}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_classify_duplicate_code(self, client):
        response = client.post(
            "/api/classify",
            data=json.dumps({"codes": ["PVS1", "PVS1"]}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Duplicate" in data["error"]

    def test_advise_pathogenic_no_upgrades(self, client):
        response = client.post(
            "/api/advise",
            data=json.dumps({"codes": ["PVS1", "PS1"]}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        assert data["current_classification"] == "Pathogenic"
        assert len(data["upgrades"]) == 0
        assert len(data["downgrades"]) > 0


class TestCodesAPI:
    def test_list_codes(self, client):
        response = client.get("/api/codes")
        data = json.loads(response.data)
        assert response.status_code == 200
        assert len(data["codes"]) == 28

    def test_codes_have_fields(self, client):
        response = client.get("/api/codes")
        data = json.loads(response.data)
        code = data["codes"][0]
        assert "code" in code
        assert "direction" in code
        assert "strength" in code
        assert "points" in code
        assert "description" in code
