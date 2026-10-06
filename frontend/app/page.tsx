'use client';
import { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';

export default function Dashboard() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) return <div className="animate-pulse space-y-6"><div className="h-32 bg-[#111118] rounded-xl"></div></div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[{l: 'Total Projects', n: 12}, {l: 'Total Assets', n: 145}, {l: 'Active Scans', n: 3}, {l: 'Vulnerabilities', n: 89}].map(x => (
          <Card key={x.l} className="flex items-center space-x-4">
            <div>
              <p className="text-gray-400 text-sm">{x.l}</p>
              <p className="text-2xl font-semibold text-white">{x.n}</p>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Risk Distribution">
          <div className="space-y-4">
            {[{label: 'Critical', count: 12, color: 'bg-red-500'}, {label: 'High', count: 24, color: 'bg-orange-500'}, {label: 'Medium', count: 35, color: 'bg-yellow-500'}, {label: 'Low', count: 18, color: 'bg-green-500'}].map(item => (
              <div key={item.label}>
                <div className="flex justify-between text-sm mb-1 text-gray-300">
                  <span>{item.label}</span>
                  <span>{item.count}</span>
                </div>
                <div className="w-full bg-[#1e1e2e] rounded-full h-2">
                  <div className={`${item.color} h-2 rounded-full`} style={{ width: `${(item.count/89)*100}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </Card>
        <Card title="Recent Vulnerabilities">
           <div className="space-y-4">
            <div className="flex justify-between items-center pb-2 border-b border-[#1e1e2e]">
                <span className="font-medium text-gray-200">SQL Injection</span>
                <Badge severity="critical" />
            </div>
            <div className="flex justify-between items-center pb-2 border-b border-[#1e1e2e]">
                <span className="font-medium text-gray-200">XSS Reflected</span>
                <Badge severity="high" />
            </div>
           </div>
        </Card>
      </div>
    </div>
  );
}
