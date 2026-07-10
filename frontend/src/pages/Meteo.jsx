import { db } from '@/api/apiClient';

import React, { useState, useEffect } from 'react';

import { CloudSun, Droplets, Wind, Thermometer, Sun, CloudRain, Loader2, MapPin, Calendar, Leaf, AlertTriangle } from 'lucide-react';
import WaxDivider from '@/components/ui/WaxDivider';
import SpeakButton from '@/components/ui/SpeakButton';

const IVORIAN_CITIES = [
  { name: 'Abidjan', lat: 5.36, lon: -4.01 },
  { name: 'Yamoussoukro', lat: 6.83, lon: -5.28 },
  { name: 'Bouaké', lat: 7.69, lon: -5.03 },
  { name: 'Daloa', lat: 6.88, lon: -6.45 },
  { name: 'San-Pédro', lat: 4.75, lon: -6.64 },
  { name: 'Man', lat: 7.41, lon: -7.55 },
  { name: 'Korhogo', lat: 9.46, lon: -5.63 },
  { name: 'Gagnoa', lat: 6.13, lon: -5.95 },
];

const seasonInfo = {
  'grande_saison_pluies': { label: 'Grande saison des pluies', icon: CloudRain, color: '#12523A', period: 'Avril - Juillet', advice: 'Période idéale pour planter le riz, le maïs et le manioc. Surveillez les maladies fongiques.' },
  'petite_saison_seche': { label: 'Petite saison sèche', icon: Sun, color: '#E8B84B', period: 'Août - Septembre', advice: 'Entretenez vos cultures. Bon moment pour la récolte du maïs précoce.' },
  'petite_saison_pluies': { label: 'Petite saison des pluies', icon: CloudRain, color: '#B4740E', period: 'Octobre - Novembre', advice: 'Deuxième cycle de culture possible. Préparez la récolte du cacao.' },
  'grande_saison_seche': { label: 'Grande saison sèche', icon: Sun, color: '#D6473B', period: 'Décembre - Mars', advice: 'Période de récolte principale. Préparez les sols pour la prochaine saison.' },
};

const alertStyles = {
  faible: { border: 'border-l-[#12523A]', bg: 'bg-[#12523A]/8', text: 'text-[#12523A]' },
  modérée: { border: 'border-l-[#E8B84B]', bg: 'bg-[#E8B84B]/10', text: 'text-[#B4740E]' },
  élevée: { border: 'border-l-[#B4740E]', bg: 'bg-[#B4740E]/10', text: 'text-[#B4740E]' },
  critique: { border: 'border-l-[#D6473B]', bg: 'bg-[#D6473B]/10', text: 'text-[#D6473B]' },
};

function getWeatherAlerts(weather) {
  if (!weather) return [];
  const alerts = [];
  const t = weather.temperature;
  const h = weather.humidity;
  const r = weather.rain_probability;

  if (t >= 35) {
    alerts.push({ level: 'critique', icon: Sun, title: 'Alerte canicule', message: 'Évitez les travaux aux champs entre 11h et 16h. Arrosez très tôt le matin ou après 18h. Ombragez les jeunes plants.' });
  } else if (t >= 30) {
    alerts.push({ level: 'élevée', icon: Thermometer, title: 'Forte chaleur', message: 'Arrosez abondamment tôt le matin. Surveillez le stress hydrique, surtout le maïs et le manioc.' });
  } else if (t <= 18) {
    alerts.push({ level: 'modérée', icon: CloudSun, title: 'Température fraîche', message: 'Ralentissez l\'irrigation. Surveillez les cultures sensibles au froid (cacao, hévéa).' });
  }

  if (r >= 70) {
    alerts.push({ level: 'élevée', icon: CloudRain, title: 'Risque de pluie élevé', message: 'Ne pulvérisez ni engrais ni pesticides aujourd\'hui. Reportez les traitements phytosanitaires à plus tard.' });
  } else if (r >= 40) {
    alerts.push({ level: 'modérée', icon: CloudRain, title: 'Pluie possible', message: 'Récoltez les cultures mûres si possible. Préparez le drainage pour éviter l\'engorgement des sols.' });
  }

  if (h < 40 && t > 28) {
    alerts.push({ level: 'élevée', icon: Droplets, title: 'Risque de sécheresse', message: 'Humidité faible et chaleur : irriguez vos cultures sans tarder. Paillez le sol pour conserver l\'eau.' });
  } else if (h >= 85) {
    alerts.push({ level: 'modérée', icon: Droplets, title: 'Humidité élevée', message: 'Risque de maladies fongiques. Surveillez la pourriture brune du cacao et le mildiou.' });
  }

  if (alerts.length === 0) {
    alerts.push({ level: 'faible', icon: Leaf, title: 'Conditions favorables', message: 'Météo idéale pour les travaux champêtres. Profitez-en pour l\'entretien et la fertilisation.' });
  }
  return alerts;
}

function getCurrentSeason() {
  const month = new Date().getMonth() + 1;
  if (month >= 4 && month <= 7) return 'grande_saison_pluies';
  if (month >= 8 && month <= 9) return 'petite_saison_seche';
  if (month >= 10 && month <= 11) return 'petite_saison_pluies';
  return 'grande_saison_seche';
}

export default function Meteo() {
  const [city, setCity] = useState(IVORIAN_CITIES[0]);
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWeather(city);
  }, [city]);

  const fetchWeather = async (selectedCity) => {
    setLoading(true);
    try {
      const result = await db.integrations.Core.GetWeather(selectedCity.name);
      setWeather(result);
    } catch (err) {
      setWeather(null);
    } finally {
      setLoading(false);
    }
  };

  const season = seasonInfo[getCurrentSeason()];
  const SeasonIcon = season.icon;

  const weatherIcon = (condition) => {
    const c = (condition || '').toLowerCase();
    if (c.includes('pluv') || c.includes('pluie') || c.includes('orag')) return CloudRain;
    if (c.includes('nuag')) return CloudSun;
    return Sun;
  };

  const speechText = weather
    ? `Météo à ${city.name}: ${weather.temperature} degrés, ${weather.condition}. Humidité ${weather.humidity} pourcent. ${weather.advice_agricole}`
    : '';

  return (
    <div className="pb-6">
      <div className="hero-gradient px-5 pt-6 pb-7 rounded-b-[36px]">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-white/15 text-[#7CF2B8]">
            <CloudSun className="w-4 h-4" strokeWidth={2.2} />
          </span>
          <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-white/85">Climat</span>
        </div>
        <h1 className="font-heading text-[26px] font-extrabold text-white mt-3">Sentinelle Climatique</h1>
        <p className="text-[13px] text-white/70 mt-1.5">Météo et calendrier agricole</p>
      </div>

      <div className="px-4 -mt-2 relative z-10">
      {/* City selector */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-4 mt-3 -mx-1 px-1 no-scrollbar">
        {IVORIAN_CITIES.map(c => (
          <button
            key={c.name}
            onClick={() => setCity(c)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-body font-medium whitespace-nowrap transition-colors ${
              city.name === c.name
                ? 'bg-[#12523A] text-[#F7FAF6]'
                : 'bg-white border border-[#DCE7E0]/50 text-[#10221A]'
            }`}
          >
            <MapPin className="w-3 h-3" />
            {c.name}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-6 h-6 text-[#12523A] animate-spin" />
        </div>
      ) : weather && (
        <>
          {/* Current weather */}
          <div className="card-soft rounded-3xl p-5 mb-4">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-xs text-[#8A9A91] font-body mb-1 flex items-center gap-1">
                  <MapPin className="w-3 h-3" /> {city.name}
                </p>
                <p className="font-heading text-4xl font-bold text-[#10221A]">{weather.temperature}°C</p>
                <p className="text-sm text-[#10221A] font-body capitalize mt-1">{weather.condition}</p>
              </div>
              {React.createElement(weatherIcon(weather.condition), { className: "w-14 h-14 text-[#E8B84B]", strokeWidth: 1.5 })}
            </div>

            <div className="grid grid-cols-3 gap-3">
              <MiniStat icon={Droplets} label="Humidité" value={`${weather.humidity}%`} />
              <MiniStat icon={Wind} label="Vent" value={`${weather.wind_speed} km/h`} />
              <MiniStat icon={CloudRain} label="Pluie" value={`${weather.rain_probability}%`} />
            </div>
          </div>

          {/* Alerts based on weather */}
          {getWeatherAlerts(weather).length > 0 && (
            <div className="mb-4">
              <h3 className="font-heading text-sm font-bold text-[#10221A] mb-2 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-[#B4740E]" />
                Alertes & recommandations
              </h3>
              <div className="space-y-2">
                {getWeatherAlerts(weather).map((alert, i) => {
                  const s = alertStyles[alert.level];
                  const Icon = alert.icon;
                  return (
                    <div key={i} className={`bg-white rounded-2xl border border-[#DCE7E0]/50 border-l-4 ${s.border} shadow-sm p-3 flex items-start gap-3`}>
                      <div className={`w-9 h-9 rounded-xl ${s.bg} flex items-center justify-center shrink-0`}>
                        <Icon className={`w-5 h-5 ${s.text}`} strokeWidth={1.5} />
                      </div>
                      <div>
                        <p className={`text-sm font-semibold font-body ${s.text}`}>{alert.title}</p>
                        <p className="text-xs text-[#10221A] font-body leading-relaxed mt-0.5">{alert.message}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Agricultural advice */}
          <div className="bg-[#12523A]/5 rounded-2xl border border-[#12523A]/20 p-4 mb-4">
            <p className="text-xs font-semibold text-[#12523A] font-body mb-1">🌾 Conseil du jour</p>
            <p className="text-sm text-[#10221A] font-body leading-relaxed">{weather.advice_agricole}</p>
            <SpeakButton text={speechText} className="mt-2" />
          </div>

          {/* 3-day forecast */}
          {weather.forecast_3days && (
            <div className="card-soft rounded-3xl p-4 mb-4">
              <h3 className="font-heading text-sm font-bold text-[#10221A] mb-3 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-[#B4740E]" />
                Prévisions 3 jours
              </h3>
              <div className="grid grid-cols-3 gap-3">
                {['day1', 'day2', 'day3'].map((key, i) => {
                  const d = weather.forecast_3days[key];
                  if (!d) return null;
                  const Icon = weatherIcon(d.condition);
                  return (
                    <div key={key} className="text-center bg-[#F7FAF6] rounded-xl p-3">
                      <p className="text-xs text-[#8A9A91] font-body mb-1">J+{i + 1}</p>
                      <Icon className="w-6 h-6 text-[#E8B84B] mx-auto mb-1" strokeWidth={1.5} />
                      <p className="text-xs font-body">
                        <span className="font-semibold text-[#10221A]">{d.temp_max}°</span>
                        <span className="text-[#8A9A91]"> / {d.temp_min}°</span>
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <WaxDivider />

          {/* Season card */}
          <div className="card-soft rounded-3xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-2xl flex items-center justify-center" style={{ backgroundColor: season.color + '20' }}>
                <SeasonIcon className="w-5 h-5" style={{ color: season.color }} strokeWidth={1.5} />
              </div>
              <div>
                <h3 className="font-heading text-sm font-bold text-[#10221A]">{season.label}</h3>
                <p className="text-xs text-[#8A9A91] font-body">{season.period}</p>
              </div>
            </div>
            <p className="text-sm text-[#10221A] font-body leading-relaxed">{season.advice}</p>
          </div>
        </>
      )}
      </div>
    </div>
  );
}

function MiniStat({ icon: Icon, label, value }) {
  return (
    <div className="bg-[#F7FAF6] rounded-xl p-2.5 text-center">
      <Icon className="w-4 h-4 text-[#B4740E] mx-auto mb-1" strokeWidth={1.5} />
      <p className="text-xs font-semibold text-[#10221A] font-body">{value}</p>
      <p className="text-[10px] text-[#8A9A91] font-body">{label}</p>
    </div>
  );
}