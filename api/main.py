from fastapi import FastAPI
from api.routers import prices, signals, backtests


app = FastAPI(title="Trading Dashboard API")

app.include_router(prices.router, prefix="/api/prices", tags=["prices"])
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(backtests.router, prefix="/api/backtests", tags=["backtests"])

@app.get("/health")
def health():
    return {"status": "ok"}