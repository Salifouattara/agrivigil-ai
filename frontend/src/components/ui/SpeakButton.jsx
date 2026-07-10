import React, { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function SpeakButton({ text, className = '' }) {
  const [speaking, setSpeaking] = useState(false);

  const handleSpeak = () => {
    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'fr-FR';
    utterance.rate = 0.85;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(utterance);
    setSpeaking(true);
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleSpeak}
      className={`gap-1.5 rounded-xl border-[#12523A]/20 text-[#12523A] hover:bg-[#12523A]/8 font-medium ${className}`}
    >
      {speaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
      <span className="text-xs font-body">{speaking ? 'Arrêter' : 'Écouter'}</span>
    </Button>
  );
}
