import pytest
import time
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

# Regression test to ensure background task run_and_save executes fully
def test_backtest_pipeline_completes_without_errors():
    
    # Trigger the backtest via POST
    payload = {
        "run_name": "regression_test_run",
        "tickers": ["AAPL", "MSFT"],
        "model_name": "xgb",
        "cost_bps": 5.0
    }
    
    post_response = client.post("/api/backtests/", json=payload)
    assert post_response.status_code == 200, f"POST failed: {post_response.text}"
    
    run_data = post_response.json()
    run_id = run_data["id"]
    
    # Initial status should be "running" right after creation
    assert run_data["status"] == "running"
    
    # Poll the GET endpoint until the status is no longer "running"
    max_retries = 30
    poll_interval = 1.0  # seconds
    
    for _ in range(max_retries):
        get_response = client.get(f"/api/backtests/{run_id}")
        assert get_response.status_code == 200
        
        current_data = get_response.json()
        if current_data["status"] != "running":
            break
            
        time.sleep(poll_interval)
        
    final_data = get_response.json()
    
    # Assert the regression fix holds
    # If the NameError or pd import bug was still there, the except block 
    # in run_and_save would have caught it and set status to "failed".
    assert final_data["status"] == "completed", f"Pipeline failed: {final_data.get('error_message')}"
    
    # Verify the specific fields that were previously crashing the app are properly populated
    assert final_data.get("start_date") is not None, "start_date was not saved"
    assert final_data.get("end_date") is not None, "end_date was not saved"
    assert final_data.get("sharpe") is not None, "metrics were not saved"