from __future__ import annotations

from .season_length import SeasonLength
from .shared.enums.position import Position
from .skaters.team import Team


class Season():
   @classmethod
   def start_year( cls, season_id: int ) -> int:
      return season_id // 10000


   @classmethod
   def years( cls, season_id: int ) -> tuple[ int, int ]:
      text = str( season_id )
      first_year = int( text[ :4 ] )
      second_year = int( text[ 4: ] )
      return first_year, second_year


   @classmethod
   def from_years( cls, first_year: int, second_year: int ) -> int:
      return int( f'{ first_year }{ second_year }' )


   @classmethod
   def age_in_year( cls, age: int, from_year: int, to_year: int ) -> int:
      return age + to_year - from_year


   @classmethod
   def recency_lag( cls, target_season_id: int, season_id: int ) -> int:
      return cls.start_year( target_season_id ) - cls.start_year( season_id ) - 1


   @classmethod
   def season_before( cls, projection_season_id: int ) -> int:
      first_year, second_year = cls.years( projection_season_id )
      previous_first_year = first_year - 1
      previous_second_year = second_year - 1
      return cls.from_years( previous_first_year, previous_second_year )


   @classmethod
   def label( cls, season_id: int ) -> str:
      start = cls.start_year( season_id )
      return f'{ start }-{ str( start + 1 )[ Position.SECOND_LAST: ] }'


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
   def latest( cls, seasons: list[ SeasonLength ] ) -> SeasonLength:
      return sorted( seasons )[ Position.LAST ]


   @classmethod
   def prior( cls, seasons: list[ SeasonLength ] ) -> SeasonLength:
      return sorted( seasons )[ Position.SECOND_LAST ]


   @classmethod
   def pace_games( cls, seasons: list[ SeasonLength ] ) -> int:
      return cls.latest( seasons ).number_of_games
