import Card from '@/components/ui/Card';
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
}
