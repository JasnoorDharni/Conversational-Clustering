import { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Area
} from 'recharts';
import { DASHBOARD_DATA } from '../data/dashboardData';

type MetricType = 'silhouette' | 'daviesBouldin';

interface TrajectoryChartProps {
  featureSet: 'F1' | 'F2';
  metric: MetricType;
}

export function TrajectoryChart({ featureSet, metric }: TrajectoryChartProps) {
  const chartData = useMemo(() => {
    const trajectories = DASHBOARD_DATA.trajectoryAggregates.filter(
      t => t.featureSet === featureSet
    );

    return trajectories.map(t => ({
      turn: t.turn,
      mean: metric === 'silhouette' ? t.silhouetteMean : t.dbMean,
      median: metric === 'silhouette' ? t.silhouetteMedian : t.dbMedian,
      q1: metric === 'silhouette' ? t.silhouetteQ1 : undefined,
      q3: metric === 'silhouette' ? t.silhouetteQ3 : undefined,
      n: t.n
    }));
  }, [featureSet, metric]);

  const metricLabel = metric === 'silhouette' ? 'Silhouette Score' : 'Davies-Bouldin Index';

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="card p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-semibold text-navy-900">
          {metricLabel} Trajectory Across Refinement Turns
        </h4>
        <span className="text-xs text-navy-500 bg-navy-50 px-2 py-1 rounded">
          Feature Set: {featureSet}
        </span>
      </div>

      <div className="mb-4 text-xs text-navy-600 bg-navy-50/50 p-3 rounded-lg">
        Turn 0 = Baseline before oracle refinement. Turns 1-5 show metric evolution through refinement iterations.
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 30, bottom: 30, left: 50 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="turn"
            tick={{ fontSize: 12, fill: '#64748b' }}
            axisLine={{ stroke: '#cbd5e1' }}
            label={{ value: 'Refinement Turn', position: 'bottom', offset: 15, fontSize: 11, fill: '#64748b' }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#64748b' }}
            axisLine={{ stroke: '#cbd5e1' }}
            tickFormatter={(v) => v.toFixed(3)}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-white border border-navy-200 shadow-lg rounded-lg p-3 text-xs">
                    <div className="font-semibold text-navy-900 mb-1">Turn {data.turn}</div>
                    <div className="text-navy-600">Mean: {data.mean.toFixed(6)}</div>
                    <div className="text-navy-600">Median: {data.median.toFixed(6)}</div>
                    <div className="text-navy-500 mt-1">N = {data.n}</div>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="mean"
            name="Mean"
            stroke="#3b82f6"
            strokeWidth={2.5}
            dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="median"
            name="Median"
            stroke="#334e68"
            strokeWidth={2.5}
            strokeDasharray="5 5"
            dot={{ fill: '#334e68', strokeWidth: 2, r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
