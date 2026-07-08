FROM python:3.11-slim

WORKDIR /app

# System-Deps für scipy/numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python-Deps installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# spaCy-Modell herunterladen
RUN python -m spacy download de_core_news_lg

# SBERT-Modell vorab cachen (wird beim ersten encode() geladen)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('T-Systems-onsite/cross-en-de-roberta-sentence-transformer')"

# Anwendungscode kopieren
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
