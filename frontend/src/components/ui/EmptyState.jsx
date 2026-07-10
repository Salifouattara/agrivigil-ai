import React from 'react';
import { Leaf } from 'lucide-react';

export default function EmptyState({ icon: Icon = Leaf, title, description }) {
  return (
    <div className="flex flex-col items-center justify-center py-14 px-8 text-center">
      <div className="w-16 h-16 rounded-3xl bg-[#E3F6EA] flex items-center justify-center mb-4">
        <Icon className="w-7 h-7 text-[#12523A]" strokeWidth={1.5} />
      </div>
      <h3 className="font-heading text-base font-bold text-[#10221A] mb-1">{title}</h3>
      <p className="text-sm text-[#5B6B62] font-body max-w-[260px] leading-relaxed">{description}</p>
    </div>
  );
}
