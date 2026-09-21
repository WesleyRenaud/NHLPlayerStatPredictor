from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class TeamEnvironment():
   roster_quality: float
   last_season_quality: float
