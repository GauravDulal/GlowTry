export type Style = { name: string; label: string; description: string };

function backendBaseUrl() {
  return process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8001";
}

export async function fetchStyles(): Promise<Style[]> {
  const res = await fetch(`${backendBaseUrl()}/styles`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load styles.");
  const json = (await res.json()) as { styles: Style[] };
  return json.styles ?? [];
}

export async function applyMakeup(params: {
  file: File;
  style: string;
  signal?: AbortSignal;
}): Promise<Blob> {
  const fd = new FormData();
  fd.append("image", params.file);
  fd.append("style", params.style);

  const res = await fetch(`${backendBaseUrl()}/apply-makeup`, {
    method: "POST",
    body: fd,
    signal: params.signal,
  });

  if (!res.ok) {
    let message = "Failed to process image.";
    try {
      const j: unknown = await res.json();
      if (typeof j === "object" && j !== null && "detail" in j) {
        const detail = (j as { detail: unknown }).detail;
        if (typeof detail === "string") message = detail;
        if (typeof detail === "object" && detail !== null && "message" in detail) {
          const m = (detail as { message?: unknown }).message;
          if (typeof m === "string" && m.trim()) message = m;
        }
      }
    } catch {
      // ignore
    }
    throw new Error(message);
  }

  return await res.blob();
}

