"use client";

import * as React from "react";
import { type FileRejection, useDropzone } from "react-dropzone";
import { ImagePlus, X } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const MAX_BYTES = 8 * 1024 * 1024;
const ACCEPTED = {
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "image/webp": [".webp"],
};

export function UploadDropzone(props: {
  value?: File | null;
  previewUrl?: string | null;
  onChange: (file: File | null, previewUrl: string | null) => void;
}) {
  const [error, setError] = React.useState<string | null>(null);

  const onDrop = React.useCallback(
    (acceptedFiles: File[], fileRejections: FileRejection[]) => {
      setError(null);
      if (fileRejections?.length) {
        setError("Unsupported file. Please upload a JPG, PNG, or WEBP image.");
        return;
      }
      const file = acceptedFiles?.[0];
      if (!file) return;
      if (file.size > MAX_BYTES) {
        setError("File is too large. Please upload an image under 8MB.");
        return;
      }
      const url = URL.createObjectURL(file);
      props.onChange(file, url);
    },
    [props],
  );

  React.useEffect(() => {
    return () => {
      if (props.previewUrl) URL.revokeObjectURL(props.previewUrl);
    };
  }, [props.previewUrl]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: ACCEPTED,
  });

  const hasImage = Boolean(props.value && props.previewUrl);

  return (
    <div className="grid gap-4">
      <Card
        className={cn(
          "relative overflow-hidden",
          isDragActive ? "ring-2 ring-zinc-300 dark:ring-zinc-700" : "",
        )}
      >
        <CardHeader className="flex-row items-center justify-between gap-3">
          <div className="grid gap-1">
            <CardTitle className="flex items-center gap-2">
              <span>Upload a selfie</span>
              <Badge>Best results</Badge>
            </CardTitle>
            <CardDescription>
              Front-facing, clear lighting, minimal occlusion (no hands over face).
            </CardDescription>
          </div>
          {hasImage ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => props.onChange(null, null)}
              aria-label="Remove uploaded image"
            >
              <X className="h-4 w-4" />
              Remove
            </Button>
          ) : null}
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={cn(
              "group flex min-h-52 cursor-pointer items-center justify-center rounded-2xl border border-dashed border-zinc-200 bg-gradient-to-b from-white to-zinc-50 p-6 text-center dark:border-zinc-800 dark:from-zinc-950 dark:to-zinc-950",
              isDragActive ? "border-zinc-400 dark:border-zinc-600" : "",
            )}
          >
            <input {...getInputProps()} />
            {!hasImage ? (
              <div className="grid justify-items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-900 text-white shadow-sm dark:bg-white dark:text-zinc-950">
                  <ImagePlus className="h-5 w-5" />
                </div>
                <div className="grid gap-1">
                  <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
                    {isDragActive ? "Drop your image here" : "Drag & drop, or click to choose a file"}
                  </p>
                  <p className="text-xs text-zinc-600 dark:text-zinc-400">
                    JPG, PNG, WEBP • up to 8MB
                  </p>
                </div>
              </div>
            ) : (
              <div className="grid w-full gap-3">
                <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={props.previewUrl ?? ""}
                    alt="Uploaded selfie preview"
                    className="max-h-[420px] w-full object-contain"
                  />
                </div>
                <p className="text-xs text-zinc-600 dark:text-zinc-400">
                  Tip: If the face isn’t detected, try cropping closer to your face and use brighter light.
                </p>
              </div>
            )}
          </div>

          {error ? (
            <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}

