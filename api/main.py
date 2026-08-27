from fastapi import FastAPI
from api.routers import prices, signals, backtests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Trading Dashboard API")

origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices.router, prefix="/api/prices", tags=["prices"])
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(backtests.router, prefix="/api/backtests", tags=["backtests"])

@app.get("/health")
def health():
    return {"status": "ok"}