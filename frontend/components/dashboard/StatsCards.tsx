import Card from '@/components/ui/Card';
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
}
