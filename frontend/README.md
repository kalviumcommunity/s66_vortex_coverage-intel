# Coverage Intel — Frontend Application

This directory hosts the dedicated frontend application for **Coverage Intel**.

## Architecture & Layout

- **`src/`**: Modern React application structured for scalable component development.
  - `src/services/api.js`: Type-safe fetch client talking to FastAPI `/ask`, `/documents`, and `/health`.
  - `src/App.jsx`: Primary application shell and multi-surface state manager.
  - `src/styles.css`: High-contrast enterprise design tokens.
- **`legacy/` or `public/`**: Contains the standalone HTML/JS build for immediate offline static serving via FastAPI.

## Development Setup (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server will run on `http://localhost:3000` with automated proxying of API requests to `http://127.0.0.1:8000`.
