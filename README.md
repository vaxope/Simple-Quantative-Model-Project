wip project that will be a personal dashboard for trading

## How it works
Everything starts off with fetch_prices, which pulls ticker data from the S&P 500 as well as SPY, QQQ, and VOO

Next is build_features, which uses that data and calculates log returns, lagged returns, rolling volatility, rolling z_score, and rsi

This project also uses linear regression and XGBoost as the baseline models, which are both in baselines.py. To actually use these models, use run_walk_forward to run it and get_run_walk_forward_predictions to get the model's predictions. 

There's also backtesting, which tells us things like net returns, turnover, and cost and a few metrics like the Sharpe and Calmar ratio
