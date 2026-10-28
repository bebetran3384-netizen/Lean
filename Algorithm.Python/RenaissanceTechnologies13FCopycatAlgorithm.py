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
### Copycat strategy that mirrors the top 50 positions of Renaissance Technologies' quarterly SEC 13F-HR filings.
### See Copycat13FAlgorithm for how filings are traded.
###
### Renaissance reports about 3,100 positions, and the top 50 are only about 30% of the book, so this is a
### concentrated slice of it. The 13F comes from its public funds and long-only book. The Medallion fund's
### short-term trading, shorts and leverage are not visible in it, and the positions turn over far faster than
### the 45-day reporting lag, so this does not reproduce Renaissance's returns.
### Add each new filing to HOLDINGS_BY_FILING_DATE when it comes out.
### </summary>
### <meta name="tag" content="strategy example" />
### <meta name="tag" content="13F" />
### <meta name="tag" content="rebalancing" />
class RenaissanceTechnologies13FCopycatAlgorithm(Copycat13FAlgorithm):

    # Filing date -> {ticker: shares held at quarter end}, top 50 by value from Renaissance 13F-HR filings on SEC EDGAR
    # (common stock only, options excluded), with CUSIPs mapped to tickers through OpenFIGI
    HOLDINGS_BY_FILING_DATE = {
        # Q4 2025 ($64.5B, 3,185 positions; top 50 are 31.5%)
        datetime(2026, 2, 12): {
            "PLTR": 8_796_727, "UTHR": 1_909_259, "MU": 3_011_143, "KGC": 24_975_313, "VRSN": 2_779_351,
            "NFLX": 7_178_287, "TSLA": 1_362_122, "EXEL": 13_914_043, "COST": 693_002, "CVNA": 1_407_398,
            "W": 5_407_325, "RBLX": 6_628_509, "FNV": 2_478_118, "RDDT": 1_883_578, "PG": 2_986_061,
            "ABNB": 2_938_461, "INCY": 3_978_332, "HOOD": 3_435_737, "NU": 22_735_260, "INTC": 9_889_367,
            "TSM": 1_167_280, "SPOT": 591_628, "GILD": 2_788_728, "CVX": 2_191_314, "MSFT": 688_118, "F": 24_730_852,
            "RIVN": 16_397_496, "NBIX": 2_238_797, "DASH": 1_322_835, "ETSY": 5_367_442, "SNDK": 1_209_000,
            "CBOE": 1_139_406, "AMD": 1_264_310, "ZM": 3_078_504, "UNH": 796_750, "MEDP": 465_908, "ALSN": 2_599_097,
            "ADBE": 725_003, "P": 3_757_034, "STRL": 803_194, "DBX": 8_376_364, "OPEN": 39_330_438, "VRTX": 505_048,
            "BSX": 2_382_705, "GEV": 345_390, "SFM": 2_779_874, "TMUS": 1_083_807, "CL": 2_769_433, "APP": 318_821,
            "KO": 3_014_392,
        },
        # Q1 2026 ($63.9B, 3,213 positions; top 50 are 28.0%)
        datetime(2026, 5, 14): {
            "UTHR": 1_787_019, "PLTR": 6_985_926, "AAPL": 3_075_638, "KGC": 25_546_413, "MU": 2_162_986,
            "VRSN": 2_818_151, "EXEL": 13_726_993, "FNV": 2_218_918, "SNDK": 799_568, "NVDA": 2_526_948,
            "CVX": 2_015_396, "RBLX": 7_126_134, "CVNA": 1_201_218, "W": 4_972_425, "HOOD": 5_104_137,
            "INCY": 3_651_532, "AGX": 610_899, "INTC": 7_399_394, "NBIX": 2_418_897, "UNH": 1_158_428,
            "STRL": 766_914, "LIN": 629_820, "WDC": 1_146_133, "CBOE": 1_100_506, "GILD": 2_152_528,
            "ETSY": 5_962_210, "ALSN": 2_260_397, "AVGO": 793_797, "VRT": 967_990, "MEDP": 504_668, "NU": 16_269_800,
            "ABNB": 1_830_841, "NYT": 2_756_180, "MSTR": 2_130_881, "CORT": 5_682_783, "AGI": 5_118_171,
            "ADBE": 925_270, "VALE": 14_053_337, "B": 5_476_478, "P": 3_759_834, "NVMI": 510_866, "ALKS": 6_160_428,
            "DASH": 1_426_355, "RDDT": 1_565_778, "MELI": 120_320, "V": 676_767, "JPM": 688_350, "BSX": 3_152_005,
            "ZM": 2_458_804, "BTU": 5_932_627,
        },
        # Q2 2026 ($72.6B, 3,140 positions; top 50 are 31.7%)
        datetime(2026, 8, 13): {
            "NVDA": 7_091_256, "META": 2_023_153, "INTC": 7_321_928, "UTHR": 1_708_739, "PLTR": 7_568_370,
            "GOOGL": 2_317_438, "EXEL": 13_427_993, "VRSN": 2_449_771, "KGC": 24_747_213, "CRWD": 748_960,
            "STRL": 672_194, "GOOG": 1_575_815, "AMZN": 2_290_710, "AGX": 648_379, "NFLX": 6_787_884,
            "CVX": 2_870_517, "TSLA": 1_110_960, "AMD": 829_697, "AAPL": 1_586_526, "CORT": 5_261_628,
            "ETSY": 5_990_442, "STX": 457_353, "FNV": 2_036_918, "TXN": 1_402_100, "W": 4_514_426, "TSM": 849_080,
            "INCY": 3_512_132, "NBIX": 2_335_897, "RBLX": 6_814_063, "WDC": 537_473, "ALKS": 6_460_928,
            "CVNA": 5_122_450, "AVGO": 849_835, "P": 3_655_134, "GILD": 2_217_376, "DELL": 646_677, "MCK": 361_086,
            "AZO": 84_260, "TJX": 1_729_400, "RDDT": 1_450_078, "CBOE": 1_026_406, "MDT": 3_167_741, "MU": 211_580,
            "NVMI": 448_586, "CRDO": 844_238, "MSTR": 2_553_692, "ABNB": 1_542_641, "HOOD": 2_196_340,
            "MEDP": 415_588, "ALSN": 1_938_997,
        },
    }
    START_DATE = datetime(2026, 2, 1)
    END_DATE = datetime(2026, 10, 27)
