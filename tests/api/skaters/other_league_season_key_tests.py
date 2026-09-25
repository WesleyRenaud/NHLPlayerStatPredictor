from __future__ import annotations

from api.skaters.other_league_season_key import OtherLeagueSeasonKey


def Test_Equality_TestSamePlayerSeasonLeague_ExpectEqual() -> None:
   player_id = 7
   season_id = 20252026
   league = 'AAA'
   key = OtherLeagueSeasonKey( player_id, season_id, league )
   duplicate = OtherLeagueSeasonKey( player_id, season_id, league )

   equal = key == duplicate

   assert equal
   assert key in { duplicate }
