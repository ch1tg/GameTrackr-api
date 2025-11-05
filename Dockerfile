FROM python:3.12-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN addgroup --system appgroup && adduser --system --no-create-home --ingroup appgroup appuser

USER appuser

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "run:app"]