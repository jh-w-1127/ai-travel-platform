# AI Travel Platform — Chongqing MVP

## Quick Start

### 1. Start Backend (Planner API)
```bash
cd services/planner-api
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Open
- Frontend: http://localhost:3000
- API Docs: http://localhost:8001/docs
- Health: http://localhost:8001/api/health

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/planner/chat | SSE streaming chat with AI |
| GET | /api/planner/pois | List/search POIs |
| GET | /api/planner/pois/:id | POI detail |
| GET | /api/planner/itinerary/generate | Quick generate itinerary |
| GET | /api/planner/price-estimate | Price estimate |
| GET | /api/planner/transport | Transport options |
| GET | /api/health | Health check |

## Chongqing Seed Data

18 curated POIs covering:
- 7 Attractions (Hongya Cave, Jiefangbei, Ciqikou, Cableway, Nanshan, Liziba, Dazu)
- 5 Restaurants (Pipa Yuan, Dongzikou, Huashi Noodles, Chenxiang, Guanyinqiao)
- 4 Hotels (InterContinental, Niccolo, Atour, Hostel)
- 2 Experiences (Night Cruise, Jiaotong Teahouse)

## Architecture

```
frontend (Next.js 14) ──→ planner-api (FastAPI) ──→ LLM (DeepSeek/GPT-4o)
                                │
                            POI Store (in-memory)
                            (18 Chongqing POIs)
```

## Project Status

See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for full sprint progress, algorithm design decisions, and known limitations.
