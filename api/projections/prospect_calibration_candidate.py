from __future__ import annotations

from dataclasses import dataclass

from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.skater_history import SkaterHistory


@dataclass( frozen=True )
class ProspectCalibrationCandidate():
   history: SkaterHistory
   outcome: NhlSkaterSeason
