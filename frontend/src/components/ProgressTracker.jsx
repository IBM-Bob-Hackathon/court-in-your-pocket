const ProgressTracker = ({ currentStep, totalSteps, label }) => {
  const progressPercentage = (currentStep / totalSteps) * 100;

  return (
    <div className="sticky top-0 z-10 bg-gradient-to-b from-slate-900 to-slate-800 text-white shadow-xl border-b border-slate-700">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm md:text-base font-semibold text-slate-200">
            Step {currentStep} of {totalSteps} — <span className="text-amber-400">{label}</span>
          </span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2.5 overflow-hidden shadow-inner">
          <div
            className="bg-gradient-to-r from-amber-400 to-amber-500 h-2.5 rounded-full transition-all duration-700 ease-out shadow-lg shadow-amber-500/50"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default ProgressTracker;

// Made with Bob
