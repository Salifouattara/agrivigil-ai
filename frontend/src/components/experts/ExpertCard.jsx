import React, { useState } from 'react';
import { MapPin, ArrowUpRight } from 'lucide-react';

export default function ExpertCard({ expert, onContact }) {
  const [failedPhoto, setFailedPhoto] = useState(null);
  const hasContact = !expert.is_demo && !!(expert.phone_number || expert.whatsapp_number);
  const initials = expert.name.replace(/^Dr[. ]*/, '').split(' ').filter(Boolean).map(n => n[0]).slice(0, 2).join('');
  return <article className="av-expert-card">
    <div className="av-expert-profile">
      <div className="av-expert-avatar" style={{ backgroundColor: expert.avatar_color || '#12523A' }}>
        {expert.photo_url && failedPhoto !== expert.photo_url ? <img src={expert.photo_url} alt={expert.name} loading="lazy" onError={() => setFailedPhoto(expert.photo_url)} /> : <span aria-label={expert.name}>{initials}</span>}
      </div>
      <div className="min-w-0"><h4>{expert.name}</h4><p className="av-expert-role">{expert.role}</p>{expert.is_demo && <span className="text-[10px] text-[#7b867b]">Profil de démonstration</span>}</div>
    </div>
    <p className="av-expert-specialty">{expert.specialty}</p>
    <div className="av-expert-bottom"><span><MapPin size={14} />{expert.location}</span><button onClick={() => onContact(expert)} disabled={!hasContact}>{expert.is_demo ? 'Contact à valider' : hasContact ? <>Contacter <ArrowUpRight size={15} /></> : 'Contact indisponible'}</button></div>
  </article>;
}
