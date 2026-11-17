import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, MapPin, CalendarDays, Loader2, ArrowUpRight, Radio } from 'lucide-react';
import { db } from '@/api/apiClient';

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
