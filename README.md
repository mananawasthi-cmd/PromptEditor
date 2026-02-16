# Prompt Editor

A Cursor-like Prompt Editor with a **Python (Flask) backend** (MVC) and **Vue.js frontend**.

## Project Structure

```
PromptEditor/
├── backend/                 # Python Flask API (MVC)
│   ├── app/
│   │   ├── models/          # Data models
│   │   ├── views/           # Response formatting
│   │   └── controllers/     # Route handlers
│   ├── run.py
│   └── requirements.txt
├── frontend/                # Vue.js SPA
│   ├── src/
│   │   ├── components/
│   │   ├── api/
│   │   └── App.vue
│   └── package.json
└── README.md
```

## MVC Structure (Backend)

- **Models** (`app/models/`): Data entities (e.g. `Prompt`)
- **Views** (`app/views/`): Format data for API responses
- **Controllers** (`app/controllers/`): Handle HTTP requests and business logic

## Setup

### Backend (Python)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

API runs at `http://localhost:5000` — endpoints: `GET/POST /api/prompts`, `GET/PUT/DELETE /api/prompts/:id`

### Frontend (Vue.js)

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173` and proxies `/api` to the backend.

## Run Both

1. Start backend: `cd backend && python run.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:5173
