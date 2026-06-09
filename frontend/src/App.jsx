import { useState } from "react";
import { analyzeResume } from "./api";
import Header from "./components/Header";
import UploadSection from "./components/UploadSection";
import JobDescription from "./components/JobDescription";
import LoadingSpinner from "./components/LoadingSpinner";
import ResultsDashboard from "./components/ResultsDashboard";
import ErrorBoundary from "./components/ErrorBoundary";

export default function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const canSubmit = resumeFile && jobDescription.trim().length > 0 && !loading;

  const handleAnalyze = async () => {
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await analyzeResume(resumeFile, jobDescription);
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setResumeFile(null);
    setJobDescription("");
    setError(null);
  };

  return (
    <div className="min-h-screen">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-brand-200/30 blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-80 h-80 rounded-full bg-purple-200/20 blur-3xl" />
      </div>

      <main className="relative max-w-5xl mx-auto px-4 py-10 md:py-16">
        <Header />

        {loading ? (
          <div className="glass-card">
            <LoadingSpinner />
          </div>
        ) : results ? (
          <ErrorBoundary onReset={handleReset}>
            <ResultsDashboard results={results} onReset={handleReset} />
          </ErrorBoundary>
        ) : (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
              <UploadSection
                file={resumeFile}
                onFileChange={setResumeFile}
                disabled={loading}
              />
              <JobDescription
                value={jobDescription}
                onChange={setJobDescription}
                disabled={loading}
              />
            </div>

            {error && (
              <div className="mb-5 px-4 py-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm">
                <div className="flex items-start gap-2.5">
                  <span className="mt-0.5 font-bold">!</span>
                  <div className="flex-1">
                    <p className="font-semibold">Couldn’t complete analysis</p>
                    <p className="mt-0.5 text-rose-700">{error}</p>
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={handleAnalyze}
              disabled={!canSubmit}
              className="w-full py-4 rounded-xl font-semibold text-white bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-700 hover:to-brand-600 shadow-lg shadow-brand-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
            >
              Analyze Resume
            </button>
          </>
        )}

        <footer className="mt-12 text-center text-xs text-slate-400">
          Built by TPF VNIT
        </footer>
      </main>
    </div>
  );
}
