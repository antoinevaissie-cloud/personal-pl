'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { UploadCard } from '@/components/upload/upload-card';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';

export function UploadTab() {
  const [selectedMonth] = useState(format(new Date(), 'yyyy-MM'));
  const [isCommitting, setIsCommitting] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleCommit = async () => {
    setIsCommitting(true);
    try {
      await api.commitImport({ period_month: selectedMonth });
      setRefreshKey(prev => prev + 1);
    } catch (error) {
      console.error('Failed to commit import:', error);
    } finally {
      setIsCommitting(false);
    }
  };

  const handleUploadComplete = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium">Upload Bank Statements</h2>
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">
            Period: {format(new Date(selectedMonth + '-01'), 'MMMM yyyy')}
          </span>
          <Button 
            onClick={handleCommit}
            disabled={isCommitting}
            variant="outline"
          >
            {isCommitting ? 'Committing...' : 'Commit Imports'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6" key={refreshKey}>
        <UploadCard
          bankName="Boursorama"
          bankType="Boursorama"
          currency="EUR"
          periodMonth={selectedMonth}
          onUploadComplete={handleUploadComplete}
        />
        <UploadCard
          bankName="BNP Paribas"
          bankType="BNP"
          currency="EUR"
          periodMonth={selectedMonth}
          onUploadComplete={handleUploadComplete}
        />
        <UploadCard
          bankName="Revolut"
          bankType="Revolut"
          currency="GBP"
          periodMonth={selectedMonth}
          onUploadComplete={handleUploadComplete}
        />
      </div>
    </div>
  );
}