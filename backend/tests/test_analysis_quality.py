import asyncio
import json
import re
from types import SimpleNamespace

import pytest
from google import genai

from backend.app.schemas import AnalysisReport, AnalyzeRequest
from backend.app.services import gemini


LISTING = """Software Development Intern
Mandatory: proficiency in at least one of JavaScript, Python, or Java; SQL; React; Git/GitHub; debugging; software testing; and unit testing.
Responsibilities include maintaining Python and JavaScript code.
Preferred: REST API development experience."""

STUDENT_A = {
    "opportunity_description": LISTING,
    "student_education": "Student A is a third-year B.E. Computer Engineering student.",
    "student_skills": ["Python", "Java", "MySQL", "HTML", "CSS", "basic DSA", "communication", "teamwork"],
    "projects_or_experience": (
        "Built a FastAPI REST API with MySQL integration and a Python face-recognition attendance project. "
        "Has no React or Git/GitHub experience. Has basic Python debugging experience. No testing experience is stated."
    ),
    "daily_preparation_minutes": 60,
}

STUDENT_B = {
    "opportunity_description": LISTING,
    "student_education": "Student B is a third-year B.E. Computer Engineering student.",
    "student_skills": ["JavaScript", "React", "HTML", "CSS", "Git", "GitHub", "basic DSA", "communication", "teamwork"],
    "projects_or_experience": (
        "Built a responsive React event-management website. Explicitly has no SQL, relational database, Python, "
        "or REST API development experience. Has basic frontend debugging experience. No testing experience is stated."
    ),
    "daily_preparation_minutes": 180,
}


def make_report(student: str) -> dict:
    if student == "A":
        mandatory = [
            {"requirement": "Proficiency in at least one of JavaScript, Python, or Java", "status": "Met", "evidence": "Student A lists Python and Java, either of which satisfies the listing's at-least-one language requirement."},
            {"requirement": "SQL", "status": "Met", "evidence": "Student A lists MySQL and describes MySQL integration in the FastAPI REST API project."},
            {"requirement": "React", "status": "Not met", "evidence": "Student A's profile explicitly says they have no React experience."},
            {"requirement": "Git/GitHub", "status": "Not met", "evidence": "Student A's profile explicitly says they have no Git/GitHub experience."},
            {"requirement": "Debugging", "status": "Met", "evidence": "Student A states they have basic Python debugging experience."},
            {"requirement": "Software testing", "status": "Unknown", "evidence": "Student A's profile states basic debugging but gives no software testing evidence."},
            {"requirement": "Unit testing", "status": "Unknown", "evidence": "Student A's profile states basic debugging but does not mention writing or running unit tests."},
        ]
        demonstrated = [
            {"skill": "Python", "evidence": "Student A lists Python and describes the Python face-recognition attendance project."},
            {"skill": "Java", "evidence": "Student A lists Java."},
            {"skill": "MySQL / SQL", "evidence": "Student A lists MySQL and describes MySQL integration in the FastAPI project."},
            {"skill": "FastAPI REST API development", "evidence": "Student A describes building a FastAPI REST API."},
            {"skill": "Debugging", "evidence": "Student A states they have basic Python debugging experience."},
        ]
        gaps = [
            {"skill": "React", "reason": "React is mandatory in the listing, and Student A explicitly reports no React experience."},
            {"skill": "Git/GitHub", "reason": "Git/GitHub is mandatory in the listing, and Student A explicitly reports no experience with it."},
        ]
        actions = [
            ("Day 1 — Build a small React component and verify its behavior (50 min)", "React is a mandatory listed skill that Student A explicitly lacks."),
            ("Day 2 — Practice initializing a Git repository, branching, and committing (50 min)", "The listing requires Git/GitHub, which Student A explicitly lacks."),
            ("Day 3 — Add focused unit tests to a small FastAPI function (50 min)", "Unit testing is separately required and is not established by the debugging experience in the profile."),
            ("Day 4 — Design manual test cases for one API behavior (50 min)", "The listing separately asks for software testing, which the profile does not establish."),
            ("Day 5 — Reproduce and document a bug in the existing FastAPI project (45 min)", "This builds on the basic debugging experience Student A described for the role's debugging requirement."),
            ("Day 6 — Prepare a short walkthrough of the Python, Java, MySQL, and FastAPI project (50 min)", "These are the programming and database technologies Student A can use as direct evidence for this internship."),
            ("Day 7 — Review the listing and organize one evidence example per requirement (45 min)", "This helps Student A explain both demonstrated qualifications and the separate testing areas to develop."),
        ]
    else:
        mandatory = [
            {"requirement": "Proficiency in at least one of JavaScript, Python, or Java", "status": "Met", "evidence": "Student B lists JavaScript, which satisfies the listing's at-least-one language requirement even though Python is not listed."},
            {"requirement": "SQL", "status": "Not met", "evidence": "Student B explicitly reports no SQL or relational database experience."},
            {"requirement": "React", "status": "Met", "evidence": "Student B lists React and describes a responsive React event-management website."},
            {"requirement": "Git/GitHub", "status": "Met", "evidence": "Student B lists Git and GitHub."},
            {"requirement": "Debugging", "status": "Met", "evidence": "Student B states they have basic frontend debugging experience."},
            {"requirement": "Software testing", "status": "Unknown", "evidence": "Student B's profile states basic debugging but gives no software testing evidence."},
            {"requirement": "Unit testing", "status": "Unknown", "evidence": "Student B's profile states basic debugging but does not mention writing or running unit tests."},
        ]
        demonstrated = [
            {"skill": "JavaScript", "evidence": "Student B lists JavaScript and describes the React event-management website."},
            {"skill": "React", "evidence": "Student B lists React and describes the responsive React event-management website."},
            {"skill": "Git/GitHub", "evidence": "Student B lists Git and GitHub."},
            {"skill": "Debugging", "evidence": "Student B states they have basic frontend debugging experience."},
        ]
        gaps = [
            {"skill": "SQL", "reason": "SQL is a mandatory listed skill, and Student B explicitly reports no SQL or relational database experience."},
            {"skill": "REST API development", "reason": "REST API development is preferred, and Student B explicitly reports no REST API development experience."},
        ]
        actions = [
            ("Day 1 — Study SQL filtering, joins, and grouping with practice queries (150 min)", "SQL is a mandatory listing requirement and Student B explicitly reports no experience with it."),
            ("Day 2 — Write and run unit tests for a small JavaScript function (150 min)", "Unit testing is independently required and is not established by the frontend project description."),
            ("Day 3 — Create a manual test checklist for one frontend user flow (150 min)", "Software testing is a separate listed requirement and is not evidenced by the profile."),
            ("Day 4 — Reproduce, isolate, and document a frontend defect (150 min)", "The listing asks for debugging, and this practice builds on Student B's stated basic frontend debugging experience."),
            ("Day 5 — Review the React project and prepare a concise technical walkthrough (150 min)", "React is a mandatory requirement, and the project is direct evidence Student B can explain."),
            ("Day 6 — Rehearse the JavaScript and Git/GitHub workflow used in the project (150 min)", "These demonstrated technologies map directly to the listing's programming-language and repository requirements."),
            ("Day 7 — Review REST API concepts and prepare one question about the preferred qualification (150 min)", "REST API development is preferred, not mandatory, and Student B explicitly reports no experience in it."),
        ]

    return {
        "role_summary": "A software development internship with mandatory language, database, frontend, version-control, debugging, and testing requirements.",
        "mandatory_requirements": mandatory,
        "preferred_requirements": [
            {"requirement": "REST API development experience", "status": "Met" if student == "A" else "Not met", "evidence": "Student A describes a FastAPI REST API with MySQL integration." if student == "A" else "Student B explicitly reports no REST API development experience; the listing places this qualification in the preferred section."}
        ],
        "demonstrated_skills": demonstrated,
        "potential_skill_gaps": gaps,
        "preparation_actions": [{"action": action, "reason": reason} for action, reason in actions],
        "missing_or_ambiguous_details": ["The listing does not provide an application deadline."],
    }


async def get_mocked_report(monkeypatch: pytest.MonkeyPatch, request: AnalyzeRequest, report: dict) -> tuple[AnalysisReport, str]:
    captured = {}

    class FakeModels:
        async def generate_content(self, **kwargs):
            captured["prompt"] = kwargs["contents"]
            return SimpleNamespace(parsed=None, text=json.dumps(report))

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
        gemini,
        "get_settings",
        lambda: SimpleNamespace(
            gemini_api_key="test-key",
            gemini_model="gemini-3.8-flash",
            gemini_http_timeout_seconds=1,
            gemini_timeout_seconds=2,
        ),
    )
    return await gemini.analyze_with_gemini(request), captured["prompt"]


@pytest.mark.parametrize(
    ("profile", "student", "expected"),
    [(STUDENT_A, "A", make_report("A")), (STUDENT_B, "B", make_report("B"))],
)
def test_profile_assessments_are_evidence_grounded_and_keep_preferred_separate(
    monkeypatch: pytest.MonkeyPatch, profile: dict, student: str, expected: dict
):
    report, prompt = asyncio.run(
        get_mocked_report(monkeypatch, AnalyzeRequest.model_validate(profile), expected)
    )
    body = report.model_dump(mode="json")
    by_requirement = {item["requirement"]: item for item in body["mandatory_requirements"]}

    assert json.dumps(LISTING) in prompt
    assert f"Student {student}" in prompt
    assert "it is an OR requirement" in prompt
    assert "debugging, software testing, and unit testing" in prompt
    assert "Evidence of debugging alone does not establish software testing or unit testing" in prompt
    assert body["mandatory_requirements"] == expected["mandatory_requirements"]
    assert by_requirement["Proficiency in at least one of JavaScript, Python, or Java"]["status"] == "Met"
    assert by_requirement["Software testing"]["status"] == "Unknown"
    assert by_requirement["Unit testing"]["status"] == "Unknown"
    assert body["preferred_requirements"][0]["requirement"] == "REST API development experience"
    assert body["preferred_requirements"][0]["status"] == ("Met" if student == "A" else "Not met")
    assert all("REST API" not in item["requirement"] for item in body["mandatory_requirements"])

    if student == "A":
        assert by_requirement["SQL"]["status"] == "Met"
        assert by_requirement["React"]["status"] == "Not met"
        assert by_requirement["Git/GitHub"]["status"] == "Not met"
        assert by_requirement["Debugging"]["status"] == "Met"
        assert body["preferred_requirements"][0]["status"] == "Met"
        assert "does not mention" in by_requirement["Unit testing"]["evidence"]
    else:
        assert by_requirement["SQL"]["status"] == "Not met"
        assert by_requirement["React"]["status"] == "Met"
        assert by_requirement["Git/GitHub"]["status"] == "Met"
        assert by_requirement["Debugging"]["status"] == "Met"
        assert body["preferred_requirements"][0]["status"] == "Not met"


@pytest.mark.parametrize(("profile", "student"), [(STUDENT_A, "A"), (STUDENT_B, "B")])
def test_daily_schedule_respects_profile_time_limit(
    monkeypatch: pytest.MonkeyPatch, profile: dict, student: str
):
    report, _ = asyncio.run(
        get_mocked_report(monkeypatch, AnalyzeRequest.model_validate(profile), make_report(student))
    )
    actions_by_day: dict[int, list[int]] = {}
    for item in report.preparation_actions:
        match = re.match(r"Day (\d) — .+ \((\d+) min\)$", item.action)
        assert match, item.action
        day, minutes = map(int, match.groups())
        actions_by_day.setdefault(day, []).append(minutes)
        assert item.reason.strip()

    assert sorted(actions_by_day) == list(range(1, 8))
    assert all(sum(durations) <= profile["daily_preparation_minutes"] for durations in actions_by_day.values())
    assert all(sum(durations) >= profile["daily_preparation_minutes"] * 0.75 for durations in actions_by_day.values())


def test_same_listing_changes_findings_and_actions_for_each_profile(monkeypatch: pytest.MonkeyPatch):
    report_a, prompt_a = asyncio.run(
        get_mocked_report(monkeypatch, AnalyzeRequest.model_validate(STUDENT_A), make_report("A"))
    )
    report_b, prompt_b = asyncio.run(
        get_mocked_report(monkeypatch, AnalyzeRequest.model_validate(STUDENT_B), make_report("B"))
    )
    mandatory_a = {item.requirement: item.status.value for item in report_a.mandatory_requirements}
    mandatory_b = {item.requirement: item.status.value for item in report_b.mandatory_requirements}

    assert STUDENT_A["opportunity_description"] == STUDENT_B["opportunity_description"]
    assert prompt_a != prompt_b
    assert mandatory_a["SQL"] == "Met" and mandatory_b["SQL"] == "Not met"
    assert mandatory_a["React"] == "Not met" and mandatory_b["React"] == "Met"
    assert report_a.preparation_actions[0].action.startswith("Day 1 — Build a small React")
    assert report_b.preparation_actions[0].action.startswith("Day 1 — Study SQL")
    assert report_a.demonstrated_skills != report_b.demonstrated_skills


def test_missing_daily_time_requests_priorities_without_invented_schedule(monkeypatch: pytest.MonkeyPatch):
    profile = {**STUDENT_A, "daily_preparation_minutes": None}
    expected = make_report("A")
    expected["preparation_actions"] = [
        {"action": "Practice a small React component", "reason": "React is mandatory and the profile explicitly reports no React experience."},
        {"action": "Practice a basic Git/GitHub workflow", "reason": "Git/GitHub is mandatory and the profile explicitly reports no experience."},
    ]
    report, prompt = asyncio.run(
        get_mocked_report(monkeypatch, AnalyzeRequest.model_validate(profile), expected)
    )
    assert "No daily preparation time was supplied" in prompt
    assert "do not invent a schedule, day labels, or minute estimates" in prompt
    assert all(not re.search(r"Day \d|\(\d+ min\)", action.action) for action in report.preparation_actions)
