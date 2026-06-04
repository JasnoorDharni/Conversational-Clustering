import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell
} from 'recharts';
import { DASHBOARD_DATA } from '../data/dashboardData';

type MetricType = 'silhouette' | 'daviesBouldin';

interface DistributionChartProps {
  metric: MetricType;
  featureSet: 'all' | 'F1' | 'F2';
}

const COLORS = {
  A: { fill: '#486581', stroke: '#334e68' },
  C: { fill: '#3b82f6', stroke: '#1e40af' }
};

export function DistributionChart({ metric, featureSet }: DistributionChartProps) {
  const [hoveredData, setHoveredData] = useState<any>(null);

  const { chartData, yDomain } = useMemo(() => {
    const cells = featureSet === 'all'
      ? ['A_F1', 'A_F2', 'C_F2', 'C_F1']
      : featureSet === 'F1'
        ? ['A_F1', 'C_F1']
        : ['A_F2', 'C_F2'];

    const allValues: number[] = [];
    const data: any[] = [];

    cells.forEach((cellKey, cellIndex) => {
      const cellData = DASHBOARD_DATA.metricsByCell[cellKey as keyof typeof DASHBOARD_DATA.metricsByCell];
      const values = cellData[metric];

      values.forEach((val, idx) => {
        if (val !== null) {
          allValues.push(val);
          const condition = cellKey.startsWith('A') ? 'A' : 'C';
          const feature = cellKey.includes('F1') ? 'F1' : 'F2';

          data.push({
            x: idx + cellIndex * 35,
            y: val,
            condition,
            conditionLabel: condition === 'A' ? 'Baseline' : 'Oracle',
            featureSet: feature,
            seed: idx,
            cellKey,
            jitter: (Math.random() - 0.5) * 0.8
          });
        }
      });
    });

    const minY = Math.min(...allValues);
    const maxY = Math.max(...allValues);
    const padding = (maxY - minY) * 0.1 || 0.05;

    return {
      chartData: data,
      yDomain: [Math.max(0, minY - padding), maxY + padding] as [number, number]
    };
  }, [metric, featureSet]);

  const { medians } = useMemo(() => {
    const cells = featureSet === 'all'
      ? ['A_F1', 'A_F2', 'C_F2', 'C_F1']
      : featureSet === 'F1'
        ? ['A_F1', 'C_F1']
        : ['A_F2', 'C_F2'];

    const meds: { x: number; y: number; condition: string }[] = [];

    cells.forEach((cellKey, idx) => {
      const summary = DASHBOARD_DATA.cellSummaries.find(s => s.cell === cellKey.replace('_', '/'));
      if (summary) {
        const median = summary[metric].median;
        if (median !== null) {
          meds.push({
            x: idx * 35 + 14,
            y: median,
            condition: cellKey.startsWith('A') ? 'A' : 'C'
          });
        }
      }
    });

    return { medians: meds };
  }, [metric, featureSet]);

  const metricLabel = metric === 'silhouette' ? 'Silhouette Score' : 'Davies-Bouldin Index';
  const metricDirection = metric === 'silhouette' ? ' (higher is better)' : ' (lower is better)';

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="card p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-semibold text-navy-900">
          {metricLabel} Distribution{metricDirection}
        </h4>
        {metric === 'daviesBouldin' && featureSet === 'all' && (
          <span className="text-xs text-navy-500 bg-navy-50 px-2 py-1 rounded">
            One infinite DB value excluded
          </span>
        )}
      </div>

      <div className="flex gap-8 justify-center mb-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS.A.fill }} />
          <span className="text-navy-600">Baseline (A)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS.C.fill }} />
          <span className="text-navy-600">Oracle (C)</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            type="number"
            dataKey="x"
            domain={[0, 140]}
            tick={false}
            axisLine={{ stroke: '#cbd5e1' }}
          />
          <YAxis
            type="number"
            dataKey="y"
            domain={yDomain}
            tick={{ fontSize: 11, fill: '#64748b' }}
            axisLine={{ stroke: '#cbd5e1' }}
          />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-white border border-navy-200 shadow-lg rounded-lg p-3 text-xs">
                    <div className="font-semibold text-navy-900 mb-1">
                      {data.conditionLabel} / {data.featureSet}
                    </div>
                    <div className="text-navy-600">Seed: {data.seed}</div>
                    <div className="text-navy-900 font-medium">
                      {metricLabel}: {data.y.toFixed(6)}
                    </div>
                  </div>
                );
              }
              return null;
            }}
          />
          <Scatter data={chartData}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[entry.condition as keyof typeof COLORS].fill}
                stroke={COLORS[entry.condition as keyof typeof COLORS].stroke}
                strokeWidth={1}
              />
            ))}
          </Scatter>
          {medians.map((m, idx) => (
            <ReferenceLine
              key={`median-${idx}`}
              x={m.x}
              stroke={COLORS[m.condition as keyof typeof COLORS].stroke}
              strokeDasharray="5 5"
              strokeWidth={2}
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>

      {featureSet === 'all' && (
        <div className="flex justify-between text-xs text-navy-500 mt-4 px-8">
          <span>A/F1</span>
          <span>A/F2</span>
          <span>C/F1</span>
          <span>C/F2</span>
        </div>
      )}
    </motion.div>
  );
}
