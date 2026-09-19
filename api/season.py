from __future__ import annotations

from datetime import date, datetime

from .season_length import SeasonLength
from .shared.enums.position import Position
from .team import Team


class Season():
   ISO_DATE_LENGTH = 10
   START_YEAR_DIVISOR = 10000


   @classmethod
   def start_year( cls, season_id: int ) -> int:
      return season_id // Season.START_YEAR_DIVISOR


   @classmethod
   def label( cls, season_id: int ) -> str:
      start = cls.start_year( season_id )
      return f'{ start }-{ str( start + 1 )[ Position.SECOND_LAST: ] }'


   @classmethod
   def parse_date( cls, value: str | None ) -> date | None:
      if not value:
         return None

      text = str( value )[ :Season.ISO_DATE_LENGTH ]

      try:
         return date.fromisoformat( text )
      except ValueError:
         return datetime.fromisoformat( str( value ).replace( 'Z', '+00:00' ) ).date()


   @classmethod
   def age_on( cls, birth_date: date, on_date: date ) -> float:
      return ( on_date - birth_date ).days / 365.25


   @classmethod
   def primary_team( cls, team_abbrevs: list[ Team ] ) -> Team:
      return team_abbrevs[ Position.LAST ]


   @classmethod
   def pace(
         cls,
         value: float,
         games_played: float,
         pace_games: int ) -> float:
      return value / games_played * pace_games


   @classmethod
   def pace_games( cls, seasons: list[ SeasonLength ] ) -> int:
      return sorted( seasons )[ Position.LAST ].number_of_games
