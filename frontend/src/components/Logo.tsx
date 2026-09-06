import React from 'react';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showTagline?: boolean;
}

export const Logo: React.FC<LogoProps> = ({ size = 'md', showTagline = true }) => {
  const iconSizes = {
    sm: 'w-7 h-7',
    md: 'w-9 h-9',
    lg: 'w-12 h-12',
  };

  const titleSizes = {
    sm: 'text-base',
    md: 'text-xl',
    lg: 'text-2xl',
  };

  return (
    <div className="flex items-center gap-3 select-none">
      {/* Sober, dignified cooperative emblem (Bridge / Interlocking Hands Motif) */}
      <div className={`${iconSizes[size]} bg-slate-900 text-white rounded-lg flex items-center justify-center p-1.5 shadow-sm border border-slate-700 flex-shrink-0`}>
        <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
          {/* Bridge arch / Foundation */}
          <path d="M6 38C6 38 14 26 24 26C34 26 42 38 42 38" stroke="#F59E0B" strokeWidth="4" strokeLinecap="round" />
          <path d="M12 38V30M24 38V26M36 38V30" stroke="#CBD5E1" strokeWidth="2.5" strokeLinecap="round" />
          
          {/* Two stylized interlocking hands / handshake forming unity */}
          <path d="M16 18L24 12L32 18" stroke="#38BDF8" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="24" cy="18" r="4" fill="#F59E0B" />
          
          {/* Ground baseline */}
          <path d="M4 42H44" stroke="#94A3B8" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
      </div>

      <div className="flex flex-col">
        <div className="flex items-baseline gap-1.5">
          <span className={`font-bold tracking-tight text-slate-900 font-sans ${titleSizes[size]}`}>
            KARM<span className="text-amber-700">SETU</span>
          </span>
          <span className="text-xs font-semibold text-slate-500 tracking-wider">
            कर्म सेतु
          </span>
        </div>
        {showTagline && (
          <span className="text-[11px] font-medium text-slate-500 leading-none">
            Cooperative Labour Digital Operating System
          </span>
        )}
      </div>
    </div>
  );
};
