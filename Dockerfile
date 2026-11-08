# One container: FastAPI serves the API and the built React app.

FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
RUN useradd --create-home app
WORKDIR /home/app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
USER app
# Download FinBERT at build time so the first request does not wait for it.
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='ProsusAI/finbert')"
COPY --chown=app backend/app ./app
COPY --from=frontend --chown=app /frontend/dist /home/app/static
ENV STATIC_DIR=/home/app/static PORT=7860
EXPOSE 7860
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
