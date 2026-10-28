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

    # Filing date -> {ticker: shares held at quarter end}, every common stock position in Berkshire Hathaway's
    # 13F-HR filings on SEC EDGAR
    HOLDINGS_BY_FILING_DATE = {
        # Q3 2025 ($267.3B, 41 positions)
        datetime(2025, 11, 14): {
            "AAPL": 238_212_764, "AXP": 151_610_700, "BAC": 568_070_012, "KO": 400_000_000, "CVX": 122_064_792,
            "OXY": 264_941_431, "MCO": 24_669_778, "CB": 31_332_895, "KHC": 325_634_818, "GOOGL": 17_846_142,
            "DVA": 32_160_579, "KR": 50_000_000, "SIRI": 124_807_117, "V": 8_297_460, "VRSN": 8_989_880,
            "MA": 3_986_648, "AMZN": 10_000_000, "STZ": 13_400_000, "UNH": 5_039_564, "COF": 7_150_000,
            "AON": 4_100_000, "DPZ": 2_981_945, "ALLY": 29_000_000, "POOL": 3_458_885, "LLYVK": 10_917_661,
            "LEN": 7_050_950, "NUE": 6_407_749, "LPX": 5_664_793, "LLYVA": 4_986_588, "HEI.A": 1_294_612,
            "FWONK": 3_018_555, "CHTR": 1_060_882, "LAMR": 1_202_110, "ALLE": 780_133, "NVR": 11_112, "JEF": 433_558,
            "LILA": 2_630_792, "DEO": 227_750, "LEN.B": 180_980, "LILAK": 1_284_020, "BATRK": 223_645,
        },
        # Q4 2025 ($274.2B, 42 positions): trimmed Apple, Bank of America and Chevron
        datetime(2026, 2, 17): {
            "AAPL": 227_917_808, "AXP": 151_610_700, "BAC": 517_295_934, "KO": 400_000_000, "CVX": 130_156_362,
            "MCO": 24_669_778, "OXY": 264_941_431, "CB": 34_249_183, "KHC": 325_634_818, "GOOGL": 17_846_142,
            "DVA": 31_759_065, "KR": 50_000_000, "V": 8_297_460, "SIRI": 124_807_117, "MA": 3_986_648,
            "VRSN": 8_989_880, "STZ": 13_000_000, "COF": 7_150_000, "UNH": 5_039_564, "DPZ": 3_350_000,
            "ALLY": 29_000_000, "AON": 3_602_995, "NUE": 6_407_749, "LLYVK": 10_917_661, "LEN": 7_050_950,
            "POOL": 3_068_885, "AMZN": 2_276_000, "LPX": 5_664_793, "LLYVA": 4_986_588, "NYT": 5_065_744,
            "HEI.A": 1_294_612, "FWONK": 3_018_555, "CHTR": 1_060_882, "LAMR": 1_202_410, "ALLE": 780_133,
            "NVR": 11_112, "JEF": 433_558, "DEO": 227_750, "LILA": 2_396_665, "LEN.B": 180_980, "LILAK": 1_284_020,
            "BATRK": 115_428,
        },
        # Q1 2026 ($263.1B, 29 positions): tripled Alphabet, new Delta stake, sold most of Constellation Brands
        datetime(2026, 5, 15): {
            "AAPL": 227_917_808, "AXP": 151_610_700, "KO": 400_000_000, "BAC": 513_624_165, "CVX": 84_375_856,
            "OXY": 264_941_431, "GOOGL": 54_249_798, "CB": 34_249_183, "MCO": 24_669_778, "KHC": 325_634_818,
            "DVA": 30_100_585, "KR": 50_000_000, "SIRI": 124_807_117, "DAL": 39_809_456, "VRSN": 8_989_880,
            "COF": 7_150_000, "NYT": 15_146_535, "ALLY": 29_000_000, "GOOG": 3_585_215, "LLYVK": 10_587_143,
            "LEN": 10_099_642, "NUE": 3_907_075, "LLYVA": 4_986_588, "LPX": 5_664_793, "STZ": 632_890, "NVR": 11_112,
            "M": 3_038_355, "LEN.B": 237_703, "JEF": 433_558,
        },
        # Q2 2026 ($299.3B, 29 positions): large Alphabet buy, new D.R. Horton, exited Constellation Brands
        datetime(2026, 8, 14): {
            "AAPL": 227_917_808, "AXP": 151_610_700, "KO": 400_000_000, "GOOGL": 78_791_167, "BAC": 483_394_015,
            "CVX": 84_375_856, "OXY": 264_941_431, "CB": 34_249_183, "MCO": 24_669_778, "GOOG": 27_188_433,
            "KHC": 325_634_818, "DVA": 28_880_209, "DAL": 57_320_000, "SIRI": 124_807_117, "VRSN": 8_989_880,
            "KR": 39_000_000, "ALLY": 27_000_000, "LEN": 13_111_741, "LLYVK": 10_587_143, "NYT": 15_700_000,
            "COF": 3_000_000, "LLYVA": 4_986_588, "LPX": 5_664_793, "NUE": 1_857_752, "M": 7_347_426, "NVR": 11_112,
            "LEN.B": 298_117, "JEF": 433_558, "DHI": 3_564,
        },
    }
    START_DATE = datetime(2025, 11, 1)
    END_DATE = datetime(2026, 10, 27)
