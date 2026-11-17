import { db } from '@/api/apiClient';

import React, { useState } from 'react';

import { Leaf, Loader2, Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Link } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await db.auth.loginViaEmailPassword(email, password);
      window.location.href = '/';
    } catch (err) {
      setError(err.message || 'Identifiants incorrects');
      setLoading(false);
    }
  };


  return (
    <div className="av-login">
      <section className="av-login-story"><div className="av-login-wordmark"><Leaf size={28} /> AgriVigil AI</div><div><p className="av-login-eyebrow">L’AGRICULTURE, MIEUX ACCOMPAGNÉE</p><h2>Le bon regard.<br />Au bon moment.</h2><p className="av-login-description">Observez vos cultures, suivez leur santé et préparez vos interventions avec l’aide de l’intelligence artificielle.</p><div className="av-login-tools"><span>01 · Diagnostic photo</span><span>02 · Suivi des cultures</span><span>03 · Météo agricole</span></div></div><p className="av-login-footnote">Pensé pour les agriculteurs de Côte d’Ivoire.</p></section>
      <div className="av-login-form-area">
      <div className="av-login-card w-full max-w-md p-7">
        <div className="flex flex-col items-center mb-7">
          <div className="w-16 h-16 rounded-3xl bg-[#12523A] flex items-center justify-center mb-3 shadow-[0_10px_24px_-8px_rgba(18,82,58,0.55)]">
            <Leaf className="w-8 h-8 text-[#9CF7C4]" />
          </div>
          <h1 className="font-heading text-3xl font-extrabold text-[#10221A]">Bienvenue</h1>
          <p className="text-sm text-[#8A9A91] font-body">Connectez-vous à votre espace agricole</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="login-email" className="text-sm font-body font-medium text-[#10221A]">Email</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8A9A91]" />
              <Input
                id="login-email"
                autoComplete="username"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="votre@email.com"
                required
                className="h-12 pl-10 rounded-2xl border-[#DCE7E0] text-base"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="login-password" className="text-sm font-body font-medium text-[#10221A]">Mot de passe</Label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8A9A91]" />
              <Input
                id="login-password"
                autoComplete="current-password"
                type={showPw ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="h-12 pl-10 pr-10 rounded-2xl border-[#DCE7E0] text-base"
              />
              <button type="button" aria-label={showPw ? "Masquer le mot de passe" : "Afficher le mot de passe"} onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8A9A91]">
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {error && <p className="text-sm text-[#D6473B] font-body">{error}</p>}

          <Button
            type="submit"
            disabled={loading}
            className="w-full h-14 text-base font-body font-semibold bg-[#12523A] hover:bg-[#0B3D2A] text-white rounded-2xl"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Se connecter'}
          </Button>
        </form>

        <button type="button" onClick={() => { setEmail('demo@monapp.com'); setPassword('Demo1234'); setError(''); }} className="w-full rounded-2xl border border-[#dce7e0] bg-[#f4f7ef] px-4 py-4 mt-4 text-sm font-semibold text-[#12523A]">Découvrir avec le compte de démonstration</button>
        <p className="text-xs leading-relaxed text-center text-[#7c8a7e] mt-2">Les identifiants seront préremplis. Cliquez ensuite sur Se connecter.</p>

        {import.meta.env.DEV ? <div className="mt-6 text-center space-y-2">
          <Link to="/forgot-password" className="text-sm text-[#B4740E] font-body hover:underline">
            Mot de passe oublié ?
          </Link>
          <p className="text-sm text-[#8A9A91] font-body">
            Pas encore de compte ?{' '}
            <Link to="/register" className="text-[#12523A] font-semibold hover:underline">Créer un compte</Link>
          </p>
        </div> : <p className="mt-6 text-center text-xs text-[#7c8a7e]">L’inscription et la récupération par e-mail seront disponibles prochainement.</p>}
      </div>
      </div>
    </div>
  );
}
