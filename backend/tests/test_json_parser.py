"""Unit tests for Gemini JSON response parsing (no API key required)."""

import unittest

from services.gemini_analyzer import clean_json_text, normalize_result, parse_json_response


class TestJsonParser(unittest.TestCase):
    def test_parse_plain_json(self):
        raw = (
            '{'
            '"ats_score": 85,'
            '"overall_feedback": "Good fit.",'
            '"top_priority_fixes": ["Add metrics","Add SQL","Fix formatting"],'
            '"resume_strengths": ["Clear tech stack"],'
            '"missing_skills": ["React"],'
            '"missing_keywords": ["API"],'
            '"formatting_issues": ["Uses tables in Skills section"],'
            '"actionable_improvements": ["Add 2 quantified outcomes to Projects"],'
            '"section_analysis": {'
            '  "skills": "Good breadth but missing React.",'
            '  "projects": "Add measurable impact.",'
            '  "experience": "Solid progression.",'
            '  "education": "Present.",'
            '  "ats_formatting": "Avoid tables/columns."'
            '}'
            '}'
        )
        result = normalize_result(parse_json_response(raw))
        self.assertEqual(result["ats_score"], 85)
        self.assertIn("React", result["missing_skills"])

    def test_parse_markdown_fenced_json(self):
        raw = """Here is the result:
```json
{"ats_score": 72, "overall_feedback": "Moderate match.", "top_priority_fixes": ["Add SQL to Skills","Add metrics to Projects","Remove tables/columns"], "resume_strengths": [], "missing_skills": [], "missing_keywords": ["SQL"], "formatting_issues": [], "actionable_improvements": ["Add SQL to Skills"], "section_analysis": {"skills": "Missing SQL.", "projects": "", "experience": "", "education": "", "ats_formatting": ""}}
```
"""
        result = normalize_result(parse_json_response(raw))
        self.assertEqual(result["ats_score"], 72)

    def test_clean_strips_preamble(self):
        text = 'Sure! {"ats_score": 90, "missing_skills": [], "missing_keywords": [], "resume_weaknesses": [], "suggestions": [], "overall_feedback": "Great."}'
        cleaned = clean_json_text(text)
        self.assertTrue(cleaned.startswith("{"))

    def test_missing_field_raises(self):
        with self.assertRaises(ValueError) as ctx:
            normalize_result({"ats_score": 50})
        self.assertIn("missing required field", str(ctx.exception).lower())

    def test_invalid_json_raises_friendly_message(self):
        with self.assertRaises(ValueError) as ctx:
            parse_json_response("not json at all")
        self.assertIn("Could not parse", str(ctx.exception))

    def test_normalize_adds_legacy_fields(self):
        raw = {
            "ats_score": 60,
            "overall_feedback": "Ok.",
            "top_priority_fixes": ["Add metrics", "Add React", "Fix formatting"],
            "resume_strengths": ["Strong Python background"],
            "missing_skills": ["React"],
            "missing_keywords": ["CI/CD"],
            "formatting_issues": ["Two-column layout"],
            "actionable_improvements": ["Add quantified outcomes"],
            "section_analysis": {
                "skills": "Missing React.",
                "projects": "Add metrics.",
                "experience": "Solid.",
                "education": "OK.",
                "ats_formatting": "Avoid columns.",
            },
        }
        result = normalize_result(raw)
        self.assertIn("resume_weaknesses", result)
        self.assertIn("suggestions", result)
        self.assertIn("top_priority_fixes", result)
        self.assertEqual(len(result["top_priority_fixes"]), 3)


if __name__ == "__main__":
    unittest.main()
