import { db } from '@/api/apiClient';

import React, { useState, useRef } from 'react';

import {
  Calculator, Sprout, Mountain, Ruler, ArrowRight, Camera, Loader2,
  Coins, Calendar, Package, CheckCircle2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import WaxDivider from '@/components/ui/WaxDivider';
import SpeakButton from '@/components/ui/SpeakButton';
import { cropIcons, soilLabels } from '@/lib/theme';
import { useToast } from '@/components/ui/use-toast';

const cropOptions = [
  'cacao', 'café', 'manioc', 'riz', 'maïs', 'igname', 'banane_plantain', 'hévéa', 'palmier_huile', 'coton'
];

function formatFcfa(amount) {
  return new Intl.NumberFormat('fr-FR').format(amount) + ' FCFA';
}

export default function Calculateur() {
  const [tab, setTab] = useState('manual');
  const [crop, setCrop] = useState('');
  const [soil, setSoil] = useState('');
  const [surface, setSurface] = useState('');
  const [result, setResult] = useState(null);
  const [calculating, setCalculating] = useState(false);

  const [soilImage, setSoilImage] = useState(null);
  const [soilImageFile, setSoilImageFile] = useState(null);
  const [soilScanResult, setSoilScanResult] = useState(null);
  const [soilScanning, setSoilScanning] = useState(false);
  const fileRef = useRef(null);

  const { toast } = useToast();

  const handleCalc = async () => {
    const hectares = parseFloat(surface);
    if (!crop || !soil || !hectares || hectares <= 0) {
      toast({ title: 'Champs requis', description: 'Remplissez tous les champs avant de calculer', variant: 'destructive' });
      return;
    }
    setCalculating(true);
    try {
      const data = await db.entities.FertilizerCalculation.create({
        crop_type: crop,
        soil_type: soil,
        surface_hectares: hectares,
      });
      setResult(data);
    } catch (err) {
      toast({ title: 'Erreur', description: err.message || 'Calcul impossible', variant: 'destructive' });
    } finally {
      setCalculating(false);
    }
  };

  const handleSoilFile = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSoilImage(URL.createObjectURL(file));
    setSoilImageFile(file);
    setSoilScanResult(null);
  };

  const handleSoilScan = async () => {
    if (!soilImageFile) return;
    setSoilScanning(true);
    try {
      const analysis = await db.integrations.Core.AnalyzeSoilImage(soilImageFile);
      setSoilScanResult(analysis);
      toast({
        title: 'Sol détecté',
        description: `${soilLabels[analysis.soil_type] || analysis.soil_type} (${analysis.confidence}% confiance)`,
      });
    } catch (err) {
      toast({ title: 'Erreur', description: err.message || "L'analyse a échoué", variant: 'destructive' });
    } finally {
      setSoilScanning(false);
    }
  };

  const applySoilToCalculator = () => {
    if (!soilScanResult?.soil_type) return;
    setSoil(soilScanResult.soil_type);
    setTab('manual');
    toast({ title: 'Sol appliqué', description: 'Le type de sol a été pré-rempli dans le calculateur.' });
  };

  const speechText = result
    ? `Pour votre parcelle de ${surface} hectares de ${crop} sur sol ${soil}, vous avez besoin de ${result.nitrogen_kg} kilogrammes d'azote, ${result.phosphorus_kg} kilogrammes de phosphore, et ${result.potassium_kg} kilogrammes de potassium. Coût estimé : ${result.total_cost_fcfa} francs CFA.`
    : '';

  return (
    <div className="pb-6">
      <div className="hero-gradient px-5 pt-6 pb-7 rounded-b-[36px]">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-white/15 text-[#7CF2B8]">
            <Calculator className="w-4 h-4" strokeWidth={2.2} />
          </span>
          <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-white/85">Sol & nutrition</span>
        </div>
        <h1 className="font-heading text-[26px] font-extrabold text-white mt-3">Calculateur d'Engrais</h1>
        <p className="text-[13px] text-white/70 mt-1.5">Dosage NPK optimal pour votre parcelle</p>
      </div>

      <div className="px-4 -mt-2 relative z-10">

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setTab('manual')}
          className={`flex-1 py-2.5 px-3 rounded-2xl text-sm font-body font-semibold transition-colors ${
            tab === 'manual' ? 'bg-[#B4740E] text-[#F7FAF6]' : 'bg-white border border-[#DCE7E0]/50 text-[#10221A]'
          }`}
        >
          <Calculator className="w-4 h-4 inline mr-1.5 -mt-0.5" />
          Calcul manuel
        </button>
        <button
          onClick={() => setTab('scan')}
          className={`flex-1 py-2.5 px-3 rounded-2xl text-sm font-body font-semibold transition-colors ${
            tab === 'scan' ? 'bg-[#12523A] text-[#F7FAF6]' : 'bg-white border border-[#DCE7E0]/50 text-[#10221A]'
          }`}
        >
          <Camera className="w-4 h-4 inline mr-1.5 -mt-0.5" />
          Scanner le sol
        </button>
      </div>

      {tab === 'scan' ? (
        <div className="space-y-4">
          <div
            onClick={() => fileRef.current?.click()}
            className="relative bg-white border-2 border-dashed border-[#DCE7E0] rounded-3xl overflow-hidden cursor-pointer hover:border-[#12523A] transition-colors"
          >
            {soilImage ? (
              <img src={soilImage} alt="Sol" className="w-full h-56 object-cover" />
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-[#8A9A91]">
                <Mountain className="w-10 h-10 mb-3 text-[#B4740E]" strokeWidth={1.5} />
                <p className="font-body text-sm font-medium">Photographier un échantillon de sol</p>
                <p className="text-xs mt-1">Surface, tranchée ou poignée de terre</p>
              </div>
            )}
            <input ref={fileRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={handleSoilFile} />
          </div>

          {soilImage && (
            <Button
              onClick={handleSoilScan}
              disabled={soilScanning}
              className="w-full h-14 text-base font-body font-semibold bg-[#12523A] hover:bg-[#0B3D2A] text-[#F7FAF6] rounded-2xl"
            >
              {soilScanning ? <Loader2 className="w-5 h-5 mr-2 animate-spin" /> : <Camera className="w-5 h-5 mr-2" />}
              Analyser le sol
            </Button>
          )}

          {soilScanResult && (
            <div className="card-soft rounded-3xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-heading text-lg font-bold text-[#10221A]">Résultat de l'analyse</h3>
                <span className="text-xs font-body text-[#12523A] bg-[#12523A]/10 px-2 py-1 rounded-full">
                  {soilScanResult.confidence}% confiance
                </span>
              </div>

              <div className="bg-[#F7FAF6] rounded-xl p-4">
                <p className="text-xs text-[#8A9A91] font-body">Type de sol détecté</p>
                <p className="font-heading text-xl font-bold text-[#B4740E] mt-0.5">
                  {soilLabels[soilScanResult.soil_type] || soilScanResult.soil_type}
                </p>
                <p className="text-sm text-[#10221A] font-body mt-2">{soilScanResult.texture_description}</p>
              </div>

              <Section label="Fertilité" value={soilScanResult.fertility_level} />
              <Section label="pH estimé" value={soilScanResult.ph_estimate} />
              <Section label="Matière organique" value={soilScanResult.organic_matter} />
              <Section label="Amendements recommandés" value={soilScanResult.amendment_advice} />
              {soilScanResult.observations && (
                <Section label="Observations" value={soilScanResult.observations} />
              )}

              <Button
                onClick={applySoilToCalculator}
                className="w-full h-12 bg-[#B4740E] hover:bg-[#8F5C0B] text-[#F7FAF6] rounded-2xl font-body font-semibold"
              >
                <CheckCircle2 className="w-4 h-4 mr-2" />
                Appliquer au calculateur
              </Button>
            </div>
          )}
        </div>
      ) : (
        <>
          <div className="card-soft rounded-3xl p-5 space-y-5">
            <div className="space-y-2">
              <Label className="text-sm font-semibold text-[#10221A] font-body flex items-center gap-2">
                <Sprout className="w-4 h-4 text-[#12523A]" strokeWidth={1.5} />
                Culture
              </Label>
              <Select value={crop} onValueChange={setCrop}>
                <SelectTrigger className="h-12 rounded-xl border-[#DCE7E0] text-base">
                  <SelectValue placeholder="Sélectionnez une culture" />
                </SelectTrigger>
                <SelectContent>
                  {cropOptions.map(c => (
                    <SelectItem key={c} value={c} className="text-base">
                      {cropIcons[c]} {c.replace('_', ' ').replace(/^./, s => s.toUpperCase())}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-semibold text-[#10221A] font-body flex items-center gap-2">
                <Mountain className="w-4 h-4 text-[#B4740E]" strokeWidth={1.5} />
                Type de sol
                {soil && soilScanResult?.soil_type === soil && (
                  <span className="text-[10px] text-[#12523A] bg-[#12523A]/10 px-1.5 py-0.5 rounded">Détecté par scan</span>
                )}
              </Label>
              <Select value={soil} onValueChange={setSoil}>
                <SelectTrigger className="h-12 rounded-xl border-[#DCE7E0] text-base">
                  <SelectValue placeholder="Sélectionnez le type de sol" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(soilLabels).map(([k, v]) => (
                    <SelectItem key={k} value={k} className="text-base">{v}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-semibold text-[#10221A] font-body flex items-center gap-2">
                <Ruler className="w-4 h-4 text-[#E8B84B]" strokeWidth={1.5} />
                Superficie (hectares)
              </Label>
              <Input
                type="number"
                inputMode="decimal"
                min="0.1"
                step="0.1"
                value={surface}
                onChange={e => setSurface(e.target.value)}
                placeholder="Ex: 2.5"
                className="h-12 rounded-xl border-[#DCE7E0] text-base"
              />
            </div>

            <Button
              onClick={handleCalc}
              disabled={calculating}
              className="w-full h-14 text-base font-body font-semibold bg-[#B4740E] hover:bg-[#8F5C0B] text-[#F7FAF6] rounded-2xl"
            >
              {calculating ? <Loader2 className="w-5 h-5 mr-2 animate-spin" /> : <Calculator className="w-5 h-5 mr-2" />}
              Calculer le dosage
            </Button>
          </div>

          {result && (
            <div className="mt-6">
              <WaxDivider />
              <div className="card-soft rounded-3xl p-5 space-y-5">
                <h3 className="font-heading text-lg font-bold text-[#10221A]">Ordonnance NPK détaillée</h3>

                <div className="grid grid-cols-3 gap-3">
                  <NutrientCard label="Azote (N)" value={result.nitrogen_kg} color="#12523A" icon="🌿" />
                  <NutrientCard label="Phosphore (P)" value={result.phosphorus_kg} color="#B4740E" icon="🪨" />
                  <NutrientCard label="Potassium (K)" value={result.potassium_kg} color="#E8B84B" icon="💧" />
                </div>

                {result.total_cost_fcfa > 0 && (
                  <div className="bg-[#12523A]/5 border border-[#12523A]/20 rounded-2xl p-4 flex items-center gap-3">
                    <Coins className="w-8 h-8 text-[#12523A] shrink-0" />
                    <div>
                      <p className="text-xs text-[#8A9A91] font-body">Coût estimé des engrais</p>
                      <p className="font-heading text-xl font-bold text-[#12523A]">{formatFcfa(result.total_cost_fcfa)}</p>
                      <p className="text-[10px] text-[#8A9A91] font-body mt-0.5">Prix indicatifs marché ivoirien</p>
                    </div>
                  </div>
                )}

                {result.products?.length > 0 && (
                  <div>
                    <h4 className="font-heading text-sm font-bold text-[#10221A] mb-2 flex items-center gap-2">
                      <Package className="w-4 h-4 text-[#B4740E]" /> Produits recommandés
                    </h4>
                    <div className="space-y-2">
                      {result.products.map((p, i) => (
                        <div key={i} className="flex justify-between items-center bg-[#F7FAF6] rounded-xl px-3 py-2.5">
                          <div>
                            <p className="text-sm font-body font-medium text-[#10221A]">{p.name}</p>
                            <p className="text-xs text-[#8A9A91] font-body">{p.quantity_kg} kg × {formatFcfa(p.unit_price_fcfa)}/kg</p>
                          </div>
                          <p className="font-heading text-sm font-bold text-[#B4740E]">{formatFcfa(p.subtotal_fcfa)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {result.application_plan?.length > 0 && (
                  <div>
                    <h4 className="font-heading text-sm font-bold text-[#10221A] mb-2 flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-[#12523A]" /> Plan de fractionnement
                    </h4>
                    <div className="space-y-2">
                      {result.application_plan.map((phase, i) => (
                        <div key={i} className="bg-[#F7FAF6] rounded-xl px-3 py-2.5 border-l-4 border-[#12523A]">
                          <div className="flex justify-between items-start">
                            <p className="text-sm font-body font-semibold text-[#10221A]">{phase.phase}</p>
                            <span className="text-xs text-[#B4740E] font-body font-medium">{phase.share_pct}%</span>
                          </div>
                          <p className="text-xs text-[#8A9A91] font-body mt-0.5">{phase.timing}</p>
                          <p className="text-xs text-[#10221A] font-body mt-1">
                            N: {phase.nitrogen_kg} kg · P: {phase.phosphorus_kg} kg · K: {phase.potassium_kg} kg
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-[#F7FAF6] rounded-xl p-3 flex items-start gap-2">
                  <ArrowRight className="w-4 h-4 text-[#12523A] mt-0.5 shrink-0" />
                  <p className="text-xs text-[#10221A] font-body leading-relaxed">
                    {result.soil_note || `Recommandation pour ${surface} ha de ${crop.replace('_', ' ')} sur sol ${soil}.`}
                  </p>
                </div>

                <SpeakButton text={speechText} className="w-full" />
              </div>
            </div>
          )}
        </>
      )}
      </div>
    </div>
  );
}

function Section({ label, value }) {
  return (
    <div>
      <p className="text-xs font-body font-semibold text-[#8A9A91] uppercase tracking-wide">{label}</p>
      <p className="text-sm text-[#10221A] font-body mt-0.5 leading-relaxed capitalize">{value}</p>
    </div>
  );
}

function NutrientCard({ label, value, color, icon }) {
  return (
    <div className="bg-[#F7FAF6] rounded-2xl p-3 text-center border border-[#DCE7E0]/30">
      <span className="text-2xl">{icon}</span>
      <p className="font-heading text-xl font-bold mt-1" style={{ color }}>{value}</p>
      <p className="text-[10px] text-[#8A9A91] font-body mt-0.5">kg</p>
      <p className="text-[10px] text-[#10221A] font-body font-medium mt-1">{label}</p>
    </div>
  );
}
