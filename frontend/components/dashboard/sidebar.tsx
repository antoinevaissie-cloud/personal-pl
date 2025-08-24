'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { BarChart3, DollarSign, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  {
    title: 'P&L and Budgeting',
    href: '/dashboard',
    icon: BarChart3,
  },
  {
    title: 'Cashflow',
    href: '/dashboard/cashflow',
    icon: DollarSign,
  },
  {
    title: 'Investment',
    href: '/dashboard/investment',
    icon: TrendingUp,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[232px] bg-white h-screen border-r border-border flex flex-col">
      <div className="p-6">
        <h1 className="text-lg font-semibold">Personal Finance</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Business accounting for personal use
        </p>
      </div>
      
      <nav className="flex-1 px-4">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || 
                           (item.href === '/dashboard' && pathname.startsWith('/dashboard') && item.href !== pathname);
            
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'sidebar-nav-item',
                    isActive && 'sidebar-nav-item-active'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.title}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}