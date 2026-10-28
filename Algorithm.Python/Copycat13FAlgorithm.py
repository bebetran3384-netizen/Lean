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
### Base class for strategies that copy a fund's long US equity book from its quarterly SEC 13F-HR filings.
###
### Subclasses set HOLDINGS_BY_FILING_DATE, START_DATE and END_DATE. Each snapshot holds the share counts reported
### for a quarter end. A snapshot is only used once its filing is public (the trading day after the filing date),
### which avoids look-ahead bias: 13F data is published up to 45 days after quarter end. On each rebalance each
### reported position is valued at its raw quarter end price, carried forward by its adjusted return since then,
### and the whole portfolio is set to those market value weights. Valuing at the quarter end keeps the reported
### share counts correct when a stock splits between the quarter end and the rebalance. A snapshot with no holdings means the fund reported no 13F positions, and the algorithm moves to cash.
###
### Limits: a 13F only shows long US-listed positions. It omits shorts, options hedges, private and foreign
### holdings and anything bought and sold inside a quarter, so the copy always trades on stale information.
### </summary>
class Copycat13FAlgorithm(QCAlgorithm):

    # Filing date -> {ticker: shares held at quarter end}
    HOLDINGS_BY_FILING_DATE = {}
    START_DATE = datetime(2025, 1, 1)
    END_DATE = datetime(2025, 12, 31)

    def initialize(self):
        self.set_start_date(self.START_DATE)
        self.set_end_date(self.END_DATE)
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
        market_values = self._market_values(holdings, self._quarter_end(self._current_filing_date))

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

    def _market_values(self, holdings, quarter_end):
        symbols = [self._symbol_by_ticker[ticker] for ticker in holdings]
        if not symbols:
            return {}
        start, end = quarter_end - timedelta(10), quarter_end + timedelta(1)
        raw = self.history(symbols, start, end, Resolution.DAILY, data_normalization_mode=DataNormalizationMode.RAW)
        adjusted = self.history(symbols, start, end, Resolution.DAILY, data_normalization_mode=DataNormalizationMode.ADJUSTED)
        available = set(raw.index.get_level_values(0)) & set(adjusted.index.get_level_values(0)) if not raw.empty else set()

        market_values = {}
        for ticker, shares in holdings.items():
            security = self.securities[self._symbol_by_ticker[ticker]]
            # Skip names without prices at the quarter end and today (e.g. missing from the data feed)
            if security.symbol not in available or security.price == 0:
                self.log(f"Skipping {ticker}: no price at {quarter_end:%Y-%m-%d} or today")
                continue
            raw_close = raw.loc[security.symbol]["close"].iloc[-1]
            adjusted_close = adjusted.loc[security.symbol]["close"].iloc[-1]
            market_values[security.symbol] = shares * raw_close * security.price / adjusted_close
        return market_values

    @staticmethod
    def _quarter_end(filing_date):
        # The last day of the quarter before the one the filing was made in
        quarter_start = datetime(filing_date.year, 3 * ((filing_date.month - 1) // 3) + 1, 1)
        return quarter_start - timedelta(1)
