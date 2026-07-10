import React from 'react';
import { ComposedChart, Area, Scatter, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import moment from 'moment';
import { severityColors } from '@/lib/theme';

const severityScore = { faible: 1, modérée: 2, élevée: 3, critique: 4 };
const severityLabel = { 1: 'Faible', 2: 'Modérée', 3: 'Élevée', 4: 'Critique' };

export default function HealthChart({ scans, days }) {
  const start = moment().subtract(days, 'days').valueOf();

  const seriesColors = ['#12523A', '#2F6FE4', '#E8B84B', '#5B6B62', '#D6473B', '#1B7049'];
  const seriesGroups = {};

  scans
    .filter(s => s.image_url && moment(s.created_date).valueOf() >= start)
    .forEach(s => {
      const seriesId = `${s.crop_name || 'Inconnu'}|${s.disease_name || 'Non spécifiée'}`;
      if (!seriesGroups[seriesId]) {
        seriesGroups[seriesId] = {
          id: seriesId,
          label: s.disease_name ? `${s.crop_name} – ${s.disease_name}` : s.crop_name || 'Inconnu',
          crop: s.crop_name,
          disease: s.disease_name,
          color: seriesColors[Object.keys(seriesGroups).length % seriesColors.length],
          points: [],
        };
      }

      const timestamp = moment(s.created_date).startOf('day').valueOf() + 12 * 3600 * 1000;
      seriesGroups[seriesId].points.push({
        timestamp,
        date: moment(s.created_date).format('DD/MM'),
        score: severityScore[s.severity] || 1,
        image_url: s.image_url,
        scanId: s.id,
        disease: s.disease_name,
        crop: s.crop_name,
        severity: s.severity,
      });
    });

  const seriesList = Object.values(seriesGroups);
  seriesList.forEach(group => {
    group.points.sort((a, b) => a.timestamp - b.timestamp);
    group.points.forEach((point, index) => {
      point.timestamp += index * 1000;
    });
  });

  const dataMap = {};
  const seriesLabelMap = {};
  seriesList.forEach(group => {
    seriesLabelMap[group.id] = group.label;
    group.points.forEach(point => {
      const key = point.timestamp;
      if (!dataMap[key]) {
        dataMap[key] = { timestamp: point.timestamp, date: point.date };
      }
      dataMap[key][group.id] = point.score;
    });
  });

  const data = Object.values(dataMap).sort((a, b) => a.timestamp - b.timestamp);

  const renderPhotoPoint = (color) => (props) => {
    const { cx, cy, payload } = props;
    if (!payload || !payload.image_url) return null;
    const clipId = `clip-${payload.scanId}`;
    const ring = severityColors[payload.severity] || color || '#12523A';
    return (
      <g>
        <defs>
          <clipPath id={clipId}>
            <circle cx={cx} cy={cy} r={8} />
          </clipPath>
        </defs>
        <circle cx={cx} cy={cy} r={10} fill="#FFFFFF" stroke={ring} strokeWidth={2.5} />
        <image
          href={payload.image_url}
          x={cx - 8}
          y={cy - 8}
          width={16}
          height={16}
          clipPath={`url(#${clipId})`}
          preserveAspectRatio="xMidYMid slice"
        />
      </g>
    );
  };

  const customTooltipFormatter = (value, name) => {
    return [value, seriesLabelMap[name] || name];
  };

  if (seriesList.length === 0) {
    return (
      <p className="text-xs text-center text-[#8A9A91] font-body py-8">
        Aucune photo sur cette période. Scannez vos cultures pour suivre l'évolution.
      </p>
    );
  }

  return (
    <div>
      <ResponsiveContainer width="100%" height={200}>
        <ComposedChart data={data} margin={{ top: 12, right: 15, left: -10, bottom: 5 }}>
          <defs>
            <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#12523A" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#12523A" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#DCE7E0" opacity={0.3} vertical={false} />
          <XAxis
            type="number"
            dataKey="timestamp"
            domain={['dataMin - 86400000', 'dataMax + 86400000']}
            tickFormatter={(ts) => moment(ts).format('DD/MM')}
            tick={{ fontSize: 10, fill: '#8A9A91' }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            domain={[0, 4]}
            ticks={[1, 2, 3, 4]}
            tickFormatter={(v) => severityLabel[v] || ''}
            tick={{ fontSize: 9, fill: '#8A9A91' }}
            tickLine={false}
            axisLine={false}
            width={62}
          />
          <Tooltip
            contentStyle={{ background: '#FFFFFF', border: '1px solid #E3EDE7', borderRadius: '8px', fontSize: '12px', fontFamily: 'Inter' }}
            labelFormatter={(ts) => moment(ts).format('DD/MM/YYYY')}
            formatter={customTooltipFormatter}
          />
          <Legend
            wrapperStyle={{ fontSize: 11, color: '#5B6B62' }}
            formatter={(value) => seriesLabelMap[value] || value}
          />
          {seriesList.map(group => (
            <React.Fragment key={group.id}>
              <Area
                type="monotone"
                dataKey={group.id}
                stroke={group.color}
                fill="none"
                strokeWidth={2}
                dot={false}
                activeDot={false}
              />
              <Scatter
                dataKey={group.id}
                shape={renderPhotoPoint(group.color)}
              />
            </React.Fragment>
          ))}
        </ComposedChart>
      </ResponsiveContainer>
      <p className="text-[10px] text-center text-[#8A9A91] font-body mt-1">
        Chaque pastille = une photo scannée (couleur = gravité)
      </p>
    </div>
  );
}