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
### Copycat strategy that mirrors the top 20 positions of Renaissance Technologies' quarterly SEC 13F-HR filings.
### See Copycat13FAlgorithm for how filings are traded.
###
### Renaissance reports about 3,100 positions, and the top 20 are only about 20% of the book, so this is a
### concentrated slice of it. The 13F comes from its public funds and long-only book. The Medallion fund's
### short-term trading, shorts and leverage are not visible in it, and the positions turn over far faster than
### the 45-day reporting lag, so this does not reproduce Renaissance's returns.
### Add each new filing to HOLDINGS_BY_FILING_DATE when it comes out.
### </summary>
### <meta name="tag" content="strategy example" />
### <meta name="tag" content="13F" />
### <meta name="tag" content="rebalancing" />
class RenaissanceTechnologies13FCopycatAlgorithm(Copycat13FAlgorithm):

    # Filing date -> {ticker: shares held at quarter end}, top 20 by value from Renaissance 13F-HR filings on SEC EDGAR.
    # Q4 2025 and Q1 2026 share counts are rounded and their dates are the SEC deadlines; replace them with the exact
    # EDGAR figures if they differ.
    HOLDINGS_BY_FILING_DATE = {
        # Q4 2025 (~$64.5B, 3,185 positions)
        datetime(2026, 2, 17): {
            "PLTR": 8_800_000, "UTHR": 1_900_000, "MU": 3_000_000, "KGC": 25_000_000, "VRSN": 2_800_000,
            "NFLX": 7_200_000, "TSLA": 1_400_000, "EXEL": 13_900_000, "COST": 693_002, "CVNA": 1_400_000,
            "W": 5_400_000, "RBLX": 6_600_000, "FNV": 2_500_000, "RDDT": 1_900_000, "PG": 3_000_000,
            "ABNB": 2_900_000, "INCY": 4_000_000, "HOOD": 3_400_000, "NU": 22_700_000, "INTC": 9_900_000,
        },
        # Q1 2026 (~$63.9B, 3,213 positions)
        datetime(2026, 5, 15): {
            "UTHR": 1_800_000, "PLTR": 7_000_000, "AAPL": 3_100_000, "KGC": 25_500_000, "MU": 2_200_000,
            "VRSN": 2_800_000, "EXEL": 13_700_000, "FNV": 2_200_000, "SNDK": 799_568, "NVDA": 2_500_000,
            "CVX": 2_000_000, "RBLX": 7_100_000, "CVNA": 1_200_000, "W": 5_000_000, "HOOD": 5_100_000,
            "INCY": 3_700_000, "AGX": 610_899, "INTC": 7_400_000, "NBIX": 2_400_000, "UNH": 1_200_000,
        },
        # Q2 2026 (~$72.6B, 3,140 positions): NVIDIA up to the largest position, new Meta stake
        datetime(2026, 8, 13): {
            "NVDA": 7_091_256, "META": 2_023_153, "INTC": 7_321_928, "UTHR": 1_708_739, "PLTR": 7_568_370,
            "GOOGL": 2_317_438, "EXEL": 13_427_993, "VRSN": 2_449_771, "KGC": 24_747_213, "CRWD": 748_960,
            "STRL": 672_194, "GOOG": 1_600_000, "AMZN": 2_300_000, "AGX": 648_379, "NFLX": 6_800_000,
            "CVX": 2_900_000, "TSLA": 1_100_000, "AMD": 829_697, "AAPL": 1_600_000, "CORT": 5_300_000,
        },
    }
    START_DATE = datetime(2026, 2, 1)
    END_DATE = datetime(2026, 10, 27)
