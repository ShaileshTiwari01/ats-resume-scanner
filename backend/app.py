import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from services.gemini_analyzer import analyze_resume, is_gemini_configured
from services.pdf_extractor import extract_text_from_pdf

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "ATS Resume Scanner API",
        "gemini_configured": is_gemini_configured(),
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "Resume PDF file is required."}), 400

    resume_file = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()

    if not resume_file.filename:
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(resume_file.filename):
        return jsonify({"error": "Only PDF files are allowed."}), 400

    if not job_description:
        return jsonify({"error": "Job description is required."}), 400

    resume_file.seek(0, os.SEEK_END)
    size = resume_file.tell()
    resume_file.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify({"error": "File size must be under 10 MB."}), 400

    if not is_gemini_configured():
        return jsonify(
            {
                "error": (
                    "Analysis service is not configured. "
                    "Please contact your administrator."
                )
            }
        ), 503

    try:
        resume_text = extract_text_from_pdf(resume_file)
        if not resume_text:
            return jsonify(
                {"error": "Could not extract text from PDF. The file may be scanned or empty."}
            ), 400

        result = analyze_resume(resume_text, job_description)
        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except json.JSONDecodeError:
        return jsonify(
            {"error": "Could not parse AI response. Please try again."}
        ), 502
    except Exception as e:
        app.logger.exception("Analysis failed")
        return jsonify(
            {"error": "Analysis failed unexpectedly. Please try again."}
        ), 500


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
