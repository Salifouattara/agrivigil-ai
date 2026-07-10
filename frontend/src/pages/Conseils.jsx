import { db } from '@/api/apiClient';

import React, { useState, useEffect } from 'react';

import { BookOpen, Loader2, Sprout, Shield, Leaf, AlertCircle } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import WaxDivider from '@/components/ui/WaxDivider';
import SpeakButton from '@/components/ui/SpeakButton';
import { cropIcons } from '@/lib/theme';

const cropOptions = [
  'cacao', 'café', 'manioc', 'riz', 'maïs', 'igname', 'banane_plantain', 'hévéa', 'palmier_huile', 'coton'
];

export default function Conseils() {
  const [crop, setCrop] = useState('cacao');
  const [advice, setAdvice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!crop) return;
    setLoading(true);
    setError(null);
    db.integrations.Core.GetCropAdvice(crop)
      .then(setAdvice)
      .catch(() => setError('Impossible de charger les conseils.'))
      .finally(() => setLoading(false));
  }, [crop]);

  const speechText = advice
    ? `Conseils pour ${advice.crop_label}. ${advice.season_tips?.[0] || ''} ${advice.best_practices?.[0] || ''}`
    : '';

  return (
    <div className="pb-6">
      <div className="hero-gradient px-5 pt-6 pb-7 rounded-b-[36px]">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-white/15 text-[#7CF2B8]">
            <BookOpen className="w-4 h-4" strokeWidth={2.2} />
          </span>
          <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-white/85">Savoir-faire</span>
        </div>
        <h1 className="font-heading text-[26px] font-extrabold text-white mt-3">Conseils Agricoles</h1>
        <p className="text-[13px] text-white/70 mt-1.5 leading-relaxed max-w-[90%]">
          Bonnes pratiques, pesticides homologués et calendrier cultural
        </p>
      </div>

      <div className="px-4 -mt-2 relative z-10">

      <div className="card-soft rounded-3xl p-4 mb-5">
        <Label className="text-sm font-semibold text-[#10221A] font-body flex items-center gap-2 mb-2">
          <Sprout className="w-4 h-4 text-[#12523A]" />
          Choisir une culture
        </Label>
        <Select value={crop} onValueChange={setCrop}>
          <SelectTrigger className="h-12 rounded-xl border-[#DCE7E0] text-base">
            <SelectValue />
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

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-6 h-6 text-[#12523A] animate-spin" />
        </div>
      ) : error ? (
        <p className="text-sm text-red-600 font-body text-center py-10">{error}</p>
      ) : advice && (
        <div className="space-y-4">
          <div className="bg-[#12523A] rounded-2xl p-4 text-[#F7FAF6]">
            <div className="flex items-center gap-2 mb-1">
              <BookOpen className="w-5 h-5 text-[#E8B84B]" />
              <h3 className="font-heading text-lg font-bold">{advice.crop_label}</h3>
            </div>
            {advice.ai_enriched && (
              <p className="text-[10px] text-[#E8B84B] font-body">Enrichi par IA · Conseils personnalisés</p>
            )}
          </div>

          <AdviceBlock
            icon={Leaf}
            title="Conseils saisonniers"
            items={advice.season_tips}
            color="#12523A"
          />

          <WaxDivider />

          <AdviceBlock
            icon={Shield}
            title="Bonnes pratiques"
            items={advice.best_practices}
            color="#B4740E"
          />

          <WaxDivider />

          <div className="card-soft rounded-3xl p-4">
            <h4 className="font-heading text-sm font-bold text-[#10221A] mb-3 flex items-center gap-2">
              <Shield className="w-4 h-4 text-[#B4740E]" />
              Pesticides homologués
            </h4>
            <div className="space-y-3">
              {advice.approved_pesticides?.map((p, i) => (
                <div key={i} className="bg-[#F7FAF6] rounded-xl p-3 border-l-4 border-[#B4740E]">
                  <p className="text-sm font-body font-semibold text-[#10221A]">{p.name}</p>
                  <p className="text-xs text-[#10221A] font-body mt-0.5">Cible : {p.target}</p>
                  <p className="text-xs text-[#8A9A91] font-body mt-1">{p.note}</p>
                </div>
              ))}
            </div>
          </div>

          {advice.common_issues?.length > 0 && (
            <div className="card-soft rounded-3xl p-4">
              <h4 className="font-heading text-sm font-bold text-[#10221A] mb-2 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-[#D6473B]" />
                Problèmes fréquents
              </h4>
              <div className="flex flex-wrap gap-2">
                {advice.common_issues.map((issue, i) => (
                  <span key={i} className="text-xs font-body bg-[#D6473B]/10 text-[#D6473B] px-2.5 py-1 rounded-full">
                    {issue}
                  </span>
                ))}
              </div>
            </div>
          )}

          {advice.additional_notes && (
            <div className="bg-[#F7FAF6] rounded-2xl p-4 border border-[#DCE7E0]/30">
              <p className="text-xs font-body font-semibold text-[#8A9A91] uppercase mb-1">Note complémentaire</p>
              <p className="text-sm text-[#10221A] font-body leading-relaxed">{advice.additional_notes}</p>
            </div>
          )}

          <SpeakButton text={speechText} className="w-full" />

          <p className="text-[10px] text-center text-[#8A9A91] font-body pb-2">
            Vérifiez toujours l'homologation en vigueur auprès du MINADER · Portez EPI lors des traitements
          </p>
        </div>
      )}
      </div>
    </div>
  );
}

function AdviceBlock({ icon: Icon, title, items, color }) {
  return (
    <div className="card-soft rounded-3xl p-4">
      <h4 className="font-heading text-sm font-bold text-[#10221A] mb-3 flex items-center gap-2">
        <Icon className="w-4 h-4" style={{ color }} />
        {title}
      </h4>
      <ul className="space-y-2">
        {items?.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-[#10221A] font-body leading-relaxed">
            <span className="w-1.5 h-1.5 rounded-full mt-2 shrink-0" style={{ backgroundColor: color }} />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
