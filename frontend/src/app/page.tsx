"use client";

import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { UploadDropzone } from "@/components/UploadDropzone";
import { TryOnWorkspace } from "@/components/TryOnWorkspace";

export default function Home() {
  const [file, setFile] = React.useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = React.useState<string | null>(null);

  function reset() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(null);
    setPreviewUrl(null);
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(60%_60%_at_50%_0%,rgba(236,72,153,0.18),transparent_60%),radial-gradient(40%_40%_at_0%_30%,rgba(168,85,247,0.14),transparent_55%),radial-gradient(50%_50%_at_100%_20%,rgba(59,130,246,0.10),transparent_55%)]">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
        <header className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-2xl bg-zinc-950 text-white shadow-sm ring-1 ring-zinc-200 dark:bg-white dark:text-zinc-950 dark:ring-zinc-800">
              <span className="text-sm font-semibold tracking-tight">GT</span>
            </div>
            <div className="grid">
              <p className="text-sm font-semibold tracking-tight text-zinc-950 dark:text-zinc-50">
                GlowTry
              </p>
              <p className="text-xs text-zinc-600 dark:text-zinc-400">
                Virtual makeup try-on MVP
              </p>
            </div>
          </div>
          <Badge className="bg-white/60 text-zinc-700 ring-1 ring-zinc-200 backdrop-blur dark:bg-zinc-950/60 dark:text-zinc-200 dark:ring-zinc-800">
            Deterministic • No GenAI
          </Badge>
        </header>

        <main className="mt-10 grid gap-8">
          <section className="grid gap-3">
            <h1 className="text-balance text-3xl font-semibold tracking-tight text-zinc-950 dark:text-zinc-50 sm:text-4xl">
              Try makeup instantly on your selfie
            </h1>
            <p className="max-w-2xl text-pretty text-base leading-7 text-zinc-700 dark:text-zinc-300">
              Upload a photo, choose a look, and preview a realistic overlay powered by facial landmarks.
              Compare before/after, then download your favorite.
            </p>
          </section>

          <div className="grid gap-6">
            <UploadDropzone
              value={file}
              previewUrl={previewUrl}
              onChange={(f, url) => {
                if (previewUrl) URL.revokeObjectURL(previewUrl);
                setFile(f);
                setPreviewUrl(url);
              }}
            />

            {file && previewUrl ? (
              <TryOnWorkspace file={file} originalUrl={previewUrl} onReset={reset} />
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>How it works</CardTitle>
                  <CardDescription>A lightweight pipeline tuned for an MVP.</CardDescription>
                </CardHeader>
                <CardContent className="grid gap-3 text-sm text-zinc-700 dark:text-zinc-300">
                  <div className="grid gap-1">
                    <p className="font-medium text-zinc-950 dark:text-zinc-50">
                      1) Face + landmarks
                    </p>
                    <p>We detect a single face and 468 landmarks (MediaPipe Face Mesh).</p>
                  </div>
                  <div className="grid gap-1">
                    <p className="font-medium text-zinc-950 dark:text-zinc-50">2) Region masks</p>
                    <p>Lips, cheeks, and eyelids are converted into soft masks.</p>
                  </div>
                  <div className="grid gap-1">
                    <p className="font-medium text-zinc-950 dark:text-zinc-50">
                      3) Feathered overlays
                    </p>
                    <p>We alpha-blend tints with blur/feathering for smoother edges.</p>
                  </div>
                  <div className="flex flex-wrap items-center gap-2 pt-2">
                    <Button variant="primary" size="sm" disabled>
                      Upload to start
                    </Button>
                    <p className="text-xs text-zinc-600 dark:text-zinc-400">
                      Best results: centered face, neutral expression, no heavy occlusion.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
