FROM python:3.11-slim AS builder

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home appuser
WORKDIR /code

COPY --from=builder /root/.local /home/appuser/.local
COPY . .

RUN chown -R appuser:appuser /code
USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]