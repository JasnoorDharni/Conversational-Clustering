import { motion } from 'framer-motion';
import { DASHBOARD_DATA } from '../data/dashboardData';

export function FeatureDecisionTable() {
  const { featureDecisions } = DASHBOARD_DATA.eda;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="overflow-x-auto"
    >
      <table className="w-full">
        <thead>
          <tr className="border-b border-navy-200">
            <th className="text-left py-3 px-4 text-sm font-semibold text-navy-900">Feature</th>
            <th className="text-left py-3 px-4 text-sm font-semibold text-navy-900">Decision</th>
            <th className="text-left py-3 px-4 text-sm font-semibold text-navy-900">Rationale</th>
          </tr>
        </thead>
        <tbody>
          {featureDecisions.map((item, index) => (
            <motion.tr
              key={item.feature}
              initial={{ opacity: 0, x: -10 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="border-b border-navy-50 hover:bg-navy-50/50 transition-colors"
            >
              <td className="py-3 px-4 text-sm font-medium text-navy-800">
                {item.feature}
              </td>
              <td className="py-3 px-4">
                <span className={`badge badge-${item.decision}`}>
                  {item.decision}
                </span>
              </td>
              <td className="py-3 px-4 text-sm text-navy-600 max-w-md">
                {item.reason}
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  );
}
