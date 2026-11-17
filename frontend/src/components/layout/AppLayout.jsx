import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { Leaf, Calculator, ClipboardList, Users, CloudSun, BookOpen, Stethoscope, Grid2x2, ChevronRight, LogOut, ArrowUpRight } from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet';
import { db } from '@/api/apiClient';

const navItems = [
  { path: '/', label: 'Vue d’ensemble', mobileLabel: 'Accueil', icon: Leaf, group: 'Exploitation' },
  { path: '/carnet', label: 'Carnet de santé', mobileLabel: 'Carnet', icon: ClipboardList, group: 'Exploitation' },
  { path: '/meteo', label: 'Météo agricole', mobileLabel: 'Météo', icon: CloudSun, group: 'Exploitation' },
  { path: '/communaute', label: 'Communauté', mobileLabel: 'Alertes', icon: Users, group: 'Exploitation' },
  { path: '/calculateur', label: 'Sol & fertilisation', icon: Calculator, group: 'Accompagnement' },
  { path: '/conseils', label: 'Conseils agricoles', icon: BookOpen, group: 'Accompagnement' },
  { path: '/experts', label: 'Hub Experts', icon: Stethoscope, group: 'Accompagnement' },
];

function Brand() {
  return <Link to="/" className="av-brand" aria-label="AgriVigil AI, accueil">
    <span className="av-brand-icon"><Leaf size={23} strokeWidth={1.8} /></span>
    <span>AgriVigil<span className="av-brand-ai"> AI</span><small>Observer. Comprendre. Agir.</small></span>
  </Link>;
}

export default function AppLayout() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [moreOpen, setMoreOpen] = useState(false);
  const current = navItems.find(item => item.path === pathname) || navItems[0];
  return <div className="av-workspace">
    <a className="av-skip-link" href="#workspace-main">Aller au contenu</a>
    <aside className="av-sidebar">
      <Brand />
      <nav aria-label="Navigation principale" className="av-side-nav">
        {['Exploitation', 'Accompagnement'].map(group => <div key={group}>
          <p className="av-nav-heading">{group}</p>
          {navItems.filter(item => item.group === group).map(({path, label, icon: Icon}) => <Link key={path} to={path} aria-current={pathname === path ? 'page' : undefined} className={`av-nav-link ${pathname === path ? 'is-active' : ''}`}>
            <Icon size={19} strokeWidth={1.8} /><span>{label}</span>{pathname === path && <span className="av-active-dot" />}
          </Link>)}
        </div>)}
      </nav>
      <div className="av-sidebar-bottom">
        <div className="av-field-note"><Leaf size={20} /><p>Une meilleure observation.<br /><strong>Des décisions plus éclairées.</strong></p></div>
        <button className="av-logout" onClick={() => db.auth.logout('/login')}><LogOut size={18} /> Se déconnecter</button>
      </div>
    </aside>
    <div className="av-work-area">
      <header className="av-topbar">
        <div className="av-mobile-brand"><Brand /></div>
        <div className="av-breadcrumb"><span>Mon espace agricole</span><ChevronRight size={14} /><strong>{current.label}</strong></div>
        <Link className="av-top-action" to="/">Nouveau diagnostic <ArrowUpRight size={16} /></Link>
      </header>
      <main id="workspace-main" tabIndex={-1} className={`workspace-content route-${pathname === '/' ? 'home' : pathname.slice(1)}`}><Outlet /></main>
      <footer className="av-footer"><span>AgriVigil AI</span><span>Au service de l’agriculture ivoirienne</span></footer>
    </div>
    <nav className="av-mobile-nav" aria-label="Navigation mobile">
      {navItems.slice(0,4).map(({path, mobileLabel, icon: Icon}) => <Link key={path} to={path} className={pathname === path ? 'is-active' : ''} aria-current={pathname === path ? 'page' : undefined}><Icon size={21} /><span>{mobileLabel}</span></Link>)}
      <button onClick={() => setMoreOpen(true)} aria-label="Afficher les autres outils" className={navItems.slice(4).some(item => item.path === pathname) ? 'is-active' : ''}><Grid2x2 size={21} /><span>Plus</span></button>
    </nav>
    <Sheet open={moreOpen} onOpenChange={setMoreOpen}>
      <SheetContent side="bottom" className="mx-auto w-full max-w-xl rounded-t-3xl p-6 pb-8">
        <SheetHeader><SheetTitle>Tous vos outils</SheetTitle><SheetDescription>Accompagner vos cultures, à chaque étape.</SheetDescription></SheetHeader>
        <div className="grid gap-2 mt-5">{navItems.slice(4).map(({path,label,icon:Icon}) => <button key={path} className="av-nav-link" onClick={() => {setMoreOpen(false); navigate(path);}}><Icon size={20} /><span>{label}</span><ChevronRight size={16} /></button>)}</div>
        <button className="av-logout mt-4" onClick={() => db.auth.logout('/login')}><LogOut size={18} />Se déconnecter</button>
      </SheetContent>
    </Sheet>
  </div>;
}
