import React from "react";

interface IllustrationProps {
  type: "inicio" | "desarrollo" | "dashboards" | "organizaciones" | "conclusiones";
  className?: string;
}

export function Illustration({ type, className }: IllustrationProps) {
  const palette = {
    midnight: "#0a0f1d",
    teal: "#3aa895",
    gold: "#d4a24c",
    rose: "#c66b7d",
  };

  switch (type) {
    case "inicio":
      return (
        <svg viewBox="0 0 400 400" fill="none" className={className}>
          <circle cx="200" cy="200" r="150" stroke={palette.gold} strokeWidth="0.5" strokeDasharray="4 4" opacity="0.3" />
          <rect x="150" y="150" width="100" height="100" rx="12" stroke={palette.teal} strokeWidth="2" />
          <path d="M100 300 C 150 250, 250 250, 300 300" stroke={palette.teal} strokeWidth="1" opacity="0.6" />
          <circle cx="120" cy="320" r="8" fill={palette.gold} />
          <circle cx="280" cy="320" r="8" fill={palette.gold} />
          <path d="M200 150 V 100" stroke={palette.gold} strokeWidth="2" strokeDasharray="2 2" />
        </svg>
      );
    case "desarrollo":
      return (
        <svg viewBox="0 0 400 400" fill="none" className={className}>
          <path d="M50 200 H 350" stroke={palette.midnight} strokeWidth="40" opacity="0.1" />
          <rect x="80" y="180" width="40" height="40" rx="8" fill={palette.teal} />
          <rect x="180" y="180" width="40" height="40" rx="8" fill={palette.gold} />
          <rect x="280" y="180" width="40" height="40" rx="8" fill={palette.teal} />
          <path d="M120 200 H 180" stroke={palette.gold} strokeWidth="2" strokeDasharray="4 4" />
          <path d="M220 200 H 280" stroke={palette.gold} strokeWidth="2" strokeDasharray="4 4" />
          <circle cx="200" cy="200" r="100" stroke={palette.gold} strokeWidth="1" opacity="0.2" />
        </svg>
      );
    case "dashboards":
      return (
        <svg viewBox="0 0 400 400" fill="none" className={className}>
          <rect x="100" y="250" width="40" height="100" rx="4" fill={palette.teal} opacity="0.6" />
          <rect x="180" y="150" width="40" height="200" rx="4" fill={palette.gold} />
          <rect x="260" y="200" width="40" height="150" rx="4" fill={palette.teal} />
          <path d="M80 150 L 200 80 L 320 120" stroke={palette.gold} strokeWidth="3" />
          <circle cx="200" cy="80" r="12" fill={palette.teal} />
        </svg>
      );
    case "organizaciones":
      return (
        <svg viewBox="0 0 400 400" fill="none" className={className}>
          <circle cx="200" cy="200" r="20" fill={palette.gold} />
          {[0, 60, 120, 180, 240, 300].map((angle) => (
            <g key={angle} transform={`rotate(${angle} 200 200)`}>
              <line x1="200" y1="180" x2="200" y2="100" stroke={palette.teal} strokeWidth="2" />
              <circle cx="200" cy="100" r="12" stroke={palette.teal} strokeWidth="2" fill={palette.midnight} />
            </g>
          ))}
        </svg>
      );
    case "conclusiones":
      return (
        <svg viewBox="0 0 400 400" fill="none" className={className}>
          <path d="M200 100 L 230 250 H 170 L 200 100 Z" fill={palette.gold} opacity="0.2" />
          <circle cx="200" cy="150" r="60" stroke={palette.gold} strokeWidth="2" />
          <path d="M180 300 H 220" stroke={palette.rose} strokeWidth="8" strokeLinecap="round" />
          <path d="M200 150 V 220" stroke={palette.rose} strokeWidth="4" />
          <circle cx="200" cy="240" r="4" fill={palette.rose} />
        </svg>
      );
    default:
      return null;
  }
}
