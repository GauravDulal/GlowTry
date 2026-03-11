"use client";

import React, { useCallback, useRef, useState } from "react";
import { Upload, ImageIcon } from "lucide-react";

interface ImageUploadProps {
  onImageSelected: (file: File, previewUrl: string) => void;
}

export default function ImageUpload({ onImageSelected }: ImageUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = useCallback(
    (file: File) => {
      if (!file.type.startsWith("image/")) return;
      const url = URL.createObjectURL(file);
      onImageSelected(file, url);
    },
    [onImageSelected]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (e.dataTransfer.files.length > 0) {
        handleFile(e.dataTransfer.files[0]);
      }
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  return (
    <div
      onClick={() => fileInputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={`
        relative flex flex-col items-center justify-center
        w-full h-72 rounded-2xl cursor-pointer
        border-2 border-dashed transition-all duration-300
        ${
          isDragging
            ? "border-rose-400 bg-rose-50/50 scale-[1.02]"
            : "border-gray-200 bg-gradient-to-br from-rose-50/30 to-purple-50/30 hover:border-rose-300 hover:bg-rose-50/40"
        }
      `}
    >
      <div className="flex flex-col items-center gap-3 pointer-events-none">
        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-rose-100 to-purple-100 flex items-center justify-center">
          {isDragging ? (
            <ImageIcon className="w-7 h-7 text-rose-500" />
          ) : (
            <Upload className="w-7 h-7 text-rose-400" />
          )}
        </div>
        <div className="text-center">
          <p className="text-sm font-medium text-gray-700">
            {isDragging ? "Drop your selfie here" : "Upload your selfie"}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Drag & drop or click to browse
          </p>
          <p className="text-xs text-gray-300 mt-0.5">
            JPG, PNG up to 10MB
          </p>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => {
          if (e.target.files?.[0]) handleFile(e.target.files[0]);
        }}
      />
    </div>
  );
}
