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
from Copycat13FAlgorithm import Copycat13FAlgorithm

### <summary>
### Copycat strategy that mirrors the long US equity book Peter Thiel's family office (Thiel Macro LLC)
### discloses in its quarterly SEC 13F-HR filings. See Copycat13FAlgorithm for how filings are traded.
### Update HOLDINGS_BY_FILING_DATE when a new filing comes out.
### </summary>
### <meta name="tag" content="strategy example" />
### <meta name="tag" content="13F" />
### <meta name="tag" content="rebalancing" />
class ThielMacro13FCopycatAlgorithm(Copycat13FAlgorithm):

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
    START_DATE = datetime(2025, 11, 1)
    END_DATE = datetime(2026, 10, 27)
