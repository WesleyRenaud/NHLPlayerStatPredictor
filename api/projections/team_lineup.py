from __future__ import annotations

from dataclasses import dataclass

from .nhl_lineup_row import NhlLineupRow
from ..skaters.team import Team
from .team_quality_calculator import TeamQualityCalculator


@dataclass( frozen=True )
class TeamLineup():
   team: Team
   skaters: list[ NhlLineupRow ]


   @classmethod
   def group( cls, rows: list[ NhlLineupRow ] ) -> list[ TeamLineup ]:
      teams: list[ Team ] = []

      for skater in rows:
         if skater.team not in teams:
            teams.append( skater.team )

      return [
         cls(
            team,
            [ skater for skater in rows if skater.team == team ] )
         for team in teams
      ]


   def total( self ) -> float:
      return TeamQualityCalculator.total( self.skaters )
