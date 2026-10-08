from __future__ import annotations

from ..database_connection_provider import DatabaseConnectionProvider
from .other_league_skater_season import OtherLeagueSkaterSeason


class OtherLeagueSeasonProvider():
   @classmethod
   def all_seasons( cls, db_path: str ) -> list[ OtherLeagueSkaterSeason ]:
      return [
         OtherLeagueSkaterSeason.from_row( row ).with_birth_date( row[ 'BIRTH_DATE' ] )
         for row in DatabaseConnectionProvider.rows(
            db_path,
            f'''
            SELECT OtherLeagueSeason.*, { cls._birth_date() }
            FROM OtherLeagueSeason
            ORDER BY PLAYER_ID, SEASON_ID, LEAGUE
            ''' )
      ]


   @classmethod
   def seasons_for_season_id(
         cls,
         season_id: int,
         db_path: str ) -> list[ OtherLeagueSkaterSeason ]:
      return [
         OtherLeagueSkaterSeason.from_row( row ).with_birth_date( row[ 'BIRTH_DATE' ] )
         for row in DatabaseConnectionProvider.rows(
            db_path,
            f'''
            SELECT OtherLeagueSeason.*, { cls._birth_date() }
            FROM OtherLeagueSeason
            WHERE SEASON_ID = ?
            ORDER BY PLAYER_ID, LEAGUE
            ''',
            [ season_id ] )
      ]


   @classmethod
   def seasons_for_player_id(
         cls,
         player_id: int,
         db_path: str ) -> list[ OtherLeagueSkaterSeason ]:
      return [
         OtherLeagueSkaterSeason.from_row( row ).with_birth_date( row[ 'BIRTH_DATE' ] )
         for row in DatabaseConnectionProvider.rows(
            db_path,
            f'''
            SELECT OtherLeagueSeason.*, { cls._birth_date() }
            FROM OtherLeagueSeason
            WHERE PLAYER_ID = ?
            ORDER BY SEASON_ID, LEAGUE
            ''',
            [ player_id ] )
      ]


   @classmethod
   def seasons_for_player_ids(
         cls,
         player_ids: list[ int ],
         db_path: str ) -> list[ OtherLeagueSkaterSeason ]:
      placeholders = ', '.join( '?' for _ in player_ids )
      return [
         OtherLeagueSkaterSeason.from_row( row ).with_birth_date( row[ 'BIRTH_DATE' ] )
         for row in DatabaseConnectionProvider.rows(
            db_path,
            f'''
            SELECT OtherLeagueSeason.*, { cls._birth_date() }
            FROM OtherLeagueSeason
            WHERE PLAYER_ID IN ( { placeholders } )
            ORDER BY PLAYER_ID, SEASON_ID, LEAGUE
            ''',
            player_ids )
      ]


   @classmethod
   def _birth_date( cls ) -> str:
      return '''
         ( SELECT BIRTH_DATE FROM SkaterSeason
           WHERE SkaterSeason.PLAYER_ID = OtherLeagueSeason.PLAYER_ID
           LIMIT 1 ) AS BIRTH_DATE
      '''
