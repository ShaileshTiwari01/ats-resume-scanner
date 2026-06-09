export default function UploadSection({ file, onFileChange, disabled }) {
  const handleDrop = (e) => {
    e.preventDefault();
    if (disabled) return;
    const dropped = e.dataTransfer.files[0];
    if (dropped?.type === "application/pdf") {
      onFileChange(dropped);
    }
  };

  const handleChange = (e) => {
    const selected = e.target.files[0];
    if (selected) onFileChange(selected);
  };

  return (
    <div className="glass-card p-6">
      <label className="block text-sm font-semibold text-slate-700 mb-3">
        Resume (PDF)
      </label>
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
          file
            ? "border-brand-400 bg-brand-50/50"
            : "border-slate-200 hover:border-brand-300 hover:bg-brand-50/30"
        } ${disabled ? "opacity-60 pointer-events-none" : "cursor-pointer"}`}
      >
        <input
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleChange}
          disabled={disabled}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <div className="flex flex-col items-center gap-3">
          <div className="w-14 h-14 rounded-2xl bg-brand-100 flex items-center justify-center">
            <svg
              className="w-7 h-7 text-brand-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>
          {file ? (
            <>
              <p className="font-medium text-brand-700">{file.name}</p>
              <p className="text-sm text-slate-500">
                {(file.size / 1024).toFixed(1)} KB — click or drop to replace
              </p>
            </>
          ) : (
            <>
              <p className="font-medium text-slate-700">
                Drag & drop your resume here
              </p>
              <p className="text-sm text-slate-500">or click to browse (PDF only)</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
