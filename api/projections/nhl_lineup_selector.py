from __future__ import annotations

from .nhl_lineup_row import NhlLineupRow
from ..skater_group import SkaterGroup
from .team_lineup import TeamLineup


class NhlLineupSelector():
   FORWARDS = 13
   DEFENSE = 7
   DRESSED_FORWARDS = 12
   DRESSED_DEFENSE = 6


   @classmethod
   def select( cls, rows: list[ NhlLineupRow ] ) -> list[ TeamLineup ]:
      return [
         TeamLineup(
            lineup.team,
            [
               *cls._top(
                  cls.matching( lineup.skaters, SkaterGroup.FORWARD ),
                  cls.FORWARDS ),
               *cls._top(
                  cls.matching( lineup.skaters, SkaterGroup.DEFENSE ),
                  cls.DEFENSE ),
            ] )
         for lineup in TeamLineup.group( rows )
      ]


   @classmethod
   def matching(
         cls,
         rows: list[ NhlLineupRow ],
         allowed: SkaterGroup ) -> list[ NhlLineupRow ]:
      return [ row for row in rows if SkaterGroup.of( row.position ) is allowed ]


   @classmethod
   def _top(
         cls,
         rows: list[ NhlLineupRow ],
         limit: int ) -> list[ NhlLineupRow ]:
      ranked = sorted(
         rows,
         key=lambda row: ( -row.contribution, row.player_id ) )
      return ranked[ :limit ]


   @classmethod
   def forwards( cls, rows: list[ NhlLineupRow ] ) -> list[ TeamLineup ]:
      return [
         TeamLineup(
            lineup.team,
            cls._top(
               cls.matching( lineup.skaters, SkaterGroup.FORWARD ),
               cls.DRESSED_FORWARDS ) )
         for lineup in TeamLineup.group( rows )
      ]
