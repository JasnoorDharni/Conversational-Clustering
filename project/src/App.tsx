import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingDown,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Map,
  Database,
  Layers,
  BarChart3
} from 'lucide-react';
import { DASHBOARD_DATA } from './data/dashboardData';
import { Navigation } from './components/Navigation';
import { MetricCard } from './components/MetricCard';
import { Section } from './components/Section';
import { DeltaChart } from './components/DeltaChart';
import { FindingCard } from './components/FindingCard';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
  Legend,
  ReferenceLine
} from 'recharts';

const SECTIONS = ['introduction', 'h1-hypothesis', 'h2-hypothesis', 'h3-hypothesis'];

function StatusBadge({ status, label }: { status: string; label: string }) {
  const colors = {
    not_supported: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
    exploratory_inconclusive: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  };

  const color = colors[status as keyof typeof colors] || colors.not_supported;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border ${color.bg} ${color.text} ${color.border}`}
    >
      <AlertCircle className="w-4 h-4" />
      <span className="font-semibold text-sm">{label}</span>
    </motion.div>
  );
}

function App() {
  const [h2ChartType, setH2ChartType] = useState<'dual' | 'medians'>('dual');

  return (
    <div className="min-h-screen bg-white">
      <Navigation sections={SECTIONS} />

      {/* SECTION 1: INTRODUCTION + EDA */}
      <header id="introduction" className="pt-24 pb-16 md:pt-32 md:pb-24 bg-gradient-to-b from-navy-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h1 className="text-4xl md:text-5xl lg:text-5xl font-bold text-navy-900 tracking-tight mb-4">
              Conversational Clustering on UCDP GEDEvent 25.1
            </h1>
            <p className="text-lg md:text-xl text-navy-600 max-w-3xl mx-auto mb-2">
              A static dashboard of a conversational clustering study on Russia-Ukraine conflict events.
            </p>
            <p className="text-sm text-navy-500">
              Built for political scientists and conflict researchers exploring structured conflict-event data.
            </p>
          </motion.div>

          {/* Intro Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-12">
            {[
              { label: 'Raw GED rows', value: '385,918' },
              { label: 'Raw columns', value: '49' },
              { label: 'Ukraine events (all years)', value: '31,547' },
              { label: 'Filtered post-2022', value: '27,942' },
              { label: 'Locked sample', value: '2,000' },
              { label: 'Duplicate IDs', value: '0' },
              { label: 'Sample seed', value: '42' },
              { label: 'Date range', value: '3 years' },
            ].map((item, idx) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: idx * 0.05 }}
                className="card p-4 text-center"
              >
                <div className="text-2xl md:text-3xl font-bold text-navy-900 mb-1">{item.value}</div>
                <div className="text-xs text-navy-500 uppercase tracking-wide">{item.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </header>

      <div className="h-px bg-gradient-to-r from-transparent via-navy-200 to-transparent" />

      {/* EDA Charts Section */}
      <Section id="eda-charts" title="Dataset Profile">
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Data Funnel */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="card p-6"
          >
            <h3 className="text-lg font-semibold text-navy-900 mb-4">Data Funnel</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={[
                  { name: 'Raw GED', value: 385918 },
                  { name: 'Ukraine (all)', value: 31547 },
                  { name: 'Post-2022', value: 27942 },
                  { name: 'Study sample', value: 2000 },
                ]}
                layout="vertical"
                margin={{ top: 0, right: 30, bottom: 0, left: 100 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #cbd5e1', borderRadius: '6px' }}
                  formatter={(value) => (value as number).toLocaleString()}
                />
                <Bar dataKey="value" fill="#486581" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Event Type Distribution */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="card p-6"
          >
            <h3 className="text-lg font-semibold text-navy-900 mb-4">Event Type Distribution</h3>
            <div className="text-center text-sm font-medium text-navy-700 mb-2">
              State-based: 99.2%
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={DASHBOARD_DATA.edaCharts.eventTypeDistribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#486581"
                  dataKey="count"
                >
                  <Cell fill="#486581" />
                  <Cell fill="#94a3b8" />
                </Pie>
                <Tooltip formatter={(value) => (value as number).toLocaleString()} />
              </PieChart>
            </ResponsiveContainer>
            <div className="text-center text-sm font-medium text-navy-500 mt-2">
              One-sided violence: 0.8%
            </div>
          </motion.div>
        </div>

        {/* Top Oblasts */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="card p-6 mb-8"
        >
          <h3 className="text-lg font-semibold text-navy-900 mb-4">Geographic Distribution (Top Oblasts)</h3>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart
              data={DASHBOARD_DATA.edaCharts.topOblasts}
              layout="vertical"
              margin={{ top: 0, right: 30, left: 150 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" tick={{ fontSize: 10, fill: '#64748b' }} />
              <YAxis dataKey="oblast" type="category" tick={{ fontSize: 10, fill: '#64748b' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #cbd5e1', borderRadius: '6px' }}
                formatter={(value: any) => [`${value.toLocaleString()} events`, 'Count']}
              />
              <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Fatality and Quality Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="card p-6"
          >
            <h4 className="text-sm font-semibold text-navy-900 mb-4 uppercase tracking-wide">Fatality Summary</h4>
            <div className="space-y-3">
              {[
                { label: 'Min', value: '0' },
                { label: 'Median', value: '2.0' },
                { label: 'Mean', value: '8.4' },
                { label: '99th percentile', value: '74' },
                { label: 'Max', value: '15,996' },
                { label: 'Zero events', value: '206 (0.7%)' },
              ].map((item) => (
                <div key={item.label} className="flex justify-between items-center py-2 border-b border-navy-100 last:border-0">
                  <span className="text-sm text-navy-600">{item.label}</span>
                  <span className="font-semibold text-navy-900">{item.value}</span>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="card p-6"
          >
            <h4 className="text-sm font-semibold text-navy-900 mb-4 uppercase tracking-wide">Data Quality</h4>
            <div className="space-y-3">
              {[
                { label: 'Valid coordinates', value: '100%' },
                { label: 'Latitude null rate', value: '0%' },
                { label: 'Longitude null rate', value: '0%' },
                { label: 'Best fatality null rate', value: '0%' },
                { label: 'adm_1 null rate', value: '6.84%' },
                { label: 'where_description non-null', value: '97.1%' },
              ].map((item) => (
                <div key={item.label} className="flex justify-between items-center py-2 border-b border-navy-100 last:border-0">
                  <span className="text-sm text-navy-600">{item.label}</span>
                  <span className="font-semibold text-navy-900">{item.value}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Feature Sets */}
        <div className="grid md:grid-cols-2 gap-6 mt-6">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="card p-6 bg-navy-50 border-navy-200"
          >
            <div className="flex items-start gap-3">
              <Map className="w-5 h-5 text-navy-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold text-navy-900 mb-1">F1: Location-only</h4>
                <p className="text-sm text-navy-700">latitude, longitude, adm_1</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="card p-6 bg-blue-50 border-blue-200"
          >
            <div className="flex items-start gap-3">
              <Layers className="w-5 h-5 text-blue-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold text-blue-900 mb-1">F2: Richer/full feature set</h4>
                <p className="text-sm text-blue-700">F1 + type_of_violence + side_b + best fatalities</p>
              </div>
            </div>
          </motion.div>
        </div>
      </Section>

      <div className="h-px bg-gradient-to-r from-transparent via-navy-200 to-transparent" />

      {/* SECTION 2: H1 */}
      <Section
        id="h1-hypothesis"
        title="H1: Human Refinement and Silhouette (F2)"
        subtitle="Examining conversational refinement vs one-shot baseline"
      >
        <StatusBadge status="not_supported" label="Not Supported" />

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="mt-6 p-4 bg-navy-50 border border-navy-100 rounded-lg"
        >
          <p className="text-sm text-navy-700">
            <strong>Hypothesis:</strong> Human conversational refinement improves final Silhouette score relative to the one-shot baseline under the richer feature set F2.
          </p>
          <p className="text-sm text-navy-700 mt-2">
            <strong>Finding:</strong> {DASHBOARD_DATA.h1.interpretation}
          </p>
        </motion.div>

        {/* H1 Summary Stats */}
        <div className="grid md:grid-cols-3 gap-4 mt-8 mb-8">
          {[
            { label: 'Median Delta (B - A)', value: '-0.000308', icon: TrendingDown },
            { label: 'Mean Delta (B - A)', value: '-0.042187', icon: TrendingDown },
            { label: 'Positive Seeds', value: '13 / 30' },
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: 0.1 + idx * 0.05 }}
                className="card p-4"
              >
                {Icon && <Icon className="w-4 h-4 text-navy-500 mb-2" />}
                <div className="text-xl font-bold text-navy-900">{item.value}</div>
                <div className="text-xs text-navy-500 uppercase tracking-wide">{item.label}</div>
              </motion.div>
            );
          })}
        </div>

        {/* H1 Charts */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Final Silhouette by Condition */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="card p-6"
          >
            <h4 className="text-sm font-semibold text-navy-900 mb-4">Final Silhouette (F2)</h4>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={[
                  { name: 'A (Baseline)', median: 0.893293, mean: 0.893578 },
                  { name: 'B (Human)', median: 0.892985, mean: 0.851391 },
                  { name: 'C (Oracle)', median: 0.886805, mean: 0.863045 },
                ]}
                margin={{ top: 20, right: 20, bottom: 20, left: 50 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} domain={[0.84, 0.9]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #cbd5e1', borderRadius: '6px' }}
                  formatter={(value) => (value as number).toFixed(6)}
                />
                <Bar dataKey="median" fill="#486581" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Per-seed Delta Chart */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="card p-6"
          >
            <h4 className="text-sm font-semibold text-navy-900 mb-4">H1 Per-Seed Silhouette Delta (B - A)</h4>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={DASHBOARD_DATA.h1.perSeedDeltas} margin={{ top: 20, right: 20, bottom: 30, left: 50 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="seed" tick={{ fontSize: 9, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                <ReferenceLine y={0} stroke="#334e68" strokeWidth={2} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #cbd5e1', borderRadius: '6px' }}
                  formatter={(value) => (value as number).toFixed(6)}
                />
                <Bar dataKey="delta" fill="#486581" radius={[2, 2, 0, 0]}>
                  {DASHBOARD_DATA.h1.perSeedDeltas.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.delta > 0.001 ? '#10b981' : entry.delta < -0.001 ? '#ef4444' : '#cbd5e1'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>
      </Section>

      <div className="h-px bg-gradient-to-r from-transparent via-navy-200 to-transparent" />

      {/* SECTION 3: H2 */}
      <Section
        id="h2-hypothesis"
        title="H2: Feature Set Effects on Refinement"
        subtitle="Does the richer feature set help conversational refinement more?"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border bg-amber-50 text-amber-700 border-amber-200">
          <AlertCircle className="w-4 h-4" />
          <span className="font-semibold text-sm">Exploratory & Inconclusive</span>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="mt-6 p-4 bg-amber-50 border border-amber-100 rounded-lg"
        >
          <p className="text-sm text-amber-800">
            <strong>Finding:</strong> {DASHBOARD_DATA.h2.interpretation}
          </p>
        </motion.div>

        {/* H2 Summary Stats */}
        <div className="grid md:grid-cols-3 gap-4 mt-8 mb-8">
          {[
            { label: 'F1 Median Delta', value: '0.000000' },
            { label: 'F2 Median Delta', value: '-0.000308' },
            { label: 'Feature Advantage (F2-F1)', value: '0.001091' },
          ].map((item, idx) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: 0.1 + idx * 0.05 }}
              className="card p-4"
            >
              <div className="text-xl font-bold text-navy-900">{item.value}</div>
              <div className="text-xs text-navy-500 uppercase tracking-wide">{item.label}</div>
            </motion.div>
          ))}
        </div>

        {/* Chart Type Toggle */}
        <div className="flex gap-2 mb-8">
          <button
            onClick={() => setH2ChartType('dual')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              h2ChartType === 'dual'
                ? 'bg-navy-900 text-white'
                : 'bg-navy-50 text-navy-600 hover:bg-navy-100'
            }`}
          >
            Dual Deltas by Seed
          </button>
          <button
            onClick={() => setH2ChartType('medians')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              h2ChartType === 'medians'
                ? 'bg-navy-900 text-white'
                : 'bg-navy-50 text-navy-600 hover:bg-navy-100'
            }`}
          >
            All Condition Medians
          </button>
        </div>

        {h2ChartType === 'dual' ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="card p-6 mb-8"
          >
            <h4 className="text-sm font-semibold text-navy-900 mb-4">Delta Comparison: F1 vs F2</h4>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={DASHBOARD_DATA.h2.perSeedComparison} margin={{ top: 20, right: 20, bottom: 20, left: 50 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="seed" tick={{ fontSize: 9, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                <ReferenceLine y={0} stroke="#334e68" strokeWidth={2} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #cbd5e1', borderRadius: '6px' }}
                  formatter={(value) => (value as number).toFixed(6)}
                />
                <Legend />
                <Line type="monotone" dataKey="f1" name="F1 Delta" stroke="#486581" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="f2" name="F2 Delta" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="card p-6 mb-8"
          >
            <h4 className="text-sm font-semibold text-navy-900 mb-4">Final Silhouette Medians: All Conditions</h4>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart
                data={DASHBOARD_DATA.h2.allConditionMedians}
                margin={{ top: 20, right: 20, bottom: 20, left: 50 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="cell" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} domain={[0.88, 0.91]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #cbd5e1', borderRadius: '6px' }}
                  formatter={(value) => (value as number).toFixed(6)}
                />
                <Bar dataKey="median" fill="#486581" radius={[4, 4, 0, 0]}>
                  {DASHBOARD_DATA.h2.allConditionMedians.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.cell.includes('A') ? '#486581' : entry.cell.includes('B') ? '#94a3b8' : '#3b82f6'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        )}
      </Section>

      <div className="h-px bg-gradient-to-r from-transparent via-navy-200 to-transparent" />

      {/* SECTION 4: H3 */}
      <Section
        id="h3-hypothesis"
        title="H3: Oracle as Human Proxy"
        subtitle="Can the LLM oracle validate cluster comparisons reliably?"
      >
        <StatusBadge status="not_supported" label="Not Supported" />

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="mt-6 p-4 bg-red-50 border border-red-100 rounded-lg"
        >
          <p className="text-sm text-red-800">
            <strong>Finding:</strong> {DASHBOARD_DATA.h3.interpretation}
          </p>
        </motion.div>

        {/* H3 Metric Cards */}
        <div className="grid md:grid-cols-4 gap-4 mt-8 mb-8">
          {[
            { label: 'Human Reliability (α)', value: '0.13' },
            { label: 'Oracle-Human Agreement', value: '65%' },
            { label: 'Cohen Kappa', value: '0.22' },
            { label: 'Position-Bias Pairs', value: '19/20' },
          ].map((item, idx) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: 0.1 + idx * 0.05 }}
              className="card p-4"
            >
              <div className="text-2xl font-bold text-navy-900">{item.value}</div>
              <div className="text-xs text-navy-500 uppercase tracking-wide">{item.label}</div>
            </motion.div>
          ))}
        </div>

        {/* Swap Diagnostic */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="card p-6 mb-8"
        >
          <h4 className="text-sm font-semibold text-navy-900 mb-4">Swap Diagnostic: Oracle Label Bias</h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={[
                { name: 'Same Displayed Label', value: 19 },
                { name: 'Same Underlying Clustering', value: 1 },
              ]}
              layout="vertical"
              margin={{ top: 20, right: 30, bottom: 20, left: 180 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #cbd5e1', borderRadius: '6px' }}
                formatter={(value) => (value as number).toLocaleString()}
              />
              <Bar dataKey="value" fill="#ef4444" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <p className="text-xs text-navy-600 mt-4">
            The oracle preserved the displayed A/B label in 19/20 cases when the clustering was swapped, indicating strong position bias rather than genuine cluster-quality judgment.
          </p>
        </motion.div>
      </Section>

      {/* Footer */}
      <footer className="py-12 border-t border-navy-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <p className="text-sm text-navy-600 mb-2">
              Conversational refinement did not reliably improve internal clustering metrics on this highly categorical conflict-event dataset. However, it remains useful as an exploratory interface that helps political scientists engage with the features, assumptions, and structure of the data.
            </p>
            <p className="text-xs text-navy-500">
              UCDP GEDEvent 25.1 | Ukraine 2022-2024 | 180 total runs across 3 conditions × 2 feature sets × 30 seeds
            </p>
          </motion.div>
        </div>
      </footer>
    </div>
  );
}

export default App;
