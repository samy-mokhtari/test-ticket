from fastapi import FastAPI

app = FastAPI(
    title="Ticket API",
    description="REST API for managing support tickets.",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Return the current health status of the API."""
    return {"status": "ok"}
