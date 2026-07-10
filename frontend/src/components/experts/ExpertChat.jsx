import { db } from '@/api/apiClient';

import React, { useState, useEffect, useRef } from 'react';

import { ArrowLeft, Send, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import moment from 'moment';

export default function ExpertChat({ expert, onBack }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [text, setText] = useState('');
  const scrollRef = useRef(null);

  useEffect(() => {
    db.entities.ExpertMessage
      .filter({ conversation_id: expert.id }, 'created_date', 50)
      .then(msgs => {
        setMessages(msgs);
        setLoading(false);
      });
    const unsub = db.entities.ExpertMessage.subscribe((event) => {
      if (event.type === 'create') {
        setMessages(prev => {
          if (prev.some(m => m.id === event.data.id)) return prev;
          return [...prev, event.data];
        });
      }
    }, 6000, { conversation_id: expert.id });
    return () => unsub();
  }, [expert.id]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const handleSend = async () => {
    const trimmed = text.trim();
    if (!trimmed || sending) return;
    setText('');
    setSending(true);
    setError(null);
    try {
      const result = await db.entities.ExpertMessage.create({
        conversation_id: expert.id,
        content: trimmed,
      });
      setMessages(prev => {
        const next = [...prev];
        [result.farmer_message, result.expert_message].forEach(msg => {
          if (msg && !next.some(m => m.id === msg.id)) next.push(msg);
        });
        return next;
      });
    } catch (err) {
      setError(err.message || "Impossible d'envoyer le message.");
      setText(trimmed);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Header */}
      <div className="px-3 py-3 flex items-center gap-3 bg-white border-b border-[#DCE7E0]/30">
        <button onClick={onBack} className="w-9 h-9 rounded-lg bg-[#F7FAF6] flex items-center justify-center text-[#10221A] hover:bg-[#DCE7E0]/30">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center font-heading font-bold text-white text-sm shrink-0"
          style={{ backgroundColor: expert.avatar_color }}
        >
          {expert.name.replace('Dr. ', '').split(' ').map(n => n[0]).join('').slice(0, 2)}
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-heading text-sm font-bold text-[#10221A] truncate">{expert.name}</p>
          <p className="text-xs text-[#B4740E] font-body flex items-center gap-1">
            {expert.role}
            {expert.online && (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-[#12523A] ml-1" /> En ligne
              </>
            )}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 min-h-0 overflow-y-auto px-4 py-3 space-y-3 bg-[#F7FAF6]">
        {loading ? (
          <div className="flex items-center justify-center py-10">
            <Loader2 className="w-5 h-5 text-[#12523A] animate-spin" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="w-14 h-14 rounded-2xl bg-[#12523A]/10 flex items-center justify-center mb-3">
              <Send className="w-7 h-7 text-[#12523A]" strokeWidth={1.5} />
            </div>
            <p className="font-heading text-base font-medium text-[#10221A]">Posez votre question</p>
            <p className="text-xs text-[#8A9A91] mt-1 max-w-[240px] font-body">
              {expert.name} vous répondra en tant que {expert.role.toLowerCase()}.
            </p>
          </div>
        ) : (
          messages.map(msg => {
            const isMe = msg.sender_role === 'farmer';
            return (
              <div key={msg.id} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                <div className="max-w-[80%]">
                  <div className={`px-3.5 py-2.5 rounded-2xl text-sm font-body leading-relaxed ${
                    isMe
                      ? 'bg-[#12523A] text-[#F7FAF6] rounded-br-md'
                      : 'bg-white border border-[#DCE7E0]/40 text-[#10221A] rounded-bl-md'
                  }`}>
                    {msg.content}
                  </div>
                  <p className={`text-[10px] text-[#DCE7E0] font-body mt-0.5 ${isMe ? 'text-right mr-1' : 'ml-1'}`}>
                    {moment(msg.created_date).format('HH:mm')}
                  </p>
                </div>
              </div>
            );
          })
        )}
        {sending && (
          <div className="flex justify-start">
            <div className="bg-white border border-[#DCE7E0]/40 rounded-2xl rounded-bl-md px-4 py-3 flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-[#8A9A91] animate-spin" />
              <span className="text-xs text-[#8A9A91] font-body">{expert.name.split(' ')[0]} rédige…</span>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3 bg-white border-t border-[#DCE7E0]/30">
        {error && (
          <p className="text-xs text-red-600 font-body mb-2">{error}</p>
        )}
        <div className="flex items-center gap-2">
          <Input
            value={text}
            onChange={e => setText(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Décrivez votre problème…"
            className="flex-1 h-12 rounded-xl border-[#DCE7E0] text-base font-body"
          />
          <Button
            onClick={handleSend}
            disabled={!text.trim() || sending}
            className="h-12 w-12 rounded-xl bg-[#12523A] hover:bg-[#0B3D2A] p-0"
          >
            {sending ? <Loader2 className="w-5 h-5 animate-spin text-[#F7FAF6]" /> : <Send className="w-5 h-5 text-[#F7FAF6]" />}
          </Button>
        </div>
      </div>
    </div>
  );
}
