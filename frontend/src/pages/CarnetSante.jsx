import { db } from '@/api/apiClient';

import React, { useState, useEffect } from 'react';

import { ClipboardList, Calendar, TrendingUp, TrendingDown, Minus, Loader2, X, BookHeart } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import SeverityBadge from '@/components/ui/SeverityBadge';
import EmptyState from '@/components/ui/EmptyState';
import WaxDivider from '@/components/ui/WaxDivider';
import SpeakButton from '@/components/ui/SpeakButton';
import HealthChart from '@/components/charts/HealthChart';
import { useToast } from '@/components/ui/use-toast';
import moment from 'moment';

const severityScore = { faible: 1, modérée: 2, élevée: 3, critique: 4 };

export default function CarnetSante() {
  const [trackings, setTrackings] = useState([]);
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('30');
  const [activeTab, setActiveTab] = useState('trackings'); // 'trackings' ou 'ordinary'
  const [selectedTrackingId, setSelectedTrackingId] = useState(null);
  const { toast } = useToast();

  useEffect(() => {
    Promise.all([
      db.entities.CropScanTracking.list(),
      db.entities.CropScan.list('-created_date', 150)
    ]).then(([trackingData, scanData]) => {
      setTrackings(trackingData);
      setScans(scanData);

      if (trackingData.length > 0) {
        setSelectedTrackingId(trackingData[0].id);
      }
      setLoading(false);
    }).catch(() => {
      setLoading(false);
    });
  }, []);

  const handleDeleteScan = async (scanId) => {
    try {
      await db.entities.CropScan.delete(scanId);
      setScans(scans.filter(s => s.id !== scanId));
      toast({ title: '✅ Supprimé', description: 'Le scan a été supprimé de votre historique' });
    } catch (err) {
      toast({ title: 'Erreur', description: 'Impossible de supprimer le scan', variant: 'destructive' });
    }
  };

  const handleDeleteTracking = async (trackingId) => {
    if (!window.confirm("Voulez-vous supprimer ce carnet de suivi ? Les scans associés resteront dans votre historique en tant que scans simples.")) return;
    try {
      await db.entities.CropScanTracking.delete(trackingId);
      setTrackings(trackings.filter(t => t.id !== trackingId));
      // Détacher localement les scans de ce suivi
      setScans(scans.map(s => s.tracking_id === trackingId ? { ...s, tracking_id: null } : s));
      toast({ title: '✅ Suivi supprimé', description: 'Le carnet de suivi a été supprimé.' });
      if (selectedTrackingId === trackingId) {
        setSelectedTrackingId(trackings.find(t => t.id !== trackingId)?.id || null);
      }
    } catch (err) {
      toast({ title: 'Erreur', description: 'Impossible de supprimer le carnet de suivi', variant: 'destructive' });
    }
  };

  const filteredScans = scans.filter(s => moment().diff(moment(s.created_date), 'days') <= parseInt(period));
  const ordinaryScans = filteredScans.filter(s => !s.tracking_id);

  const selectedTracking = trackings.find(t => t.id === selectedTrackingId);
  const trackingScans = filteredScans.filter(s => s.tracking_id === selectedTrackingId);
  const trackingScansWithPhotos = trackingScans.filter(s => s.image_url).sort((a, b) => new Date(a.created_date) - new Date(b.created_date));

  const first = trackingScansWithPhotos[0];
  const latest = trackingScansWithPhotos[trackingScansWithPhotos.length - 1];

  let evolutionPct = 0;
  let evolutionLabel = 'STABLE';
  if (first && latest && first.id !== latest.id) {
    const s0 = severityScore[first.severity] || 1;
    const s1 = severityScore[latest.severity] || 1;
    evolutionPct = Math.round(((s1 - s0) / s0) * 100);
    evolutionLabel = evolutionPct < -5 ? 'EN AMÉLIORATION' : evolutionPct > 5 ? 'EN AGGRAVATION' : 'STABLE';
  }
  const currentLevel = latest ? Math.round((severityScore[latest.severity] || 1) * 25) : 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-6 h-6 text-[#12523A] animate-spin" />
      </div>
    );
  }

  return (
    <div className="pb-6">
      <div className="hero-gradient px-5 pt-6 pb-8 rounded-b-[36px]">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-white/15 text-[#7CF2B8]">
            <BookHeart className="w-4 h-4" strokeWidth={2.2} />
          </span>
          <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-white/85">Suivi</span>
        </div>
        <h1 className="font-heading text-[26px] font-extrabold text-white mt-3">Carnet de Santé</h1>
        <p className="text-[13px] text-white/70 mt-1.5">Suivi rigoureux et indépendant de la santé de vos cultures et de vos animaux</p>

        <Tabs value={period} onValueChange={setPeriod} className="mt-4">
          <TabsList className="w-full bg-white/10 rounded-2xl h-10 p-1">
            <TabsTrigger value="7" className="flex-1 rounded-xl text-[12px] font-semibold text-white/70 data-[state=active]:bg-white data-[state=active]:text-[#12523A]">7 jours</TabsTrigger>
            <TabsTrigger value="30" className="flex-1 rounded-xl text-[12px] font-semibold text-white/70 data-[state=active]:bg-white data-[state=active]:text-[#12523A]">30 jours</TabsTrigger>
            <TabsTrigger value="90" className="flex-1 rounded-xl text-[12px] font-semibold text-white/70 data-[state=active]:bg-white data-[state=active]:text-[#12523A]">90 jours</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div className="px-4 mt-4">
        <div className="flex rounded-2xl bg-[#E8F1EC] p-1 gap-1">
          <button
            onClick={() => setActiveTab('trackings')}
            className={`flex-1 py-2.5 rounded-xl text-center text-[12px] font-bold transition-all ${activeTab === 'trackings' ? 'bg-[#12523A] text-white shadow-sm' : 'text-[#5B6B62] hover:text-[#12523A]'}`}
          >
            Mes Carnets de Suivi
          </button>
          <button
            onClick={() => setActiveTab('ordinary')}
            className={`flex-1 py-2.5 rounded-xl text-center text-[12px] font-bold transition-all ${activeTab === 'ordinary' ? 'bg-[#12523A] text-white shadow-sm' : 'text-[#5B6B62] hover:text-[#12523A]'}`}
          >
            Scans simples (Ordinaires)
          </button>
        </div>
      </div>

      {activeTab === 'trackings' ? (
        <div className="mt-4 space-y-4">
          {trackings.length === 0 ? (
            <div className="px-4">
              <EmptyState
                icon={BookHeart}
                title="Aucun carnet de suivi"
                description="Vous n'avez pas encore créé de carnet de suivi. Lorsque vous faites un scan de diagnostic IA, choisissez l'option 'Scan de suivi' pour commencer à mesurer l'évolution d'un sujet dans le temps."
              />
            </div>
          ) : (
            <>
              {/* Sélecteur de suivi horizontal */}
              <div className="flex items-center gap-2 overflow-x-auto pb-1 px-4 scrollbar-none">
                {trackings.map(t => {
                  const isSelected = t.id === selectedTrackingId;
                  const count = scans.filter(s => s.tracking_id === t.id).length;
                  return (
                    <button
                      key={t.id}
                      onClick={() => setSelectedTrackingId(t.id)}
                      className={`flex items-center gap-1.5 px-3.5 py-2 shrink-0 rounded-2xl text-[12px] font-bold transition-all border ${isSelected ? 'bg-[#12523A] border-[#12523A] text-white shadow-sm' : 'bg-white border-[#DCE7E0] text-[#10221A] hover:bg-[#F0FAF4]'}`}
                    >
                      <BookHeart className="w-3.5 h-3.5" />
                      {t.name}
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${isSelected ? 'bg-white/20 text-white' : 'bg-[#DCE7E0] text-[#5B6B62]'}`}>
                        {count}
                      </span>
                    </button>
                  );
                })}
              </div>

              {selectedTracking && (
                <div className="px-4 space-y-4 animate-fadeIn">
                  <div className="flex items-center justify-between gap-4 bg-[#F0FAF4] p-3 rounded-2xl border border-[#DCE7E0]/40">
                    <div>
                      <h2 className="font-heading text-[15px] font-bold text-[#10221A]">{selectedTracking.name}</h2>
                      <p className="text-[10px] text-[#8A9A91] mt-0.5">Suivi initié le {moment(selectedTracking.created_date).format('DD/MM/YYYY')}</p>
                    </div>
                    <button
                      onClick={() => handleDeleteTracking(selectedTracking.id)}
                      className="text-[10px] px-2.5 py-1.5 bg-[#FEECEC] hover:bg-[#FCDAD7] text-[#D6473B] font-bold rounded-xl transition-all"
                    >
                      Supprimer
                    </button>
                  </div>

                  <div className="grid grid-cols-3 gap-2.5">
                    <StatCard label="Scans" value={trackingScans.length} color="#12523A" />
                    <StatCard label="Critiques" value={trackingScans.filter(s => s.severity === 'critique').length} color="#D6473B" />
                    <StatCard label="Traités" value={trackingScans.filter(s => s.status === 'treated' || s.status === 'resolved').length} color="#B4740E" />
                  </div>

                  {trackingScans.length === 0 ? (
                    <EmptyState
                      icon={ClipboardList}
                      title="Aucun scan"
                      description="Aucun scan enregistré dans cette période pour ce carnet de suivi."
                    />
                  ) : (
                    <div className="card-soft rounded-3xl p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <TrendingUp className="w-4 h-4 text-[#12523A]" />
                        <h3 className="font-heading text-[13px] font-bold text-[#10221A]">
                          Courbe de santé : {latest?.disease_name || latest?.crop_name || 'Éléments'}
                        </h3>
                      </div>

                      {trackingScansWithPhotos.length > 1 ? (
                        <HealthChart scans={trackingScans} days={parseInt(period)} />
                      ) : (
                        <div className="py-7 text-center bg-[#F0FAF4] rounded-2xl border border-dashed border-[#1B7049]/20">
                          <p className="text-xs text-[#12523A] font-bold">Un seul scan disponible pour la période.</p>
                          <p className="text-[10px] text-[#8A9A91] mt-1">Ajoutez d'autres scans à ce carnet pour afficher l'évolution.</p>
                        </div>
                      )}

                      <WaxDivider className="my-3" />

                      <p className="text-[12px] font-bold text-[#10221A] mb-2">Évolution constatée</p>
                      <span className={`chip ${evolutionLabel === 'EN AMÉLIORATION' ? 'bg-[#E3F6EA] text-[#1B7049]' : evolutionLabel === 'EN AGGRAVATION' ? 'bg-[#FEECEC] text-[#D6473B]' : 'bg-[#FFF7E6] text-[#B4740E]'}`}>
                        {evolutionLabel === 'EN AMÉLIORATION' ? <TrendingDown className="w-3.5 h-3.5" /> : evolutionLabel === 'EN AGGRAVATION' ? <TrendingUp className="w-3.5 h-3.5" /> : <Minus className="w-3.5 h-3.5" />}
                        {evolutionLabel} ({evolutionPct > 0 ? '+' : ''}{evolutionPct}%)
                      </span>

                      <div className="mt-3">
                        <div className="flex items-center justify-between text-[11px] text-[#5B6B62] mb-1">
                          <span>Niveau d'infection actuel</span><span className="font-semibold text-[#10221A]">{currentLevel}%</span>
                        </div>
                        <div className="h-2 rounded-full bg-[#DCE7E0] overflow-hidden">
                          <div className="h-full rounded-full bg-gradient-to-r from-[#1B7049] via-[#E8B84B] to-[#D6473B]" style={{ width: `${currentLevel}%` }} />
                        </div>
                      </div>

                      {first && latest && first.id !== latest.id && (
                        <div className="flex items-center gap-3 mt-4">
                          <div className="flex-1 text-center">
                            <img src={first.image_url} alt="Premier scan" className="w-full h-24 object-cover rounded-2xl shadow-sm" />
                            <span className="chip bg-[#F0FAF4] text-[#12523A] mt-2 justify-center w-full">Début : {Math.round((severityScore[first.severity] || 1) * 25)}%</span>
                          </div>
                          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#F0FAF4] text-[#12523A] shadow-sm">→</div>
                          <div className="flex-1 text-center">
                            {latest.image_url ? (
                              <img src={latest.image_url} alt="Dernier scan" className="w-full h-24 object-cover rounded-2xl shadow-sm" />
                            ) : (
                              <div className="w-full h-24 rounded-2xl bg-[#F0FAF4]" />
                            )}
                            <span className="chip bg-[#12523A] text-white mt-2 justify-center w-full">Actuel : {currentLevel}%</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  <WaxDivider />

                  {trackingScans.length > 0 && (
                    <div className="space-y-2.5">
                      <h3 className="font-heading text-[13px] font-bold text-[#5B6B62]">Scans de ce carnet</h3>
                      {trackingScans.map(scan => (
                        <ScanCard key={scan.id} scan={scan} onDelete={handleDeleteScan} />
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      ) : (
        <div className="px-4 mt-4 space-y-4">
          <div className="grid grid-cols-2 gap-2.5">
            <StatCard label="Scans Ordinaires" value={ordinaryScans.length} color="#12523A" />
            <StatCard label="Cas Critiques" value={ordinaryScans.filter(s => s.severity === 'critique').length} color="#D6473B" />
          </div>

          {ordinaryScans.length === 0 ? (
            <EmptyState icon={ClipboardList} title="Aucun scan simple" description="Vos analyses rapides sans suivi d'évolution s'afficheront ici." />
          ) : (
            <div className="space-y-2.5">
              <h3 className="font-heading text-[13px] font-bold text-[#5B6B62]">Historique des scans simples</h3>
              {ordinaryScans.map(scan => (
                <ScanCard key={scan.id} scan={scan} onDelete={handleDeleteScan} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div className="card-soft rounded-2xl p-3 text-center">
      <p className="font-heading text-xl font-extrabold" style={{ color }}>{value}</p>
      <p className="text-[10px] text-[#8A9A91] mt-0.5">{label}</p>
    </div>
  );
}

function ScanCard({ scan, onDelete }) {
  const speechText = `Culture: ${scan.crop_name}. Maladie: ${scan.disease_name}. Gravité: ${scan.severity}. Remède: ${scan.remedy}.`;
  return (
    <div className="card-soft rounded-2xl overflow-hidden shadow-sm">
      <div className="flex">
        {scan.image_url && (
          <img src={scan.image_url} alt={scan.crop_name} className="w-20 h-20 object-cover" />
        )}
        <div className="flex-1 p-3">
          <div className="flex items-center justify-between mb-1">
            <span className="font-heading text-sm font-bold text-[#10221A]">{scan.crop_name}</span>
            <div className="flex items-center gap-2">
              <SeverityBadge severity={scan.severity} />
              <button onClick={() => onDelete(scan.id)} className="p-1 hover:bg-[#FEECEC] rounded-md text-[#D6473B]" title="Supprimer ce scan">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
          <p className="text-xs text-[#5B6B62] line-clamp-1">{scan.disease_name}</p>
          <div className="flex items-center justify-between mt-2">
            <span className="text-[10px] text-[#8A9A91] flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {moment(scan.created_date).format('DD/MM/YYYY')}
            </span>
            <SpeakButton text={speechText} className="h-6 text-[10px] px-2" />
          </div>
        </div>
      </div>
    </div>
  );
}
