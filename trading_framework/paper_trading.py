from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Protocol

from .strategy import Signal, Strategy


class QuoteProvider(Protocol):
    def get_last_price(self, symbol: str) -> float:
        """Return the latest market price for a symbol."""


class YahooQuoteProvider:
    """Simple quote provider based on Yahoo Finance public quote endpoint."""

    def get_last_price(self, symbol: str) -> float:
        query = urllib.parse.urlencode({"symbols": symbol})
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?{query}"
        with urllib.request.urlopen(url, timeout=10) as response:  # nosec B310
            payload = json.loads(response.read().decode("utf-8"))

        results = payload.get("quoteResponse", {}).get("result", [])
        if not results:
            raise ValueError(f"No quote returned for symbol {symbol!r}")

        price = results[0].get("regularMarketPrice")
        if price is None:
            raise ValueError(f"Quote missing price for symbol {symbol!r}")

        return float(price)


@dataclass(frozen=True)
class Order:
    timestamp: datetime
    symbol: str
    side: str
    quantity: int
    fill_price: float


class PaperBroker:
    """Paper broker that tracks virtual cash, positions, and order history."""

    def __init__(self, starting_cash: float = 10_000.0):
        self.cash = starting_cash
        self.positions: Dict[str, int] = {}
        self.orders: list[Order] = []

    def buy(self, symbol: str, quantity: int, price: float) -> Order:
        cost = quantity * price
        if cost > self.cash:
            raise ValueError("Insufficient cash for paper trade")

        self.cash -= cost
        self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        order = Order(datetime.now(timezone.utc), symbol, "BUY", quantity, price)
        self.orders.append(order)
        return order

    def sell(self, symbol: str, quantity: int, price: float) -> Order:
        held = self.positions.get(symbol, 0)
        if quantity > held:
            raise ValueError("Insufficient position for paper trade")

        self.cash += quantity * price
        new_qty = held - quantity
        if new_qty:
            self.positions[symbol] = new_qty
        else:
            self.positions.pop(symbol, None)

        order = Order(datetime.now(timezone.utc), symbol, "SELL", quantity, price)
        self.orders.append(order)
        return order

    def account_equity(self, latest_prices: Dict[str, float]) -> float:
        position_value = sum(qty * latest_prices.get(sym, 0.0) for sym, qty in self.positions.items())
        return self.cash + position_value


class PaperTradingEngine:
    """Runs strategy decisions against live quotes while executing only paper trades."""

    def __init__(self, symbol: str, strategy: Strategy, quote_provider: QuoteProvider, broker: PaperBroker):
        self.symbol = symbol
        self.strategy = strategy
        self.quote_provider = quote_provider
        self.broker = broker

    def run_once(self) -> Signal:
        price = self.quote_provider.get_last_price(self.symbol)
        signal = self.strategy.on_bar(price)

        if signal == Signal.BUY:
            self.broker.buy(self.symbol, quantity=1, price=price)
        elif signal == Signal.SELL and self.broker.positions.get(self.symbol, 0) > 0:
            self.broker.sell(self.symbol, quantity=1, price=price)

        return signal
