import React from 'react';
import { MapPin, PhoneCall, Smartphone, User } from 'lucide-react';

export default function ExpertCard({ expert, onContact }) {
  const hasContact = !!(expert.phone_number || expert.whatsapp_number);

  return (
    <div className="card-soft rounded-2xl p-3 flex items-center gap-3">
      <div
        className="w-14 h-14 rounded-full overflow-hidden flex items-center justify-center shrink-0"
        style={{ backgroundColor: expert.avatar_color }}
      >
        {expert.photo_url ? (
          <img src={expert.photo_url} alt={expert.name} className="h-full w-full object-cover" />
        ) : (
          <User className="h-6 w-6 text-white" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <p className="font-heading text-sm font-bold text-[#10221A] truncate">{expert.name}</p>
          {expert.online && <span className="w-2 h-2 rounded-full bg-[#12523A] shrink-0" />}
        </div>
        <p className="text-xs text-[#B4740E] font-body font-medium">{expert.role}</p>
        <p className="text-[11px] text-[#8A9A91] font-body truncate">{expert.specialty}</p>
        <p className="text-[10px] text-[#8A9A91] font-body flex items-center gap-1 mt-0.5">
          <MapPin className="w-2.5 h-2.5" /> {expert.location}
        </p>
      </div>
      <button
        onClick={() => onContact(expert)}
        disabled={!hasContact}
        className={`inline-flex h-10 w-10 items-center justify-center rounded-full text-white shadow-sm transition-colors ${
          hasContact
            ? 'bg-[#12523A] hover:bg-[#0B3D2A]'
            : 'bg-[#DCE7E0]/30 text-[#8A9A91] cursor-not-allowed'
        }`}
        aria-label={hasContact ? 'Contacter' : 'Pas de contact'}
      >
        {expert.whatsapp_number ? <Smartphone className="h-5 w-5" /> : <PhoneCall className="h-5 w-5" />}
      </button>
    </div>
  );
}