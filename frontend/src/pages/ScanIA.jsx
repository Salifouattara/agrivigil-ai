import { db } from '@/api/apiClient';

import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import {
  Camera, Loader2, Leaf, AlertTriangle, Bell, ShieldCheck,
  ClipboardCheck, ShieldAlert, CloudSun, TrendingDown, TrendingUp, Minus, Sprout, PawPrint,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import SeverityBadge from '@/components/ui/SeverityBadge';
import SpeakButton from '@/components/ui/SpeakButton';
import WaxDivider from '@/components/ui/WaxDivider';
import HealthAlertsFeed from '@/components/scan/HealthAlertsFeed';
import { useToast } from '@/components/ui/use-toast';

const severityScore = { faible: 1, modérée: 2, élevée: 3, critique: 4 };

export default function ScanIA() {
  const [image, setImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [subjectType, setSubjectType] = useState('plante');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [stats, setStats] = useState({ scans: 0, alerts: 0, treated: 0 });
  const [weather, setWeather] = useState(null);
  const [topAlert, setTopAlert] = useState(null);
  const fileRef = useRef(null);
  const { toast } = useToast();
  const navigate = useNavigate();

  // Nouveaux états pour le suivi
  const [trackings, setTrackings] = useState([]);
  const [scanType, setScanType] = useState('ordinary'); // 'ordinary' ou 'tracking'
  const [selectedTrackingId, setSelectedTrackingId] = useState('new'); // id ou 'new'
  const [newTrackingName, setNewTrackingName] = useState('');
  const [evolutionTrend, setEvolutionTrend] = useState(0);
  const [evolutionLabel, setEvolutionLabel] = useState('Aucun suivi');

  useEffect(() => {
    db.entities.CropScan.list().then(scans => {
      setStats(s => ({
        ...s,
        scans: scans.length,
        treated: scans.filter(sc => sc.status === 'treated' || sc.status === 'resolved').length,
      }));

      // Calculer l'évolution dynamique du dernier suivi mis à jour
      const scansWithTracking = scans.filter(s => s.tracking_id);
      if (scansWithTracking.length > 0) {
        const sorted = [...scansWithTracking].sort((a, b) => new Date(a.created_date) - new Date(b.created_date));
        const latestScan = sorted[sorted.length - 1];
        const latestTrackingId = latestScan.tracking_id;
        const trackingScans = sorted.filter(s => s.tracking_id === latestTrackingId);
        if (trackingScans.length > 1) {
          const s0 = severityScore[trackingScans[0].severity] || 1;
          const s1 = severityScore[trackingScans[trackingScans.length - 1].severity] || 1;
          const pct = Math.round(((s1 - s0) / s0) * 100);
          setEvolutionTrend(pct);
          setEvolutionLabel(pct < -5 ? 'En amélioration' : pct > 5 ? 'En aggravation' : 'Stable');
        } else {
          setEvolutionTrend(0);
          setEvolutionLabel('Stable');
        }
      } else {
        setEvolutionTrend(0);
        setEvolutionLabel('Aucun suivi');
      }
    }).catch(() => {});

    db.entities.HealthAlert.list().then(alerts => {
      setStats(s => ({ ...s, alerts: alerts.filter(a => a.status === 'active').length }));
      const nearby = alerts.find(a => a.distance_km > 0) || alerts[0];
      if (nearby) setTopAlert(nearby);
    }).catch(() => {});

    db.integrations.Core.GetWeather('Abidjan').then(setWeather).catch(() => {});

    // Charger les suivis
    db.entities.CropScanTracking.list().then(list => {
      setTrackings(list);
      if (list.length > 0) {
        setSelectedTrackingId(list[0].id);
      } else {
        setSelectedTrackingId('new');
      }
    }).catch(() => {});
  }, []);

  const handleFile = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImage(URL.createObjectURL(file));
    setImageFile(file);
    setResult(null);
  };

  const handleScan = async () => {
    if (!imageFile) return;
    if (scanType === 'tracking' && selectedTrackingId === 'new' && !newTrackingName.trim()) {
      toast({
        title: '⚠️ Nom requis',
        description: 'Veuillez saisir un nom pour le nouveau carnet de suivi.',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      const position = await new Promise((resolve) => {
        if (!navigator.geolocation) return resolve(null);
        navigator.geolocation.getCurrentPosition(
          (pos) => resolve(pos.coords),
          () => resolve(null),
          { timeout: 3000 }
        );
      });

      const diagnosis = await db.integrations.Core.AnalyzeCropImage(imageFile, {
        location_lat: position?.latitude,
        location_lng: position?.longitude,
        subject_type: subjectType,
        tracking_id: scanType === 'tracking' && selectedTrackingId !== 'new' ? selectedTrackingId : undefined,
        new_tracking_name: scanType === 'tracking' && selectedTrackingId === 'new' ? newTrackingName.trim() : undefined,
      });

      setResult(diagnosis);
      setStats(s => ({ ...s, scans: s.scans + 1 }));

      // Recharger les suivis s'il y a eu changement
      db.entities.CropScanTracking.list().then(list => {
        setTrackings(list);
        if (diagnosis.tracking_id) {
          setSelectedTrackingId(diagnosis.tracking_id);
          setScanType('tracking');
        }
      }).catch(() => {});
      setNewTrackingName('');

      toast({
        title: diagnosis.is_healthy ? '✅ Sain' : '⚠️ Maladie détectée',
        description: diagnosis.disease_name || 'Aucune maladie identifiée',
      });
    } catch (err) {
      toast({ title: 'Erreur', description: err.message || "L'analyse a échoué", variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const speechText = result ? `Culture: ${result.crop_name}. ${result.is_healthy ? 'La plante est saine.' : `Maladie détectée: ${result.disease_name}. Gravité: ${result.severity}. Remède: ${result.remedy}. Dosage: ${result.dosage}.`}` : '';

  return (
    <div className="pb-6">
      {/* ------------------------------------------------------------- */}
      {/* Hero — en-tête vert émeraude + carte de scan animée            */}
      {/* ------------------------------------------------------------- */}
      <div className="hero-gradient px-5 pt-6 pb-8 rounded-b-[36px]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-white/15 text-[#7CF2B8]">
              <Leaf className="w-4 h-4" strokeWidth={2.2} />
            </span>
            <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-white/85">AgrivigilAI</span>
          </div>
          <button onClick={() => navigate('/communaute')} className="relative flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-white">
            <Bell className="w-4 h-4" />
            {stats.alerts > 0 && <span className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-[#FF6B57] ring-2 ring-[#0B3D2A]" />}
          </button>
        </div>

        <p className="mt-4 text-[13px] font-medium text-white/70">Bonjour, bon retour sur AgrivigilAI</p>
        <h1 className="font-heading text-[28px] leading-tight font-extrabold text-white mt-0.5">Diagnostic IA</h1>
        <p className="text-[13px] text-white/70 mt-1.5 leading-relaxed max-w-[85%]">
          Scannez vos cultures et vos animaux, détectez les maladies en temps réel.
        </p>

        {/* Toggle plante / animal */}
        <div className="mt-4 inline-flex rounded-2xl bg-white/10 p-1">
          {[{ v: 'plante', label: 'Plante', icon: Sprout }, { v: 'animal', label: 'Animal', icon: PawPrint }].map(({ v, label, icon: Icon }) => (
            <button
              key={v}
              onClick={() => setSubjectType(v)}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-[12px] font-semibold transition-all ${subjectType === v ? 'bg-white text-[#12523A] shadow-sm' : 'text-white/75'}`}
            >
              <Icon className="w-3.5 h-3.5" /> {label}
            </button>
          ))}
        </div>

        {/* Carte de scan avec animation */}
        <div
          onClick={() => fileRef.current?.click()}
          className="scan-frame mt-4 aspect-[4/3] cursor-pointer"
        >
          <span className="corner tl" /><span className="corner tr" /><span className="corner bl" /><span className="corner br" />
          {image ? (
            <img src={image} alt="Culture scannée" className="w-full h-full object-cover" />
          ) : (
            <div className="flex h-full flex-col items-center justify-center gap-3">
              <div className="float-slow relative flex h-16 w-16 items-center justify-center rounded-full bg-white/10">
                <span className="pulse-ring" />
                {subjectType === 'plante'
                  ? <Sprout className="w-8 h-8 text-[#9CF7C4]" strokeWidth={1.5} />
                  : <PawPrint className="w-8 h-8 text-[#9CF7C4]" strokeWidth={1.5} />}
              </div>
              <p className="text-[13px] font-medium text-white/85">Touchez pour prendre une photo</p>
            </div>
          )}
          {(loading || !image) && (
            <div className="scan-line" style={{ animationPlayState: image && !loading ? 'paused' : 'running' }} />
          )}
          {loading && (
            <div className="absolute inset-x-0 bottom-3 flex justify-center">
              <span className="chip bg-white/15 text-white backdrop-blur-sm">
                <Loader2 className="w-3 h-3 animate-spin" /> Analyse en cours…
              </span>
            </div>
          )}
          <input ref={fileRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={handleFile} />
        </div>

        {image && !loading && (
          <div className="mt-4 space-y-3.5">
            <div className="p-4 rounded-2xl bg-white/10 text-white space-y-3.5 backdrop-blur-md">
              <p className="text-[12px] font-bold uppercase tracking-wider text-white/95">Type de diagnostic</p>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setScanType('ordinary')}
                  className={`py-2 px-3 rounded-xl text-[12px] font-semibold transition-all border ${scanType === 'ordinary' ? 'bg-white text-[#12523A] border-white shadow-sm' : 'bg-transparent text-white border-white/20 hover:bg-white/5'}`}
                >
                  Scan ordinaire
                </button>
                <button
                  type="button"
                  onClick={() => setScanType('tracking')}
                  className={`py-2 px-3 rounded-xl text-[12px] font-semibold transition-all border ${scanType === 'tracking' ? 'bg-white text-[#12523A] border-white shadow-sm' : 'bg-transparent text-white border-white/20 hover:bg-white/5'}`}
                >
                  Scan de suivi
                </button>
              </div>

              {scanType === 'tracking' && (
                <div className="space-y-3.5 animate-fadeIn">
                  <div>
                    <label className="block text-[11px] font-semibold text-white/75 mb-1">Lier à un carnet existant</label>
                    <select
                      value={selectedTrackingId}
                      onChange={(e) => setSelectedTrackingId(e.target.value)}
                      className="w-full bg-[#1b6b4b] border border-white/20 rounded-xl px-3 py-2 text-[12px] font-medium text-white focus:outline-none focus:ring-1 focus:ring-white/40"
                    >
                      {trackings.map((t) => (
                        <option key={t.id} value={t.id} className="text-black">
                          {t.name}
                        </option>
                      ))}
                      <option value="new" className="text-black">+ Nouveau carnet de suivi...</option>
                    </select>
                  </div>

                  {selectedTrackingId === 'new' && (
                    <div>
                      <label className="block text-[11px] font-semibold text-white/75 mb-1">Nom du nouveau carnet de suivi</label>
                      <input
                        type="text"
                        placeholder="Ex: Manioc parcelle Nord, Patte Poule..."
                        value={newTrackingName}
                        onChange={(e) => setNewTrackingName(e.target.value)}
                        className="w-full bg-[#1b6b4b] placeholder-white/40 border border-white/20 rounded-xl px-3 py-2 text-[12px] font-medium text-white focus:outline-none focus:ring-1 focus:ring-white/40"
                      />
                    </div>
                  )}
                </div>
              )}
            </div>

            <Button
              onClick={handleScan}
              className="w-full mt-1 h-12 text-[14px] font-bold bg-white hover:bg-white/90 text-[#12523A] rounded-2xl shadow-md"
            >
              <Leaf className="w-4 h-4 mr-2" /> Analyser maintenant
            </Button>
          </div>
        )}

        {/* Stat chips */}
        <div className="mt-5 flex items-center gap-2 flex-wrap">
          <span className="chip bg-white/12 text-white">
            <ShieldCheck className="w-3.5 h-3.5 text-[#7CF2B8]" /> {stats.scans} scans
          </span>
          <span className="chip bg-white/12 text-white">
            <ShieldAlert className="w-3.5 h-3.5 text-[#FFD98A]" /> {stats.alerts} alerte{stats.alerts > 1 ? 's' : ''}
          </span>
          <span className="chip bg-white/12 text-white">
            <ClipboardCheck className="w-3.5 h-3.5 text-[#9CF7C4]" /> {stats.treated} cas traité{stats.treated > 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* Corps — alerte de proximité + résumé météo/évolution           */}
      {/* ------------------------------------------------------------- */}
      <div className="px-4 -mt-3 space-y-3 relative z-10">
        {topAlert && (
          <button
            onClick={() => navigate('/communaute')}
            className="card-soft w-full text-left rounded-3xl border-l-4 border-l-[#D6473B] p-3.5 flex items-start gap-3 fade-up"
          >
            <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-[#FEECEC] text-[#D6473B]">
              <AlertTriangle className="w-[18px] h-[18px]" />
            </span>
            <div className="min-w-0">
              <p className="text-[12px] font-bold text-[#D6473B]">Alerte de Proximité</p>
              <p className="text-[13px] text-[#10221A] mt-0.5 leading-snug">
                <strong>{topAlert.disease_name}</strong> signalé{topAlert.distance_km ? ` à moins de ${Math.ceil(topAlert.distance_km)} km` : ' près de chez vous'}.
              </p>
            </div>
            <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-[#D6473B] severity-pulse" />
          </button>
        )}

        <div className="grid grid-cols-2 gap-3">
          <button onClick={() => navigate('/meteo')} className="card-soft text-left rounded-3xl p-3.5 bg-[#EEF5FF]/60">
            <span className="flex items-center gap-1.5 text-[11px] font-bold text-[#2F6FE4]">
              <CloudSun className="w-3.5 h-3.5" /> Météo
            </span>
            <p className="mt-2 text-[11px] text-[#5B6B62]">📍 Abidjan</p>
            {weather ? (
              <>
                <p className="text-[15px] font-extrabold text-[#10221A] mt-0.5">{weather.temperature}°C · {weather.condition}</p>
                <p className="text-[11px] text-[#5B6B62] mt-0.5">Humidité : {weather.humidity}%</p>
              </>
            ) : (
              <p className="text-[11px] text-[#5B6B62] mt-1">Chargement…</p>
            )}
          </button>

          <button onClick={() => navigate('/carnet')} className="card-soft text-left rounded-3xl p-3.5 bg-[#F0FAF4]/60">
            <span className="flex items-center gap-1.5 text-[11px] font-bold text-[#1B7049]">
              {evolutionTrend < 0 ? <TrendingDown className="w-3.5 h-3.5" /> : evolutionTrend > 0 ? <TrendingUp className="w-3.5 h-3.5" /> : <Minus className="w-3.5 h-3.5" />} Évolution
            </span>
            <p className="mt-2 text-[22px] font-extrabold text-[#1B7049] leading-none">
              {evolutionTrend > 0 ? `+${evolutionTrend}` : evolutionTrend}%
            </p>
            <p className="text-[11px] text-[#5B6B62] mt-1">{evolutionLabel}</p>
            <p className="text-[10px] text-[#8A9A91] mt-1.5">Voir les courbes</p>
          </button>
        </div>

        <HealthAlertsFeed />

        {/* Résultat du diagnostic */}
        {result && (
          <div className="fade-up">
            <WaxDivider />
            <div className="card-soft rounded-3xl overflow-hidden">
              <div className={`px-4 py-3.5 ${result.is_healthy ? 'bg-[#E3F6EA]' : 'bg-[#FEECEC]'}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {result.is_healthy ? (
                      <Leaf className="w-5 h-5 text-[#1B7049]" />
                    ) : (
                      <AlertTriangle className="w-5 h-5 text-[#D6473B]" />
                    )}
                    <span className="font-heading font-bold text-[#10221A]">{result.crop_name || 'Culture'}</span>
                  </div>
                  {!result.is_healthy && <SeverityBadge severity={result.severity} />}
                </div>
              </div>

              {result.tracking_name && (
                <div className="px-4 py-2 bg-[#F0FAF4] text-[#12523A] border-b border-[#DCE7E0]/60 text-[11px] font-bold flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#1B7049] animate-pulse" />
                  Suivi rattaché : {result.tracking_name}
                </div>
              )}

              <div className="p-4 space-y-4">
                {result.is_healthy ? (
                  <div className="text-center py-4">
                    <div className="w-12 h-12 rounded-full bg-[#E3F6EA] flex items-center justify-center mx-auto mb-2">
                      <Leaf className="w-6 h-6 text-[#1B7049]" />
                    </div>
                    <p className="font-heading text-lg font-bold text-[#1B7049]">En bonne santé !</p>
                    <p className="text-sm text-[#5B6B62] mt-1">Aucune maladie détectée</p>
                  </div>
                ) : (
                  <>
                    <Section title="🦠 Maladie" content={result.disease_name} />
                    {result.remedy && (
                      <div className="bg-[#FFF7E6] border border-[#B4740E]/15 rounded-2xl p-3">
                        <p className="text-xs font-semibold text-[#B4740E] mb-1">💊 Remède</p>
                        <p className="text-sm text-[#10221A] leading-relaxed">{result.remedy}</p>
                      </div>
                    )}
                    {result.dosage && <Section title="⚖️ Dosage" content={result.dosage} />}
                    {result.symptoms && <Section title="🔍 Symptômes" content={result.symptoms} />}
                    {result.prevention && <Section title="🛡️ Prévention" content={result.prevention} />}
                  </>
                )}

                {result.confidence > 0 && (
                  <div className="flex items-center gap-2 text-xs text-[#5B6B62]">
                    <div className="flex-1 h-1.5 bg-[#DCE7E0] rounded-full overflow-hidden">
                      <div className="h-full bg-[#12523A] rounded-full" style={{ width: `${result.confidence}%` }} />
                    </div>
                    <span>{result.confidence}% confiance</span>
                  </div>
                )}

                <SpeakButton text={speechText} className="w-full" />
                <Button onClick={() => navigate('/carnet')} className="w-full mt-1 h-11 text-sm rounded-2xl bg-[#12523A] hover:bg-[#0B3D2A]">
                  Suivre l'évolution
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Section({ title, content }) {
  if (!content) return null;
  return (
    <div>
      <p className="text-xs font-semibold text-[#5B6B62] mb-1">{title}</p>
      <p className="text-sm text-[#10221A] leading-relaxed">{content}</p>
    </div>
  );
}
