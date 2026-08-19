from src.pipeline import fetch_or_load_prices
from src.db.session import SessionLocal
from src.db.models import Price
import yaml
import pandas as pd

def load_prices_to_db(config_path: str = "config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Fetch/load long form df
    df = fetch_or_load_prices(config["data"])

    # Ensure data column contains native datetime.date objects 
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.date

    db = SessionLocal()
    # Iterate and merge rows
    try:
        for idx, row in df.iterrows():
            price_obj = Price(
                ticker=row["ticker"],
                date=row["date"],
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"])
            )
            db.merge(price_obj)

        db.commit()
        print(f"Loaded {len(df)} rows into database")
    except Exception as e:
        db.rollback()
        print(f"Error loading prices into database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    load_prices_to_db()

