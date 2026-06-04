import { motion } from 'framer-motion';
import { CheckCircle2 } from 'lucide-react';
import { DASHBOARD_DATA } from '../data/dashboardData';

export function ExperimentMatrix() {
  const { experimentStatus } = DASHBOARD_DATA;

  const conditions = [
    { id: 'A', label: 'A Baseline', sublabel: 'k-means' },
    { id: 'C', label: 'C Oracle', sublabel: 'refinement' }
  ];

  const featureSets = [
    { id: 'F1', label: 'F1 Location-only' },
    { id: 'F2', label: 'F2 EDA-informed full' }
  ];

  const getStatus = (conditionId: string, featureSetId: string) => {
    return experimentStatus.find(
      s => s.condition === conditionId && s.featureSet === featureSetId
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="card overflow-hidden"
    >
      <table className="w-full">
        <thead>
          <tr className="bg-navy-50">
            <th className="text-left py-4 px-6 text-sm font-semibold text-navy-900 w-40">
              Condition
            </th>
            {featureSets.map(fs => (
              <th key={fs.id} className="text-center py-4 px-6 text-sm font-semibold text-navy-900">
                {fs.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {conditions.map((cond, idx) => (
            <tr key={cond.id} className={idx === 0 ? 'border-b border-navy-100' : ''}>
              <td className="py-5 px-6">
                <div className="font-medium text-navy-900">{cond.label}</div>
                <div className="text-xs text-navy-500">{cond.sublabel}</div>
              </td>
              {featureSets.map(fs => {
                const status = getStatus(cond.id, fs.id);
                return (
                  <td key={fs.id} className="py-5 px-6 text-center">
                    {status?.status === 'complete' && (
                      <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-50 text-emerald-700">
                        <CheckCircle2 className="w-4 h-4" />
                        <span className="text-sm font-medium">
                          {status.complete}/{status.target}
                        </span>
                      </div>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      <div className="px-6 py-4 bg-navy-50/50 border-t border-navy-100">
        <div className="flex flex-wrap gap-4 text-xs text-navy-600">
          <span>K fixed at 8</span>
          <span className="text-navy-300">|</span>
          <span>30 seeds per cell</span>
          <span className="text-navy-300">|</span>
          <span>Condition C uses 5 refinement turns</span>
          <span className="text-navy-300">|</span>
          <span>All records logged</span>
        </div>
      </div>
    </motion.div>
  );
}
