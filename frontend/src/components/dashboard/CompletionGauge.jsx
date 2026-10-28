import React from 'react';

export default function CompletionGauge({ percentage = 98.4 }) {
  const radius = 34;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="gauge-container">
      <svg className="gauge-svg" width="88" height="88" viewBox="0 0 88 88">
        <circle
          className="gauge-bg"
          strokeWidth="7"
          stroke="rgba(226, 232, 240, 0.8)"
          fill="transparent"
          r={radius}
          cx="44"
          cy="44"
        />
        <circle
          className="gauge-progress"
          strokeWidth="7"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          stroke="#0284c7"
          fill="transparent"
          r={radius}
          cx="44"
          cy="44"
          transform="rotate(-90 44 44)"
        />
        <text
          x="44"
          y="49"
          className="gauge-text"
          textAnchor="middle"
          dominantBaseline="middle"
        >
          {percentage}%
        </text>
      </svg>
    </div>
  );
}

