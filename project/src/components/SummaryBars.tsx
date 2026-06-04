import { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ErrorBar,
  Cell
} from 'recharts';
import { DASHBOARD_DATA } from '../data/dashboardData';

type MetricType = 'silhouette' | 'daviesBouldin';

interface SummaryBarsProps {
  metric: MetricType;
  featureSet: 'all' | 'F1' | 'F2';
}

const COLORS = {
  A: { fill: '#486581', stroke: '#334e68' },
  C: { fill: '#3b82f6', stroke: '#1e40af' }
};

export function SummaryBars({ metric, featureSet }: SummaryBarsProps) {
  const chartData = useMemo(() => {
    let cells = featureSet === 'all'
      ? ['A/F1', 'A/F2', 'C/F2', 'C/F1']
      : featureSet === 'F1'
        ? ['A/F1', 'C/F1']
        : ['A/F2', 'C/F2'];

    return cells.map(cell => {
      const summary = DASHBOARD_DATA.cellSummaries.find(s => s.cell === cell);
      if (!summary) return null;

      const metricSummary = summary[metric];
      return {
        name: cell,
        displayName: cell.replace('/', ' / '),
        value: metricSummary.median,
        q1: metricSummary.q1,
        q3: metricSummary.q3,
        mean: metricSummary.mean,
        condition: cell.startsWith('A') ? 'A' : 'C',
        errorMin: Math.abs(metricSummary.median - metricSummary.q1),
        errorMax: Math.abs(metricSummary.q3 - metricSummary.median)
      };
    }).filter(Boolean) as any[];
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
          {metricLabel} Summary{metricDirection}
        </h4>
        {metric === 'daviesBouldin' && (
          <span className="text-xs text-navy-500 bg-navy-50 px-2 py-1 rounded">
            Median + IQR
          </span>
        )}
      </div>

      <div className="flex gap-8 justify-center mb-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: COLORS.A.fill }} />
          <span className="text-navy-600">Baseline (A)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: COLORS.C.fill }} />
          <span className="text-navy-600">Oracle (C)</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, bottom: 30, left: 50 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="displayName"
            tick={{ fontSize: 12, fill: '#64748b' }}
            axisLine={{ stroke: '#cbd5e1' }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#64748b' }}
            axisLine={{ stroke: '#cbd5e1' }}
            domain={['auto', 'auto']}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-white border border-navy-200 shadow-lg rounded-lg p-3 text-xs">
                    <div className="font-semibold text-navy-900 mb-1">{data.displayName}</div>
                    <div className="text-navy-600">Median: {data.value.toFixed(6)}</div>
                    <div className="text-navy-500">Q1: {data.q1.toFixed(6)}</div>
                    <div className="text-navy-500">Q3: {data.q3.toFixed(6)}</div>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            <ErrorBar dataKey="errorMin" direction="y" width={8} stroke="#334e68" />
            <ErrorBar dataKey="errorMax" direction="y" width={8} stroke="#334e68" />
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[entry.condition as keyof typeof COLORS].fill}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
