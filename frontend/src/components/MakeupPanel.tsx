"use client";

import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import type { MakeupConfig } from "@/lib/api";

// ─── Color Swatches ───
const LIPSTICK_SWATCHES = [
  { name: "Classic Red", color: [200, 40, 40] },
  { name: "Deep Berry", color: [140, 30, 80] },
  { name: "Soft Pink", color: [220, 130, 140] },
  { name: "Nude", color: [190, 140, 120] },
  { name: "Coral", color: [230, 100, 80] },
  { name: "Mauve", color: [160, 100, 120] },
  { name: "Plum", color: [120, 40, 90] },
  { name: "Peach", color: [240, 160, 130] },
];

const BLUSH_SWATCHES = [
  { name: "Rose", color: [220, 140, 140] },
  { name: "Peach", color: [240, 170, 140] },
  { name: "Berry", color: [200, 100, 120] },
  { name: "Coral", color: [230, 130, 110] },
  { name: "Nude", color: [210, 170, 155] },
  { name: "Mauve", color: [190, 130, 150] },
];

const EYESHADOW_SWATCHES = [
  { name: "Champagne", color: [220, 200, 170] },
  { name: "Rose Gold", color: [200, 150, 140] },
  { name: "Smoky", color: [80, 70, 70] },
  { name: "Lavender", color: [180, 150, 210] },
  { name: "Bronze", color: [180, 130, 80] },
  { name: "Teal", color: [80, 160, 160] },
  { name: "Plum", color: [140, 80, 130] },
  { name: "Gold", color: [210, 180, 100] },
];

const EYELINER_SWATCHES = [
  { name: "Black", color: [20, 20, 20] },
  { name: "Dark Brown", color: [60, 40, 30] },
  { name: "Navy", color: [30, 30, 80] },
  { name: "Forest", color: [30, 60, 40] },
];

interface MakeupPanelProps {
  config: MakeupConfig;
  onChange: (config: MakeupConfig) => void;
}

function ColorSwatch({
  swatches,
  selected,
  onSelect,
}: {
  swatches: { name: string; color: number[] }[];
  selected: [number, number, number];
  onSelect: (color: [number, number, number]) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {swatches.map((s) => {
        const isSelected =
          s.color[0] === selected[0] &&
          s.color[1] === selected[1] &&
          s.color[2] === selected[2];
        return (
          <button
            key={s.name}
            title={s.name}
            onClick={() => onSelect(s.color as [number, number, number])}
            className={`w-8 h-8 rounded-full border-2 transition-all duration-200 hover:scale-110 ${
              isSelected
                ? "border-rose-500 ring-2 ring-rose-300 scale-110"
                : "border-gray-200 hover:border-gray-300"
            }`}
            style={{
              backgroundColor: `rgb(${s.color[0]}, ${s.color[1]}, ${s.color[2]})`,
            }}
          />
        );
      })}
    </div>
  );
}

function CustomColorPicker({
  color,
  onChange,
}: {
  color: [number, number, number];
  onChange: (color: [number, number, number]) => void;
}) {
  const hex = `#${color.map((c) => c.toString(16).padStart(2, "0")).join("")}`;
  return (
    <div className="flex items-center gap-2">
      <Label className="text-xs text-gray-500">Custom:</Label>
      <input
        type="color"
        value={hex}
        onChange={(e) => {
          const h = e.target.value;
          const r = parseInt(h.slice(1, 3), 16);
          const g = parseInt(h.slice(3, 5), 16);
          const b = parseInt(h.slice(5, 7), 16);
          onChange([r, g, b]);
        }}
        className="w-8 h-8 rounded-lg border border-gray-200 cursor-pointer p-0"
      />
    </div>
  );
}

export default function MakeupPanel({ config, onChange }: MakeupPanelProps) {
  const update = (partial: Partial<MakeupConfig>) => {
    onChange({ ...config, ...partial });
  };

  return (
    <Tabs defaultValue="lipstick" className="w-full">
      <TabsList className="w-full grid grid-cols-4 mb-4">
        <TabsTrigger value="lipstick" className="text-xs sm:text-sm">
          💄 Lipstick
        </TabsTrigger>
        <TabsTrigger value="blush" className="text-xs sm:text-sm">
          🌸 Blush
        </TabsTrigger>
        <TabsTrigger value="eyeshadow" className="text-xs sm:text-sm">
          ✨ Shadow
        </TabsTrigger>
        <TabsTrigger value="eyeliner" className="text-xs sm:text-sm">
          ✏️ Liner
        </TabsTrigger>
      </TabsList>

      {/* ─── Lipstick ─── */}
      <TabsContent value="lipstick" className="space-y-4">
        <div className="flex items-center justify-between">
          <Label className="font-medium">Enable Lipstick</Label>
          <Switch
            checked={config.lipstick.enabled}
            onCheckedChange={(checked) =>
              update({ lipstick: { ...config.lipstick, enabled: checked } })
            }
          />
        </div>

        <div className="space-y-2">
          <Label className="text-xs text-gray-500">Shade</Label>
          <ColorSwatch
            swatches={LIPSTICK_SWATCHES}
            selected={config.lipstick.color}
            onSelect={(color) =>
              update({ lipstick: { ...config.lipstick, color } })
            }
          />
          <CustomColorPicker
            color={config.lipstick.color}
            onChange={(color) =>
              update({ lipstick: { ...config.lipstick, color } })
            }
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-xs text-gray-500">Intensity</Label>
            <span className="text-xs text-gray-400">
              {Math.round(config.lipstick.intensity * 100)}%
            </span>
          </div>
          <Slider
            value={[config.lipstick.intensity * 100]}
            onValueChange={(val) => {
              const v = Array.isArray(val) ? val[0] : val;
              update({ lipstick: { ...config.lipstick, intensity: v / 100 } });
            }}
            min={10}
            max={100}
            step={5}
          />
        </div>

        <div className="flex items-center justify-between">
          <Label className="text-xs text-gray-500">Finish</Label>
          <div className="flex gap-2">
            <button
              onClick={() =>
                update({ lipstick: { ...config.lipstick, matte: true } })
              }
              className={`text-xs px-3 py-1 rounded-full border transition-all ${
                config.lipstick.matte
                  ? "bg-rose-500 text-white border-rose-500"
                  : "bg-white text-gray-600 border-gray-200 hover:border-gray-300"
              }`}
            >
              Matte
            </button>
            <button
              onClick={() =>
                update({ lipstick: { ...config.lipstick, matte: false } })
              }
              className={`text-xs px-3 py-1 rounded-full border transition-all ${
                !config.lipstick.matte
                  ? "bg-rose-500 text-white border-rose-500"
                  : "bg-white text-gray-600 border-gray-200 hover:border-gray-300"
              }`}
            >
              Glossy
            </button>
          </div>
        </div>
      </TabsContent>

      {/* ─── Blush ─── */}
      <TabsContent value="blush" className="space-y-4">
        <div className="flex items-center justify-between">
          <Label className="font-medium">Enable Blush</Label>
          <Switch
            checked={config.blush.enabled}
            onCheckedChange={(checked) =>
              update({ blush: { ...config.blush, enabled: checked } })
            }
          />
        </div>

        <div className="space-y-2">
          <Label className="text-xs text-gray-500">Shade</Label>
          <ColorSwatch
            swatches={BLUSH_SWATCHES}
            selected={config.blush.color}
            onSelect={(color) =>
              update({ blush: { ...config.blush, color } })
            }
          />
          <CustomColorPicker
            color={config.blush.color}
            onChange={(color) =>
              update({ blush: { ...config.blush, color } })
            }
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-xs text-gray-500">Intensity</Label>
            <span className="text-xs text-gray-400">
              {Math.round(config.blush.intensity * 100)}%
            </span>
          </div>
          <Slider
            value={[config.blush.intensity * 100]}
            onValueChange={(val) => {
              const v = Array.isArray(val) ? val[0] : val;
              update({ blush: { ...config.blush, intensity: v / 100 } });
            }}
            min={10}
            max={100}
            step={5}
          />
        </div>
      </TabsContent>

      {/* ─── Eyeshadow ─── */}
      <TabsContent value="eyeshadow" className="space-y-4">
        <div className="flex items-center justify-between">
          <Label className="font-medium">Enable Eyeshadow</Label>
          <Switch
            checked={config.eyeshadow.enabled}
            onCheckedChange={(checked) =>
              update({
                eyeshadow: { ...config.eyeshadow, enabled: checked },
              })
            }
          />
        </div>

        <div className="space-y-2">
          <Label className="text-xs text-gray-500">Shade</Label>
          <ColorSwatch
            swatches={EYESHADOW_SWATCHES}
            selected={config.eyeshadow.color}
            onSelect={(color) =>
              update({ eyeshadow: { ...config.eyeshadow, color } })
            }
          />
          <CustomColorPicker
            color={config.eyeshadow.color}
            onChange={(color) =>
              update({ eyeshadow: { ...config.eyeshadow, color } })
            }
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-xs text-gray-500">Intensity</Label>
            <span className="text-xs text-gray-400">
              {Math.round(config.eyeshadow.intensity * 100)}%
            </span>
          </div>
          <Slider
            value={[config.eyeshadow.intensity * 100]}
            onValueChange={(val) => {
              const v = Array.isArray(val) ? val[0] : val;
              update({ eyeshadow: { ...config.eyeshadow, intensity: v / 100 } });
            }}
            min={10}
            max={100}
            step={5}
          />
        </div>
      </TabsContent>

      {/* ─── Eyeliner ─── */}
      <TabsContent value="eyeliner" className="space-y-4">
        <div className="flex items-center justify-between">
          <Label className="font-medium">Enable Eyeliner</Label>
          <Switch
            checked={config.eyeliner.enabled}
            onCheckedChange={(checked) =>
              update({ eyeliner: { ...config.eyeliner, enabled: checked } })
            }
          />
        </div>

        <div className="space-y-2">
          <Label className="text-xs text-gray-500">Color</Label>
          <ColorSwatch
            swatches={EYELINER_SWATCHES}
            selected={config.eyeliner.color}
            onSelect={(color) =>
              update({ eyeliner: { ...config.eyeliner, color } })
            }
          />
          <CustomColorPicker
            color={config.eyeliner.color}
            onChange={(color) =>
              update({ eyeliner: { ...config.eyeliner, color } })
            }
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-xs text-gray-500">Thickness</Label>
            <span className="text-xs text-gray-400">
              {config.eyeliner.thickness}px
            </span>
          </div>
          <Slider
            value={[config.eyeliner.thickness]}
            onValueChange={(val) => {
              const v = Array.isArray(val) ? val[0] : val;
              update({ eyeliner: { ...config.eyeliner, thickness: v } });
            }}
            min={1}
            max={5}
            step={1}
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-xs text-gray-500">Intensity</Label>
            <span className="text-xs text-gray-400">
              {Math.round(config.eyeliner.intensity * 100)}%
            </span>
          </div>
          <Slider
            value={[config.eyeliner.intensity * 100]}
            onValueChange={(val) => {
              const v = Array.isArray(val) ? val[0] : val;
              update({ eyeliner: { ...config.eyeliner, intensity: v / 100 } });
            }}
            min={10}
            max={100}
            step={5}
          />
        </div>

        <div className="flex items-center justify-between">
          <Label className="text-xs text-gray-500">Wing</Label>
          <Switch
            checked={config.eyeliner.wing}
            onCheckedChange={(checked) =>
              update({ eyeliner: { ...config.eyeliner, wing: checked } })
            }
          />
        </div>
      </TabsContent>
    </Tabs>
  );
}
