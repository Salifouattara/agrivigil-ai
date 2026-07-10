import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Leaf, Calculator, ClipboardList, Users, CloudSun, BookOpen,
  Sparkles, Grid2x2, X, ChevronRight, LogOut,
} from 'lucide-react';
import {
  Sheet, SheetContent, SheetHeader, SheetTitle,
} from '@/components/ui/sheet';
import { db } from '@/api/apiClient';

// Onglets principaux visibles en permanence dans la barre de navigation.
const primaryNavItems = [
  { path: '/', label: 'Accueil', icon: Leaf },
  { path: '/communaute', label: 'Communauté', icon: Users },
  { path: '/carnet', label: 'Carnet', icon: ClipboardList },
  { path: '/meteo', label: 'Météo', icon: CloudSun },
];

// Fonctionnalités secondaires regroupées dans le tiroir "Plus", pour garder
// une barre de navigation mobile aérée (4 onglets + un bouton "Plus").
const moreNavItems = [
  { path: '/calculateur', label: 'Calculateur d\'engrais', description: 'Dosage NPK optimal pour votre parcelle', icon: Calculator, tint: '#2F6FE4' },
  { path: '/conseils', label: 'Conseils agricoles', description: 'Bonnes pratiques & calendrier cultural', icon: BookOpen, tint: '#B4740E' },
  { path: '/experts', label: 'Hub Experts', description: 'Chatbot IA & professionnels de terrain', icon: Sparkles, tint: '#12523A' },
];

export default function AppLayout() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [moreOpen, setMoreOpen] = useState(false);

  const isMoreActive = moreNavItems.some(i => pathname.startsWith(i.path));

  return (
    <div className="h-screen flex items-center justify-center bg-[#EAF4EC] px-3 py-4 overflow-hidden sm:px-4">
      <div className="relative w-full max-w-[23rem] h-[calc(100vh-2rem)] overflow-hidden">
        <div className="pointer-events-none absolute -inset-2 rounded-[36px] bg-[radial-gradient(circle_at_top_left,_rgba(18,82,58,0.16),_transparent_45%)]" />
        <div className="relative surface-card h-full flex flex-col overflow-hidden rounded-[32px]">

          <main className="flex-1 min-h-0 overflow-y-auto no-scrollbar">
            <Outlet />
          </main>

          <nav className="glass-panel sticky bottom-0 border-t border-[#10221A]/[0.06] px-3 pt-2 pb-3">
            <div className="grid grid-cols-5 gap-1">
              {primaryNavItems.map(({ path, label, icon: Icon }) => {
                const isActive = path === '/' ? pathname === '/' : pathname.startsWith(path);
                return (
                  <Link
                    key={path}
                    to={path}
                    className="group flex flex-col items-center justify-center gap-1 rounded-2xl px-1 py-1.5 text-[10px] transition-all"
                  >
                    <span className={`flex items-center justify-center w-9 h-9 rounded-2xl transition-all ${isActive ? 'bg-[#12523A] text-white shadow-[0_6px_16px_-4px_rgba(18,82,58,0.55)]' : 'text-[#5B6B62] group-hover:bg-[#12523A]/8'}`}>
                      <Icon className="w-[18px] h-[18px]" strokeWidth={isActive ? 2.4 : 1.6} />
                    </span>
                    <span className={isActive ? 'font-semibold text-[#12523A]' : 'font-medium text-[#5B6B62]'}>{label}</span>
                  </Link>
                );
              })}
              <button
                onClick={() => setMoreOpen(true)}
                className="group flex flex-col items-center justify-center gap-1 rounded-2xl px-1 py-1.5 text-[10px] transition-all"
              >
                <span className={`flex items-center justify-center w-9 h-9 rounded-2xl transition-all ${isMoreActive ? 'bg-[#12523A] text-white shadow-[0_6px_16px_-4px_rgba(18,82,58,0.55)]' : 'text-[#5B6B62] group-hover:bg-[#12523A]/8'}`}>
                  <Grid2x2 className="w-[18px] h-[18px]" strokeWidth={isMoreActive ? 2.4 : 1.6} />
                </span>
                <span className={isMoreActive ? 'font-semibold text-[#12523A]' : 'font-medium text-[#5B6B62]'}>Plus</span>
              </button>
            </div>
          </nav>
        </div>
      </div>

      <Sheet open={moreOpen} onOpenChange={setMoreOpen}>
        <SheetContent side="bottom" className="mx-auto max-w-[23rem] rounded-t-[28px] border-0 p-0 overflow-hidden">
          <div className="hero-gradient px-5 pt-5 pb-6">
            <SheetHeader>
              <SheetTitle className="text-white font-heading text-lg">Plus d'outils</SheetTitle>
            </SheetHeader>
            <p className="text-[13px] text-white/70 mt-1">Toutes les fonctionnalités AgrivigilAI en un tap.</p>
          </div>
          <div className="px-4 py-4 space-y-2 bg-white">
            {moreNavItems.map(({ path, label, description, icon: Icon, tint }) => (
              <button
                key={path}
                onClick={() => { setMoreOpen(false); navigate(path); }}
                className="w-full flex items-center gap-3 rounded-2xl border border-[#10221A]/[0.06] bg-white hover:bg-[#F0FAF4] px-3 py-3 text-left transition-colors"
              >
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl" style={{ backgroundColor: `${tint}14`, color: tint }}>
                  <Icon className="w-5 h-5" strokeWidth={1.8} />
                </span>
                <span className="flex-1 min-w-0">
                  <span className="block font-heading text-sm font-bold text-[#10221A]">{label}</span>
                  <span className="block text-xs text-[#5B6B62] mt-0.5 truncate">{description}</span>
                </span>
                <ChevronRight className="w-4 h-4 text-[#5B6B62] shrink-0" />
              </button>
            ))}
            <button
              onClick={() => db.auth.logout('/login')}
              className="w-full flex items-center gap-3 rounded-2xl px-3 py-3 text-left text-[#D6473B] hover:bg-[#FEECEC] transition-colors mt-1"
            >
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[#FEECEC]">
                <LogOut className="w-5 h-5" strokeWidth={1.8} />
              </span>
              <span className="font-heading text-sm font-bold">Se déconnecter</span>
            </button>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
