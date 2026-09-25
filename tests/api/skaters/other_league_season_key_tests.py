from __future__ import annotations

from api.skaters.other_league_season_key import OtherLeagueSeasonKey


def Test_Equality_TestSamePlayerSeasonLeague_ExpectEqual() -> None:
   key = OtherLeagueSeasonKey( 7, 20252026, 'AAA' )
   assert key == OtherLeagueSeasonKey( 7, 20252026, 'AAA' )
   assert key in { OtherLeagueSeasonKey( 7, 20252026, 'AAA' ) }
