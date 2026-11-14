# One container: FastAPI serves the API and the built React app.

FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
RUN useradd --create-home --uid 1000 app
WORKDIR /home/app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
USER app
# Download FinBERT at build time (same revision as sentiment_analyzer.py), then run offline,
# so the first request does not wait and the app never writes to the cache at run time.
ENV HF_HOME=/home/app/.cache/huggingface
ARG FINBERT_REVISION=0bc2ac10dda6929bcb1f77ccc43c7ec5c424f031
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('ProsusAI/finbert', revision='${FINBERT_REVISION}', allow_patterns=['*.json', '*.txt', 'model.safetensors'])"
ENV HF_HUB_OFFLINE=1
COPY --chown=app backend/app ./app
COPY --from=frontend --chown=app /frontend/dist /home/app/static
ENV STATIC_DIR=/home/app/static PORT=7860
EXPOSE 7860
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
