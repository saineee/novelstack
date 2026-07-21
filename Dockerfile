FROM python:3.12-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y curl
RUN curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
RUN chmod +x tailwindcss-linux-x64

COPY tailwind/ ./tailwind/
COPY templates/ ./templates/
COPY books/ ./books/
COPY library/ ./library/
COPY users/ ./users/

RUN ./tailwindcss-linux-x64 -i tailwind/input.css -o static/css/output.css --minify

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY --from=builder /app/static/css/output.css ./static/css/output.css

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "novelstack.wsgi:application", "--bind", "0.0.0.0:8000"]