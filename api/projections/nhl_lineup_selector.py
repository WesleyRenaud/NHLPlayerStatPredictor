from __future__ import annotations

from collections import defaultdict

from .nhl_lineup_row import NhlLineupRow
from ..skater_position import SkaterPosition
from ..team import Team


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
   def select( cls, rows: list[ NhlLineupRow ] ) -> list[ NhlLineupRow ]:
      by_team: dict[ Team, list[ NhlLineupRow ] ] = defaultdict( list )

      for row in rows:
         by_team[ row.team ].append( row )

      selected: list[ NhlLineupRow ] = []

      for team_rows in by_team.values():
         selected.extend(
            cls._top(
               cls._matching( team_rows, cls.FORWARD_POSITIONS ),
               cls.FORWARDS ) )
         selected.extend(
            cls._top(
               cls._matching( team_rows, cls.DEFENSE_POSITIONS ),
               cls.DEFENSE ) )

      return selected


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
