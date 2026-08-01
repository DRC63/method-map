# Stage 1: build the React frontend
FROM node:22-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Base path the SPA is built under. Default '/' (root deploy). Render passes the
# service's APP_BASE env var as a build arg, so setting APP_BASE=/prince2/ (or
# /msp/) makes this build serve behind the shared apps.p3mai.com front door.
ARG APP_BASE=/
ENV APP_BASE=$APP_BASE
RUN npm run build

# Stage 2: Python backend, serving the built frontend from Stage 1
FROM python:3.12-slim
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
