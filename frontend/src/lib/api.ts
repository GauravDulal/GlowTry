/**
 * API client for the GlowTry backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface MakeupConfig {
  lipstick: {
    enabled: boolean;
    color: [number, number, number]; // RGB
    intensity: number;
    matte: boolean;
  };
  blush: {
    enabled: boolean;
    color: [number, number, number];
    intensity: number;
  };
  eyeshadow: {
    enabled: boolean;
    color: [number, number, number];
    intensity: number;
  };
  eyeliner: {
    enabled: boolean;
    color: [number, number, number];
    intensity: number;
    thickness: number;
    wing: boolean;
  };
}

export const DEFAULT_CONFIG: MakeupConfig = {
  lipstick: {
    enabled: false,
    color: [180, 60, 60],
    intensity: 0.5,
    matte: true,
  },
  blush: {
    enabled: false,
    color: [220, 150, 150],
    intensity: 0.4,
  },
  eyeshadow: {
    enabled: false,
    color: [160, 120, 200],
    intensity: 0.4,
  },
  eyeliner: {
    enabled: false,
    color: [30, 30, 30],
    intensity: 0.7,
    thickness: 2,
    wing: false,
  },
};

export interface ApplyMakeupResponse {
  status?: string;
  image: string; // base64 PNG
  error?: string;
}

export async function applyMakeup(
  imageFile: File,
  config: MakeupConfig
): Promise<ApplyMakeupResponse> {
  const formData = new FormData();
  formData.append("image", imageFile);
  formData.append("config", JSON.stringify(config));

  const response = await fetch(`${API_BASE}/apply-makeup`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `Server error: ${response.status}`);
  }

  return response.json();
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    const data = await response.json();
    return data.status === "ok";
  } catch {
    return false;
  }
}
