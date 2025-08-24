'use client';

export function FiltersTab() {
  return (
    <div className="flex flex-col items-center justify-center h-64 space-y-4">
      <h3 className="text-lg font-medium">Filters & Analysis</h3>
      <p className="text-muted-foreground">No transactions available</p>
      <p className="text-sm text-muted-foreground text-center max-w-md">
        Upload and commit account statements to analyze transactions here.
      </p>
    </div>
  );
}