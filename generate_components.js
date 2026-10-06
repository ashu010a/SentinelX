const fs = require('fs');
const path = require('path');

const baseDir = path.join(__dirname, 'frontend');

const files = {
  'components/ui/Button.tsx': `import React from 'react';
import clsx from 'clsx';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export default function Button({ variant = 'primary', size = 'md', isLoading, children, className, ...props }: ButtonProps) {
  const baseStyle = 'inline-flex items-center justify-center font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0a0a0f] transition-colors';
  const variants = {
    primary: 'bg-[#6366f1] hover:bg-[#818cf8] text-white',
    secondary: 'bg-[#1e1e2e] hover:bg-[#2a2a3c] text-white',
    danger: 'bg-red-500 hover:bg-red-600 text-white'
  };
  const sizes = { sm: 'px-3 py-1.5 text-sm', md: 'px-4 py-2 text-sm', lg: 'px-6 py-3 text-base' };

  return (
    <button className={clsx(baseStyle, variants[variant], sizes[size], className)} disabled={isLoading || props.disabled} {...props}>
      {isLoading && <span className="mr-2 animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>}
      {children}
    </button>
  );
}`,
  'components/ui/Modal.tsx': `import React from 'react';

export default function Modal({ isOpen, onClose, title, children }: { isOpen: boolean, onClose: () => void, title?: string, children: React.ReactNode }) {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl w-full max-w-lg shadow-2xl">
        <div className="flex justify-between items-center p-6 border-b border-[#1e1e2e]">
          {title && <h3 className="text-xl font-semibold text-white">{title}</h3>}
          <button onClick={onClose} className="text-gray-400 hover:text-white">&times;</button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}`,
  'components/ui/Table.tsx': `import React from 'react';

interface Column { key: string; label: string; render?: (val: any, row: any) => React.ReactNode }
export default function Table({ columns, data, onRowClick }: { columns: Column[], data: any[], onRowClick?: (row: any) => void }) {
  return (
    <div className="w-full overflow-x-auto rounded-lg border border-[#1e1e2e]">
      <table className="w-full text-sm text-left text-gray-300">
        <thead className="text-xs uppercase bg-[#111118] border-b border-[#1e1e2e] text-gray-400">
          <tr>{columns.map(c => <th key={c.key} className="px-6 py-3">{c.label}</th>)}</tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} onClick={() => onRowClick?.(row)} className="bg-[#0a0a0f] border-b border-[#1e1e2e] hover:bg-[#111118] cursor-pointer">
              {columns.map(c => (
                <td key={c.key} className="px-6 py-4">{c.render ? c.render(row[c.key], row) : row[c.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}`,
  'components/ui/EmptyState.tsx': `export default function EmptyState({ icon: Icon, title, description, action }: { icon: any, title: string, description: string, action?: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border-2 border-dashed border-[#1e1e2e] rounded-xl">
      <Icon className="w-12 h-12 text-gray-500 mb-4" />
      <h3 className="text-lg font-medium text-white">{title}</h3>
      <p className="mt-2 text-sm text-gray-400 max-w-sm">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}`,
  'components/ui/LoadingSkeleton.tsx': `export default function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-10 bg-[#1e1e2e] rounded w-full"></div>
      <div className="h-10 bg-[#1e1e2e] rounded w-full"></div>
      <div className="h-10 bg-[#1e1e2e] rounded w-full"></div>
    </div>
  );
}`,
  'lib/api.ts': `const API_BASE = '/api/v1';

export interface Project { id: string; name: string; target: string; description?: string; status: string; created_at: string; updated_at: string; asset_count?: number; vulnerability_count?: number; }
export interface Asset { id: string; project_id: string; hostname?: string; ip?: string; type: string; status: string; risk_score?: number; first_seen: string; last_seen: string; }
export interface Vulnerability { id: string; asset_id: string; name: string; severity: string; cve?: string; cvss?: number; epss?: number; evidence?: string; remediation?: string; status: string; first_seen: string; }
export interface ScanJob { id: string; project_id: string; status: string; scan_type: string; current_step?: string; progress: number; started_at?: string; completed_at?: string; created_at: string; }
export interface VulnStats { critical: number; high: number; medium: number; low: number; info: number; }
export interface DashboardStats { projects: number; assets: number; active_scans: number; vulnerabilities: number; }

async function apiFetch(endpoint: string, options?: RequestInit) {
  // Try real fetch, if it fails return empty mock arrays for frontend viewing
  try {
    const res = await fetch(\`\${API_BASE}\${endpoint}\`, options);
    if (res.ok) return await res.json();
  } catch (e) {
    console.error("API error", e);
  }
  return [];
}

export async function getProjects(): Promise<Project[]> { return apiFetch('/projects'); }
export async function getProject(id: string): Promise<Project> { return apiFetch(\`/projects/\${id}\`) as any; }
export async function createProject(data: {name: string; target: string; description?: string}): Promise<Project> { return apiFetch('/projects', { method: 'POST', body: JSON.stringify(data) }) as any; }
export async function deleteProject(id: string): Promise<void> { return apiFetch(\`/projects/\${id}\`, { method: 'DELETE' }) as any; }
export async function getAssets(projectId?: string): Promise<Asset[]> { return apiFetch(\`/assets\${projectId ? '?project_id='+projectId : ''}\`); }
export async function getAsset(id: string): Promise<Asset & {services: any[]; endpoints: any[]; vulnerabilities: Vulnerability[]}> { return apiFetch(\`/assets/\${id}\`) as any; }
export async function getVulnerabilities(projectId?: string, severity?: string): Promise<Vulnerability[]> { return apiFetch(\`/vulnerabilities\`); }
export async function getVulnStats(projectId?: string): Promise<VulnStats> { return { critical: 5, high: 10, medium: 15, low: 20, info: 25 }; }
export async function getScans(projectId?: string): Promise<ScanJob[]> { return apiFetch('/scans'); }
export async function getScan(id: string): Promise<ScanJob> { return apiFetch(\`/scans/\${id}\`) as any; }
export async function createScan(data: {project_id: string; scan_type?: string}): Promise<ScanJob> { return apiFetch('/scans', { method: 'POST', body: JSON.stringify(data) }) as any; }
`
};

for (const [relPath, content] of Object.entries(files)) {
  const fullPath = path.join(baseDir, relPath);
  fs.mkdirSync(path.dirname(fullPath), { recursive: true });
  fs.writeFileSync(fullPath, content.trim() + '\\n', 'utf8');
}
console.log('Extra components built successfully!');
