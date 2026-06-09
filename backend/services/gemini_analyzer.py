import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from datetime import datetime

# Load backend/.env when this module is imported (tests, scripts, Flask)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)

_PLACEHOLDER_KEYS = frozenset({"", "your_gemini_api_key_here"})

# Use placeholders that are NOT interpreted by str.format (avoids KeyError on JSON braces).
ANALYSIS_PROMPT = """You are an expert ATS (Applicant Tracking System) resume analyzer.

Analyze the resume against the job description and return a richer, structured ATS evaluation.

CRITICAL OUTPUT RULES (MUST FOLLOW):
- Return ONLY a single valid JSON object
- Do NOT use markdown
- Do NOT wrap in ```json or ``` code blocks
- Do NOT add explanations, notes, or text before or after the JSON
- Use double quotes for all keys and all string values
- Use plain ASCII quotes (")
- Arrays must contain strings only
- ats_score must be an integer from 0 to 100

Return JSON in EXACTLY this format (same keys, same nesting). Fill values with your analysis:

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

QUALITY REQUIREMENTS:
- top_priority_fixes: EXACTLY 3 items, highest impact first. Each must be job-relevant and specific (1 sentence max).
- Keep each array to 5-8 high-impact items (strings). Avoid generic filler.
- actionable_improvements must be concrete, resume-ready edits (e.g., \"Add 2 quantified outcomes to Projects\"). Keep each item under 120 characters and start with an action verb.
- formatting_issues must focus on ATS-readability problems (tables, columns, headers/footers, images, unusual symbols).
- section_analysis values: 1-3 concise sentences each; include what's good + what's missing.
- overall_feedback: one concise paragraph, practical and specific.

SCORING GUIDELINES:
- 90-100: Excellent match, minor tweaks only
- 70-89: Good match, some gaps
- 50-69: Moderate match, notable gaps
- 30-49: Weak match, significant gaps
- 0-29: Poor match

JOB DESCRIPTION:
__JOB_DESCRIPTION__

RESUME TEXT:
__RESUME_TEXT__
"""

def _gemini_generate_url() -> str:
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    return (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )

REQUIRED_KEYS = (
    "ats_score",
    "overall_feedback",
    "top_priority_fixes",
    "resume_strengths",
    "missing_skills",
    "missing_keywords",
    "formatting_issues",
    "actionable_improvements",
    "section_analysis",
)

LIST_KEYS = (
    "top_priority_fixes",
    "resume_strengths",
    "missing_skills",
    "missing_keywords",
    "formatting_issues",
    "actionable_improvements",
)


def build_prompt(job_description: str, resume_text: str) -> str:
    """Build prompt without str.format to avoid brace conflicts in JSON examples."""
    return (
        ANALYSIS_PROMPT.replace("__JOB_DESCRIPTION__", job_description.strip())
        .replace("__RESUME_TEXT__", resume_text.strip())
    )


def clean_json_text(text: str) -> str:
    """Strip markdown, code fences, and surrounding noise before json.loads."""
    if not text or not text.strip():
        raise ValueError("Analysis service returned an empty response.")

    cleaned = text.strip()

    # Remove markdown code fences (```json ... ``` or ``` ... ```)
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    # Remove leading "json" label sometimes left after fence strip
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].strip()

    # Extract outermost JSON object if extra text wraps it
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]

    return cleaned.strip()


def _log_raw_model_output(response_text: str, attempt: int) -> None:
    """Log raw model output to the terminal for debugging parse issues."""
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    safe_text = (response_text or "").replace("\r\n", "\n")
    print(
        "\n".join(
            [
                f"[TPF VNIT AI][raw-output][{ts}][attempt={attempt}] --- BEGIN ---",
                safe_text,
                f"[TPF VNIT AI][raw-output][{ts}][attempt={attempt}] --- END ---",
            ]
        )
    )


def parse_json_response(text: str) -> dict:
    """Parse Gemini text into a dict with fallback cleaning."""
    cleaned = clean_json_text(text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as first_error:
        # Fallback: fix trailing commas and retry
        repaired = re.sub(r",\s*}", "}", cleaned)
        repaired = re.sub(r",\s*]", "]", repaired)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            snippet = cleaned[:200].replace("\n", " ")
            raise ValueError(
                "Could not parse AI response as JSON. "
                f"Please try again. (Parse error near: {snippet!r}...)"
            ) from first_error


def normalize_result(raw: dict) -> dict:
    """Validate and normalize fields for a consistent API response."""
    if not isinstance(raw, dict):
        raise ValueError("AI response was not a JSON object.")

    result: dict = {}
    for key in REQUIRED_KEYS:
        if key not in raw:
            raise ValueError(f"AI response is missing required field: {key}")

    try:
        result["ats_score"] = max(0, min(100, int(raw["ats_score"])))
    except (TypeError, ValueError) as e:
        raise ValueError("AI response has an invalid ats_score (must be 0-100).") from e

    for key in LIST_KEYS:
        value = raw[key]
        if isinstance(value, list):
            result[key] = [str(item).strip() for item in value if str(item).strip()]
        elif isinstance(value, str) and value.strip():
            result[key] = [value.strip()]
        else:
            result[key] = []

    # Ensure priority list is exactly 3 items when possible.
    if isinstance(result.get("top_priority_fixes"), list):
        result["top_priority_fixes"] = result["top_priority_fixes"][:3]
        if len(result["top_priority_fixes"]) < 3:
            # Derive missing items from the most actionable signals
            derived: list[str] = []
            derived.extend(result.get("actionable_improvements", [])[:3])
            derived.extend(result.get("missing_skills", [])[:3])
            derived.extend(result.get("formatting_issues", [])[:3])
            for d in derived:
                if len(result["top_priority_fixes"]) >= 3:
                    break
                if d and d not in result["top_priority_fixes"]:
                    result["top_priority_fixes"].append(d)
            result["top_priority_fixes"] = result["top_priority_fixes"][:3]

    feedback = raw["overall_feedback"]
    result["overall_feedback"] = str(feedback).strip() if feedback is not None else ""

    if not result["overall_feedback"]:
        result["overall_feedback"] = "Analysis complete. Review the details below."

    # section_analysis
    section_analysis = raw.get("section_analysis", {})
    if not isinstance(section_analysis, dict):
        section_analysis = {}

    result["section_analysis"] = {
        "skills": str(section_analysis.get("skills", "") or "").strip(),
        "projects": str(section_analysis.get("projects", "") or "").strip(),
        "experience": str(section_analysis.get("experience", "") or "").strip(),
        "education": str(section_analysis.get("education", "") or "").strip(),
        "ats_formatting": str(section_analysis.get("ats_formatting", "") or "").strip(),
    }

    # Backward-compatible fields for existing UI (frontend can ignore extras)
    # - resume_weaknesses: combine formatting_issues (ATS blockers) + 1-3 top improvements
    weaknesses: list[str] = []
    weaknesses.extend(result.get("formatting_issues", [])[:5])
    weaknesses.extend(result.get("actionable_improvements", [])[:3])
    result["resume_weaknesses"] = [w for w in weaknesses if w][:8]

    # - suggestions: map actionable improvements
    result["suggestions"] = result.get("actionable_improvements", [])[:8]

    return result


def is_gemini_configured() -> bool:
    """Return True if a non-placeholder GEMINI_API_KEY is loaded."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return bool(key) and key not in _PLACEHOLDER_KEYS


def get_gemini_api_key() -> str:
    """Read and validate GEMINI_API_KEY from environment."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key in _PLACEHOLDER_KEYS:
        raise ValueError(
            "Analysis service is not configured. Please contact your administrator."
        )
    return api_key


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """Analyze resume against job description using Gemini REST API."""
    api_key = get_gemini_api_key()

    if not resume_text.strip():
        raise ValueError("Resume text is empty after PDF extraction.")
    if not job_description.strip():
        raise ValueError("Job description is empty.")

    def _call_model(prompt_text: str) -> str:
        payload = {
            "contents": [{"parts": [{"text": prompt_text}]}],
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
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            try:
                err_json = json.loads(body)
                message = err_json.get("error", {}).get("message", body)
            except json.JSONDecodeError:
                message = body
            raise ValueError(f"Analysis service error ({e.code}): {message}") from e
        except urllib.error.URLError as e:
            raise ValueError(f"Could not reach analysis service: {e.reason}") from e

        if data.get("candidates") and data["candidates"][0].get("finishReason") == "SAFETY":
            raise ValueError("Analysis blocked by content safety filters. Try a different resume.")

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(
                "Unexpected response from analysis service. No result was returned."
            ) from e

    # Attempt 1
    prompt = build_prompt(job_description, resume_text)
    response_text = _call_model(prompt)
    try:
        parsed = parse_json_response(response_text)
        return normalize_result(parsed)
    except ValueError as e:
        # Log raw output and retry once with an extra strictness reminder.
        _log_raw_model_output(response_text, attempt=1)

        retry_prompt = (
            prompt
            + "\n\nFINAL REMINDER: Return ONLY valid JSON. No markdown. No extra text."
        )
        response_text_2 = _call_model(retry_prompt)
        try:
            parsed_2 = parse_json_response(response_text_2)
            return normalize_result(parsed_2)
        except ValueError:
            _log_raw_model_output(response_text_2, attempt=2)
            raise ValueError(
                "We couldn't generate a valid analysis response right now. Please try again."
            ) from e
