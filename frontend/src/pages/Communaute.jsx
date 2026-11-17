import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, MapPin, CalendarDays, Loader2, ArrowUpRight, Radio } from 'lucide-react';
import { db } from '@/api/apiClient';
import abidjanMap from '@/assets/abidjan_map.png';

export default function Communaute() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const load = () => {
    setLoading(true); setError('');
    db.entities.HealthAlert.list().then(setAlerts).catch(() => setError('Les signalements ne sont pas disponibles pour le moment.')).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);
  return <div className="av-page pb-6">
    <header className="av-page-header hero-gradient">
      <div className="flex items-center gap-2 text-[#a9e4bb] text-xs uppercase tracking-widest font-semibold"><Radio size={17} />Veille collective</div>
      <h1 className="font-heading text-[28px] font-extrabold text-white mt-4">Observer ensemble.<br />Mieux protéger les cultures.</h1>
      <p className="text-sm text-white/75 mt-3 leading-relaxed">Les signalements partagés par la communauté AgriVigil. Chaque observation aide à mieux comprendre la situation sur le terrain.</p>
    </header>
    <section className="mt-6" aria-labelledby="demo-alert-map-title">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 id="demo-alert-map-title" className="font-heading text-lg font-bold">Carte des alertes</h2>
        <span className="chip bg-[#f7eee0] text-[#8c6428]">Démonstration</span>
      </div>
      <div className="relative h-64 sm:h-80 overflow-hidden rounded-3xl border border-[#10221A]/[0.06] bg-gray-100 shadow-sm">
        <img src={abidjanMap} alt="Carte de démonstration des alertes à Abidjan" className="h-full w-full object-cover" />
        <div className="absolute inset-0 flex items-center justify-center" aria-hidden="true">
          <div className="h-40 w-40 sm:h-56 sm:w-56 rounded-full border-2 border-[#D6473B] bg-[#D6473B]/5" />
        </div>
        <div aria-hidden="true">
          <span className="absolute top-[23%] left-[19%] h-3 w-3 rounded-full border-2 border-white bg-[#D6473B] shadow-md" />
          <span className="absolute top-[48%] left-[49%] h-3 w-3 rounded-full border-2 border-white bg-[#D6473B] shadow-md" />
          <span className="absolute top-[62%] left-[49%] h-3 w-3 rounded-full border-2 border-white bg-[#D6473B] shadow-md" />
          <span className="absolute top-[45%] left-[86%] h-3 w-3 rounded-full border-2 border-white bg-[#D6473B] shadow-md" />
          <span className="absolute top-[38%] left-[42%] h-3 w-3 rounded-full border-2 border-white bg-[#D6473B] shadow-md" />
        </div>
        <span className="absolute top-3 left-3 rounded-full bg-[#D6473B] px-3 py-1 text-[10px] font-extrabold uppercase tracking-wider text-white shadow-sm">5 foyers simulés</span>
        <span className="absolute bottom-3 right-3 rounded-full border border-[#D6473B] bg-white px-3 py-1 text-[10px] font-extrabold uppercase tracking-wider text-[#D6473B] shadow-sm">Rayon 10 km</span>
      </div>
    </section>
    <div className="mt-6 flex flex-wrap items-center justify-between gap-3 mb-5"><div><h2 className="text-lg font-heading font-bold">Signalements récents</h2><p className="text-xs text-[#6b7e70] mt-1">{loading ? 'Chargement…' : `${alerts.length} observation${alerts.length > 1 ? 's' : ''} enregistrée${alerts.length > 1 ? 's' : ''}`}</p></div><Link to="/" className="inline-flex items-center gap-2 text-sm text-[#12523A] font-semibold">Faire un diagnostic <ArrowUpRight size={16} /></Link></div>
    <p className="rounded-xl border border-[#dde7d8] bg-[#edf3e8] p-4 text-xs leading-relaxed text-[#526b48] mb-5">Les signalements sont des observations déclarées, pas des foyers confirmés par une autorité sanitaire. Une validation sur le terrain reste nécessaire.</p>
    {loading ? <div role="status" className="flex justify-center p-12"><Loader2 className="animate-spin text-[#12523A]" /><span className="sr-only">Chargement des signalements</span></div> : error ? <div role="alert" className="card-soft rounded-2xl p-6"><p>{error}</p><button onClick={load} className="mt-3 underline text-[#12523A]">Réessayer</button></div> : alerts.length === 0 ? <div className="card-soft rounded-3xl p-10 text-center"><ShieldCheck className="mx-auto text-[#12523A] mb-4" size={36} /><h3 className="font-heading font-bold">Aucun signalement enregistré</h3><p className="text-sm text-[#6b7e70] mt-2">Vous pouvez partager une observation depuis le résultat d’un diagnostic.</p></div> : <div className="av-alert-grid">{alerts.map(alert => <article key={alert.id} className="card-soft rounded-2xl p-6">
      <div className="flex flex-wrap gap-2 mb-4"><span className="chip bg-[#eff4e9] text-[#526b38]">{alert.crop_name}</span><span className="chip bg-[#f7eee0] text-[#8c6428]">{alert.status === 'active' ? 'À vérifier' : 'Traitée'}</span></div>
      <h3 className="font-heading text-lg font-bold">{alert.disease_name}</h3>
      <div className="mt-4 flex flex-wrap gap-4 text-xs text-[#6b7e70]"><span className="flex items-center gap-1"><MapPin size={14} />{alert.location_label || 'Localisation non précisée'}</span><span className="flex items-center gap-1"><CalendarDays size={14} />{new Date(alert.created_date).toLocaleDateString('fr-FR')}</span></div>
      <p className="mt-4 pt-4 border-t border-[#e5ebe0] text-xs text-[#6b7e70]">Gravité déclarée : {alert.severity}. Contactez un professionnel pour confirmer le diagnostic.</p>
    </article>)}</div>}
  </div>;
}
