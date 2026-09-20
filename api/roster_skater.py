from __future__ import annotations

from dataclasses import dataclass

from .skater_position import SkaterPosition
from .team import Team


@dataclass( frozen=True )
class RosterSkater():
   player_id: int
   player_name: str
   position: SkaterPosition
   team: Team
