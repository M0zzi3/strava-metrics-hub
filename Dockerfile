FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for psycopg2 (Postgres driver)
# Sometimes 'slim' images miss C build tools, though psycopg2-binary usually works.
# If you get build errors, uncomment the next line:
# RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]