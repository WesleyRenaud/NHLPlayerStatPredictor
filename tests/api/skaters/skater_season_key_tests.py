from __future__ import annotations

from api.skaters.skater_season_key import SkaterSeasonKey


def Test_FromRow_TestPlayerAndSeason_ExpectFields() -> None:
   key = SkaterSeasonKey( 8478402, 20252026 )

   loaded = SkaterSeasonKey.from_row( {
      'PLAYER_ID': key.player_id,
      'SEASON_ID': key.season_id,
   } )

   assert loaded == key


def Test_Equality_TestSamePlayerAndSeason_ExpectEqual() -> None:
   player_id = 8478402
   season_id = 20252026
   key = SkaterSeasonKey( player_id, season_id )
   duplicate = SkaterSeasonKey( player_id, season_id )

   equal = key == duplicate

   assert equal
   assert key in { duplicate }
