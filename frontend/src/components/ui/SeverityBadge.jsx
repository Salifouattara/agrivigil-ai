import React from 'react';

const config = {
  faible: { bg: 'bg-[#E3F6EA]', text: 'text-[#1B7049]', label: 'Faible' },
  modérée: { bg: 'bg-[#FFF7E6]', text: 'text-[#B4740E]', label: 'Modérée' },
  élevée: { bg: 'bg-[#FFF0E2]', text: 'text-[#C9762E]', label: 'Élevée' },
  critique: { bg: 'bg-[#FEECEC]', text: 'text-[#D6473B]', label: 'Critique', pulse: true },
};

export default function SeverityBadge({ severity }) {
  const c = config[severity] || config.faible;
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold font-body ${c.bg} ${c.text} ${c.pulse ? 'severity-pulse' : ''}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.text} bg-current`} />
      {c.label}
    </span>
  );
}
