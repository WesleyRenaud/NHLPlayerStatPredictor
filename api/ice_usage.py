from __future__ import annotations

from dataclasses import dataclass

from .skater_position import SkaterPosition
from .team import Team


@dataclass( frozen=True )
class IceUsage():
   toi: float
   games: int
   team: Team
   position: SkaterPosition
