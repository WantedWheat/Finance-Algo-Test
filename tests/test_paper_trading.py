import unittest

from trading_framework.paper_trading import PaperBroker, PaperTradingEngine
from trading_framework.strategy import Signal


class ConstantPriceProvider:
    def __init__(self, price: float):
        self.price = price

    def get_last_price(self, symbol: str) -> float:
        return self.price


class BuySignalStrategy:
    def on_bar(self, close_price: float) -> Signal:
        return Signal.BUY


class PaperTradingFrameworkTests(unittest.TestCase):
    def test_engine_executes_buy_order_for_buy_signal(self):
        broker = PaperBroker(starting_cash=100)
        engine = PaperTradingEngine(
            symbol="AAPL",
            strategy=BuySignalStrategy(),
            quote_provider=ConstantPriceProvider(price=10),
            broker=broker,
        )

        signal = engine.run_once()

        self.assertEqual(Signal.BUY, signal)
        self.assertEqual(90, broker.cash)
        self.assertEqual(1, broker.positions["AAPL"])
        self.assertEqual(1, len(broker.orders))

    def test_broker_rejects_buy_when_cash_is_insufficient(self):
        broker = PaperBroker(starting_cash=5)

        with self.assertRaises(ValueError):
            broker.buy("AAPL", quantity=1, price=10)


if __name__ == "__main__":
    unittest.main()
