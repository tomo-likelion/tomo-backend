from fastapi import FastAPI

app = FastAPI(
    title="TOMO API",
    description="TOMO Backend API",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }