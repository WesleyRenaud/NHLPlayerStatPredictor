from __future__ import annotations

from dataclasses import dataclass

from .scoring_paces import ScoringPaces


@dataclass( frozen=True )
class PaceValues( ScoringPaces ):
   penalty_minutes: float | None
   shots: float | None = None
