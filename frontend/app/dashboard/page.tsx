'use client';

import { useState } from 'react';
import { TabNavigation, TabKey } from '@/components/dashboard/tab-navigation';
import { UploadTab } from '@/components/tabs/upload-tab';
import { PLViewTab } from '@/components/tabs/pl-view-tab';
import { FiltersTab } from '@/components/tabs/filters-tab';
import { ReviewLogTab } from '@/components/tabs/review-log-tab';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('upload');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold mb-2">P&L and Budgeting</h1>
        <p className="text-muted-foreground">
          Upload and analyze your account statements with business accounting principles
        </p>
      </div>

      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="mt-6">
        {activeTab === 'upload' && <UploadTab />}
        {activeTab === 'pl' && <PLViewTab />}
        {activeTab === 'filters' && <FiltersTab />}
        {activeTab === 'review' && <ReviewLogTab />}
      </div>
    </div>
  );
}