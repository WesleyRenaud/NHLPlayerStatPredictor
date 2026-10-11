from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class ProductionKeepBand():
   relative_slope_below: float
   kept_share: float
