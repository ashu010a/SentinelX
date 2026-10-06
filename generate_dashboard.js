const fs = require('fs');
const path = require('path');

const baseDir = path.join(__dirname, 'frontend');

const files = {
  'components/dashboard/StatsCards.tsx': `import Card from '@/components/ui/Card';
import { FolderIcon, ServerIcon, BugAntIcon, PlayIcon } from '@heroicons/react/24/outline';
import { DashboardStats } from '@/lib/api';

export default function StatsCards({ stats }: { stats?: DashboardStats }) {
  if (!stats) return null;
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card className="flex items-center space-x-4">
        <div className="p-3 bg-[#6366f1]/10 rounded-lg"><FolderIcon className="w-6 h-6 text-[#6366f1]" /></div>
        <div><p className="text-gray-400 text-sm">Total Projects</p><p className="text-2xl font-semibold text-white">{stats.projects}</p></div>
      </Card>
      <Card className="flex items-center space-x-4">
        <div className="p-3 bg-blue-500/10 rounded-lg"><ServerIcon className="w-6 h-6 text-blue-500" /></div>
        <div><p className="text-gray-400 text-sm">Total Assets</p><p className="text-2xl font-semibold text-white">{stats.assets}</p></div>
      </Card>
      <Card className="flex items-center space-x-4">
        <div className="p-3 bg-green-500/10 rounded-lg"><PlayIcon className="w-6 h-6 text-green-500" /></div>
        <div><p className="text-gray-400 text-sm">Active Scans</p><p className="text-2xl font-semibold text-white">{stats.active_scans}</p></div>
      </Card>
      <Card className="flex items-center space-x-4">
        <div className="p-3 bg-red-500/10 rounded-lg"><BugAntIcon className="w-6 h-6 text-red-500" /></div>
        <div><p className="text-gray-400 text-sm">Vulnerabilities</p><p className="text-2xl font-semibold text-white">{stats.vulnerabilities}</p></div>
      </Card>
    </div>
  );
}`,
  'components/dashboard/RiskDistribution.tsx': `import Card from '@/components/ui/Card';
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
              <div className={\`\${item.color} h-2 rounded-full\`} style={{ width: \`\${(item.count / total) * 100}%\` }}></div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}`,
  'components/dashboard/RecentAssets.tsx': `import Card from '@/components/ui/Card';
import Table from '@/components/ui/Table';
import Badge from '@/components/ui/Badge';
import { Asset } from '@/lib/api';

export default function RecentAssets({ assets }: { assets: Asset[] }) {
  const columns = [
    { key: 'hostname', label: 'Hostname' },
    { key: 'ip', label: 'IP' },
    { key: 'type', label: 'Type' },
    { key: 'risk_score', label: 'Risk', render: (val: number) => <Badge severity={val > 80 ? 'critical' : val > 60 ? 'high' : val > 40 ? 'medium' : 'low'} /> }
  ];
  return (
    <Card title="Recent Assets">
      <Table columns={columns} data={assets} />
    </Card>
  );
}`,
  'components/dashboard/RecentVulnerabilities.tsx': `import Card from '@/components/ui/Card';
import Table from '@/components/ui/Table';
import Badge from '@/components/ui/Badge';
import { Vulnerability } from '@/lib/api';

export default function RecentVulnerabilities({ vulns }: { vulns: Vulnerability[] }) {
  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'severity', label: 'Severity', render: (val: string) => <Badge severity={val as any} /> },
    { key: 'status', label: 'Status' }
  ];
  return (
    <Card title="Recent Vulnerabilities">
      <Table columns={columns} data={vulns} />
    </Card>
  );
}`
};

for (const [relPath, content] of Object.entries(files)) {
  const fullPath = path.join(baseDir, relPath);
  fs.mkdirSync(path.dirname(fullPath), { recursive: true });
  fs.writeFileSync(fullPath, content.trim() + '\\n', 'utf8');
}
console.log('Dashboard components built successfully!');
