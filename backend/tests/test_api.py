import asyncio
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from google import genai
from google.genai import errors

from backend.app.main import app
from backend.app.schemas import AnalysisReport, AnalyzeRequest
from backend.app.services.errors import AnalysisError
from backend.app.services.gemini import build_gemini_response_schema
from backend.app.services.gemini import analyze_with_gemini

client = TestClient(app)


def sample_report() -> dict:
    return {
        "role_summary": "A student internship focused on data analysis.",
        "mandatory_requirements": [
            {"requirement": "Python", "status": "Met", "evidence": "The student lists Python as a skill."},
            {"requirement": "Currently enrolled", "status": "Unknown", "evidence": "Enrollment status was not provided."},
        ],
        "preferred_requirements": [],
        "demonstrated_skills": [{"skill": "Python", "evidence": "Listed in student skills."}],
        "potential_skill_gaps": [],
        "preparation_actions": [{"action": "Prepare a project example.", "reason": "The role asks for analytical work."}],
        "missing_or_ambiguous_details": ["The application deadline is not stated."],
    }


def valid_request() -> dict:
    return {
        "opportunity_description": "Data intern. Mandatory: Python and current enrollment.",
        "company_name": "Example Co",
        "source_url": "https://example.com/jobs/data-intern",
        "student_education": "BSc Computer Science student",
        "student_skills": ["Python", "Excel"],
        "graduation_year": 2027,
        "projects_or_experience": "Course project using Python for data cleanup.",
        "daily_preparation_minutes": 45,
    }


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_gemini_schema_omits_unsupported_additional_properties():
    schema = build_gemini_response_schema()

    def contains_additional_properties(value):
        if isinstance(value, dict):
            return "additionalProperties" in value or any(contains_additional_properties(child) for child in value.values())
        if isinstance(value, list):
            return any(contains_additional_properties(child) for child in value)
        return False

    assert not contains_additional_properties(schema)


def test_analyze_returns_validated_report(monkeypatch: pytest.MonkeyPatch):
    async def fake_analysis(_request):
        return AnalysisReport.model_validate(sample_report())

    monkeypatch.setattr("backend.app.api.analyze_with_gemini", fake_analysis)
    response = client.post("/api/analyze", json=valid_request())

    assert response.status_code == 200
    body = response.json()
    assert body["mandatory_requirements"][0]["status"] == "Met"
    assert body["mandatory_requirements"][1]["status"] == "Unknown"
    assert "salary" not in body


def test_invalid_request_is_rejected_before_analysis():
    payload = valid_request()
    payload["student_skills"] = []
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 422


def test_missing_api_key_error_is_safe(monkeypatch: pytest.MonkeyPatch):
    async def missing_key(_request):
        raise AnalysisError("AI analysis is not configured. Set GEMINI_API_KEY in the backend environment.", 503)

    monkeypatch.setattr("backend.app.api.analyze_with_gemini", missing_key)
    response = client.post("/api/analyze", json=valid_request())
    assert response.status_code == 503
    assert response.json()["detail"] == "AI analysis is not configured. Set GEMINI_API_KEY in the backend environment."


def test_provider_failures_are_sanitized(monkeypatch: pytest.MonkeyPatch):
    async def provider_failure(_request):
        raise AnalysisError("The AI analysis timed out. Please try again.", 504)

    monkeypatch.setattr("backend.app.api.analyze_with_gemini", provider_failure)
    response = client.post("/api/analyze", json=valid_request())
    assert response.status_code == 504
    assert response.json() == {"detail": "The AI analysis timed out. Please try again."}


def run_gemini_failure(monkeypatch: pytest.MonkeyPatch, failure: Exception, timeout: float = 1):
    class FakeModels:
        async def generate_content(self, **_kwargs):
            if isinstance(failure, asyncio.TimeoutError):
                await asyncio.sleep(2)
            raise failure

    class FakeAsyncClient:
        models = FakeModels()

        async def aclose(self):
            return None

    class FakeClient:
        aio = FakeAsyncClient()

        def __init__(self, **_kwargs):
            pass

    monkeypatch.setattr(genai, "Client", FakeClient)
    monkeypatch.setattr(
        "backend.app.services.gemini.get_settings",
        lambda: SimpleNamespace(
            gemini_api_key="test-key",
            gemini_model="gemini-3.8-flash",
            gemini_http_timeout_seconds=0.5,
            gemini_timeout_seconds=timeout,
        ),
    )


@pytest.mark.parametrize(
    ("status", "expected_status", "message"),
    [
        (401, 502, "Gemini authentication failed."),
        (403, 502, "Gemini authentication failed."),
        (429, 503, "The AI service quota is temporarily unavailable."),
        (503, 503, "Gemini is temporarily unavailable."),
    ],
)
def test_gemini_provider_statuses_are_classified(
    monkeypatch: pytest.MonkeyPatch, status: int, expected_status: int, message: str
):
    from backend.app.services.errors import AnalysisError

    run_gemini_failure(monkeypatch, errors.APIError(status, {"error": {"message": "sensitive provider detail"}}))
    with pytest.raises(AnalysisError) as caught:
        asyncio.run(analyze_with_gemini(AnalyzeRequest.model_validate(valid_request())))

    assert caught.value.status_code == expected_status
    assert caught.value.message.startswith(message)
    assert "sensitive provider detail" not in caught.value.message


def test_gemini_request_timeout_is_classified(monkeypatch: pytest.MonkeyPatch):
    from backend.app.services.errors import AnalysisTimeoutError

    run_gemini_failure(monkeypatch, asyncio.TimeoutError(), timeout=0.01)
    with pytest.raises(AnalysisTimeoutError):
        asyncio.run(analyze_with_gemini(AnalyzeRequest.model_validate(valid_request())))
