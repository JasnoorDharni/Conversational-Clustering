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
  ReferenceLine,
  Cell
} from 'recharts';
import { DASHBOARD_DATA } from '../data/dashboardData';

interface DeltaChartProps {
  featureSet: 'F1' | 'F2';
}

const IMPROVEMENT_COLOR = '#10b981';
const WORSEN_COLOR = '#ef4444';
const NEUTRAL_COLOR = '#94a3b8';

export function DeltaChart({ featureSet }: DeltaChartProps) {
  const chartData = useMemo(() => {
    const delta = DASHBOARD_DATA.deltaBySeed[featureSet];
    return delta.seed.map((seed, index) => ({
      seed,
      delta: delta.silhouetteDelta[index],
      isPositive: delta.silhouetteDelta[index] > 0.001,
      isNegative: delta.silhouetteDelta[index] < -0.001,
      isNeutral: Math.abs(delta.silhouetteDelta[index]) <= 0.001
    }));
  }, [featureSet]);

  const statTest = DASHBOARD_DATA.statTests.find(s => s.featureSet === featureSet);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="card p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-semibold text-navy-900">
          C/F{featureSet.slice(1)} vs A/F{featureSet.slice(1)} Silhouette Delta by Seed
        </h4>
        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: IMPROVEMENT_COLOR }} />
            <span className="text-navy-500">Improved</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: WORSEN_COLOR }} />
            <span className="text-navy-500">Worsened</span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 20, bottom: 30, left: 50 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="seed"
            tick={{ fontSize: 10, fill: '#94a3b8' }}
            axisLine={{ stroke: '#cbd5e1' }}
            label={{ value: 'Seed', position: 'bottom', offset: 15, fontSize: 11, fill: '#64748b' }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#64748b' }}
            axisLine={{ stroke: '#cbd5e1' }}
            tickFormatter={(v) => v.toFixed(3)}
          />
          <ReferenceLine y={0} stroke="#334e68" strokeWidth={2} />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-white border border-navy-200 shadow-lg rounded-lg p-3 text-xs">
                    <div className="font-semibold text-navy-900 mb-1">Seed {data.seed}</div>
                    <div className={`font-medium ${data.delta > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      Delta: {data.delta >= 0 ? '+' : ''}{data.delta.toFixed(6)}
                    </div>
                    <div className="text-navy-500 mt-1">
                      {data.delta > 0.001 ? 'Oracle improved over baseline' :
                       data.delta < -0.001 ? 'Oracle worsened from baseline' : 'No change'}
                    </div>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="delta" radius={[2, 2, 2, 2]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={
                  entry.isPositive ? IMPROVEMENT_COLOR :
                  entry.isNegative ? WORSEN_COLOR : NEUTRAL_COLOR
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {statTest && (
        <div className="mt-6 p-4 bg-navy-50 rounded-lg border border-navy-100">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-navy-500 text-xs uppercase tracking-wide mb-1">Median Delta</div>
              <div className="font-semibold text-navy-900">
                {statTest.medianDelta_C_minus_A.toFixed(6)}
              </div>
            </div>
            <div>
              <div className="text-navy-500 text-xs uppercase tracking-wide mb-1">Wilcoxon W</div>
              <div className="font-semibold text-navy-900">{statTest.wilcoxonW}</div>
            </div>
            <div>
              <div className="text-navy-500 text-xs uppercase tracking-wide mb-1">One-sided p</div>
              <div className="font-semibold text-navy-900">{statTest.pValueOneSided.toFixed(6)}</div>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-navy-200">
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-0.5 rounded ${
                statTest.interpretation === 'supported' ? 'bg-emerald-100 text-emerald-700' :
                'bg-amber-100 text-amber-700'
              }`}>
                {statTest.interpretation === 'supported' ? 'Supported' : 'Not Supported'}
              </span>
              <span className="text-xs text-navy-600">
                One-sided Wilcoxon test (C &gt; A)
              </span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
