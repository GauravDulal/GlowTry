# GlowTry

Virtual makeup try-on MVP. Upload a selfie, detect facial landmarks, apply a few deterministic makeup looks, compare before/after, and download the result.

## Tech stack

- **Frontend**: Next.js (App Router) + TypeScript + Tailwind CSS + lightweight shadcn-style UI components
- **Backend**: Python FastAPI + MediaPipe Face Landmarker (Tasks) + OpenCV + Pillow + NumPy
- **API**: REST (`/styles`, `/apply-makeup`)

## Project structure

- `frontend/` — Next.js web app
- `backend/` — FastAPI image processing service

## Local setup

### 1) Backend (FastAPI)

> On first run, the backend auto-downloads the MediaPipe Face Landmarker `.task` model.

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Check:
- `GET http://localhost:8001/health`
- `GET http://localhost:8001/styles`

### 2) Frontend (Next.js)

```bash
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

If your backend is not on `http://localhost:8001`, set `NEXT_PUBLIC_BACKEND_URL` in `frontend/.env.local`.

## How the processing pipeline works (MVP)

1. **Validate upload**: basic type/size checks (frontend and backend).
2. **Landmarks**: backend runs **MediaPipe Face Landmarker** (single-face only) to get face landmarks.
3. **Regions**:
   - **Lips**: outer lip polygon with inner “cutout” polygon
   - **Cheeks**: soft circular blush around cheek anchors
   - **Eyes**: simple eyelid/shadow polygon + subtle liner hint
4. **Deterministic overlays**: OpenCV masks + Gaussian feathering + alpha blending (no generative synthesis).
5. **Return image**: processed PNG, preserving original dimensions.

## API

### `GET /styles`

Returns available presets:

- `natural-glow`
- `soft-glam`
- `bold-lips`
- `bridal-touch`
- `party-look`

### `POST /apply-makeup`

Multipart form data:
- `image`: file
- `style`: one of the preset names (or label-like equivalents)

Responses:
- `200 image/png`: processed image
- `400`: user-friendly error (`NO_FACE_DETECTED`, `MULTIPLE_FACES_DETECTED`, `UNSUPPORTED_FORMAT`, etc.)
- `500`: processing failure

## Known MVP limitations

- **Not AR video**: single static image only (no live camera).
- **Simple region definitions**: eyes/liner are approximations; results vary with pose/occlusion.
- **Hair/hand occlusion** can confuse landmarks.
- **Lighting/skin tone diversity**: colors are fixed per preset; no per-user tone adaptation yet.
- **Single face only**: multiple faces are rejected for clarity.

## Next steps (future versions)

- Add live camera mode (WebRTC) + on-device landmarks
- Better region masks (eyeliner wing, brows, lashes) and occlusion handling
- Color adaptation by skin undertone and user preference sliders
- Face-aware smoothing/skin enhancement with safe limits
- Preset gallery and “recommend a look” logic (non-generative)

## Brand / UI notes (bonus)

- **Brand color suggestion**: Pink-to-purple gradient (`#ec4899 → #a855f7 → #3b82f6`)
- **Logo treatment**: “GT” monogram (see `frontend/src/app/icon.svg`)