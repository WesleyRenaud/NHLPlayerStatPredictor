from __future__ import annotations

from dataclasses import dataclass

from .previous_season_skater import PreviousSeasonSkater
from ..team import Team


@dataclass( frozen=True )
class PreviousSeasonNhlSkater( PreviousSeasonSkater ):
   team: Team
