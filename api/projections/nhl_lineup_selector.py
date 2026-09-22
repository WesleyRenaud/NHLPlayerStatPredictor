from __future__ import annotations

from .nhl_lineup_row import NhlLineupRow
from ..skater_position import SkaterPosition
from .team_lineup import TeamLineup


class NhlLineupSelector():
   FORWARDS = 13
   DEFENSE = 7
   FORWARD_POSITIONS = {
      SkaterPosition.CENTER,
      SkaterPosition.LEFT_WING,
      SkaterPosition.RIGHT_WING,
   }
   DEFENSE_POSITIONS = {
      SkaterPosition.DEFENSE,
   }


   @classmethod
   def select( cls, rows: list[ NhlLineupRow ] ) -> list[ TeamLineup ]:
      return [
         TeamLineup(
            lineup.team,
            [
               *cls._top(
                  cls._matching( lineup.skaters, cls.FORWARD_POSITIONS ),
                  cls.FORWARDS ),
               *cls._top(
                  cls._matching( lineup.skaters, cls.DEFENSE_POSITIONS ),
                  cls.DEFENSE ),
            ] )
         for lineup in TeamLineup.group( rows )
      ]


   @classmethod
   def _matching(
         cls,
         rows: list[ NhlLineupRow ],
         allowed: set[ SkaterPosition ] ) -> list[ NhlLineupRow ]:
      return [ row for row in rows if row.position in allowed ]


   @classmethod
   def _top(
         cls,
         rows: list[ NhlLineupRow ],
         limit: int ) -> list[ NhlLineupRow ]:
      ranked = sorted(
         rows,
         key=lambda row: ( -row.contribution, row.player_id ) )
      return ranked[ :limit ]
