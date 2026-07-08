"""
FastAPI-Backend für die hybride Kompetenzformulierungs-Analyse.

Startet den Server mit:
    uvicorn main:app --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager
from dataclasses import asdict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pipeline import AnalysisPipeline

pipeline = AnalysisPipeline()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lädt alle Modelle beim Serverstart."""
    pipeline.load()
    yield


app = FastAPI(
    title="Kompetenzeditor Analyse-Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool


@app.get("/health")
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        models_loaded=pipeline.nlp is not None,
    )


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Analysiert einen Text (ein oder mehrere Sätze) mit der Hybrid-Cascading-Pipeline.

    Gibt pro Satz zurück: Typ (K/I/S), Taxonomiestufe (1-6), Konfidenz,
    Quelle (regel/embedding), erkannte Verben, ähnliche Formulierungen.
    """
    result = pipeline.analyze(request.text)
    return asdict(result)
