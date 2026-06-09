const API_BASE = import.meta.env.VITE_API_URL || "";

function parseErrorMessage(data, status) {
  if (data && typeof data.error === "string" && data.error.trim()) {
    return data.error;
  }
  if (status === 413) return "File is too large. Maximum size is 10 MB.";
  if (status === 502)
    return "We received an invalid analysis response. Please try again.";
  if (status === 503)
    return "Analysis service is temporarily unavailable. Please try again later.";
  if (status >= 500) return "Server error. Please try again in a moment.";
  return "Analysis failed. Please try again.";
}

export async function analyzeResume(resumeFile, jobDescription) {
  const formData = new FormData();
  formData.append("resume", resumeFile);
  formData.append("job_description", jobDescription);

  let response;
  try {
    response = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error(
      "Cannot reach the analysis server. Make sure the Flask backend is running on port 5000."
    );
  }

  let data = {};
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      data = await response.json();
    } catch {
      throw new Error("Received an invalid response from the server.");
    }
  }

  if (!response.ok) {
    throw new Error(parseErrorMessage(data, response.status));
  }

  if (typeof data.ats_score !== "number") {
    throw new Error("Analysis completed but the response format was invalid.");
  }

  return data;
}
