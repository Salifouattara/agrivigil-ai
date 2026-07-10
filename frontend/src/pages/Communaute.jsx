import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, ShieldAlert } from 'lucide-react';
import abidjanMap from '@/assets/abidjan_map.png';

export default function Communaute() {
  return (
    <div className="pb-6 bg-white min-h-full">
      {/* Header */}
      <div className="flex items-center px-4 pt-5 pb-3 bg-white border-b border-[#10221A]/[0.04]">
        <Link
          to="/"
          className="flex h-8 w-8 items-center justify-center rounded-full bg-[#EAF4EC] text-[#12523A] hover:bg-[#D4ECD8] transition-colors"
        >
          <ChevronLeft className="w-5 h-5" />
        </Link>
        <h2 className="font-heading text-lg font-extrabold text-[#D6473B] text-center flex-1 pr-8">
          Alerte Sanitaire
        </h2>
      </div>

      <div className="px-4 mt-4 space-y-4">
        {/* Banner alerte critique */}
        <div className="rounded-3xl p-4 flex items-center gap-4 bg-[#D6473B] shadow-sm">
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-white text-[#D6473B]">
            <ShieldAlert className="w-7 h-7" />
          </span>
          <div>
            <h3 className="font-heading text-white text-lg font-extrabold leading-tight">
              Peste Porcine Africaine
            </h3>
            <p className="text-[12px] text-white/85 mt-0.5 font-medium">
              Alerte critique dans votre zone
            </p>
          </div>
        </div>

        {/* Carte stylisée avec fond image */}
        <div className="relative rounded-3xl overflow-hidden h-52 border border-[#10221A]/[0.06] shadow-sm bg-gray-100">
          <img
            src={abidjanMap}
            alt="Carte d'Abidjan"
            className="w-full h-full object-cover animate-fade-in"
          />
          {/* Cercle de rayon 10 km */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-[160px] h-[160px] rounded-full border-2 border-[#D6473B] bg-[#D6473B]/5 pointer-events-none" />
          </div>

          {/* Points de foyers */}
          <div className="absolute top-[23%] left-[19%] w-3 h-3 bg-[#D6473B] rounded-full border-2 border-white shadow-md" />
          <div className="absolute top-[48%] left-[49%] w-3 h-3 bg-[#D6473B] rounded-full border-2 border-white shadow-md" />
          <div className="absolute top-[62%] left-[49%] w-3 h-3 bg-[#D6473B] rounded-full border-2 border-white shadow-md" />
          <div className="absolute top-[45%] left-[86%] w-3 h-3 bg-[#D6473B] rounded-full border-2 border-white shadow-md" />
          <div className="absolute top-[38%] left-[42%] w-3 h-3 bg-[#D6473B] rounded-full border-2 border-white shadow-md" />

          {/* Badges */}
          <span className="absolute top-3 left-3 px-3 py-1 bg-[#D6473B] text-white text-[10px] font-extrabold uppercase rounded-full shadow-sm tracking-wider">
            5 Foyers Signalés
          </span>
          <span className="absolute bottom-3 right-3 px-3 py-1 bg-white border border-[#D6473B] text-[#D6473B] text-[10px] font-extrabold uppercase rounded-full shadow-sm tracking-wider">
            Rayon 10 KM
          </span>
        </div>

        {/* État de l'épidémie */}
        <div className="card-soft rounded-3xl p-4 bg-white border border-[#10221A]/[0.06] shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-[12px] font-extrabold text-[#12523A] uppercase tracking-wider">
              État de l'épidémie
            </h4>
            <span className="px-3 py-0.5 bg-[#E8F8EE] border border-[#1B7049]/10 text-[#1B7049] text-[11px] font-extrabold uppercase rounded-full">
              Contenue
            </span>
          </div>

          {/* Jauge */}
          <div className="relative h-2 rounded-full mt-4" style={{ background: 'linear-gradient(90deg, #D6473B 0%, #E8B84B 35%, #F2C879 70%, #1B7049 100%)' }}>
            <div
              className="absolute -top-1.5 right-0 h-5 w-5 rounded-full bg-white border-[3px] border-[#10221A] shadow-md"
            />
          </div>

          <div className="flex justify-between mt-2.5">
            <span className="text-[10px] text-[#8A9A91] font-medium">Émergence</span>
            <span className="text-[10px] text-[#8A9A91] font-medium">Propagation</span>
            <span className="text-[10px] text-[#8A9A91] font-medium">Pic</span>
            <span className="text-[10px] text-[#1B7049] font-bold">Contenue</span>
          </div>
        </div>

        {/* Recommandations */}
        <div className="pt-2">
          <h4 className="text-[12px] font-extrabold text-[#12523A] uppercase tracking-wider mb-3">
            Recommandations de protection
          </h4>
          <div className="space-y-3">
            <div className="card-soft rounded-2xl p-3.5 flex items-center gap-3 bg-white border border-[#10221A]/[0.06] shadow-sm">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#FEECEC] text-[#D6473B] text-xs font-bold">
                1
              </span>
              <p className="text-[13px] text-[#10221A] leading-normal">
                <span className="font-bold">Isoler</span> immédiatement les animaux suspects
              </p>
            </div>

            <div className="card-soft rounded-2xl p-3.5 flex items-center gap-3 bg-white border border-[#10221A]/[0.06] shadow-sm">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#FEECEC] text-[#D6473B] text-xs font-bold">
                2
              </span>
              <p className="text-[13px] text-[#10221A] leading-normal">
                <span className="font-bold">Désinfecter</span> les locaux et équipements
              </p>
            </div>

            <div className="card-soft rounded-2xl p-3.5 flex items-center gap-3 bg-white border border-[#10221A]/[0.06] shadow-sm">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#FEECEC] text-[#D6473B] text-xs font-bold">
                3
              </span>
              <p className="text-[13px] text-[#10221A] leading-normal">
                <span className="font-bold">Vacciner</span> si possible, contacter un vétérinaire
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
