from __future__ import annotations

from dataclasses import dataclass

from .last_season_skater import LastSeasonSkater
from ..team import Team


@dataclass( frozen=True )
class LastSeasonNhlSkater( LastSeasonSkater ):
   team: Team
