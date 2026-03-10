# GlowTry Backend (FastAPI)

Deterministic makeup overlays using **MediaPipe Face Landmarker (Tasks API)** + **OpenCV**.

## Run locally

> Note: On first run, the service auto-downloads the MediaPipe Face Landmarker `.task` model into `backend/app/assets/`.

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Endpoints:
- `GET /health`
- `GET /styles`
- `POST /apply-makeup` (multipart: `image` file, `style` string)

