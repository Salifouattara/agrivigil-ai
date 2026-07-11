import { db } from '@/api/apiClient';

import React, { useState, useEffect } from 'react';

import { Loader2, Sparkles, PhoneCall, MessageSquare } from 'lucide-react';
import ExpertCard from '@/components/experts/ExpertCard';
import ExpertChat from '@/components/experts/ExpertChat';
import WaxDivider from '@/components/ui/WaxDivider';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog';

const chatbotAgent = {
  id: 'chatbot',
  name: 'Agrivigil IA',
  role: 'Assistant virtuel',
  specialty: 'Conseils agronomiques et vétérinaires',
  location: 'Disponible en continu',
  avatar_color: '#1B7049',
  online: true,
};

const WhatsAppIcon = (props) => (
  <svg viewBox="0 0 24 24" fill="currentColor" {...props}>
    <path d="M12 2.04C6.49 2.04 2.04 6.49 2.04 12c0 2.1.64 4.08 1.74 5.74L2 22l4.46-1.28a9.93 9.93 0 0 0 5.54 1.28c5.51 0 9.96-4.45 9.96-9.96S17.51 2.04 12 2.04z" />
    <path d="M16.24 14.38c-.22-.1-1.35-.68-1.58-.75-.23-.08-.39-.1-.57.12-.18.22-.67.7-.86.84-.19.15-.39.17-.61.06-.22-.11-.93-.35-1.83-1.38-.62-.68-1.03-1.43-1.16-1.69-.12-.26-.01-.43.1-.57.1-.13.25-.32.39-.46.14-.14.2-.24.3-.4.09-.15.06-.31 0-.44-.06-.13-.58-1.27-.8-1.74-.22-.47-.43-.4-.59-.41-.16-.01-.32-.01-.49-.01-.16 0-.41.05-.62.33-.21.28-.81.87-.81 2.29 0 1.42.71 2.77.88 3.14.17.36 2.02 3.19 4.93 4.3.69.28 1.2.45 1.62.45.36 0 .77-.12 1.11-.48.34-.37 1.06-1.22 1.06-2.41 0-1.19-.86-1.75-1.02-1.89-.16-.14-.36-.17-.57-.27z" />
    <path d="M14.29 11.66l-.86-.86c-.18-.18-.46-.18-.64 0l-.37.37c-.18.18-.22.43-.12.65.09.21.26.36.47.36h.18c.13 0 .25-.06.34-.15l.19-.19c.14-.14.14-.36 0-.5z" />
  </svg>
);

const normalizeRole = (value = '') => `${value || ''}`.normalize('NFKD').replace(/[^\w\sÀ-ÿ]/g, '').trim().toLowerCase();

export default function HubExperts() {
  const [experts, setExperts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chatbotOpen, setChatbotOpen] = useState(false);
  const [contactExpert, setContactExpert] = useState(null);

  useEffect(() => {
    db.entities.Expert.list()
      .then(setExperts)
      .catch(() => setError('Impossible de charger les experts.'))
      .finally(() => setLoading(false));
  }, []);

  if (chatbotOpen) {
    return <ExpertChat expert={chatbotAgent} onBack={() => setChatbotOpen(false)} />;
  }

  const plantDocs = experts.filter((e) => {
    const role = normalizeRole(e.role);
    return role.includes('medecin') || role.includes('plante') || role.includes('phytopathologie');
  });
  const vets = experts.filter((e) => {
    const role = normalizeRole(e.role);
    return role.includes('veterinaire') || role.includes('veterinaires');
  });

  const getContactBody = (expert) => {
    if (!expert) return '';
    const subject = expert.role === 'Vétérinaire'
      ? 'je souhaite prendre rendez-vous pour une consultation vétérinaire.'
      : 'je souhaite un conseil agronomique pour ma culture.';
    return encodeURIComponent(`Bonjour ${expert.name}, ${subject}`);
  };

  return (
    <div className="pb-6">
      <div className="hero-gradient px-5 pt-6 pb-8 rounded-b-[36px]">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-white/15 text-[#7CF2B8]">
            <Sparkles className="w-4 h-4" strokeWidth={2.2} />
          </span>
          <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-white/85">Assistance</span>
        </div>
        <h1 className="font-heading text-[26px] font-extrabold text-white mt-3">Hub Experts</h1>
        <p className="text-[13px] text-white/70 mt-1.5 leading-relaxed max-w-[90%]">
          Posez vos questions à un chatbot ou contactez un professionnel de terrain.
        </p>

        <div className="mt-4 rounded-3xl bg-white/10 p-3 flex items-center gap-3">
          <div className="rounded-2xl bg-white/15 p-2.5 text-[#9CF7C4] shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-heading text-[13px] font-bold text-white">Chatbot Agrivigil IA</p>
            <p className="text-[11px] text-white/70 mt-0.5 leading-snug">Assistance instantanée, disponible en continu.</p>
          </div>
          <button
            onClick={() => setChatbotOpen(true)}
            className="inline-flex shrink-0 items-center justify-center rounded-xl bg-white px-3.5 py-2 text-[12px] font-bold text-[#12523A]"
          >
            Discuter
          </button>
        </div>
      </div>

      <div className="px-4 -mt-2 relative z-10">
        <div className="mt-3">
          <h3 className="font-heading text-[15px] font-bold text-[#10221A]">Experts professionnels</h3>
          <p className="text-xs text-[#8A9A91] mt-0.5">Agronomes et vétérinaires disponibles pour contact direct.</p>
        </div>

        <div className="mt-3 space-y-3">
          {loading ? (
            <div className="flex items-center justify-center py-10">
              <Loader2 className="w-6 h-6 text-[#12523A] animate-spin" />
            </div>
          ) : error ? (
            <p className="text-sm text-red-600 font-body text-center py-8">{error}</p>
          ) : (
            <>
                <div className="space-y-4">
                <div>
                  <h3 className="font-heading text-sm font-bold text-[#12523A] mb-2 flex items-center gap-2">
                    <span className="w-1.5 h-4 bg-[#12523A] rounded-full" /> Médecins de plantes
                  </h3>
                  <div className="space-y-2">
                    {plantDocs.map(e => <ExpertCard key={e.id} expert={e} onContact={setContactExpert} />)}
                  </div>
                </div>

                <WaxDivider className="my-1" />

                <div>
                  <h3 className="font-heading text-sm font-bold text-[#B4740E] mb-2 flex items-center gap-2">
                    <span className="w-1.5 h-4 bg-[#B4740E] rounded-full" /> Vétérinaires
                  </h3>
                  <div className="space-y-2">
                    {vets.map(e => <ExpertCard key={e.id} expert={e} onContact={setContactExpert} />)}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      <p className="text-[10px] text-center text-[#8A9A91] font-body mt-5">
       · Ne remplace pas un diagnostic sur le terrain ·
      </p>
      {contactExpert && (
        <Dialog open={!!contactExpert} onOpenChange={(open) => { if (!open) setContactExpert(null); }}>
          <DialogContent className="max-w-[32rem] mx-auto max-h-[85vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Contactez {contactExpert.name}</DialogTitle>
              <DialogDescription>Choisissez un mode de contact direct.</DialogDescription>
            </DialogHeader>
            <div className="grid grid-cols-3 gap-3 mt-4">
              {contactExpert.phone_number && (
                <a
                  href={`tel:${contactExpert.phone_number}`}
                  title="Appel"
                  className="inline-flex min-h-[5.5rem] w-full flex-col items-center justify-center gap-3 rounded-[28px] border border-slate-200 bg-white px-3 text-center text-slate-900 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-slate-50 focus-visible:ring-2 focus-visible:ring-[#F29B2C]/20"
                >
                  <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#F29B2C] text-white shadow-md shadow-[#F29B2C]/20">
                    <PhoneCall className="h-5 w-5" />
                  </span>
                  <span className="text-xs font-semibold uppercase tracking-[0.18em]">Appel</span>
                </a>
              )}
              {contactExpert.phone_number && (
                <a
                  href={`sms:${contactExpert.phone_number}?body=${getContactBody(contactExpert)}`}
                  title="SMS"
                  className="inline-flex min-h-[5.5rem] w-full flex-col items-center justify-center gap-3 rounded-[28px] border border-slate-200 bg-white px-3 text-center text-slate-900 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-slate-50 focus-visible:ring-2 focus-visible:ring-[#2563EB]/20"
                >
                  <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#2563EB] text-white shadow-md shadow-[#2563EB]/20">
                    <MessageSquare className="h-5 w-5" />
                  </span>
                  <span className="text-xs font-semibold uppercase tracking-[0.18em]">SMS</span>
                </a>
              )}
              {(contactExpert.whatsapp_number || contactExpert.phone_number) && (
                <a
                  href={`https://wa.me/${(contactExpert.whatsapp_number || contactExpert.phone_number).replace(/\D/g, '')}?text=${getContactBody(contactExpert)}`}
                  target="_blank"
                  rel="noreferrer"
                  title="WhatsApp"
                  className="inline-flex min-h-[5.5rem] w-full flex-col items-center justify-center gap-3 rounded-[28px] border border-slate-200 bg-white px-3 text-center text-slate-900 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-slate-50 focus-visible:ring-2 focus-visible:ring-[#25D366]/20"
                >
                  <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#25D366] text-white shadow-md shadow-[#25D366]/20">
                    <WhatsAppIcon className="h-5 w-5" />
                  </span>
                  <span className="text-xs font-semibold uppercase tracking-[0.18em]">WhatsApp</span>
                </a>
              )}
            </div>
            <DialogFooter>
              <DialogClose className="inline-flex items-center justify-center rounded-full bg-[#12523A] px-4 py-3 text-sm font-semibold text-[#F7FAF6] shadow-sm shadow-slate-200/80 transition duration-200 hover:bg-[#0B3D2A]">
                Fermer
              </DialogClose>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
