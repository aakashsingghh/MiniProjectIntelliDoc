import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, Loader2, CheckCircle2 } from 'lucide-react';
import { cn } from '@/src/lib/utils';

interface FileUploadProps {
  onUploadComplete: (data: any) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [language, setLanguage] = useState('eng');
  const [progress, setProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/pdf': ['.pdf']
    },
    multiple: false
  });

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setProgress(10);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);

    try {
      setProgress(30);
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      setProgress(70);
      const data = await response.json();
      setProgress(100);
      onUploadComplete(data);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to process document. Please try again.');
    } finally {
      setIsUploading(false);
      setProgress(0);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <div
        {...getRootProps()}
        className={cn(
          "relative border-2 border-dashed rounded-2xl p-12 transition-all duration-300 cursor-pointer group",
          isDragActive ? "border-emerald-500 bg-emerald-50/50" : "border-slate-200 hover:border-emerald-400 hover:bg-slate-50",
          file && "border-emerald-500 bg-emerald-50/10"
        )}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <div className={cn(
            "p-4 rounded-full transition-colors",
            file ? "bg-emerald-100 text-emerald-600" : "bg-slate-100 text-slate-400 group-hover:bg-emerald-100 group-hover:text-emerald-600"
          )}>
            {file ? <CheckCircle2 className="w-8 h-8" /> : <Upload className="w-8 h-8" />}
          </div>
          <div>
            <p className="text-lg font-medium text-slate-900">
              {file ? file.name : "Drop your document here"}
            </p>
            <p className="text-sm text-slate-500">
              Supports PNG, JPG, JPEG, and PDF
            </p>
          </div>
        </div>
      </div>

      {file && !isUploading && (
        <div className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-xl shadow-sm animate-in fade-in slide-in-from-bottom-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-900">{file.name}</p>
              <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="text-sm border-slate-200 rounded-lg focus:ring-emerald-500 focus:border-emerald-500"
            >
              <option value="eng">English</option>
              <option value="hin">Hindi</option>
              <option value="spa">Spanish</option>
              <option value="fra">French</option>
            </select>
            <button
              onClick={() => setFile(null)}
              className="p-1 hover:bg-slate-100 rounded-full text-slate-400 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {isUploading && (
        <div className="space-y-3 p-6 bg-white border border-slate-200 rounded-xl shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin text-emerald-600" />
              <span className="text-sm font-medium text-slate-700">Processing Document...</span>
            </div>
            <span className="text-sm text-slate-500">{progress}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className="bg-emerald-500 h-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-slate-400 text-center italic">
            "Image preprocessing and OCR extraction in progress..."
          </p>
        </div>
      )}

      {file && !isUploading && (
        <button
          onClick={handleUpload}
          className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl shadow-lg shadow-emerald-200 transition-all active:scale-[0.98]"
        >
          Start Intelligent Processing
        </button>
      )}
    </div>
  );
};
