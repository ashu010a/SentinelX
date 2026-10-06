'use client';
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
}
