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
### Copycat strategy that mirrors the long US equity book Peter Thiel's family office (Thiel Macro LLC)
### discloses in its quarterly SEC 13F-HR filings.
###
### Each snapshot holds the share counts reported for a quarter end. The algorithm only acts on a
### snapshot once its filing is public (the trading day after the filing date), which avoids look-ahead
### bias: 13F data is published up to 45 days after quarter end. On each rebalance the reported share
### counts are converted to market value weights at current prices and the whole portfolio is set to them.
### A snapshot with no holdings means the fund reported no 13F positions, and the algorithm moves to cash.
###
### Limits: a 13F only shows long US-listed positions. It omits shorts, options hedges, private holdings
### and anything bought and sold inside a quarter, so the copy always trades on stale information.
### Update HOLDINGS_BY_FILING_DATE when a new filing comes out.
### </summary>
### <meta name="tag" content="strategy example" />
### <meta name="tag" content="13F" />
### <meta name="tag" content="rebalancing" />
class ThielMacro13FCopycatAlgorithm(QCAlgorithm):

    # Filing date -> {ticker: shares held at quarter end}, from Thiel Macro LLC 13F-HR filings on SEC EDGAR.
    # Dates for the Q3 2025 to Q1 2026 filings are the SEC deadlines; replace them with the exact EDGAR dates if they differ.
    HOLDINGS_BY_FILING_DATE = {
        # Q3 2025: sold its Nvidia and Vistra stakes, cut Tesla, opened Apple and Microsoft
        datetime(2025, 11, 14): {"TSLA": 65_000, "AAPL": 79_181, "MSFT": 49_000},
        # Q4 2025: exited Apple, Microsoft and Tesla, no reported US equity holdings
        datetime(2026, 2, 17): {},
        # Q1 2026: still no reported US equity holdings
        datetime(2026, 5, 15): {},
        # Q2 2026: rebuilt around Amazon, power producers and utilities (~$418.7M reported)
        datetime(2026, 8, 14): {
            "AMZN": 495_000,
            "VIST": 1_189_792,
            "VST": 372_755,
            "AEP": 308_617,
            "DTE": 264_450,
            "FE": 839_319,
            "CMS": 517_124,
            "XE": 200_000,
        },
    }

    def initialize(self):
        self.set_start_date(2025, 11, 1)
        self.set_end_date(2026, 10, 27)
        self.set_cash(100000)
        spy = self.add_equity("SPY", Resolution.DAILY).symbol
        self.set_benchmark(spy)

        self._symbol_by_ticker = {}
        for holdings in self.HOLDINGS_BY_FILING_DATE.values():
            for ticker in holdings:
                if ticker not in self._symbol_by_ticker:
                    self._symbol_by_ticker[ticker] = self.add_equity(ticker, Resolution.DAILY).symbol

        self._pending_filing_dates = sorted(self.HOLDINGS_BY_FILING_DATE)
        self._current_filing_date = None
        self._applied_filing_date = None

        # Filings usually land after the close, so check each morning and trade at the open
        self.schedule.on(self.date_rules.every_day(spy),
                         self.time_rules.after_market_open(spy, 1),
                         self._rebalance_on_new_filing)

    def _rebalance_on_new_filing(self):
        # Pick the latest filing that was public before today
        while self._pending_filing_dates and self._pending_filing_dates[0].date() < self.time.date():
            self._current_filing_date = self._pending_filing_dates.pop(0)
        if self._current_filing_date is None or self._current_filing_date == self._applied_filing_date:
            return
        self._applied_filing_date = self._current_filing_date

        holdings = self.HOLDINGS_BY_FILING_DATE[self._current_filing_date]
        market_values = {}
        for ticker, shares in holdings.items():
            security = self.securities[self._symbol_by_ticker[ticker]]
            # Skip names without a price yet (e.g. a recent IPO missing from the data feed)
            if security.price > 0:
                market_values[security.symbol] = shares * security.price

        total_value = sum(market_values.values())
        filing = self._current_filing_date.strftime("%Y-%m-%d")
        if total_value == 0:
            self.liquidate(tag=f"13F filed {filing} reports no holdings")
            self.log(f"13F filed {filing}: no holdings, moved to cash")
            return

        targets = [PortfolioTarget(symbol, value / total_value) for symbol, value in market_values.items()]
        self.set_holdings(targets, liquidate_existing_holdings=True, tag=f"Copy 13F filed {filing}")
        weights = ", ".join(f"{symbol.value} {value / total_value:.1%}" for symbol, value in market_values.items())
        self.log(f"13F filed {filing}: {weights}")

