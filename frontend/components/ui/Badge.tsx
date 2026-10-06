import clsx from 'clsx';
export default function Badge({ severity, className = '' }: { severity: 'critical' | 'high' | 'medium' | 'low' | 'info', className?: string }) {
  const colors = {
    critical: 'bg-red-500/10 text-red-500 border-red-500/20',
    high: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
    medium: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    low: 'bg-green-500/10 text-green-500 border-green-500/20',
    info: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  };
  return (
    <span className={clsx('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize', colors[severity], className)}>
      {severity}
    </span>
  );
}
