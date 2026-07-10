import React from 'react';

// Conserve le nom historique du composant (utilisé dans tout le front) mais
// affiche désormais un séparateur fin et moderne au lieu du motif wax.
export default function WaxDivider({ className = '' }) {
  return <div className={`section-divider my-5 ${className}`} />;
}
