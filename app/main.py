from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.recipients import router as recipients_router

app = FastAPI(
    title="TOMO API",
    description="TOMO Backend API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(recipients_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
