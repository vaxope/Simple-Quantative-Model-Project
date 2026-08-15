from pathlib import Path
import pandas as pd
import yfinance as yf

from src.data.fetch_prices import get_sp500_tickers, fetch_prices
from src.data.features.build_features import (
    load_prices_long,
    add_log_returns,
    add_lagged_returns,
    add_log_rolling_volatility,
    add_rolling_z_score,
    add_rsi,
)
from src.data.targets.build_targets import add_volatility_target
from src.models.baselines import linear_baseline, xgb_baseline
from src.backtest.position_sizing import compute_position_size
from src.backtest.backtest import run_backtest, compute_backtest_metrics
from src.models.evaluation import get_walk_forward_predictions, run_walk_forward, evaluate_predictions

MODEL_REGISTRY = {
    "linear": linear_baseline,
    "xgb": xgb_baseline
}


def fetch_or_load_prices(config: dict) -> pd.DataFrame:
    price_path = Path(config.get("price_path", "data/raw_prices.parquet"))    
    force_download = config.get("force_download", False)

    # Chooses what tickers to get
    use_sp500 = config.get("use_sp500", False)
    if use_sp500:
        sp500_ticks = get_sp500_tickers()
        extra_etfs = config.get("etfs", ["SPY", "QQQ", "VOO"])
        tickers = list(set(extra_etfs + sp500_ticks))
    else:
        tickers = config.get("tickers", ["SPY", "QQQ", "VOO", "NVDA", "MSFT", "AAPL"])

    start_date = config.get("start_date", "2018-01-01")
    end_date = config.get("end_date", "2026-08-01")

    # Load prices if available
    if price_path.exists() and not force_download:
        return load_prices_long(str(price_path), tickers)

    
    # Fetches and downloads ticker data
    df_raw = fetch_prices(tickers, start=start_date, end=end_date)
    price_path.parent.mkdir(parents=True, exist_ok=True)
    df_raw.to_parquet(price_path)
    df = load_prices_long(str(price_path), tickers)

    # Date bounds filter
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

    return df.reset_index(drop=True)

# Attaches every feature column config asks for
def build_feature_frame(config: dict) -> pd.DataFrame:
    df = fetch_or_load_prices(config["data"])
    df = add_log_returns(df)
    df = add_lagged_returns(df, lags=config["features"]["lags"])
    df = add_log_rolling_volatility(df, windows=config["features"]["vol_windows"])
    df = add_rolling_z_score(df, windows=config["features"]["zscore_windows"])
    df = add_rsi(df, windows=config["features"]["rsi_windows"])
    return df

def build_target_frame(df, config: dict) -> pd.DataFrame:
    target_type = config["target"]["type"]
    horizons = config["target"]["horizons"]

    df = add_volatility_target(df, horizons=horizons)
    target_col = f"target_vol_{horizons[0]}d"
    return df, target_col

def get_feature_cols(config: dict) -> list[str]:
    cols = []
    cols += [f"return{l}d" for l in config["features"]["lags"]]
    cols += [f"vol_{w}d" for w in config["features"]["vol_windows"]]
    cols += [f"z_{w}d" for w in config["features"]["zscore_windows"]]
    cols += [f"rsi_{w}d" for w in config["features"]["rsi_windows"]]
    return cols

def run_full_pipeline(config: dict) -> dict:
    df = build_feature_frame(config)
    df, target_col = build_target_frame(df, config)
    feature_cols = get_feature_cols(config)

    model_name = config["model"]["name"]
    if model_name not in MODEL_REGISTRY:
        raise ValueError(
            f"Unknown Model {model_name}. Options: {list(MODEL_REGISTRY)}"
        )

    model_factory = MODEL_REGISTRY[model_name]

    preds = get_walk_forward_predictions(
        df,
        feature_cols,
        target_col,
        model_factory,
        train_size = config["model"]["train_size"],
        test_size = config["model"]["test_size"],
        step = config["model"]["step"]
    )

    preds["position"] = compute_position_size(
        preds["predicted_log_vol"],
        target_vol = config["position_sizing"]["target_vol"],
        max_leverage = config["position_sizing"]["max_leverage"]
    )

    # run_backtest expects 'return', name it 'log_return' so rename on thew ay in rather than chaning entire function contract 
    bt_input = preds[["ticker", "date", "log_return", "position"]].rename(
        columns={"log_return": "return"}
    )

    backtest_results = run_backtest(
        bt_input,
        position_col="position",
        return_col="return",
        cost_bps=config["backtest"]["cost_bps"],
    )

    metrics = compute_backtest_metrics(
        backtest_results["net_return"],
        periods_per_year=config["backtest"]["periods_per_year"],
    )

    return {
        "predictions": preds,
        "backtest_results": backtest_results,
        "metrics": metrics,
    }