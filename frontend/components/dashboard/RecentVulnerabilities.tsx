import Card from '@/components/ui/Card';
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
}
