const TypingIndicator = () => {
  return (
    <div className="flex justify-start transform transition-all duration-300 ease-out animate-fade-in">
      <div className="mr-auto bg-slate-700 text-slate-100 rounded-2xl rounded-tl-md px-5 py-4 shadow-lg shadow-slate-900/50 max-w-[85%] md:max-w-[75%]">
        <div className="flex space-x-2 items-center">
          <div className="w-2.5 h-2.5 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0ms', animationDuration: '1s' }}></div>
          <div className="w-2.5 h-2.5 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '200ms', animationDuration: '1s' }}></div>
          <div className="w-2.5 h-2.5 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '400ms', animationDuration: '1s' }}></div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;

// Made with Bob
