import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // Keep this lightweight; Vite/console will show stack traces in dev.
    console.error("UI crashed:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="glass-card p-6 md:p-8">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-100 text-rose-700 flex items-center justify-center font-bold">
              !
            </div>
            <div>
              <h2 className="text-base md:text-lg font-semibold text-slate-900">
                Something went wrong
              </h2>
              <p className="text-sm text-slate-600 mt-1">
                The app hit an unexpected issue while rendering results. Please
                refresh and try again.
              </p>
              {this.props.onReset ? (
                <button
                  type="button"
                  onClick={this.props.onReset}
                  className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-brand-700 bg-brand-100/60 hover:bg-brand-100 rounded-xl px-4 py-2.5 transition-colors"
                >
                  Reset scanner
                </button>
              ) : null}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

