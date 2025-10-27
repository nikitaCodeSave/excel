/**
 * Компонент загрузки файла
 */
import { useState, useRef, DragEvent } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isUploading: boolean;
}

export function FileUpload({ onFileSelect, isUploading }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    const file = files[0];

    if (file && isValidFile(file)) {
      onFileSelect(file);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0] && isValidFile(files[0])) {
      onFileSelect(files[0]);
    }
  };

  const isValidFile = (file: File): boolean => {
    const validExtensions = ['.xlsx', '.xls', '.csv'];
    const extension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    return validExtensions.includes(extension);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div
      className={`
        border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
        transition-all duration-200
        ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
        ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".xlsx,.xls,.csv"
        onChange={handleFileInput}
        className="hidden"
        disabled={isUploading}
      />

      <div className="space-y-4">
        {isUploading ? (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-gray-600">Загрузка файла...</p>
          </>
        ) : (
          <>
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div>
              <p className="text-lg font-medium text-gray-700">
                Перетащите файл сюда
              </p>
              <p className="text-sm text-gray-500 mt-1">
                или нажмите для выбора
              </p>
            </div>
            <p className="text-xs text-gray-400">
              Поддерживаются форматы: .xlsx, .xls, .csv
            </p>
          </>
        )}
      </div>
    </div>
  );
}
