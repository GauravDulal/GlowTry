"use client";

import React, { useState, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import ImageUpload from "@/components/ImageUpload";
import MakeupPanel from "@/components/MakeupPanel";
import BeforeAfterSlider from "@/components/BeforeAfterSlider";
import { applyMakeup, DEFAULT_CONFIG, type MakeupConfig } from "@/lib/api";
import {
  Sparkles,
  Download,
  RotateCcw,
  ImagePlus,
  Loader2,
  AlertCircle,
} from "lucide-react";

export default function Home() {
  // ─── State ───
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [config, setConfig] = useState<MakeupConfig>(DEFAULT_CONFIG);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showComparison, setShowComparison] = useState(false);

  const resultRef = useRef<HTMLDivElement>(null);

  // ─── Handlers ───
  const handleImageSelected = useCallback((file: File, url: string) => {
    setImageFile(file);
    setPreviewUrl(url);
    setResultUrl(null);
    setError(null);
    setShowComparison(false);
  }, []);

  const handleApplyMakeup = useCallback(async () => {
    if (!imageFile) return;

    // Check if at least one product is enabled
    const anyEnabled =
      config.lipstick.enabled ||
      config.blush.enabled ||
      config.eyeshadow.enabled ||
      config.eyeliner.enabled;

    if (!anyEnabled) {
      setError("Please enable at least one makeup product.");
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const response = await applyMakeup(imageFile, config);
      
      if (response.error) {
        setError(response.error);
        setIsProcessing(false);
        return;
      }

      const url = `data:image/png;base64,${response.image}`;
      setResultUrl(url);
      setShowComparison(true);

      // Scroll to result
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong. Please try again."
      );
    } finally {
      setIsProcessing(false);
    }
  }, [imageFile, config]);

  const handleRemoveAll = useCallback(() => {
    setConfig(DEFAULT_CONFIG);
    setResultUrl(null);
    setShowComparison(false);
    setError(null);
  }, []);

  const handleNewImage = useCallback(() => {
    setImageFile(null);
    setPreviewUrl(null);
    setResultUrl(null);
    setConfig(DEFAULT_CONFIG);
    setError(null);
    setShowComparison(false);
  }, []);

  const handleDownload = useCallback(() => {
    if (!resultUrl) return;
    const a = document.createElement("a");
    a.href = resultUrl;
    a.download = "glowtry-makeup.png";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }, [resultUrl]);

  // ─── Render ───
  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50/60 via-white to-purple-50/40">
      {/* Header */}
      <header className="border-b border-rose-100/60 bg-white/70 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-rose-400 to-pink-500 flex items-center justify-center shadow-lg shadow-rose-200/50">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-gradient">
                GlowTry
              </h1>
              <p className="text-[10px] text-gray-400 -mt-0.5 tracking-wider uppercase">
                Virtual Makeup
              </p>
            </div>
          </div>

          {previewUrl && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleNewImage}
              className="text-gray-500 hover:text-rose-500 transition-colors"
            >
              <ImagePlus className="w-4 h-4 mr-1.5" />
              New Photo
            </Button>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {!previewUrl ? (
          /* ─── Upload State ─── */
          <div className="max-w-xl mx-auto space-y-6">
            <div className="text-center space-y-3">
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
                Try before you <span className="text-gradient">buy</span>
              </h2>
              <p className="text-gray-500 text-sm sm:text-base max-w-md mx-auto">
                Upload a selfie and virtually try on lipstick, blush, eyeshadow,
                and eyeliner — powered by real computer vision.
              </p>
            </div>
            <ImageUpload onImageSelected={handleImageSelected} />
            <p className="text-center text-xs text-gray-300">
              Your photos are processed on-device and never stored.
            </p>
          </div>
        ) : (
          /* ─── Makeup Workspace ─── */
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-6">
            {/* Left: Image Preview */}
            <div className="space-y-4" ref={resultRef}>
              <Card className="overflow-hidden border-rose-100/50 shadow-lg shadow-rose-100/20">
                <CardContent className="p-0">
                  {showComparison && resultUrl && previewUrl ? (
                    <BeforeAfterSlider
                      beforeSrc={previewUrl}
                      afterSrc={resultUrl}
                    />
                  ) : (
                    <div className="relative">
                      <img
                        src={resultUrl || previewUrl}
                        alt="Your selfie"
                        className="w-full h-auto object-contain rounded-xl"
                      />
                      {isProcessing && (
                        <div className="absolute inset-0 bg-white/60 backdrop-blur-sm flex flex-col items-center justify-center gap-3 rounded-xl">
                          <Loader2 className="w-8 h-8 text-rose-500 animate-spin" />
                          <p className="text-sm text-gray-600 font-medium animate-glow-pulse">
                            Applying makeup...
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Action buttons */}
              <div className="flex flex-wrap gap-2">
                <Button
                  onClick={handleApplyMakeup}
                  disabled={isProcessing}
                  className="bg-gradient-to-r from-rose-500 to-pink-500 hover:from-rose-600 hover:to-pink-600 text-white shadow-lg shadow-rose-200/50 flex-1 sm:flex-none"
                >
                  {isProcessing ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4 mr-2" />
                  )}
                  {isProcessing ? "Processing..." : "Apply Makeup"}
                </Button>

                {resultUrl && (
                  <>
                    <Button
                      variant="outline"
                      onClick={() => setShowComparison(!showComparison)}
                      className="border-rose-200 text-rose-600 hover:bg-rose-50"
                    >
                      {showComparison ? "Hide" : "Before / After"}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleDownload}
                      className="border-rose-200 text-rose-600 hover:bg-rose-50"
                    >
                      <Download className="w-4 h-4 mr-1.5" />
                      Download
                    </Button>
                  </>
                )}

                <Button
                  variant="ghost"
                  onClick={handleRemoveAll}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <RotateCcw className="w-4 h-4 mr-1.5" />
                  Reset All
                </Button>
              </div>

              {/* Error display */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-start gap-2 text-sm">
                  <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  {error}
                </div>
              )}
            </div>

            {/* Right: Makeup Controls */}
            <div className="space-y-4">
              <Card className="border-rose-100/50 shadow-lg shadow-rose-100/20">
                <CardContent className="p-5">
                  <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                    Makeup Studio
                  </h3>
                  <MakeupPanel config={config} onChange={setConfig} />
                </CardContent>
              </Card>

              {/* Active products summary */}
              <Card className="border-rose-100/50 bg-gradient-to-br from-rose-50/50 to-purple-50/30">
                <CardContent className="p-4">
                  <p className="text-xs text-gray-400 mb-2 font-medium">
                    Active Products
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {config.lipstick.enabled && (
                      <span className="text-xs bg-white border border-rose-200 text-rose-600 px-2.5 py-1 rounded-full">
                        💄 Lipstick
                      </span>
                    )}
                    {config.blush.enabled && (
                      <span className="text-xs bg-white border border-pink-200 text-pink-600 px-2.5 py-1 rounded-full">
                        🌸 Blush
                      </span>
                    )}
                    {config.eyeshadow.enabled && (
                      <span className="text-xs bg-white border border-purple-200 text-purple-600 px-2.5 py-1 rounded-full">
                        ✨ Shadow
                      </span>
                    )}
                    {config.eyeliner.enabled && (
                      <span className="text-xs bg-white border border-gray-200 text-gray-600 px-2.5 py-1 rounded-full">
                        ✏️ Liner
                      </span>
                    )}
                    {!config.lipstick.enabled &&
                      !config.blush.enabled &&
                      !config.eyeshadow.enabled &&
                      !config.eyeliner.enabled && (
                        <span className="text-xs text-gray-300 italic">
                          No products selected
                        </span>
                      )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-rose-100/40 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 flex items-center justify-between">
          <p className="text-xs text-gray-300">
            © 2026 GlowTry. All makeup effects applied using computer vision.
          </p>
          <p className="text-xs text-gray-300">
            No generative AI · No CSS filters
          </p>
        </div>
      </footer>
    </div>
  );
}
