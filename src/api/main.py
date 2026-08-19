"""Point d'entrée de l'application API du Lot D."""

from fastapi import FastAPI

from src.api.v1.agents_endpoints import router as agents_router

app = FastAPI(title="Virtual AI Manager - Lot D")
app.include_router(agents_router, prefix="/v1")


@app.get("/health")
def health():
    return {"status": "ok"}