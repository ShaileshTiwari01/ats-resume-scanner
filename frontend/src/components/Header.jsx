export default function Header() {
  return (
    <header className="text-center mb-10 md:mb-14">
      <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-100 text-brand-700 text-sm font-medium mb-4">
        <span className="w-2 h-2 rounded-full bg-brand-500 animate-pulse" />
        TPF VNIT AI
      </div>
      <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-slate-900">
        ATS Resume{" "}
        <span className="bg-gradient-to-r from-brand-600 to-brand-400 bg-clip-text text-transparent">
          Scanner
        </span>
      </h1>
      <p className="mt-3 text-slate-500 text-base md:text-lg max-w-xl mx-auto">
        Upload your resume, paste the job description, and get instant
        AI-powered resume analysis by TPF VNIT.
      </p>
    </header>
  );
}
