import json
import os
import random
import time
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------------------------
# Load backend/.env
# ---------------------------------------------------------

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)


_PLACEHOLDER_KEYS = frozenset({
    "",
    "your_gemini_api_key_here",
})


# ---------------------------------------------------------
# Gemini configuration
# ---------------------------------------------------------

def _get_model() -> str:
    return os.getenv(
        "GEMINI_MODEL",
        "gemini-3.1-flash-lite"
    ).strip()


def _gemini_generate_url() -> str:
    model = _get_model()

    return (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
    )


# ---------------------------------------------------------
# ATS prompt
# ---------------------------------------------------------

ANALYSIS_PROMPT = """
You are an expert ATS (Applicant Tracking System) resume analyzer.

Analyze the candidate's resume against the provided job description.

Your task is to provide a practical, honest and actionable ATS evaluation.

Return ONLY valid JSON.

The JSON must contain exactly these top-level fields:

{
  "ats_score": 0,
  "overall_feedback": "",
  "top_priority_fixes": [],
  "resume_strengths": [],
  "missing_skills": [],
  "missing_keywords": [],
  "formatting_issues": [],
  "actionable_improvements": [],
  "section_analysis": {
    "skills": "",
    "projects": "",
    "experience": "",
    "education": "",
    "ats_formatting": ""
  }
}

Rules:

1. ats_score must be an integer from 0 to 100.

2. overall_feedback should briefly explain how well the resume matches
   the job description.

3. top_priority_fixes must contain the 3 most important improvements.
   Keep them concise and actionable.

4. resume_strengths should list the strongest relevant parts of the resume.

5. missing_skills should contain skills required or strongly implied by
   the job description that are missing from the resume.

6. missing_keywords should contain important job-description keywords
   that are missing or insufficiently represented in the resume.

7. formatting_issues should contain ATS-related formatting problems.
   If there are no major issues, return an empty array.

8. actionable_improvements should contain specific improvements the
   candidate can make to improve their ATS match.

9. section_analysis should separately evaluate:
   - skills
   - projects
   - experience
   - education
   - ats_formatting

10. Do not invent experience, skills, projects, certifications or
    achievements that are not present in the resume.

11. Base the score primarily on relevance to the provided job description.

12. Keep the response useful and reasonably concise.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""


# ---------------------------------------------------------
# Errors
# ---------------------------------------------------------

class GeminiTransientError(Exception):
    """Temporary Gemini API error that can be retried."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


# ---------------------------------------------------------
# Gemini configuration helpers
# ---------------------------------------------------------

def is_gemini_configured() -> bool:
    """Return True if a valid non-placeholder GEMINI_API_KEY exists."""

    key = os.getenv("GEMINI_API_KEY", "").strip()

    return bool(key) and key not in _PLACEHOLDER_KEYS


def get_gemini_api_key() -> str:
    """Read and validate GEMINI_API_KEY from environment."""

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key or api_key in _PLACEHOLDER_KEYS:
        raise ValueError(
            "Analysis service is not configured. "
            "Please contact your administrator."
        )

    return api_key


# ---------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------

def parse_json_response(text: str) -> dict:
    """Parse Gemini's JSON response safely."""

    if not text or not text.strip():
        raise ValueError("Gemini returned an empty response.")

    cleaned = text.strip()

    # Remove markdown code fences if Gemini adds them.
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Gemini returned invalid JSON."
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError("Gemini returned an unexpected JSON structure.")

    return parsed


# ---------------------------------------------------------
# Normalize result for frontend
# ---------------------------------------------------------

def normalize_result(raw: dict) -> dict:
    """Normalize Gemini output into the structure expected by the UI."""

    required_list_keys = [
        "top_priority_fixes",
        "resume_strengths",
        "missing_skills",
        "missing_keywords",
        "formatting_issues",
        "actionable_improvements",
    ]

    result = {}

    # ATS score
    try:
        result["ats_score"] = max(
            0,
            min(100, int(raw.get("ats_score", 0)))
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "AI response has an invalid ats_score."
        ) from exc

    # Lists
    for key in required_list_keys:
        value = raw.get(key, [])

        if isinstance(value, list):
            result[key] = [
                str(item).strip()
                for item in value
                if str(item).strip()
            ]
        elif isinstance(value, str) and value.strip():
            result[key] = [value.strip()]
        else:
            result[key] = []

    # Exactly 3 priority fixes where possible
    result["top_priority_fixes"] = result["top_priority_fixes"][:3]

    if len(result["top_priority_fixes"]) < 3:
        derived = []

        derived.extend(result["actionable_improvements"][:3])
        derived.extend(result["missing_skills"][:3])
        derived.extend(result["formatting_issues"][:3])

        for item in derived:
            if len(result["top_priority_fixes"]) >= 3:
                break

            if item and item not in result["top_priority_fixes"]:
                result["top_priority_fixes"].append(item)

    result["top_priority_fixes"] = result["top_priority_fixes"][:3]

    # Overall feedback
    feedback = raw.get("overall_feedback", "")

    if isinstance(feedback, str):
        result["overall_feedback"] = feedback.strip()
    else:
        result["overall_feedback"] = str(feedback).strip()

    if not result["overall_feedback"]:
        result["overall_feedback"] = (
            "Analysis complete. Review the details below."
        )

    # Section analysis
    section_analysis = raw.get("section_analysis", {})

    if not isinstance(section_analysis, dict):
        section_analysis = {}

    result["section_analysis"] = {
        "skills": str(
            section_analysis.get("skills", "") or ""
        ).strip(),

        "projects": str(
            section_analysis.get("projects", "") or ""
        ).strip(),

        "experience": str(
            section_analysis.get("experience", "") or ""
        ).strip(),

        "education": str(
            section_analysis.get("education", "") or ""
        ).strip(),

        "ats_formatting": str(
            section_analysis.get("ats_formatting", "") or ""
        ).strip(),
    }

    # Backward-compatible fields for existing frontend
    weaknesses = []

    weaknesses.extend(result["formatting_issues"][:5])
    weaknesses.extend(result["actionable_improvements"][:3])

    result["resume_weaknesses"] = weaknesses[:8]

    result["suggestions"] = result[
        "actionable_improvements"
    ][:8]

    return result


# ---------------------------------------------------------
# Build prompt
# ---------------------------------------------------------

def build_prompt(
    job_description: str,
    resume_text: str
) -> str:

    return (
        ANALYSIS_PROMPT
        .replace("{resume_text}", resume_text.strip())
        .replace("{job_description}", job_description.strip())
    )

# ---------------------------------------------------------
# Gemini API call with retry
# ---------------------------------------------------------

def _call_model(prompt_text: str) -> str:
    """
    Call Gemini REST API.

    Automatically retries temporary errors such as:
    408, 429 and 5xx.

    Retry delays use exponential backoff with jitter.
    """

    api_key = get_gemini_api_key()

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt_text
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.15,
            "maxOutputTokens": 4096,
            "responseMimeType": "application/json",
        },
    }

    url = f"{_gemini_generate_url()}?key={api_key}"

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    # 4 retries = up to 5 total attempts.
    max_retries = 4

    for attempt in range(max_retries + 1):

        try:

            with urllib.request.urlopen(
                request,
                timeout=120
            ) as response:

                body = response.read().decode("utf-8")

                data = json.loads(body)

                # Safety block
                if (
                    data.get("candidates")
                    and data["candidates"][0].get(
                        "finishReason"
                    ) == "SAFETY"
                ):
                    raise ValueError(
                        "Analysis was blocked by content safety "
                        "filters. Try a different resume."
                    )

                try:
                    return (
                        data["candidates"][0]
                        ["content"]
                        ["parts"][0]
                        ["text"]
                    )

                except (
                    KeyError,
                    IndexError,
                    TypeError
                ) as exc:

                    raise ValueError(
                        "Unexpected response from analysis service. "
                        "No result was returned."
                    ) from exc

        except urllib.error.HTTPError as exc:

            body = exc.read().decode(
                "utf-8",
                errors="replace"
            )

            try:
                err_json = json.loads(body)

                message = (
                    err_json
                    .get("error", {})
                    .get("message", body)
                )

            except json.JSONDecodeError:
                message = body

            # Retry only transient errors.
            if (
                exc.code == 408
                or exc.code == 429
                or 500 <= exc.code < 600
            ):

                if attempt < max_retries:

                    # 1s, 2s, 4s, 8s + small jitter
                    delay = min(
                        8,
                        2 ** attempt
                    )

                    jitter = random.uniform(
                        0,
                        0.5
                    )

                    time.sleep(delay + jitter)

                    continue

                raise GeminiTransientError(
                    exc.code,
                    message
                ) from exc

            # Non-transient errors should NOT be retried.
            raise ValueError(
                f"Analysis service error ({exc.code}): "
                f"{message}"
            ) from exc

        except urllib.error.URLError as exc:

            # Network errors are transient.
            if attempt < max_retries:

                delay = min(
                    8,
                    2 ** attempt
                )

                jitter = random.uniform(
                    0,
                    0.5
                )

                time.sleep(delay + jitter)

                continue

            raise ValueError(
                f"Could not reach analysis service: "
                f"{exc.reason}"
            ) from exc

    raise ValueError(
        "Analysis service is temporarily unavailable. "
        "Please try again."
    )


# ---------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------

def analyze_resume(
    resume_text: str,
    job_description: str
) -> dict:
    """
    Analyze resume against job description using Gemini REST API.
    """

    if not resume_text or not resume_text.strip():
        raise ValueError(
            "Resume text is empty after PDF extraction."
        )

    if not job_description or not job_description.strip():
        raise ValueError(
            "Job description is empty."
        )

    prompt = build_prompt(
        job_description,
        resume_text
    )

    # First attempt
    response_text = _call_model(prompt)

    try:
        parsed = parse_json_response(response_text)

        return normalize_result(parsed)

    except ValueError as first_error:

        # One additional attempt only for malformed JSON.
        retry_prompt = (
            prompt
            + "\n\nIMPORTANT: Return ONLY valid JSON. "
              "Do not use markdown, explanations, or code fences."
        )

        try:
            response_text = _call_model(retry_prompt)

            parsed = parse_json_response(response_text)

            return normalize_result(parsed)

        except ValueError as second_error:

            raise ValueError(
                "The analysis service returned an invalid "
                "result. Please try again."
            ) from second_error