FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HF_HOME=/app/.cache/hf
WORKDIR /app

# CPU-only torch keeps the image small; sentence-transformers pulls the rest.
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt requirements-dev.txt ./
ARG DEV=0
RUN pip install --no-cache-dir -r $([ "$DEV" = "1" ] && echo requirements-dev.txt || echo requirements.txt)

COPY . .
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
