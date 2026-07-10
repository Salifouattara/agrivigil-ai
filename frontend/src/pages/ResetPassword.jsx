import { db } from '@/api/apiClient';

import React, { useState } from 'react';

import { Leaf, Loader2, Lock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function ResetPassword() {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirm) { setError('Les mots de passe ne correspondent pas'); return; }
    setError('');
    setLoading(true);
    try {
      await db.auth.resetPassword({ resetToken: token, newPassword: password });
      window.location.href = '/login';
    } catch (err) {
      setError(err.message || 'Erreur lors de la réinitialisation');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen hero-gradient flex flex-col items-center justify-center px-6 py-10">
      <div className="w-full max-w-sm surface-card rounded-[32px] p-7">
        <div className="flex flex-col items-center mb-7">
          <div className="w-16 h-16 rounded-3xl bg-[#12523A] flex items-center justify-center mb-3 shadow-[0_10px_24px_-8px_rgba(18,82,58,0.55)]">
            <Leaf className="w-8 h-8 text-[#9CF7C4]" />
          </div>
          <h1 className="font-heading text-2xl font-extrabold text-[#10221A]">Nouveau mot de passe</h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <Label className="text-sm font-body font-medium text-[#10221A]">Nouveau mot de passe</Label>
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
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Réinitialiser'}
          </Button>
        </form>
      </div>
    </div>
  );
}
