'use client'

import { useState, useRef } from 'react'
import { uploadBankCSV, importCommit } from '@/lib/api'
import { 
  Upload, 
  CheckCircle2,
  AlertCircle,
  FileUp,
  Loader2,
  Check,
  ChevronRight,
  Calendar,
  Building2,
  FileText,
  ArrowRight
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

const banks = [
  { id: 'Boursorama', name: 'Boursorama', color: 'border-pink-500 bg-pink-50', textColor: 'text-pink-700' },
  { id: 'BNP', name: 'BNP Paribas', color: 'border-green-600 bg-green-50', textColor: 'text-green-700' },
  { id: 'Revolut', name: 'Revolut', color: 'border-blue-600 bg-blue-50', textColor: 'text-blue-700' }
]

export default function UploadPage() {
  const [month, setMonth] = useState<string>('')
  const [bank, setBank] = useState<'BNP' | 'Boursorama' | 'Revolut'>('Boursorama')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploadedBanks, setUploadedBanks] = useState<Set<string>>(new Set())
  const [uploadStep, setUploadStep] = useState<'select' | 'upload' | 'complete'>('select')

  async function handleUpload() {
    if (!file || !month) {
      toast.error('Please select both a month and a file')
      return
    }
    
    setLoading(true)
    
    try {
      const result = await uploadBankCSV({ bank, period_month: month, file })
      
      if (result.success) {
        toast.success(`Successfully uploaded ${result.rows} transactions`)
        setUploadedBanks(prev => new Set([...prev, bank]))
        setFile(null)
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
        setUploadStep('complete')
      } else if (result.duplicate_detected) {
        toast.error('This file has already been imported')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  async function handleCommit() {
    if (!month) {
      toast.error('Please select a month to commit')
      return
    }
    
    setLoading(true)
    
    try {
      const result = await importCommit(month)
      
      if (result.success) {
        toast.success(`Successfully processed ${result.inserted || 0} transactions`)
        setUploadedBanks(new Set())
        setUploadStep('select')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Commit failed'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">Upload Bank Statements</h1>
        <p className="text-sm text-gray-500 mt-1">Import your bank transactions from CSV files</p>
      </div>

      {/* Progress Indicator */}
      <div className="flex items-center justify-center mb-8">
        <div className="flex items-center gap-4">
          <div className={cn(
            "flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors",
            uploadStep === 'select' ? "bg-gray-900 border-gray-900" : "bg-white border-gray-300"
          )}>
            <span className={cn(
              "text-sm font-medium",
              uploadStep === 'select' ? "text-white" : "text-gray-500"
            )}>1</span>
          </div>
          <div className="w-24 h-0.5 bg-gray-300"></div>
          <div className={cn(
            "flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors",
            uploadStep === 'upload' ? "bg-gray-900 border-gray-900" : 
            uploadStep === 'complete' ? "bg-green-600 border-green-600" : "bg-white border-gray-300"
          )}>
            <span className={cn(
              "text-sm font-medium",
              uploadStep === 'upload' || uploadStep === 'complete' ? "text-white" : "text-gray-500"
            )}>2</span>
          </div>
          <div className="w-24 h-0.5 bg-gray-300"></div>
          <div className={cn(
            "flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors",
            uploadStep === 'complete' ? "bg-green-600 border-green-600" : "bg-white border-gray-300"
          )}>
            {uploadStep === 'complete' ? (
              <Check className="w-5 h-5 text-white" />
            ) : (
              <span className="text-sm font-medium text-gray-500">3</span>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto">
        {/* Month Selection */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <Calendar className="w-5 h-5 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-900">Select Period</h2>
          </div>
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            placeholder="Select month"
          />
        </div>

        {/* Bank Selection */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <Building2 className="w-5 h-5 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-900">Select Bank</h2>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {banks.map((b) => (
              <button
                key={b.id}
                onClick={() => setBank(b.id as any)}
                className={cn(
                  "p-4 rounded-lg border-2 transition-all",
                  bank === b.id 
                    ? `${b.color} ${b.textColor} border-2` 
                    : "border-gray-200 hover:border-gray-300 bg-white"
                )}
              >
                <div className="text-center">
                  <p className={cn(
                    "font-medium",
                    bank === b.id ? b.textColor : "text-gray-900"
                  )}>{b.name}</p>
                  {uploadedBanks.has(b.id) && (
                    <div className="flex items-center justify-center gap-1 mt-2">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span className="text-xs text-green-600">Uploaded</span>
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* File Upload */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <FileText className="w-5 h-5 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-900">Upload CSV File</h2>
          </div>
          
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={cn(
              "relative border-2 border-dashed rounded-lg p-8 text-center transition-colors",
              dragActive ? "border-gray-900 bg-gray-50" : "border-gray-300 hover:border-gray-400"
            )}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            
            <div className="flex flex-col items-center">
              <div className={cn(
                "w-16 h-16 rounded-full flex items-center justify-center mb-4",
                file ? "bg-green-100" : "bg-gray-100"
              )}>
                {file ? (
                  <CheckCircle2 className="w-8 h-8 text-green-600" />
                ) : (
                  <Upload className="w-8 h-8 text-gray-600" />
                )}
              </div>
              
              {file ? (
                <>
                  <p className="text-lg font-medium text-gray-900 mb-1">{file.name}</p>
                  <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setFile(null)
                      if (fileInputRef.current) {
                        fileInputRef.current.value = ''
                      }
                    }}
                    className="mt-3 text-sm text-red-600 hover:text-red-700"
                  >
                    Remove file
                  </button>
                </>
              ) : (
                <>
                  <p className="text-lg font-medium text-gray-900 mb-1">
                    Drop your CSV file here
                  </p>
                  <p className="text-sm text-gray-500 mb-3">or click to browse</p>
                  <p className="text-xs text-gray-400">Maximum file size: 10MB</p>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={handleUpload}
            disabled={!file || !month || loading}
            className={cn(
              "flex-1 py-3 px-6 rounded-lg font-medium transition-all flex items-center justify-center gap-2",
              (!file || !month || loading)
                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                : "bg-gray-900 text-white hover:bg-gray-800"
            )}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <FileUp className="w-4 h-4" />
                Upload File
              </>
            )}
          </button>

          {uploadedBanks.size > 0 && (
            <button
              onClick={handleCommit}
              disabled={loading}
              className={cn(
                "flex-1 py-3 px-6 rounded-lg font-medium transition-all flex items-center justify-center gap-2",
                loading
                  ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                  : "bg-green-600 text-white hover:bg-green-700"
              )}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <ArrowRight className="w-4 h-4" />
                  Commit {uploadedBanks.size} Bank{uploadedBanks.size > 1 ? 's' : ''}
                </>
              )}
            </button>
          )}
        </div>

        {/* Info Section */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-blue-900 mb-1">Import Instructions</p>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Select the month for your bank statements</li>
                <li>• Choose your bank from the options above</li>
                <li>• Upload the CSV file exported from your bank</li>
                <li>• Files are checked for duplicates automatically</li>
                <li>• Click "Commit" after uploading all banks for the month</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}