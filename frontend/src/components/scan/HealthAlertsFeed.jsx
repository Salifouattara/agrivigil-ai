import { db } from '@/api/apiClient';

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/components/ui/use-toast';

import { ShieldAlert, MapPin, Loader2, Trash2, ArrowUpRight } from 'lucide-react';
import SeverityBadge from '@/components/ui/SeverityBadge';
import moment from 'moment';

export default function HealthAlertsFeed({ compact = true }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    db.entities.HealthAlert.list('-created_date', 10).then(data => {
      setAlerts(data);
      setLoading(false);
    });
    const unsub = db.entities.HealthAlert.subscribe((event) => {
      if (event.type === 'create') {
        setAlerts(prev => {
          if (prev.some(a => a.id === event.data.id)) return prev;
          return [event.data, ...prev].slice(0, 10);
        });
      }
    });
    return () => unsub();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center gap-2 py-2">
        <Loader2 className="w-4 h-4 animate-spin text-[#8A9A91]" />
        <span className="text-xs text-[#8A9A91]">Chargement des alertes…</span>
      </div>
    );
  }

  if (alerts.length === 0) return null;

  const shown = compact ? alerts.slice(0, 3) : alerts;

  return (
    <div className="fade-up">
      <div className="flex items-center justify-between mb-2.5">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-xl bg-[#FEECEC] flex items-center justify-center">
            <ShieldAlert className="w-4 h-4 text-[#D6473B]" strokeWidth={1.5} />
          </div>
          <div>
            <h3 className="font-heading text-[13px] font-bold text-[#10221A]">Alertes sanitaires à proximité</h3>
            <p className="text-[10px] text-[#8A9A91]">Rayon de 10 km</p>
          </div>
        </div>
        {compact && (
          <button onClick={() => navigate('/communaute')} className="text-[11px] font-semibold text-[#12523A] flex items-center gap-0.5">
            Tout voir <ArrowUpRight className="w-3 h-3" />
          </button>
        )}
      </div>
      <div className="space-y-2">
        {shown.map(alert => {
          const isOwn = alert.distance_km === 0;
          return (
            <div key={alert.id} className="card-soft rounded-2xl border-l-4 border-l-[#D6473B]/70 p-2.5 flex items-center gap-2.5">
              {alert.image_url ? (
                <img src={alert.image_url} alt="" className="w-10 h-10 rounded-xl object-cover shrink-0" />
              ) : (
                <div className="w-10 h-10 rounded-xl bg-[#FEECEC] flex items-center justify-center shrink-0">
                  <ShieldAlert className="w-5 h-5 text-[#D6473B]" strokeWidth={1.5} />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-xs font-semibold text-[#10221A] truncate">{alert.disease_name}</p>
                  <SeverityBadge severity={alert.severity} />
                </div>
                <p className="text-[11px] text-[#5B6B62] truncate">{alert.crop_name}</p>
                <div className="flex items-center justify-between mt-0.5">
                  <span className="text-[10px] text-[#8A9A91] flex items-center gap-1">
                    <MapPin className="w-2.5 h-2.5" />
                    {isOwn ? 'Votre signalement' : `${alert.distance_km} km · ${alert.location_label || 'À proximité'}`}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-[#C4D2CB]">{moment(alert.created_date).fromNow()}</span>
                    <button
                      onClick={() => navigate('/communaute', { state: { alertId: alert.id } })}
                      className="text-[11px] font-medium text-[#12523A] hover:underline"
                    >
                      Voir plus
                    </button>
                    {isOwn && (
                      <button
                        onClick={async () => {
                          try {
                            await db.entities.HealthAlert.delete(alert.id);
                            setAlerts(prev => prev.filter(a => a.id !== alert.id));
                            toast({ title: 'Alerte supprimée' });
                          } catch (e) {
                            toast({ title: 'Erreur suppression', description: e.message || 'Impossible de supprimer', variant: 'destructive' });
                          }
                        }}
                        className="p-0.5 rounded hover:bg-[#FEECEC]"
                        aria-label="Supprimer"
                      >
                        <Trash2 className="w-3.5 h-3.5 text-[#D6473B]" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
