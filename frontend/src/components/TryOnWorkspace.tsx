"use client";

import * as React from "react";
import { Download, Loader2, RefreshCcw } from "lucide-react";
import { ReactCompareSlider, ReactCompareSliderImage } from "react-compare-slider";

import { applyMakeup, fetchStyles, type Style } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type ViewMode = "slider" | "toggle";

export function TryOnWorkspace(props: {
  file: File;
  originalUrl: string;
  onReset: () => void;
}) {
  const [styles, setStyles] = React.useState<Style[]>([
    { name: "natural-glow", label: "Natural Glow", description: "Soft pink lips, subtle blush." },
    { name: "soft-glam", label: "Soft Glam", description: "Nude-rose lips, warm blush." },
    { name: "bold-lips", label: "Bold Lips", description: "Strong lip tint, minimal blush." },
    { name: "bridal-touch", label: "Bridal Touch", description: "Rosy lips, elegant eyes." },
    { name: "party-look", label: "Party Look", description: "Deeper lips, stronger blush." },
  ]);
  const [selected, setSelected] = React.useState<string>("natural-glow");
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [resultUrl, setResultUrl] = React.useState<string | null>(null);
  const [viewMode, setViewMode] = React.useState<ViewMode>("slider");
  const [showAfter, setShowAfter] = React.useState(true);

  React.useEffect(() => {
    let cancelled = false;
    fetchStyles()
      .then((s) => {
        if (!cancelled && s?.length) setStyles(s);
      })
      .catch(() => {
        // fall back to built-in list
      });
    return () => {
      cancelled = true;
    };
  }, []);

  React.useEffect(() => {
    return () => {
      if (resultUrl) URL.revokeObjectURL(resultUrl);
    };
  }, [resultUrl]);

  async function run(styleName: string) {
    setSelected(styleName);
    setError(null);
    setIsLoading(true);
    try {
      const blob = await applyMakeup({ file: props.file, style: styleName });
      const url = URL.createObjectURL(blob);
      setResultUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return url;
      });
      setShowAfter(true);
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Failed to process image.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  function download() {
    if (!resultUrl) return;
    const a = document.createElement("a");
    a.href = resultUrl;
    a.download = `glowtry-${selected}.png`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  return (
    <div className="grid gap-6">
      <div className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
        <Card className="overflow-hidden">
          <CardHeader className="flex-row items-center justify-between gap-4">
            <div className="grid gap-1">
              <CardTitle>Try-on workspace</CardTitle>
              <CardDescription>Choose a look and preview before/after.</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setViewMode((m) => (m === "slider" ? "toggle" : "slider"))}
                disabled={!resultUrl}
                title={resultUrl ? "Switch compare mode" : "Apply a look to compare"}
              >
                {viewMode === "slider" ? "Toggle" : "Slider"}
              </Button>
              <Button variant="secondary" size="sm" onClick={props.onReset}>
                <RefreshCcw className="h-4 w-4" />
                New photo
              </Button>
            </div>
          </CardHeader>
          <CardContent className="grid gap-4">
            <div className="relative overflow-hidden rounded-2xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
              {isLoading ? (
                <div className="absolute inset-0 z-10 grid place-items-center bg-white/70 backdrop-blur-sm dark:bg-black/50">
                  <div className="flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-medium text-zinc-950 shadow-sm ring-1 ring-zinc-200 dark:bg-zinc-950 dark:text-zinc-50 dark:ring-zinc-800">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Applying look…
                  </div>
                </div>
              ) : null}

              {!resultUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={props.originalUrl}
                  alt="Original"
                  className="max-h-[520px] w-full object-contain"
                />
              ) : viewMode === "slider" ? (
                <ReactCompareSlider
                  className="max-h-[520px] w-full"
                  itemOne={
                    <ReactCompareSliderImage src={props.originalUrl} alt="Before" />
                  }
                  itemTwo={<ReactCompareSliderImage src={resultUrl} alt="After" />}
                />
              ) : (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={showAfter ? resultUrl : props.originalUrl}
                  alt={showAfter ? "After" : "Before"}
                  className="max-h-[520px] w-full object-contain"
                />
              )}
            </div>

            {resultUrl && viewMode === "toggle" ? (
              <div className="flex items-center justify-center gap-2">
                <Button
                  variant={showAfter ? "secondary" : "primary"}
                  size="sm"
                  onClick={() => setShowAfter(false)}
                >
                  Before
                </Button>
                <Button
                  variant={showAfter ? "primary" : "secondary"}
                  size="sm"
                  onClick={() => setShowAfter(true)}
                >
                  After
                </Button>
              </div>
            ) : null}

            {error ? (
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            ) : null}

            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-xs text-zinc-600 dark:text-zinc-400">
                If it looks off: try a sharper, front-facing photo without hair covering the cheeks.
              </p>
              <Button
                onClick={download}
                variant="primary"
                size="sm"
                disabled={!resultUrl || isLoading}
              >
                <Download className="h-4 w-4" />
                Download
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Makeup presets</CardTitle>
            <CardDescription>Pick one to apply to your selfie.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            {styles.map((s) => (
              <button
                key={s.name}
                className={cn(
                  "group rounded-2xl border p-4 text-left transition-colors",
                  selected === s.name
                    ? "border-zinc-900 bg-zinc-950 text-white dark:border-white dark:bg-white dark:text-zinc-950"
                    : "border-zinc-200 bg-white hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950 dark:hover:bg-zinc-900",
                )}
                disabled={isLoading}
                onClick={() => run(s.name)}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="grid gap-1">
                    <p className="text-sm font-semibold">{s.label}</p>
                    <p
                      className={cn(
                        "text-xs leading-5",
                        selected === s.name
                          ? "text-white/80 dark:text-zinc-700"
                          : "text-zinc-600 dark:text-zinc-400",
                      )}
                    >
                      {s.description}
                    </p>
                  </div>
                  <span
                    className={cn(
                      "rounded-full px-2.5 py-1 text-xs font-medium",
                      selected === s.name
                        ? "bg-white/15 text-white dark:bg-zinc-100 dark:text-zinc-900"
                        : "bg-zinc-100 text-zinc-700 dark:bg-zinc-900 dark:text-zinc-200",
                    )}
                  >
                    {selected === s.name ? "Selected" : "Apply"}
                  </span>
                </div>
              </button>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

