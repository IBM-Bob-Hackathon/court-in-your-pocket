import { useState, useEffect } from 'react';

const MessageBubble = ({ message, sender, timestamp }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 50);
    return () => clearTimeout(timer);
  }, []);

  const isUser = sender === 'user';

  const formatTime = (date) => {
    if (!date) return '';
    const d = new Date(date);
    let hours = d.getHours();
    const minutes = d.getMinutes();
    const ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12;
    const minutesStr = minutes < 10 ? '0' + minutes : minutes;
    return `${hours}:${minutesStr} ${ampm}`;
  };

  if (isUser) {
    return (
      <div 
        className={`flex justify-end mb-2 transform transition-all duration-300 ease-out ${
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
        }`}
      >
        <div className="bg-green-500 text-white rounded-2xl rounded-tr-sm px-3 py-2 max-w-[75%] shadow-md">
          <p className="text-sm text-left whitespace-pre-wrap break-words leading-relaxed mb-1">
            {message}
          </p>
          <div className="flex items-center justify-end gap-1 text-[11px] text-white/70">
            <span>{formatTime(timestamp)}</span>
            <span className="text-[11px]">✓✓</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`flex justify-start mb-2 transform transition-all duration-300 ease-out ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}
    >
      <div className="bg-slate-700 text-white rounded-2xl rounded-tl-sm px-3 py-2 max-w-[75%] shadow-md">
        <p className="text-sm text-left whitespace-pre-wrap break-words leading-relaxed mb-1">
          {message}
        </p>
        <div className="flex items-center justify-start text-[11px] text-slate-400">
          <span>{formatTime(timestamp)}</span>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;

// Made with Bob
