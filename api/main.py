from fastapi import FastAPI
from api.routers import prices

app = FastAPI(title="Trading Dashboard API")
app.include_router(prices.router, prefix="/api/prices", tags=["prices"])
app.include_router(prices.router, prefix="/api/signals", tags=["signals"])

@app.get("/health")
def health():
    return {"status": "ok"}