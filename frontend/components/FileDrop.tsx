'use client'

import { useState, useCallback } from 'react'
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FileDropProps {
  onFilesSelected: (files: File[]) => void
  acceptedTypes?: string[]
  maxFiles?: number
  className?: string
}

export default function FileDrop({
  onFilesSelected,
  acceptedTypes = ['.csv'],
  maxFiles = 3,
  className
}: FileDropProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)

    const files = Array.from(e.dataTransfer.files).filter(file => 
      acceptedTypes.some(type => file.name.toLowerCase().endsWith(type.replace('.', '')))
    )

    if (files.length > maxFiles) {
      files.splice(maxFiles)
    }

    setSelectedFiles(files)
    onFilesSelected(files)
  }, [acceptedTypes, maxFiles, onFilesSelected])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    
    if (files.length > maxFiles) {
      files.splice(maxFiles)
    }

    setSelectedFiles(files)
    onFilesSelected(files)
  }, [maxFiles, onFilesSelected])

  const removeFile = useCallback((index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index)
    setSelectedFiles(newFiles)
    onFilesSelected(newFiles)
  }, [selectedFiles, onFilesSelected])

  return (
    <div className={className}>
      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer',
          isDragOver
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        )}
      >
        <input
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileInput}
          className="hidden"
          id="file-upload"
        />
        
        <label htmlFor="file-upload" className="cursor-pointer">
          <Upload className={cn(
            'mx-auto h-12 w-12 mb-4',
            isDragOver ? 'text-blue-500' : 'text-gray-400'
          )} />
          
          <div className="text-lg font-medium text-gray-900 mb-2">
            {isDragOver ? 'Drop files here' : 'Drop CSV files or click to browse'}
          </div>
          
          <p className="text-sm text-gray-600">
            Upload up to {maxFiles} CSV files ({acceptedTypes.join(', ')})
          </p>
          
          <p className="text-xs text-gray-500 mt-2">
            Supported banks: BNP, Boursorama, Revolut
          </p>
        </label>
      </div>

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            Selected Files ({selectedFiles.length})
          </h4>
          
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border"
              >
                <div className="flex items-center min-w-0">
                  <FileText className="h-5 w-5 text-gray-400 mr-3 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
                
                <button
                  onClick={() => removeFile(index)}
                  className="ml-4 text-red-600 hover:text-red-800 p-1"
                  title="Remove file"
                >
                  <AlertCircle className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* File Status Messages */}
      {selectedFiles.length > 0 && (
        <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-sm text-green-800">
              {selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''} ready for upload
            </span>
          </div>
        </div>
      )}
    </div>
  )
}