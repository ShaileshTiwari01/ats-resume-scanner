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
        placeholder="Paste the full job description here — include required skills, qualifications, and responsibilities for best results..."
        className="w-full rounded-xl border border-slate-200 bg-white/60 px-4 py-3 text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-400 focus:border-transparent resize-y min-h-[200px] disabled:opacity-60"
      />
      <p className="mt-2 text-xs text-slate-400">
        Tip: Include the full posting for more accurate keyword matching.
      </p>
    </div>
  );
}
