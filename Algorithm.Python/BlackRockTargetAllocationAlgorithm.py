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

### <summary>
### Replicates BlackRock's iShares Core allocation model portfolios (AOK, AOM, AOR, AOA) by holding their
### underlying iShares ETFs directly and rebalancing them every quarter.
###
### The "profile" parameter picks the stock/bond mix:
###   conservative (AOK, 30/70), moderate (AOM, 40/60), growth (AOR, 60/40, default), aggressive (AOA, 80/20).
###
### The split inside each sleeve comes from AOR's holdings as of February 28, 2026, and is applied to every
### profile, so the other profiles are approximations. Refresh EQUITY_SLEEVE and BOND_SLEEVE from BlackRock's
### fund pages to track the current model.
### </summary>
### <meta name="tag" content="strategy example" />
### <meta name="tag" content="asset allocation" />
### <meta name="tag" content="rebalancing" />
class BlackRockTargetAllocationAlgorithm(QCAlgorithm):

    EQUITY_SHARE_BY_PROFILE = {
        "conservative": 0.30,
        "moderate": 0.40,
        "growth": 0.60,
        "aggressive": 0.80,
    }
    # Weights inside each sleeve, from AOR holdings (stocks 60.4%, bonds 39.2%), normalized to 1
    EQUITY_SLEEVE = {
        "IVV": 31.5,   # S&P 500
        "IJH": 2.0,    # S&P mid cap 400
        "IJR": 0.8,    # S&P small cap 600
        "IEFA": 19.0,  # Developed markets ex US
        "IEMG": 7.1,   # Emerging markets
    }
    BOND_SLEEVE = {
        "IUSB": 33.4,  # Total USD bond market
        "IAGG": 5.8,   # International aggregate bonds, USD hedged
    }

    def initialize(self):
        self.set_start_date(2016, 1, 1)
        self.set_end_date(2024, 12, 31)
        self.set_cash(100000)
        self.set_benchmark("SPY")

        profile = self.get_parameter("profile", "growth")
        if profile not in self.EQUITY_SHARE_BY_PROFILE:
            raise ValueError(f"Unknown profile '{profile}', expected one of {list(self.EQUITY_SHARE_BY_PROFILE)}")
        self._profile = profile

        equity_share = self.EQUITY_SHARE_BY_PROFILE[profile]
        weights = {**self._scale(self.EQUITY_SLEEVE, equity_share), **self._scale(self.BOND_SLEEVE, 1 - equity_share)}
        self._targets = [PortfolioTarget(self.add_equity(ticker, Resolution.DAILY).symbol, weight)
                         for ticker, weight in weights.items()]

        # Rebalance at the start of each quarter
        first = self._targets[0].symbol
        self.schedule.on(self.date_rules.month_start(first),
                         self.time_rules.after_market_open(first, 1),
                         self._rebalance)

    def on_data(self, data):
        # Invest on the first day with data instead of waiting for the next quarter
        if not self.portfolio.invested:
            self._rebalance(force=True)

    def _rebalance(self, force=False):
        if not force and self.time.month not in (1, 4, 7, 10):
            return
        self.set_holdings(self._targets)
        self.log(f"{self._profile}: " + ", ".join(f"{t.symbol.value} {t.quantity:.1%}" for t in self._targets))

    @staticmethod
    def _scale(sleeve, share):
        total = sum(sleeve.values())
        return {ticker: share * weight / total for ticker, weight in sleeve.items()}
