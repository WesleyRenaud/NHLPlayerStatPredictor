from __future__ import annotations

from typing import Protocol

from ..skaters.skater_position import SkaterPosition
from ..skaters.team import Team


class NhlLineupRow( Protocol ):
   player_id: int
   team: Team
   position: SkaterPosition
   contribution: float
