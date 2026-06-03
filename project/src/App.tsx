import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { DASHBOARD_DATA } from './data/dashboardData';

const SECTION_IDS = ['context', 'h1', 'h2', 'h3'] as const;

const COLORS = {
  ink: '#191610',
  muted: '#6f675c',
  panel: '#fffaf0',
  line: '#d7ccb8',
  gold: '#b7791f',
  teal: '#0f766e',
  rust: '#b45309',
  slate: '#465467',
  red: '#b91c1c',
  green: '#047857',
};

const STATUS_STYLES = {
  not_supported: 'bg-[var(--accent-rose-soft)] text-[var(--accent-rose)] border-[var(--accent-rose-border)]',
  inconclusive: 'bg-[var(--accent-gold-soft)] text-[var(--accent-gold)] border-[var(--accent-gold-border)]',
  supported: 'bg-[var(--accent-teal-soft)] text-[var(--accent-teal)] border-[var(--accent-teal-border)]',
} as const;

function fmt(value: number, digits = 3) {
  return value.toFixed(digits);
}

function tooltipNumber(value: number | string | readonly (number | string)[] | undefined, digits = 4) {
  if (Array.isArray(value)) {
    return value.join(', ');
  }

  if (typeof value === 'number') {
    return fmt(value, digits);
  }

  return `${value ?? ''}`;
}

function statusLabel(status: keyof typeof STATUS_STYLES) {
  if (status === 'not_supported') return 'Not Supported';
  if (status === 'inconclusive') return 'Inconclusive';
  return 'Supported';
}

function Section({
  id,
  eyebrow,
  title,
  children,
}: {
  id: string;
  eyebrow: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 py-14 md:py-20">
      <div className="mb-8 md:mb-10">
        <div className="eyebrow mb-3">{eyebrow}</div>
        <h2 className="text-3xl md:text-5xl font-semibold tracking-tight text-[var(--ink)]">
          {title}
        </h2>
      </div>
      {children}
    </section>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="panel p-5">
      <div className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">{label}</div>
      <div className="mt-3 text-3xl md:text-4xl font-semibold text-[var(--ink)]">{value}</div>
    </div>
  );
}

function InsightCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail?: string;
}) {
  return (
    <div className="panel p-5">
      <div className="text-xs uppercase tracking-[0.22em] text-[var(--muted)]">{label}</div>
      <div className="mt-3 text-2xl font-semibold text-[var(--ink)]">{value}</div>
      {detail ? <div className="mt-2 text-sm text-[var(--muted)]">{detail}</div> : null}
    </div>
  );
}

function HypothesisHeader({
  title,
  statement,
  status,
  note,
}: {
  title: string;
  statement: string;
  status: keyof typeof STATUS_STYLES;
  note: string;
}) {
  return (
    <div className="mb-8 grid gap-4 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
      <div>
        <div className="eyebrow mb-3">{title}</div>
        <p className="max-w-3xl text-lg text-[var(--ink)]">{statement}</p>
      </div>
      <div className="flex flex-col items-start gap-3 lg:items-end">
        <span className={`rounded-full border px-3 py-1 text-xs uppercase tracking-[0.24em] ${STATUS_STYLES[status]}`}>
          {statusLabel(status)}
        </span>
        <p className="max-w-md text-sm text-[var(--muted)] lg:text-right">{note}</p>
      </div>
    </div>
  );
}

function App() {
  const f2Cells = DASHBOARD_DATA.cells.filter((cell) => cell.featureSet === 'F2');
  const groupedCells = ['A', 'B', 'C'].map((condition) => {
    const f1 = DASHBOARD_DATA.cells.find((cell) => cell.condition === condition && cell.featureSet === 'F1');
    const f2 = DASHBOARD_DATA.cells.find((cell) => cell.condition === condition && cell.featureSet === 'F2');

    return {
      condition,
      F1: f1?.silhouetteMedian ?? 0,
      F2: f2?.silhouetteMedian ?? 0,
    };
  });

  const h3BiasData = [
    { label: 'Same displayed label after swap', value: DASHBOARD_DATA.h3.sameDisplayedLabelAfterSwap, fill: COLORS.rust },
    { label: 'Same underlying choice after swap', value: DASHBOARD_DATA.h3.sameUnderlyingAfterSwap, fill: COLORS.teal },
  ];

  return (
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)]">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top_left,rgba(183,121,31,0.12),transparent_28%),radial-gradient(circle_at_top_right,rgba(15,118,110,0.1),transparent_22%),linear-gradient(to_bottom,rgba(255,250,240,0.92),rgba(248,242,231,0.96))]" />

      <header className="sticky top-0 z-20 border-b border-[var(--line)] bg-[rgba(248,242,231,0.88)] backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <div className="text-xs uppercase tracking-[0.28em] text-[var(--muted)]">Study Dashboard</div>
            <div className="font-display text-lg tracking-tight">Conversational Clustering</div>
          </div>
          <nav className="flex gap-2 md:gap-3">
            {SECTION_IDS.map((id) => (
              <a
                key={id}
                href={`#${id}`}
                className="rounded-full border border-[var(--line)] px-3 py-1.5 text-xs uppercase tracking-[0.22em] text-[var(--muted)] transition hover:border-[var(--ink)] hover:text-[var(--ink)]"
              >
                {id.toUpperCase()}
              </a>
            ))}
          </nav>
        </div>
      </header>

      <main className="relative z-10">
        <section className="mx-auto max-w-7xl px-4 pb-10 pt-10 sm:px-6 lg:px-8 md:pb-16 md:pt-16">
          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="hero-panel overflow-hidden p-8 md:p-12"
          >
            <div className="grid gap-10 lg:grid-cols-[1.15fr_0.85fr]">
              <div>
                <div className="eyebrow mb-4">Committed Evidence Only</div>
                <h1 className="font-display max-w-4xl text-4xl leading-none tracking-tight md:text-6xl">
                  {DASHBOARD_DATA.overview.title}
                </h1>
                <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--muted)] md:text-lg">
                  {DASHBOARD_DATA.overview.subtitle}. The layout is organized around the three study
                  hypotheses, with dataset context kept compact and all headline numbers grounded in the
                  project outputs.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {DASHBOARD_DATA.overview.metrics.map((metric) => (
                  <MetricCard key={metric.label} label={metric.label} value={metric.value} />
                ))}
              </div>
            </div>
          </motion.div>
        </section>

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <Section id="context" eyebrow="Context" title="Dataset and experiment frame">
            <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
              <div className="panel p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-xl font-semibold">Filter funnel</h3>
                  <div className="text-sm text-[var(--muted)]">{DASHBOARD_DATA.dataset.dateRange}</div>
                </div>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={DASHBOARD_DATA.dataset.funnel} layout="vertical" margin={{ top: 8, right: 16, left: 10, bottom: 8 }}>
                      <CartesianGrid strokeDasharray="2 6" stroke={COLORS.line} horizontal={false} />
                      <XAxis type="number" tick={{ fill: COLORS.muted, fontSize: 12 }} tickFormatter={(value) => `${Math.round(value / 1000)}k`} />
                      <YAxis dataKey="label" type="category" width={128} tick={{ fill: COLORS.ink, fontSize: 12 }} />
                      <Tooltip formatter={(value) => (typeof value === 'number' ? value.toLocaleString() : `${value ?? ''}`)} />
                      <Bar dataKey="value" radius={[0, 12, 12, 0]} fill={COLORS.gold} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="panel p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-xl font-semibold">Where events concentrate</h3>
                  <div className="text-sm text-[var(--muted)]">Top oblast counts</div>
                </div>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={DASHBOARD_DATA.dataset.topOblasts} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
                      <CartesianGrid strokeDasharray="2 6" stroke={COLORS.line} vertical={false} />
                      <XAxis dataKey="label" tick={{ fill: COLORS.ink, fontSize: 11 }} interval={0} angle={-18} textAnchor="end" height={56} />
                      <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} tickFormatter={(value) => `${Math.round(value / 1000)}k`} />
                      <Tooltip formatter={(value) => (typeof value === 'number' ? value.toLocaleString() : `${value ?? ''}`)} />
                      <Bar dataKey="value" radius={[12, 12, 0, 0]} fill={COLORS.teal} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="mt-6 grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
              <div className="grid gap-4 sm:grid-cols-2">
                <InsightCard label="Event type mix" value="99.2% state-based" detail="0.8% one-sided violence" />
                <InsightCard label="Fatality skew" value={`Median ${DASHBOARD_DATA.dataset.fatalities.median}`} detail={`99th pct ${DASHBOARD_DATA.dataset.fatalities.p99}, max ${DASHBOARD_DATA.dataset.fatalities.max.toLocaleString()}`} />
                {DASHBOARD_DATA.dataset.quality.map((item) => (
                  <InsightCard key={item.label} label={item.label} value={item.value} />
                ))}
              </div>

              <div className="panel p-6">
                <div className="grid gap-4 md:grid-cols-2">
                  {DASHBOARD_DATA.dataset.featureSets.map((featureSet) => (
                    <div key={featureSet.id} className="rounded-3xl border border-[var(--line)] bg-white/70 p-5">
                      <div className="text-xs uppercase tracking-[0.22em] text-[var(--muted)]">{featureSet.id}</div>
                      <div className="mt-2 text-xl font-semibold">{featureSet.label}</div>
                      <div className="mt-3 text-sm leading-6 text-[var(--muted)]">{featureSet.detail}</div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 grid gap-3 sm:grid-cols-3">
                  {DASHBOARD_DATA.cells.map((cell) => (
                    <div key={cell.key} className="rounded-3xl border border-[var(--line)] bg-white/70 p-4">
                      <div className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">
                        {cell.conditionLabel} / {cell.featureSet}
                      </div>
                      <div className="mt-2 text-2xl font-semibold">{fmt(cell.silhouetteMedian, 3)}</div>
                      <div className="mt-1 text-sm text-[var(--muted)]">Median silhouette</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Section>

          <Section id="h1" eyebrow="H1" title="Human refinement vs baseline under F2">
            <HypothesisHeader
              title={DASHBOARD_DATA.h1.title}
              statement={DASHBOARD_DATA.h1.statement}
              status={DASHBOARD_DATA.h1.status}
              note={`Median Δ(B−A) = ${fmt(DASHBOARD_DATA.h1.medianDelta, 4)} with 95% bootstrap CI [${fmt(DASHBOARD_DATA.h1.ci95[0], 4)}, ${fmt(DASHBOARD_DATA.h1.ci95[1], 4)}].`}
            />

            <div className="grid gap-4 md:grid-cols-4">
              <InsightCard label="Median delta" value={fmt(DASHBOARD_DATA.h1.medianDelta, 4)} detail="Silhouette, B − A on F2" />
              <InsightCard label="95% CI" value={`${fmt(DASHBOARD_DATA.h1.ci95[0], 3)} to ${fmt(DASHBOARD_DATA.h1.ci95[1], 3)}`} />
              <InsightCard label="Seed split" value={`${DASHBOARD_DATA.h1.positiveSeeds} / ${DASHBOARD_DATA.h1.negativeSeeds} / ${DASHBOARD_DATA.h1.zeroSeeds}`} detail="positive / negative / zero" />
              <InsightCard label="Mean delta" value={fmt(DASHBOARD_DATA.h1.meanDelta, 3)} />
            </div>

            <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
              <div className="panel p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-xl font-semibold">Paired seed-level F2 deltas</h3>
                  <div className="text-sm text-[var(--muted)]">Human and oracle deltas vs baseline</div>
                </div>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={DASHBOARD_DATA.h1.pairedDeltas} margin={{ top: 12, right: 16, left: 0, bottom: 6 }}>
                      <CartesianGrid strokeDasharray="2 6" stroke={COLORS.line} vertical={false} />
                      <XAxis dataKey="seed" tick={{ fill: COLORS.ink, fontSize: 11 }} />
                      <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} domain={[-0.35, 0.15]} />
                      <Tooltip formatter={(value) => tooltipNumber(value, 4)} />
                      <Legend />
                      <ReferenceLine y={0} stroke={COLORS.ink} strokeOpacity={0.45} />
                      <Bar dataKey="humanDelta" name="Human (B − A)" radius={[6, 6, 0, 0]} fill={COLORS.teal} />
                      <Bar dataKey="oracleDelta" name="Oracle (C − A)" radius={[6, 6, 0, 0]} fill={COLORS.gold} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="panel p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-xl font-semibold">Final F2 medians by condition</h3>
                  <div className="text-sm text-[var(--muted)]">Silhouette</div>
                </div>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={f2Cells} margin={{ top: 12, right: 16, left: 0, bottom: 6 }}>
                      <CartesianGrid strokeDasharray="2 6" stroke={COLORS.line} vertical={false} />
                      <XAxis dataKey="conditionLabel" tick={{ fill: COLORS.ink, fontSize: 12 }} interval={0} angle={-10} textAnchor="end" height={50} />
                      <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} domain={[0.84, 0.91]} />
                      <Tooltip formatter={(value) => tooltipNumber(value, 4)} />
                      <Bar dataKey="silhouetteMedian" radius={[12, 12, 0, 0]}>
                        {f2Cells.map((cell) => (
                          <Cell
                            key={cell.key}
                            fill={cell.condition === 'B' ? COLORS.teal : cell.condition === 'C' ? COLORS.gold : COLORS.slate}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="mt-6 panel p-6">
              <div className="mb-4 flex items-center justify-between">
                <h3 className="text-xl font-semibold">Refinement trajectory under F2</h3>
                <div className="text-sm text-[var(--muted)]">Median silhouette by turn</div>
              </div>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={DASHBOARD_DATA.trajectories.filter((row) => row.featureSet === 'F2')}
                    margin={{ top: 12, right: 16, left: 0, bottom: 6 }}
                  >
                    <CartesianGrid strokeDasharray="2 6" stroke={COLORS.line} vertical={false} />
                    <XAxis dataKey="turn" tick={{ fill: COLORS.ink, fontSize: 12 }} />
                    <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} domain={[0.82, 0.9]} />
                    <Tooltip formatter={(value) => tooltipNumber(value, 4)} />
                    <Legend />
                    <Line type="monotone" dataKey="humanMedian" name="Human" stroke={COLORS.teal} strokeWidth={3} dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="oracleMedian" name="Oracle" stroke={COLORS.gold} strokeWidth={3} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Section>

          <Section id="h2" eyebrow="H2" title="Does the richer feature set help refinement more?">
            <HypothesisHeader
              title={DASHBOARD_DATA.h2.title}
              statement={DASHBOARD_DATA.h2.statement}
              status={DASHBOARD_DATA.h2.status}
              note={`Feature-set advantage median = ${fmt(DASHBOARD_DATA.h2.featureAdvantageMedian, 4)} with 95% CI [${fmt(DASHBOARD_DATA.h2.featureAdvantageCi95[0], 4)}, ${fmt(DASHBOARD_DATA.h2.featureAdvantageCi95[1], 4)}].`}
            />

            <div className="grid gap-4 md:grid-cols-3">
              <InsightCard label="F1 median delta" value={fmt(DASHBOARD_DATA.h2.f1MedianDelta, 4)} detail={`95% CI ${fmt(DASHBOARD_DATA.h2.f1Ci95[0], 3)} to ${fmt(DASHBOARD_DATA.h2.f1Ci95[1], 3)}`} />
              <InsightCard label="F2 median delta" value={fmt(DASHBOARD_DATA.h2.f2MedianDelta, 4)} detail={`95% CI ${fmt(DASHBOARD_DATA.h2.f2Ci95[0], 3)} to ${fmt(DASHBOARD_DATA.h2.f2Ci95[1], 3)}`} />
              <InsightCard label="F2 − F1 median gap" value={fmt(DASHBOARD_DATA.h2.featureAdvantageMedian, 4)} detail={`95% CI ${fmt(DASHBOARD_DATA.h2.featureAdvantageCi95[0], 3)} to ${fmt(DASHBOARD_DATA.h2.featureAdvantageCi95[1], 3)}`} />
            </div>

            <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
              <div className="panel p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-xl font-semibold">Seed-level improvement by feature set</h3>
                  <div className="text-sm text-[var(--muted)]">Human refinement only</div>
                </div>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={DASHBOARD_DATA.h2.deltas} margin={{ top: 12, right: 16, left: 0, bottom: 6 }}>
                      <CartesianGrid strokeDasharray="2 6" stroke={COLORS.line} vertical={false} />
                      <XAxis dataKey="seed" tick={{ fill: COLORS.ink, fontSize: 11 }} />
                      <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} domain={[-0.35, 0.15]} />
                      <Tooltip formatter={(value) => tooltipNumber(value, 4)} />
                      <Legend />
                      <ReferenceLine y={0} stroke={COLORS.ink} strokeOpacity={0.45} />
                      <Line type="monotone" dataKey="F1" stroke={COLORS.slate} strokeWidth={3} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="F2" stroke={COLORS.teal} strokeWidth={3} dot={{ r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="panel p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-xl font-semibold">Condition medians across F1 and F2</h3>
                  <div className="text-sm text-[var(--muted)]">Silhouette</div>
                </div>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={groupedCells} margin={{ top: 12, right: 16, left: 0, bottom: 6 }}>
                      <CartesianGrid strokeDasharray="2 6" stroke={COLORS.line} vertical={false} />
                      <XAxis dataKey="condition" tick={{ fill: COLORS.ink, fontSize: 12 }} />
                      <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} domain={[0.84, 0.91]} />
                      <Tooltip formatter={(value) => tooltipNumber(value, 4)} />
                      <Legend />
                      <Bar dataKey="F1" radius={[8, 8, 0, 0]} fill={COLORS.slate} />
                      <Bar dataKey="F2" radius={[8, 8, 0, 0]} fill={COLORS.gold} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </Section>

          <Section id="h3" eyebrow="H3" title="Oracle validity against human judgment">
            <HypothesisHeader
              title={DASHBOARD_DATA.h3.title}
              statement={DASHBOARD_DATA.h3.statement}
              status={DASHBOARD_DATA.h3.status}
              note={`Human reliability is low (α = ${fmt(DASHBOARD_DATA.h3.alpha, 2)}) and the swap diagnostic shows ${DASHBOARD_DATA.h3.sameDisplayedLabelAfterSwap} same-label responses versus ${DASHBOARD_DATA.h3.sameUnderlyingAfterSwap} same-underlying responses.`}
            />

            <div className="grid gap-4 md:grid-cols-4">
              <InsightCard label="Krippendorff alpha" value={fmt(DASHBOARD_DATA.h3.alpha, 2)} />
              <InsightCard label="Original-order agreement" value={`${Math.round(DASHBOARD_DATA.h3.originalAgreement * 100)}%`} detail="13 / 20 pairs" />
              <InsightCard label="Cohen kappa" value={fmt(DASHBOARD_DATA.h3.kappa, 2)} />
              <InsightCard label="Bias-flagged pairs" value={`${DASHBOARD_DATA.h3.positionBiasPairs} / 20`} />
            </div>

            <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_1fr]">
              <div className="panel p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-xl font-semibold">Human majority choices in H3 pair families</h3>
                  <div className="text-sm text-[var(--muted)]">5 pairs per family</div>
                </div>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={DASHBOARD_DATA.h3.groups} margin={{ top: 12, right: 16, left: 0, bottom: 6 }}>
                      <CartesianGrid strokeDasharray="2 6" stroke={COLORS.line} vertical={false} />
                      <XAxis dataKey="label" tick={{ fill: COLORS.ink, fontSize: 12 }} />
                      <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} domain={[0, 5]} />
                      <Tooltip formatter={(value) => `${value ?? ''} pairs`} />
                      <Legend />
                      <Bar dataKey="leftCount" name="Left label count" radius={[8, 8, 0, 0]} fill={COLORS.slate} />
                      <Bar dataKey="rightCount" name="Right label count" radius={[8, 8, 0, 0]} fill={COLORS.gold} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="panel p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-xl font-semibold">Swap diagnostic</h3>
                  <div className="text-sm text-[var(--muted)]">Displayed-label bias check</div>
                </div>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={h3BiasData} layout="vertical" margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
                      <CartesianGrid strokeDasharray="2 6" stroke={COLORS.line} horizontal={false} />
                      <XAxis type="number" tick={{ fill: COLORS.muted, fontSize: 12 }} domain={[0, 20]} />
                      <YAxis dataKey="label" type="category" width={170} tick={{ fill: COLORS.ink, fontSize: 12 }} />
                      <Tooltip formatter={(value) => `${value ?? ''} pairs`} />
                      <Bar dataKey="value" radius={[0, 12, 12, 0]}>
                        {h3BiasData.map((row) => (
                          <Cell key={row.label} fill={row.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </Section>

          <footer className="border-t border-[var(--line)] py-10 text-sm text-[var(--muted)]">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>Design document: `docs/dashboard_design.md`</div>
              <div className="max-w-3xl">
                Sources: {DASHBOARD_DATA.sources.join(' • ')}
              </div>
            </div>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
