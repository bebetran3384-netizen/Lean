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
### Copycat strategy that mirrors the long US equity book Warren Buffett's Berkshire Hathaway discloses in its
### quarterly SEC 13F-HR filings. See Copycat13FAlgorithm for how filings are traded.
### Foreign stakes (such as the Japanese trading houses) are not in a 13F and are not copied.
### Add each new filing to HOLDINGS_BY_FILING_DATE when it comes out.
### </summary>
### <meta name="tag" content="strategy example" />
### <meta name="tag" content="13F" />
### <meta name="tag" content="rebalancing" />
class BerkshireHathaway13FCopycatAlgorithm(Copycat13FAlgorithm):

    # Filing date -> {ticker: shares held at quarter end}, from Berkshire Hathaway 13F-HR filings on SEC EDGAR
    HOLDINGS_BY_FILING_DATE = {
        # Q2 2026 (~$299B reported): large Alphabet buy, new D.R. Horton, exited Constellation Brands,
        # trimmed Bank of America, Capital One, Kroger and Ally
        datetime(2026, 8, 14): {
            "AAPL": 227_917_808,
            "AXP": 151_610_700,
            "KO": 400_000_000,
            "GOOGL": 78_791_167,
            "BAC": 483_394_015,
            "CVX": 84_375_856,
            "OXY": 264_941_431,
            "CB": 34_249_183,
            "MCO": 24_669_778,
            "GOOG": 27_188_433,
            "KHC": 325_634_818,
            "DVA": 28_880_209,
            "DAL": 57_320_000,
            "SIRI": 124_807_117,
            "VRSN": 8_989_880,
            "KR": 39_000_000,
            "ALLY": 27_000_000,
            "LEN": 13_111_741,
            "NYT": 15_700_000,
            "COF": 3_000_000,
            "LPX": 5_664_793,
            "NUE": 1_857_752,
            "M": 7_347_426,
            "NVR": 11_112,
            "LEN.B": 298_117,
            "JEF": 433_558,
            "DHI": 3_564,
        },
    }
    START_DATE = datetime(2026, 8, 1)
    END_DATE = datetime(2026, 10, 27)
