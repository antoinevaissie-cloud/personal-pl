'use client';

import { useState, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, Upload } from 'lucide-react';
import { BankType } from '@/types/api.types';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';

interface UploadCardProps {
  bankName: string;
  bankType: BankType;
  currency: string;
  periodMonth: string;
  onUploadComplete?: () => void;
}

export function UploadCard({ 
  bankName, 
  bankType, 
  currency, 
  periodMonth,
  onUploadComplete 
}: UploadCardProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0 && files[0].type === 'text/csv') {
      setFile(files[0]);
      setUploadStatus('idle');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setFile(files[0]);
      setUploadStatus('idle');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setErrorMessage('');
    setUploadStatus('idle');

    try {
      console.log(`Uploading ${file.name} for ${bankType} (${periodMonth})`);
      await api.uploadCSV(file, bankType, periodMonth);
      setUploadStatus('success');
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      onUploadComplete?.();
    } catch (error) {
      setUploadStatus('error');
      console.error('Upload error:', error);
      let message = 'Upload failed';
      if (error instanceof Error) {
        message = error.message;
        // Parse common backend errors
        if (message.includes('Validation error')) {
          message = 'Invalid file format or missing required fields';
        } else if (message.includes('duplicate') || message.includes('already been imported')) {
          message = 'This file has already been uploaded. To re-upload, you need to clear existing data.';
        } else if (message.includes('No columns to parse')) {
          message = `Invalid ${bankType} CSV format. Please ensure the file is exported from ${bankName}.`;
        } else if (message.includes('Missing required columns')) {
          message = 'CSV file is missing required columns for this bank.';
        }
      }
      setErrorMessage(message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card className="upload-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <FileText className="w-5 h-5 text-muted-foreground" />
          <div>
            <h3 className="font-medium">{bankName}</h3>
            <p className="text-sm text-muted-foreground">
              {bankName} statements (CSV format)
            </p>
          </div>
        </div>
        <span className="px-2 py-1 bg-muted text-xs font-medium rounded">
          {currency}
        </span>
      </div>

      <div
        className={cn(
          'border-2 border-dashed rounded-lg p-6 text-center transition-colors',
          isDragging ? 'border-primary bg-primary/5' : 'border-border',
          uploadStatus === 'success' && 'border-green-500 bg-green-50',
          uploadStatus === 'error' && 'border-destructive bg-destructive/5'
        )}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <Upload className="w-8 h-8 mx-auto mb-3 text-muted-foreground" />
        
        {file ? (
          <div className="space-y-2">
            <p className="text-sm font-medium">{file.name}</p>
            <p className="text-xs text-muted-foreground">
              {(file.size / 1024).toFixed(2)} KB
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              Drag and drop your CSV file here, or
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
            >
              Choose file
            </Button>
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={handleFileSelect}
        />
      </div>

      {uploadStatus === 'success' && (
        <div className="mt-3 text-sm text-green-600">
          File uploaded successfully!
        </div>
      )}

      {uploadStatus === 'error' && errorMessage && (
        <div className="mt-3 text-sm text-destructive">
          {errorMessage}
        </div>
      )}

      {file && uploadStatus !== 'success' && (
        <Button
          className="w-full mt-4"
          onClick={handleUpload}
          disabled={isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload CSV File'}
        </Button>
      )}
    </Card>
  );
}