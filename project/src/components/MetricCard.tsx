import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  value: number | string;
  label: string;
  icon?: LucideIcon;
  sublabel?: string;
  delay?: number;
}

export function MetricCard({ value, label, icon: Icon, sublabel, delay = 0 }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="card p-6 text-center"
    >
      {Icon && (
        <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-navy-50 mb-3">
          <Icon className="w-5 h-5 text-navy-600" />
        </div>
      )}
      <div className="metric-value mb-1">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      <div className="metric-label">{label}</div>
      {sublabel && (
        <div className="text-xs text-navy-400 mt-1">{sublabel}</div>
      )}
    </motion.div>
  );
}
