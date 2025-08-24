'use client';

import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChevronRight, TrendingUp, TrendingDown } from 'lucide-react';
import { api } from '@/lib/api';
import { PLSummaryResponse, CategoryRow } from '@/types/api.types';
import { cn } from '@/lib/utils';

export function PLViewTab() {
  const [selectedMonth] = useState(format(new Date(), 'yyyy-MM'));
  const [data, setData] = useState<PLSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadPLData();
  }, [selectedMonth]);

  const loadPLData = async () => {
    setIsLoading(true);
    try {
      const response = await api.getPLSummary({
        month: selectedMonth,
        exclude_transfers: true,
        currency_view: 'native'
      });
      setData(response);
    } catch (error) {
      console.error('Failed to load P&L data:', error);
      setData(null);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${Math.abs(value).toFixed(1)}%`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading P&L data...</p>
      </div>
    );
  }

  if (!data || data.rows.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <h3 className="text-lg font-medium">P&L Statement View</h3>
        <p className="text-muted-foreground">No statements uploaded yet</p>
        <p className="text-sm text-muted-foreground">
          Upload account statements in the Upload tab to view P&L statements here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium">P&L Statement</h2>
        <span className="text-sm text-muted-foreground">
          {format(new Date(selectedMonth + '-01'), 'MMMM yyyy')}
        </span>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Income
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(data.summary.income)}</div>
            {data.summary.delta_mom !== 0 && (
              <div className={cn(
                "flex items-center gap-1 text-sm mt-1",
                data.summary.delta_mom > 0 ? "text-green-600" : "text-red-600"
              )}>
                {data.summary.delta_mom > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {formatPercentage(data.summary.delta_mom)}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Expenses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(Math.abs(data.summary.expenses))}</div>
            {data.summary.delta_expenses !== 0 && (
              <div className={cn(
                "flex items-center gap-1 text-sm mt-1",
                data.summary.delta_expenses < 0 ? "text-green-600" : "text-red-600"
              )}>
                {data.summary.delta_expenses < 0 ? <TrendingDown className="w-3 h-3" /> : <TrendingUp className="w-3 h-3" />}
                {formatPercentage(data.summary.delta_expenses)}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Net Income
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={cn(
              "text-2xl font-bold",
              data.summary.net > 0 ? "text-green-600" : "text-red-600"
            )}>
              {formatCurrency(data.summary.net)}
            </div>
            {data.summary.delta_net !== 0 && (
              <div className={cn(
                "flex items-center gap-1 text-sm mt-1",
                data.summary.delta_net > 0 ? "text-green-600" : "text-red-600"
              )}>
                {data.summary.delta_net > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {formatPercentage(data.summary.delta_net)}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Savings Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatPercentage(data.summary.savings_rate)}</div>
            <div className="text-sm text-muted-foreground mt-1">
              of income
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Category Breakdown Table */}
      <Card>
        <CardHeader>
          <CardTitle>Category Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-2 text-sm font-medium text-muted-foreground">Category</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">Income</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">Expenses</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">Net</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">% of Income</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">% of Expenses</th>
                </tr>
              </thead>
              <tbody>
                {data.categories.map((category) => (
                  <tr key={category.category} className="border-b hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-2">
                      <button
                        onClick={() => category.subcategory_count > 0 && toggleCategory(category.category)}
                        className="flex items-center gap-2 text-left w-full"
                      >
                        {category.subcategory_count > 0 && (
                          <ChevronRight className={cn(
                            "w-4 h-4 transition-transform",
                            expandedCategories.has(category.category) && "rotate-90"
                          )} />
                        )}
                        <span className="font-medium">{category.category}</span>
                        {category.subcategory_count > 0 && (
                          <span className="text-xs text-muted-foreground">
                            ({category.subcategory_count})
                          </span>
                        )}
                      </button>
                    </td>
                    <td className="text-right py-3 px-2">
                      {category.income > 0 ? formatCurrency(category.income) : '-'}
                    </td>
                    <td className="text-right py-3 px-2">
                      {category.expense < 0 ? formatCurrency(Math.abs(category.expense)) : '-'}
                    </td>
                    <td className={cn(
                      "text-right py-3 px-2 font-medium",
                      category.net > 0 ? "text-green-600" : "text-red-600"
                    )}>
                      {formatCurrency(category.net)}
                    </td>
                    <td className="text-right py-3 px-2 text-sm text-muted-foreground">
                      {category.income_pct > 0 ? formatPercentage(category.income_pct) : '-'}
                    </td>
                    <td className="text-right py-3 px-2 text-sm text-muted-foreground">
                      {category.expense_pct > 0 ? formatPercentage(category.expense_pct) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.uncategorized_count > 0 && (
            <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-sm text-amber-800">
                {data.uncategorized_count} uncategorized transaction{data.uncategorized_count > 1 ? 's' : ''} found.
                Review them in the Filters & Analysis tab.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}