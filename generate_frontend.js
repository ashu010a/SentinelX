const fs = require('fs');
const path = require('path');

const baseDir = path.join(__dirname, 'frontend');

const files = {
  'package.json': `{
  "name": "sentinelx-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.2.14",
    "react": "^18",
    "react-dom": "^18",
    "@heroicons/react": "^2.1.5",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.0.1",
    "postcss": "^8",
    "tailwindcss": "^3.4.1",
    "eslint": "^8",
    "eslint-config-next": "14.2.14"
  }
}`,
  'next.config.mjs': `/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://backend:8000/api/:path*',
      },
    ];
  },
};
export default nextConfig;`,
  'tsconfig.json': `{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}`,
  'tailwind.config.ts': `import type { Config } from "tailwindcss";
const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
export default config;`,
  'postcss.config.mjs': `/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
export default config;`,
  'app/globals.css': `@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: #0a0a0f;
  --foreground: #e5e7eb;
  --card: #111118;
  --card-border: #1e1e2e;
  --primary: #6366f1;
  --primary-hover: #818cf8;
  --critical: #ef4444;
  --high: #f97316;
  --medium: #eab308;
  --low: #22c55e;
  --info: #3b82f6;
}

body {
  background: var(--background);
  color: var(--foreground);
}`,
  'components/layout/Sidebar.tsx': `'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ShieldCheckIcon, HomeIcon, FolderIcon, ServerIcon, BugAntIcon, PlayIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Projects', href: '/projects', icon: FolderIcon },
  { name: 'Assets', href: '/assets', icon: ServerIcon },
  { name: 'Vulnerabilities', href: '/vulnerabilities', icon: BugAntIcon },
  { name: 'Scans', href: '/scans', icon: PlayIcon },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <div className="flex h-full w-64 flex-col bg-[#0a0a0f] border-r border-[#1e1e2e]">
      <div className="flex h-16 shrink-0 items-center px-6 border-b border-[#1e1e2e]">
        <ShieldCheckIcon className="h-8 w-8 text-[#6366f1]" />
        <span className="ml-4 text-xl font-bold text-white">SentinelX</span>
      </div>
      <nav className="flex flex-1 flex-col px-4 py-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/' && pathname?.startsWith(item.href));
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                isActive ? 'bg-[#6366f1]/10 text-[#6366f1]' : 'text-gray-400 hover:text-white hover:bg-[#111118]',
                'group flex items-center rounded-md px-3 py-2 text-sm font-medium'
              )}
            >
              <item.icon className={clsx(isActive ? 'text-[#6366f1]' : 'text-gray-400 group-hover:text-white', 'mr-3 h-5 w-5 flex-shrink-0')} />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}`,
  'app/layout.tsx': `import './globals.css';
import { Inter } from 'next/font/google';
import Sidebar from '@/components/layout/Sidebar';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'SentinelX',
  description: 'Attack Surface Management Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={\`\${inter.className} h-screen flex overflow-hidden bg-[var(--background)] text-[var(--foreground)]\`}>
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-8">
          {children}
        </main>
      </body>
    </html>
  );
}`,
  'components/ui/Card.tsx': `export default function Card({ title, children, className = '' }: { title?: string, children: React.ReactNode, className?: string }) {
  return (
    <div className={\`bg-[#111118] border border-[#1e1e2e] rounded-xl p-6 \${className}\`}>
      {title && <h3 className="text-lg font-medium mb-4 text-white">{title}</h3>}
      {children}
    </div>
  );
}`,
  'components/ui/Badge.tsx': `import clsx from 'clsx';
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
}`,
  'app/page.tsx': `'use client';
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
                  <div className={\`\${item.color} h-2 rounded-full\`} style={{ width: \`\${(item.count/89)*100}%\` }}></div>
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
}`,
  'app/projects/page.tsx': `'use client';
export default function Projects() { return <div className="text-white"><h1 className="text-2xl font-bold mb-4">Projects</h1><p className="text-gray-400">List of projects goes here.</p></div>; }`,
  'app/projects/[id]/page.tsx': `'use client';
export default function ProjectDetail() { return <div className="text-white"><h1 className="text-2xl font-bold mb-4">Project Details</h1></div>; }`,
  'app/assets/page.tsx': `'use client';
export default function Assets() { return <div className="text-white"><h1 className="text-2xl font-bold mb-4">Assets</h1><p className="text-gray-400">Asset inventory goes here.</p></div>; }`,
  'app/vulnerabilities/page.tsx': `'use client';
export default function Vulnerabilities() { return <div className="text-white"><h1 className="text-2xl font-bold mb-4">Vulnerabilities</h1><p className="text-gray-400">Vulnerabilities list goes here.</p></div>; }`,
  'app/scans/page.tsx': `'use client';
export default function Scans() { return <div className="text-white"><h1 className="text-2xl font-bold mb-4">Scans</h1><p className="text-gray-400">Scan history goes here.</p></div>; }`,
  'Dockerfile': `FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]`
};

for (const [relPath, content] of Object.entries(files)) {
  const fullPath = path.join(baseDir, relPath);
  fs.mkdirSync(path.dirname(fullPath), { recursive: true });
  fs.writeFileSync(fullPath, content.trim() + '\\n', 'utf8');
}
console.log('Frontend built successfully!');
