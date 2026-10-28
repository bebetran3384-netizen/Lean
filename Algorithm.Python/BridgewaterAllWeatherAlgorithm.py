# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from AlgorithmImports import *
from Portfolio.RiskParityPortfolioOptimizer import RiskParityPortfolioOptimizer

### <summary>
### ETF approximation of Bridgewater's All Weather strategy, which spreads risk evenly across assets that
### do well in each economic regime (rising or falling growth, rising or falling inflation) instead of
### concentrating it in stocks.
###
### Two modes, chosen with the "mode" parameter:
###   - "classic" (default): the fixed weights Ray Dalio described publicly for individual investors
###     (30% stocks, 40% long-term Treasuries, 15% intermediate Treasuries, 7.5% gold, 7.5% commodities).
###   - "risk_parity": closer to how the fund is run. Each month, weights are solved so every asset
###     contributes the same share of portfolio volatility, using the trailing year of daily returns.
###
### Bridgewater's actual fund also uses leverage, futures, inflation-linked and foreign bonds, which these
### unlevered US ETFs only approximate.
### </summary>
### <meta name="tag" content="strategy example" />
### <meta name="tag" content="risk parity" />
### <meta name="tag" content="rebalancing" />
class BridgewaterAllWeatherAlgorithm(QCAlgorithm):

    CLASSIC_WEIGHTS = {
        "VTI": 0.30,   # US stocks: rising growth
        "TLT": 0.40,   # 20+ year Treasuries: falling growth and inflation
        "IEF": 0.15,   # 7-10 year Treasuries: falling growth and inflation
        "GLD": 0.075,  # Gold: rising inflation
        "DBC": 0.075,  # Broad commodities: rising inflation and growth
    }
    LOOKBACK_DAYS = 252

    def initialize(self):
        self.set_start_date(2008, 1, 1)
        self.set_end_date(2024, 12, 31)
        self.set_cash(100000)
        self.set_benchmark("SPY")

        self._mode = self.get_parameter("mode", "classic")
        if self._mode not in ("classic", "risk_parity"):
            raise ValueError(f"Unknown mode '{self._mode}', expected 'classic' or 'risk_parity'")

        self._classic_weights = {self.add_equity(ticker, Resolution.DAILY).symbol: weight
                                 for ticker, weight in self.CLASSIC_WEIGHTS.items()}
        self._symbols = list(self._classic_weights)
        self._optimizer = RiskParityPortfolioOptimizer()

        # Rebalance once a month, as soon as the first trading day opens
        self.schedule.on(self.date_rules.month_start(self._symbols[0]),
                         self.time_rules.after_market_open(self._symbols[0], 1),
                         self._rebalance)
        self.set_warm_up(self.LOOKBACK_DAYS, Resolution.DAILY)

    def on_warmup_finished(self):
        self._rebalance()

    def _rebalance(self):
        if self.is_warming_up:
            return

        weights = self._risk_parity_weights() if self._mode == "risk_parity" else None
        if weights is None:
            weights = self._classic_weights

        self.set_holdings([PortfolioTarget(symbol, weight) for symbol, weight in weights.items()])
        self.log(f"{self._mode}: " + ", ".join(f"{symbol.value} {weight:.1%}" for symbol, weight in weights.items()))

    def _risk_parity_weights(self):
        history = self.history(self._symbols, self.LOOKBACK_DAYS + 1, Resolution.DAILY)
        if history.empty:
            return None
        available = history.index.get_level_values(0)
        # Fall back to the classic weights until every ETF has enough price history
        if any(symbol not in available for symbol in self._symbols):
            return None
        returns = pd.DataFrame({symbol: history.loc[symbol]["close"] for symbol in self._symbols}).pct_change().dropna()
        if len(returns) < self.LOOKBACK_DAYS // 2:
            return None

        weights = self._optimizer.optimize(returns)
        return dict(zip(self._symbols, weights))
