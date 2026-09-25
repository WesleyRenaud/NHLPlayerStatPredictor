from __future__ import annotations

from api.skaters.skater_season_key import SkaterSeasonKey


def Test_FromRow_TestPlayerAndSeason_ExpectFields() -> None:
   key = SkaterSeasonKey.from_row( { 'PLAYER_ID': 8478402, 'SEASON_ID': 20252026 } )
   assert key.player_id == 8478402
   assert key.season_id == 20252026


def Test_Equality_TestSamePlayerAndSeason_ExpectEqual() -> None:
   key = SkaterSeasonKey( 8478402, 20252026 )
   assert key == SkaterSeasonKey( 8478402, 20252026 )
   assert key in { SkaterSeasonKey( 8478402, 20252026 ) }
