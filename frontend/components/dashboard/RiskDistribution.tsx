import Card from '@/components/ui/Card';
import { VulnStats } from '@/lib/api';

export default function RiskDistribution({ stats }: { stats?: VulnStats }) {
  if (!stats) return null;
  const total = stats.critical + stats.high + stats.medium + stats.low + stats.info || 1;
  const data = [
    { label: 'Critical', count: stats.critical, color: 'bg-red-500' },
    { label: 'High', count: stats.high, color: 'bg-orange-500' },
    { label: 'Medium', count: stats.medium, color: 'bg-yellow-500' },
    { label: 'Low', count: stats.low, color: 'bg-green-500' },
    { label: 'Info', count: stats.info, color: 'bg-blue-500' }
  ];

  return (
    <Card title="Risk Distribution">
      <div className="space-y-4">
        {data.map(item => (
          <div key={item.label}>
            <div className="flex justify-between text-sm mb-1 text-gray-300">
              <span>{item.label}</span>
              <span>{item.count}</span>
            </div>
            <div className="w-full bg-[#1e1e2e] rounded-full h-2">
              <div className={`${item.color} h-2 rounded-full`} style={{ width: `${(item.count / total) * 100}%` }}></div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
