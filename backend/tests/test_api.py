"""API tests with mocked Gemini (no API key required)."""

import io
import json
import unittest
from unittest.mock import patch

from app import app


MOCK_RESULT = {
    "ats_score": 85,
    "overall_feedback": "Strong resume but missing some required skills.",
    "resume_strengths": ["Clear experience progression"],
    "missing_skills": ["React", "SQL"],
    "missing_keywords": ["API", "analytics"],
    "formatting_issues": ["Tables in Skills section"],
    "actionable_improvements": ["Add measurable impact in projects"],
    "section_analysis": {
        "skills": "Missing React/SQL.",
        "projects": "Add metrics.",
        "experience": "Solid.",
        "education": "OK.",
        "ats_formatting": "Avoid tables.",
    },
    # legacy keys still supported
    "resume_weaknesses": ["Tables in Skills section"],
    "suggestions": ["Add measurable impact in projects"],
}


class TestAnalyzeAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("app.analyze_resume", return_value=MOCK_RESULT)
    @patch("app.extract_text_from_pdf", return_value="Jane Doe\nPython developer")
    def test_analyze_returns_full_payload(self, _pdf, _gemini):
        data = {
            "resume": (io.BytesIO(b"%PDF-1.4 fake"), "resume.pdf"),
            "job_description": "Looking for a Python developer with React experience.",
        }
        response = self.client.post(
            "/api/analyze",
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.data)
        self.assertEqual(body["ats_score"], 85)
        self.assertIn("resume_weaknesses", body)
        self.assertIn("overall_feedback", body)

    def test_analyze_missing_job_description(self):
        data = {
            "resume": (io.BytesIO(b"%PDF-1.4"), "resume.pdf"),
            "job_description": "",
        }
        response = self.client.post(
            "/api/analyze",
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.data)
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()
