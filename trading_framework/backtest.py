from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from .strategy import Signal, Strategy


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Trade:
    timestamp: datetime
    side: str
    quantity: int
    price: float


@dataclass(frozen=True)
class BacktestResult:
    starting_cash: float
    ending_cash: float
    open_shares: int
    final_equity: float
    trades: List[Trade]
    equity_curve: List[float]


class CSVHistoricalDataLoader:
    """Loads OHLCV candles from CSV files with Date/Open/High/Low/Close/Volume columns."""

    def load(self, csv_path: str | Path) -> List[Candle]:
        path = Path(csv_path)
        candles: List[Candle] = []
        with path.open("r", newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                timestamp = datetime.fromisoformat(row["Date"])
                candles.append(
                    Candle(
                        timestamp=timestamp,
                        open=float(row["Open"]),
                        high=float(row["High"]),
                        low=float(row["Low"]),
                        close=float(row["Close"]),
                        volume=float(row["Volume"]),
                    )
                )

        candles.sort(key=lambda item: item.timestamp)
        return candles


class Backtester:
    """Beginner-friendly long-only backtester with fixed one-share market orders."""

    def __init__(self, initial_cash: float = 10_000.0, commission_per_trade: float = 0.0):
        self.initial_cash = initial_cash
        self.commission_per_trade = commission_per_trade

    def run(self, candles: List[Candle], strategy: Strategy) -> BacktestResult:
        cash = self.initial_cash
        shares = 0
        trades: List[Trade] = []
        equity_curve: List[float] = []

        for candle in candles:
            signal = strategy.on_bar(candle.close)

            if signal == Signal.BUY and cash >= candle.close + self.commission_per_trade:
                cash -= candle.close + self.commission_per_trade
                shares += 1
                trades.append(Trade(candle.timestamp, "BUY", 1, candle.close))
            elif signal == Signal.SELL and shares > 0:
                cash += candle.close - self.commission_per_trade
                shares -= 1
                trades.append(Trade(candle.timestamp, "SELL", 1, candle.close))

            equity_curve.append(cash + shares * candle.close)

        final_price = candles[-1].close if candles else 0.0
        final_equity = cash + shares * final_price

        return BacktestResult(
            starting_cash=self.initial_cash,
            ending_cash=cash,
            open_shares=shares,
            final_equity=final_equity,
            trades=trades,
            equity_curve=equity_curve,
        )
