# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend + serve frontend
FROM python:3.12-slim
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy backend code
COPY backend/ ./
RUN chmod +x start.sh

# Copy built frontend from stage 1
COPY --from=frontend-build /app/frontend/dist ./static

ENV FLASK_APP=run:app

EXPOSE 5000

# Railway injects PORT at runtime - MUST use it
CMD ["./start.sh"]
