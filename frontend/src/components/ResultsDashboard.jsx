function ScoreRing({ score }) {
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score / 100) * circumference;

  const getColor = () => {
    if (score >= 76) return "text-emerald-500";
    if (score >= 51) return "text-amber-500";
    return "text-rose-500";
  };

  const getLabel = () => {
    if (score >= 76) return "Strong Match";
    if (score >= 51) return "Moderate Match";
    return "Poor Match";
  };

  return (
    <div className="glass-card p-7 md:p-8 flex flex-col items-center justify-center h-full transition-all duration-200 hover:-translate-y-0.5 hover:shadow-glow">
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-6">
        <span className="inline-flex items-center justify-center w-8 h-8 rounded-xl bg-brand-100 text-brand-700">
          {/* gauge icon */}
          <svg
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 3v2m0 14v2m9-9h-2M5 12H3m15.364-6.364l-1.414 1.414M7.05 16.95l-1.414 1.414m0-11.314L7.05 7.05m10.9 10.9l1.414 1.414M12 8a4 4 0 100 8 4 4 0 000-8z"
            />
          </svg>
        </span>
        ATS Score
      </div>
      <div className="relative w-36 h-36">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle
            cx="60"
            cy="60"
            r="54"
            fill="none"
            stroke="currentColor"
            strokeWidth="10"
            className="text-brand-100"
          />
          <circle
            cx="60"
            cy="60"
            r="54"
            fill="none"
            stroke="currentColor"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className={`${getColor()} transition-all duration-1000 ease-out`}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-extrabold ${getColor()}`}>{score}</span>
          <span className="text-sm text-slate-400">/ 100</span>
        </div>
      </div>
      <p className={`mt-4 font-semibold ${getColor()}`}>{getLabel()}</p>
      <p className="mt-1 text-xs text-slate-400">ATS compatibility rating</p>
    </div>
  );
}

function SaaSCard({ title, icon, badge, children }) {
  return (
    <div className="glass-card p-6 md:p-7 h-full transition-all duration-200 hover:-translate-y-0.5 hover:shadow-glow">
      <div className="flex items-start justify-between gap-3 mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-600 to-brand-400 flex items-center justify-center text-white shadow-md">
            {icon}
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-900 leading-tight">
              {title}
            </h3>
            {badge ? (
              <p className="text-xs text-slate-500 mt-0.5">{badge}</p>
            ) : null}
          </div>
        </div>
      </div>
      {children}
    </div>
  );
}

function truncateLine(text, maxChars = 140) {
  const s = String(text || "").trim();
  if (!s) return "";
  if (s.length <= maxChars) return s;
  return `${s.slice(0, maxChars - 1).trimEnd()}…`;
}

function toBullets(input, { max = 4 } = {}) {
  if (!input) return [];
  if (Array.isArray(input)) {
    return input.map((x) => String(x || "").trim()).filter(Boolean).slice(0, max);
  }

  const text = String(input).trim();
  if (!text) return [];

  // split on newlines, bullet glyphs, or sentence boundaries
  const parts = text
    .replace(/\r\n/g, "\n")
    .split(/\n|•|\u2022|-\s+|\u2014|\u2013|(?<=[.!?])\s+/g)
    .map((p) => p.trim())
    .filter(Boolean);

  const uniq = [];
  for (const p of parts) {
    const cleaned = p.replace(/^[-–—•\s]+/, "").trim();
    if (!cleaned) continue;
    if (!uniq.includes(cleaned)) uniq.push(cleaned);
    if (uniq.length >= max) break;
  }
  return uniq;
}

function EmphasisLine({ text }) {
  const s = truncateLine(text);
  if (!s) return null;

  // Bold common action verbs (keeps items readable without over-highlighting)
  const verbMatch = s.match(
    /^(Add|Fix|Remove|Include|Replace|Quantify|Highlight|Clarify|Reorder|Use|Avoid|Ensure)\b/i
  );
  if (verbMatch) {
    const verb = verbMatch[0];
    const rest = s.slice(verb.length);
    return (
      <span className="leading-relaxed">
        <strong className="font-semibold text-slate-900">{verb}</strong>
        {rest}
      </span>
    );
  }

  // Bold leading clause before ":" if present
  const idx = s.indexOf(":");
  if (idx > 0 && idx < 40) {
    const head = s.slice(0, idx);
    const tail = s.slice(idx);
    return (
      <span className="leading-relaxed">
        <strong className="font-semibold text-slate-900">{head}</strong>
        {tail}
      </span>
    );
  }

  return <span className="leading-relaxed">{s}</span>;
}

function ListBlock({ items, emptyText = "No items identified." }) {
  const list = Array.isArray(items) ? items : [];
  if (list.length === 0) {
    return <p className="text-sm text-slate-400 italic">{emptyText}</p>;
  }
  return (
    <ul className="space-y-2.5 md:space-y-3">
      {list.map((item, i) => (
        <li
          key={i}
          className="flex items-start gap-2.5 text-sm text-slate-700 bg-slate-50/80 rounded-xl px-3 py-2.5 border border-white/60"
        >
          <span className="mt-2 w-1.5 h-1.5 rounded-full bg-brand-500 shrink-0" />
          <EmphasisLine text={item} />
        </li>
      ))}
    </ul>
  );
}

function SectionMiniCard({ title, bullets }) {
  return (
    <div className="rounded-2xl bg-slate-50/80 border border-white/60 p-4 md:p-5">
      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
        {title}
      </p>
      {bullets.length === 0 ? (
        <p className="mt-2 text-sm text-slate-400 italic">No notes.</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {bullets.map((b, idx) => (
            <li key={idx} className="flex items-start gap-2 text-sm text-slate-700">
              <span className="mt-2 w-1.5 h-1.5 rounded-full bg-brand-500 shrink-0" />
              <EmphasisLine text={b} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function SectionAnalysisGrid({ section_analysis }) {
  const s = section_analysis || {};
  const cards = [
    ["Skills", toBullets(s.skills, { max: 3 })],
    ["Projects", toBullets(s.projects, { max: 3 })],
    ["Experience", toBullets(s.experience, { max: 3 })],
    ["Education", toBullets(s.education, { max: 3 })],
    ["ATS Formatting", toBullets(s.ats_formatting, { max: 3 })],
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3 md:gap-4">
      {cards.map(([title, bullets]) => (
        <SectionMiniCard key={title} title={title} bullets={bullets} />
      ))}
    </div>
  );
}

export default function ResultsDashboard({ results, onReset }) {
  const {
    ats_score = 0,
    overall_feedback = "",
    top_priority_fixes = [],
    resume_strengths = [],
    missing_skills = [],
    missing_keywords = [],
    formatting_issues = [],
    actionable_improvements = [],
    section_analysis = {},
  } = results ?? {};

  const overallBullets = toBullets(overall_feedback, { max: 4 });

  return (
    <div className="space-y-6 md:space-y-7">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-slate-900">
            ATS Analysis
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            A structured, ATS-focused breakdown with practical improvements.
          </p>
        </div>
        <button
          type="button"
          onClick={onReset}
          className="inline-flex items-center gap-2 text-sm font-semibold text-brand-700 bg-brand-100/60 hover:bg-brand-100 rounded-xl px-4 py-2.5 transition-colors w-fit"
        >
          <span aria-hidden>←</span> Scan another resume
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <div className="lg:col-span-4">
          <ScoreRing score={ats_score} />
        </div>

        <div className="lg:col-span-8">
          <SaaSCard
            title="Overall Feedback"
            badge="High-level summary (quick scan)"
            icon={
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 8h10M7 12h6m-2 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2h-3l-4 4z"
                />
              </svg>
            }
          >
            {overallBullets.length === 0 ? (
              <p className="text-sm text-slate-400 italic">No summary provided.</p>
            ) : (
              <ul className="space-y-2.5 md:space-y-3">
                {overallBullets.map((b, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2.5 text-sm md:text-[15px] text-slate-700"
                  >
                    <span className="mt-2 w-1.5 h-1.5 rounded-full bg-brand-500 shrink-0" />
                    <EmphasisLine text={b} />
                  </li>
                ))}
              </ul>
            )}
          </SaaSCard>
        </div>
      </div>

      <div className="glass-card p-6 md:p-7 border border-brand-100/60 bg-gradient-to-br from-white/80 to-brand-50/60">
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-600 to-brand-400 flex items-center justify-center text-white shadow-md">
              <span className="text-lg" aria-hidden>🏆</span>
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-900 leading-tight">
                Top 3 Priority Fixes
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Fix these first for the biggest ATS impact
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
          {[0, 1, 2].map((idx) => {
            const text = (Array.isArray(top_priority_fixes) ? top_priority_fixes[idx] : "") || "";
            return (
              <div
                key={idx}
                className="rounded-2xl bg-white/70 border border-white/60 p-4 md:p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-glow"
              >
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-xl bg-brand-100 text-brand-700 flex items-center justify-center font-extrabold">
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    {text ? (
                      <p className="text-sm text-slate-800">
                        <EmphasisLine text={text} />
                      </p>
                    ) : (
                      <p className="text-sm text-slate-400 italic">No priority fix provided.</p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        <SaaSCard
          title="Resume Strengths"
          badge="What you’re doing well"
          icon={<span className="text-lg" aria-hidden>✅</span>}
        >
          <ListBlock items={resume_strengths} emptyText="No strengths detected." />
        </SaaSCard>

        <SaaSCard
          title="Missing Skills"
          badge="Skills required by the job"
          icon={<span className="text-lg" aria-hidden>⚡</span>}
        >
          <ListBlock items={missing_skills} />
        </SaaSCard>

        <SaaSCard
          title="Missing Keywords"
          badge="ATS keywords/phrases to include"
          icon={<span className="text-lg" aria-hidden>🔑</span>}
        >
          <ListBlock items={missing_keywords} />
        </SaaSCard>

        <SaaSCard
          title="Formatting Issues"
          badge="ATS readability blockers"
          icon={<span className="text-lg" aria-hidden>🧾</span>}
        >
          <ListBlock
            items={formatting_issues}
            emptyText="No major ATS formatting issues detected."
          />
        </SaaSCard>

        <SaaSCard
          title="Actionable Improvements"
          badge="High-impact, resume-ready edits"
          icon={<span className="text-lg" aria-hidden>✨</span>}
        >
          <ListBlock
            items={actionable_improvements}
            emptyText="No improvements suggested."
          />
        </SaaSCard>

        <div className="md:col-span-2 xl:col-span-3">
          <SaaSCard
            title="Section Analysis"
            badge="Skills · Projects · Experience · Education · ATS Formatting"
            icon={<span className="text-lg" aria-hidden>📌</span>}
          >
            <SectionAnalysisGrid section_analysis={section_analysis} />
          </SaaSCard>
        </div>
      </div>
    </div>
  );
}
