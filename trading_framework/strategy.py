from __future__ import annotations

from enum import Enum
from typing import Protocol


class Signal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Strategy(Protocol):
    def on_bar(self, close_price: float) -> Signal:
        """Return a trading signal based on the latest close price."""
