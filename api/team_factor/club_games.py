from __future__ import annotations

from dataclasses import dataclass

from ..skaters.team import Team


@dataclass( frozen=True )
class ClubGames():
   team: Team
   games: int
