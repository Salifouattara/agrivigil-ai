import { db } from '@/api/apiClient';

import React, { useState } from 'react';

import { Leaf, Loader2, Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Link } from 'react-router-dom';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    await db.auth.resetPasswordRequest(email);
    setSent(true);
    setLoading(false);
  };

  return (
    <div className="min-h-screen hero-gradient flex flex-col items-center justify-center px-6 py-10">
      <div className="w-full max-w-sm surface-card rounded-[32px] p-7">
        <div className="flex flex-col items-center mb-7">
          <div className="w-16 h-16 rounded-3xl bg-[#12523A] flex items-center justify-center mb-3 shadow-[0_10px_24px_-8px_rgba(18,82,58,0.55)]">
            <Leaf className="w-8 h-8 text-[#9CF7C4]" />
          </div>
          <h1 className="font-heading text-2xl font-extrabold text-[#10221A]">Mot de passe oublié</h1>
          <p className="text-sm text-[#8A9A91] font-body mt-1">Entrez votre email pour réinitialiser</p>
        </div>

        {sent ? (
          <div className="bg-[#E3F6EA] rounded-2xl p-5 text-center">
            <p className="text-sm text-[#12523A] font-body font-medium">Si un compte existe avec cet email, un lien de réinitialisation a été envoyé.</p>
            <Link to="/login" className="inline-block mt-4 text-sm text-[#B4740E] font-body hover:underline">Retour à la connexion</Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label className="text-sm font-body font-medium text-[#10221A]">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8A9A91]" />
                <Input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="votre@email.com" required className="h-12 pl-10 rounded-2xl border-[#DCE7E0] text-base" />
              </div>
            </div>
            <Button type="submit" disabled={loading} className="w-full h-14 text-base font-body font-semibold bg-[#12523A] hover:bg-[#0B3D2A] text-white rounded-2xl">
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Envoyer le lien'}
            </Button>
            <div className="text-center">
              <Link to="/login" className="text-sm text-[#8A9A91] font-body hover:underline">Retour à la connexion</Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
