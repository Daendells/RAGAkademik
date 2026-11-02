FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HF_HOME=/app/.cache/hf
WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# The dev image adds CPU-only PyTorch for the evaluation scripts; the app image stays without it.
ARG DEV=0
RUN if [ "$DEV" = "1" ]; then       pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu &&       pip install --no-cache-dir -r requirements-dev.txt; fi

# Bake the quantised embedding model into the image so the app never downloads at runtime.
RUN python -c "from huggingface_hub import hf_hub_download as d; m='intfloat/multilingual-e5-small'; d(m, 'onnx/model_qint8_avx512_vnni.onnx'); d(m, 'onnx/sentencepiece.bpe.model')"

COPY . .
EXPOSE 7860
# Render and similar hosts pass the port in $PORT.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}
