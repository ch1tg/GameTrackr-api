FROM python:3.12-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN addgroup --system appgroup && adduser --system --no-create-home --ingroup appgroup appuser

USER appuser

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "5000", "--workers", "4", "run:app"]