import tempfile
import unittest
from pathlib import Path

from trading_framework.backtest import Backtester, CSVHistoricalDataLoader
from trading_framework.strategy import Signal


class FirstBuyLastSellStrategy:
    def __init__(self):
        self.calls = 0

    def on_bar(self, close_price: float) -> Signal:
        self.calls += 1
        if self.calls == 1:
            return Signal.BUY
        if self.calls == 3:
            return Signal.SELL
        return Signal.HOLD


class BacktestFrameworkTests(unittest.TestCase):
    def test_loads_csv_and_runs_backtest(self):
        csv_data = """Date,Open,High,Low,Close,Volume
2024-01-01T00:00:00,100,105,95,101,1000
2024-01-02T00:00:00,101,107,100,106,1000
2024-01-03T00:00:00,106,108,104,107,1000
"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "candles.csv"
            csv_file.write_text(csv_data, encoding="utf-8")

            candles = CSVHistoricalDataLoader().load(csv_file)
            result = Backtester(initial_cash=1000).run(candles, FirstBuyLastSellStrategy())

        self.assertEqual(2, len(result.trades))
        self.assertEqual("BUY", result.trades[0].side)
        self.assertEqual("SELL", result.trades[1].side)
        self.assertEqual(1006.0, result.final_equity)


if __name__ == "__main__":
    unittest.main()
