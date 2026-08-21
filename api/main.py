from fastapi import FastAPI

app = FastAPI(title="Trading Dashboard API")

@app.get("/health")
def health():
    return {"status": "ok"}