# Finance-Algo-Test

Beginner-friendly framework for building a trading algorithm with:

- **Backtesting** against real historical OHLCV CSV data
- **Paper trading** against live market quotes (no real order execution)

## Project structure

- `/trading_framework/backtest.py` - historical data loader + simple backtester
- `/trading_framework/paper_trading.py` - live quote integration + paper broker
- `/trading_framework/strategy.py` - strategy interface and `BUY/SELL/HOLD` signals
- `/tests` - focused unit tests for framework behavior

## Quick start

### 1) Backtest a strategy on historical data

Historical CSV format must include:

`Date,Open,High,Low,Close,Volume`

Example strategy shape:

```python
from trading_framework.strategy import Signal

class MyStrategy:
    def on_bar(self, close_price: float) -> Signal:
        if close_price < 100:
            return Signal.BUY
        if close_price > 110:
            return Signal.SELL
        return Signal.HOLD
```

Run with:

```python
from trading_framework.backtest import Backtester, CSVHistoricalDataLoader

candles = CSVHistoricalDataLoader().load("historical_data.csv")
result = Backtester(initial_cash=10_000).run(candles, MyStrategy())
print(result.final_equity, len(result.trades))
```

### 2) Paper trade the live market

`YahooQuoteProvider` reads live quotes from Yahoo Finance's public quote API.

```python
from trading_framework.paper_trading import PaperBroker, PaperTradingEngine, YahooQuoteProvider

broker = PaperBroker(starting_cash=10_000)
engine = PaperTradingEngine(
    symbol="AAPL",
    strategy=MyStrategy(),
    quote_provider=YahooQuoteProvider(),
    broker=broker,
)

engine.run_once()  # fetches latest quote, generates signal, places paper order if needed
```

## Run tests

```bash
python -m unittest discover -s tests
```
