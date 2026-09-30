export default function JobDescription({ value, onChange, disabled }) {
  return (
    <div className="glass-card p-6">
      <label
        htmlFor="job-description"
        className="block text-sm font-semibold text-slate-700 mb-3"
      >
        Job Description
      </label>
      <textarea
        id="job-description"
        rows={10}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="Paste the job description for the role you are applying to with this resume. Include the role title, requirements, skills, and responsibilities for a more accurate match."
        className="w-full rounded-xl border border-slate-200 bg-white/60 px-4 py-3 text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-400 focus:border-transparent resize-y min-h-[200px] disabled:opacity-60"
      />
      <p className="mt-2 text-xs text-slate-400">
        Tip: Copy the complete job description from the job posting for the most accurate match.
      </p>
    </div>
  );
}
