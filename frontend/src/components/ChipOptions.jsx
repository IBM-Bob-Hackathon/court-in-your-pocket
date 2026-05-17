const ChipOptions = ({ options, onSelect }) => {
  if (!options || options.length === 0) return null;

  return (
    <div className="flex justify-start animate-fade-in">
      <div className="flex flex-wrap gap-2 max-w-[85%] md:max-w-[75%]">
        {options.map((option, index) => (
          <button
            key={index}
            onClick={() => onSelect(option)}
            className="px-4 py-2.5 bg-slate-700 hover:bg-slate-600 text-amber-400 hover:text-amber-300 border-2 border-amber-500/30 hover:border-amber-500/60 rounded-full text-sm font-medium transition-all duration-200 shadow-lg shadow-slate-900/30 hover:shadow-amber-500/20 hover:scale-105 active:scale-95"
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ChipOptions;

// Made with Bob
