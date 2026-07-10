// AgriIA Côte d'Ivoire — Design System
// Inspired by Ivorian terroir: cacao forests, laterite soil, savanna sun

export const colors = {
  primary: '#12523A',        // Vert émeraude profond
  primaryLight: '#1B7049',
  primaryDark: '#06281C',
  secondary: '#2F6FE4',      // Bleu ciel doux (météo)
  secondaryLight: '#5A8FEE',
  accent: '#E8B84B',         // Jaune miel
  accentLight: '#F0CC73',
  cream: '#F7FAF6',          // Toile crème très douce
  warmGray: '#5B6B62',       // Gris vert doux
  warmGrayLight: '#8A9A91',
  warmGrayLighter: '#DCE7E0',
  alert: '#D6473B',          // Rouge corail
  alertLight: '#E17167',
  white: '#FFFFFF',
  black: '#10221A',
};

export const severityColors = {
  faible: '#1B7049',
  modérée: '#B4740E',
  élevée: '#C9762E',
  critique: '#D6473B',
};

export const cropIcons = {
  cacao: '🫘',
  café: '☕',
  manioc: '🌿',
  riz: '🌾',
  maïs: '🌽',
  igname: '🥔',
  banane_plantain: '🍌',
  hévéa: '🌳',
  palmier_huile: '🌴',
  coton: '🧶',
};

export const soilLabels = {
  argileux: 'Argileux (lourd)',
  sableux: 'Sableux (léger)',
  limoneux: 'Limoneux (fertile)',
  latéritique: 'Latéritique (rouge)',
  tourbeux: 'Tourbeux (organique)',
};

// Fertilizer recommendation data (NPK per hectare by crop and soil)
export const fertilizerData = {
  cacao: {
    base: { N: 60, P: 30, K: 80 },
    soilModifier: {
      argileux: { N: 0.9, P: 1.0, K: 0.85 },
      sableux: { N: 1.2, P: 1.1, K: 1.3 },
      limoneux: { N: 1.0, P: 1.0, K: 1.0 },
      latéritique: { N: 1.1, P: 1.2, K: 1.0 },
      tourbeux: { N: 0.8, P: 1.1, K: 1.1 },
    },
  },
  café: {
    base: { N: 80, P: 40, K: 60 },
    soilModifier: {
      argileux: { N: 0.9, P: 1.0, K: 0.9 },
      sableux: { N: 1.2, P: 1.2, K: 1.2 },
      limoneux: { N: 1.0, P: 1.0, K: 1.0 },
      latéritique: { N: 1.1, P: 1.15, K: 1.05 },
      tourbeux: { N: 0.85, P: 1.1, K: 1.1 },
    },
  },
  manioc: {
    base: { N: 40, P: 20, K: 100 },
    soilModifier: {
      argileux: { N: 0.85, P: 0.9, K: 0.8 },
      sableux: { N: 1.15, P: 1.2, K: 1.3 },
      limoneux: { N: 1.0, P: 1.0, K: 1.0 },
      latéritique: { N: 1.1, P: 1.15, K: 1.0 },
      tourbeux: { N: 0.8, P: 1.0, K: 1.1 },
    },
  },
  riz: {
    base: { N: 90, P: 45, K: 45 },
    soilModifier: {
      argileux: { N: 0.95, P: 1.0, K: 0.9 },
      sableux: { N: 1.2, P: 1.15, K: 1.25 },
      limoneux: { N: 1.0, P: 1.0, K: 1.0 },
      latéritique: { N: 1.1, P: 1.2, K: 1.05 },
      tourbeux: { N: 0.85, P: 1.05, K: 1.1 },
    },
  },
  maïs: {
    base: { N: 100, P: 50, K: 50 },
    soilModifier: {
      argileux: { N: 0.9, P: 0.95, K: 0.85 },
      sableux: { N: 1.2, P: 1.2, K: 1.3 },
      limoneux: { N: 1.0, P: 1.0, K: 1.0 },
      latéritique: { N: 1.1, P: 1.15, K: 1.0 },
      tourbeux: { N: 0.85, P: 1.05, K: 1.1 },
    },
  },
  igname: {
    base: { N: 50, P: 25, K: 90 },
    soilModifier: {
      argileux: { N: 0.85, P: 0.9, K: 0.8 },
      sableux: { N: 1.15, P: 1.2, K: 1.25 },
      limoneux: { N: 1.0, P: 1.0, K: 1.0 },
      latéritique: { N: 1.1, P: 1.15, K: 1.0 },
      tourbeux: { N: 0.8, P: 1.05, K: 1.1 },
    },
  },
  banane_plantain: {
    base: { N: 70, P: 30, K: 120 },
    soilModifier: {
      argileux: { N: 0.9, P: 0.95, K: 0.85 },
      sableux: { N: 1.15, P: 1.15, K: 1.3 },
      limoneux: { N: 1.0, P: 1.0, K: 1.0 },
      latéritique: { N: 1.1, P: 1.15, K: 1.0 },
      tourbeux: { N: 0.85, P: 1.05, K: 1.1 },
    },
  },
  hévéa: {
    base: { N: 55, P: 35, K: 45 },
    soilModifier: {
      argileux: { N: 0.9, P: 1.0, K: 0.9 },
      sableux: { N: 1.15, P: 1.15, K: 1.2 },
      limoneux: { N: 1.0, P: 1.0, K: 1.0 },
      latéritique: { N: 1.1, P: 1.1, K: 1.05 },
      tourbeux: { N: 0.85, P: 1.05, K: 1.1 },
    },
  },
  palmier_huile: {
    base: { N: 60, P: 30, K: 100 },
    soilModifier: {
      argileux: { N: 0.9, P: 0.95, K: 0.85 },
      sableux: { N: 1.2, P: 1.2, K: 1.3 },
      limoneux: { N: 1.0, P: 1.0, K: 1.0 },
      latéritique: { N: 1.1, P: 1.15, K: 1.0 },
      tourbeux: { N: 0.85, P: 1.05, K: 1.1 },
    },
  },
  coton: {
    base: { N: 80, P: 40, K: 40 },
    soilModifier: {
      argileux: { N: 0.9, P: 0.95, K: 0.85 },
      sableux: { N: 1.2, P: 1.2, K: 1.25 },
      limoneux: { N: 1.0, P: 1.0, K: 1.0 },
      latéritique: { N: 1.1, P: 1.15, K: 1.0 },
      tourbeux: { N: 0.85, P: 1.05, K: 1.1 },
    },
  },
};

export function calculateFertilizer(cropType, soilType, hectares) {
  const crop = fertilizerData[cropType];
  if (!crop) return null;
  const mod = crop.soilModifier[soilType] || { N: 1, P: 1, K: 1 };
  return {
    nitrogen_kg: Math.round(crop.base.N * mod.N * hectares * 10) / 10,
    phosphorus_kg: Math.round(crop.base.P * mod.P * hectares * 10) / 10,
    potassium_kg: Math.round(crop.base.K * mod.K * hectares * 10) / 10,
  };
}