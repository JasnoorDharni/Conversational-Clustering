import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { AlertCircle, CheckCircle2, Info } from 'lucide-react';

interface FindingCardProps {
  title: string;
  children: ReactNode;
  type?: 'success' | 'warning' | 'info';
}

export function FindingCard({ title, children, type = 'info' }: FindingCardProps) {
  const iconMap = {
    success: CheckCircle2,
    warning: AlertCircle,
    info: Info
  };

  const colorMap = {
    success: { bg: 'bg-emerald-50', border: 'border-emerald-200', icon: 'text-emerald-600', text: 'text-emerald-800' },
    warning: { bg: 'bg-amber-50', border: 'border-amber-200', icon: 'text-amber-600', text: 'text-amber-800' },
    info: { bg: 'bg-navy-50', border: 'border-navy-200', icon: 'text-navy-600', text: 'text-navy-800' }
  };

  const Icon = iconMap[type];
  const colors = colorMap[type];

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4 }}
      className={`${colors.bg} ${colors.border} border rounded-lg p-4`}
    >
      <div className="flex gap-3">
        <Icon className={`w-5 h-5 ${colors.icon} flex-shrink-0 mt-0.5`} />
        <div>
          <h4 className={`font-semibold ${colors.text} mb-1`}>{title}</h4>
          <p className="text-sm text-navy-600">{children}</p>
        </div>
      </div>
    </motion.div>
  );
}
