from __future__ import annotations

from datetime import date
from pathlib import Path

from api.database_connection_provider import DatabaseConnectionProvider
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.skater_season import SkaterSeason
from api.skater_season_store import SkaterSeasonStore
from api.team import Team


def Test_InsertRows_TestInsertedPlayer_ExpectPersistedPoints( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   SkaterSeasonStore.insert_rows(
      [ SkaterSeason(
         player_id=8478402,
         season_id=20252026,
         player_name='Connor McDavid',
         position=list( SkaterPosition )[ Position.FIRST ],
         birth_date=date( 1997, 1, 13 ),
         age=28.7,
         team=list( Team )[ Position.FIRST ],
         games_played=82,
         goals=48,
         assists=90,
         points=138,
         schedule_games=82,
         pace_games=84,
         g_pace=48.0,
         a_pace=90.0,
         p_pace=138.0,
         gp_share=1.0 ) ],
      db_path=db_path )

   conn = DatabaseConnectionProvider.open( db_path )

   try:
      row = conn.execute( 'SELECT POINTS FROM SkaterSeason' ).fetchone()
   finally:
      DatabaseConnectionProvider.close( conn )

   assert row[ Position.FIRST ] == 138
