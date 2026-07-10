import { db } from '@/api/apiClient';

import React, { useState } from 'react';

import { Leaf, Loader2, Mail, Lock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Link } from 'react-router-dom';
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/components/ui/input-otp";

export default function Register() {
  const [step, setStep] = useState('register'); // register | otp
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    if (password !== confirm) { setError('Les mots de passe ne correspondent pas'); return; }
    setError('');
    setLoading(true);
    try {
      const res = await db.auth.register({ email, password });
      if (res && res.debug_otp_code) {
        setOtp(res.debug_otp_code);
      }
      setStep('otp');
    } catch (err) {
      setError(err.message || 'Erreur lors de l\'inscription');
    }
    setLoading(false);
  };

  const handleOtp = async () => {
    setError('');
    setLoading(true);
    try {
      const { access_token } = await db.auth.verifyOtp({ email, otpCode: otp });
      db.auth.setToken(access_token);
      window.location.href = '/';
    } catch (err) {
      setError(err.message || 'Code invalide');
      setLoading(false);
    }
  };

  const handleResend = async () => {
    await db.auth.resendOtp(email);
  };

  return (
    <div className="min-h-screen hero-gradient flex flex-col items-center justify-center px-6 py-10">
      <div className="w-full max-w-sm surface-card rounded-[32px] p-7">
        <div className="flex flex-col items-center mb-7">
          <div className="w-16 h-16 rounded-3xl bg-[#12523A] flex items-center justify-center mb-3 shadow-[0_10px_24px_-8px_rgba(18,82,58,0.55)]">
            <Leaf className="w-8 h-8 text-[#9CF7C4]" />
          </div>
          <h1 className="font-heading text-2xl font-extrabold text-[#10221A]">Créer un compte</h1>
          <p className="text-sm text-[#8A9A91] font-body">Rejoignez la communauté AgrivigilAI</p>
        </div>

        {step === 'register' ? (
          <form onSubmit={handleRegister} className="space-y-4">
            <div className="space-y-1.5">
              <Label className="text-sm font-body font-medium text-[#10221A]">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8A9A91]" />
                <Input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="votre@email.com" required className="h-12 pl-10 rounded-2xl border-[#DCE7E0] text-base" />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label className="text-sm font-body font-medium text-[#10221A]">Mot de passe</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8A9A91]" />
                <Input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required className="h-12 pl-10 rounded-2xl border-[#DCE7E0] text-base" />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label className="text-sm font-body font-medium text-[#10221A]">Confirmer</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8A9A91]" />
                <Input type="password" value={confirm} onChange={e => setConfirm(e.target.value)} placeholder="••••••••" required className="h-12 pl-10 rounded-2xl border-[#DCE7E0] text-base" />
              </div>
            </div>
            {error && <p className="text-sm text-[#D6473B] font-body">{error}</p>}
            <Button type="submit" disabled={loading} className="w-full h-14 text-base font-body font-semibold bg-[#12523A] hover:bg-[#0B3D2A] text-white rounded-2xl">
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Créer mon compte'}
            </Button>
          </form>
        ) : (
          <div className="space-y-4 text-center">
            <p className="text-sm text-[#10221A] font-body">Un code a été envoyé à <strong>{email}</strong></p>
            <div className="flex justify-center">
              <InputOTP value={otp} onChange={setOtp} maxLength={6}>
                <InputOTPGroup>
                  {[0,1,2,3,4,5].map(i => <InputOTPSlot key={i} index={i} className="w-11 h-12 text-lg" />)}
                </InputOTPGroup>
              </InputOTP>
            </div>
            {error && <p className="text-sm text-[#D6473B] font-body">{error}</p>}
            <Button onClick={handleOtp} disabled={loading || otp.length < 6} className="w-full h-14 text-base font-body font-semibold bg-[#12523A] hover:bg-[#0B3D2A] text-white rounded-2xl">
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Vérifier'}
            </Button>
            <button onClick={handleResend} className="text-sm text-[#B4740E] font-body hover:underline">Renvoyer le code</button>
          </div>
        )}

        <div className="mt-6 text-center">
          <p className="text-sm text-[#8A9A91] font-body">
            Déjà un compte ?{' '}
            <Link to="/login" className="text-[#12523A] font-semibold hover:underline">Se connecter</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
