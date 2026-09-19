from __future__ import annotations

from .paths import Paths
from .season import Season
from .shared.enums.position import Position
from .skater_key import SkaterKey
from .skater_season import SkaterSeason
from .skater_season_provider import SkaterSeasonProvider


class SkaterSeasonFinder():
   @classmethod
   def main( cls, query: str ) -> None:
      rows = SkaterSeasonProvider.seasons_for_name( query, str( Paths.DB_PATH ) )

      if not rows:
         print( f'No skater-seasons found for "{ query }". Run ingest first.' )
         raise SystemExit( Position.SECOND )

      print( cls.format_table( rows ) )


   @classmethod
   def format_table( cls, rows: list[ SkaterSeason ] ) -> str:
      grouped: dict[ SkaterKey, list[ SkaterSeason ] ] = {}

      for row in rows:
         key = SkaterKey.from_row( row )
         grouped.setdefault( key, [] ).append( row )

      blocks: list[ str ] = []

      for key, player_rows in grouped.items():
         first = player_rows[ Position.FIRST ]
         pace_header = f'/{ first.pace_games }'
         header = f'{ key.player_name } ({ first.position.value }, #{ key.player_id })'
         lines = [
            header,
            (
               'Season'.ljust( 9 )
               + 'Team'.ljust( 6 )
               + 'GP'.rjust( 4 )
               + 'G'.rjust( 5 )
               + 'A'.rjust( 5 )
               + 'P'.rjust( 5 )
               + ( 'G' + pace_header ).rjust( 8 )
               + ( 'A' + pace_header ).rjust( 8 )
               + ( 'P' + pace_header ).rjust( 8 ) ),
         ]

         for row in player_rows:
            lines.append(
               (
                  Season.label( row.season_id ).ljust( 9 )
                  + row.team.value.ljust( 6 )
                  + str( row.games_played ).rjust( 4 )
                  + str( row.goals ).rjust( 5 )
                  + str( row.assists ).rjust( 5 )
                  + str( row.points ).rjust( 5 )
                  + cls._fmt_pace( row.g_pace ).rjust( 8 )
                  + cls._fmt_pace( row.a_pace ).rjust( 8 )
                  + cls._fmt_pace( row.p_pace ).rjust( 8 ) ) )

         blocks.append( '\n'.join( lines ) )

      return '\n\n'.join( blocks )


   @classmethod
   def _fmt_pace( cls, value: float ) -> str:
      return format( value, '.1f' )
