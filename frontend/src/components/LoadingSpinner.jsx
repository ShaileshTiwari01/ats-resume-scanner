export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-7">
      <div className="relative w-20 h-20">
        <div className="absolute inset-0 rounded-full border-4 border-brand-100" />
        <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-brand-600 animate-spin-slow" />
        <div className="absolute inset-3 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-glow">
          <svg
            className="w-6 h-6 text-white"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
      </div>
      <div className="text-center">
        <p className="text-lg md:text-xl font-semibold text-slate-900">
          Analyzing your resume…
        </p>
        <p className="text-sm text-slate-500 mt-1 animate-pulse-slow max-w-md mx-auto">
          Extracting content, matching requirements, and generating a structured ATS report with TPF VNIT AI
        </p>
      </div>
      <div className="flex gap-2">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-2 h-2 rounded-full bg-brand-500 animate-bounce"
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </div>
    </div>
  );
}
