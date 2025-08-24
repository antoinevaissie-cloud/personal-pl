'use client';

import { cn } from '@/lib/utils';

export type TabKey = 'upload' | 'pl' | 'filters' | 'review';

interface TabNavigationProps {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
}

const tabs: { key: TabKey; label: string }[] = [
  { key: 'upload', label: 'Upload Statements' },
  { key: 'pl', label: 'P&L View' },
  { key: 'filters', label: 'Filters & Analysis' },
  { key: 'review', label: 'Review Log' },
];

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  return (
    <div className="bg-muted/40 p-1 rounded-full inline-flex">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onTabChange(tab.key)}
          className={cn(
            'tab-button',
            activeTab === tab.key && 'tab-button-active'
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}