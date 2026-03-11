# GlowTry — Virtual Makeup Try-On

A web app that lets you upload a selfie and try on **lipstick, blush, eyeshadow, and eyeliner** using real computer vision — no AI filters, no CSS tricks.

![Tech Stack](https://img.shields.io/badge/Next.js-black?logo=next.js) ![Python](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![MediaPipe](https://img.shields.io/badge/MediaPipe-4285F4?logo=google&logoColor=white)

---

## Features

- 📸 Upload any selfie
- 💄 Apply lipstick (color picker, swatches, intensity, matte/glossy)
- 🌸 Apply blush (soft gradient, cheek detection)
- ✨ Apply eyeshadow (eyelid detection, tint overlay)
- ✏️ Apply eyeliner (lash line, adjustable thickness, optional wing)
- 🔀 Before / After comparison slider
- ⬇️ Download the final image
- 🔄 Reset and try again

## Tech Stack

| Layer    | Technology                                   |
| -------- | -------------------------------------------- |
| Frontend | Next.js, TypeScript, TailwindCSS, shadcn/ui  |
| Backend  | FastAPI, Python, MediaPipe FaceMesh, OpenCV   |
| CV       | 468-point face landmarks, polygon masks, alpha blending |

## Project Structure

```
glow/
├── backend/
│   ├── main.py              # FastAPI app with /health and /apply-makeup
│   ├── face_detection.py    # MediaPipe FaceMesh landmark detection
│   ├── utils.py             # Image encoding, alpha blending, mask helpers
│   ├── makeup/
│   │   ├── lipstick.py      # Lip mask + color overlay
│   │   ├── blush.py         # Cheek gradient blush
│   │   ├── eyeshadow.py     # Eyelid tint overlay
│   │   └── eyeliner.py      # Lash line drawing with optional wing
│   └── requirements.txt
├── frontend/                # Next.js app
│   └── src/
│       ├── app/page.tsx     # Main GlowTry page
│       ├── components/      # MakeupPanel, ImageUpload, BeforeAfterSlider
│       └── lib/api.ts       # Backend API client
└── README.md
```

## Quick Start

### Prerequisites

- **Python 3.10+** with `pip`
- **Node.js 18+** with `npm`

### 1. Start the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API is now running at `http://localhost:8000`. Verify with:
```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

### 3. Try It Out

1. Upload a selfie (clear, front-facing works best)
2. Enable a makeup product (e.g., Lipstick)
3. Pick a shade and adjust intensity
4. Click **Apply Makeup**
5. Use the **Before / After** slider to compare
6. **Download** the final image

## How It Works

All makeup effects are applied using **real computer vision**, not generative AI or CSS filters:

1. **MediaPipe FaceMesh** detects 468 facial landmarks
2. Landmark subsets define regions (lips, cheeks, eyelids, lash lines)
3. **Polygon masks** are created and **Gaussian-blurred** for feathered edges
4. Color is applied via **alpha blending** at user-specified intensity
5. The result preserves original skin texture for a natural look

## API Reference

### `GET /health`
Returns `{"status": "ok"}`

### `POST /apply-makeup`
- **Body**: `multipart/form-data`
  - `image`: Selfie image file (JPG/PNG)
  - `config`: JSON string with makeup settings

```json
{
  "lipstick":  { "enabled": true, "color": [200, 50, 50], "intensity": 0.6, "matte": true },
  "blush":     { "enabled": true, "color": [220, 150, 150], "intensity": 0.4 },
  "eyeshadow": { "enabled": true, "color": [160, 120, 200], "intensity": 0.4 },
  "eyeliner":  { "enabled": true, "color": [30, 30, 30], "intensity": 0.7, "thickness": 2, "wing": true }
}
```

- **Response**: `{ "status": "success", "image": "<base64 PNG>" }`

## License

MIT
