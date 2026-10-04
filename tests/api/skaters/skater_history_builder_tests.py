from __future__ import annotations

import pytest

from api.projections.draft_pick import DraftPick
from api.projections.prospect_profile import ProspectProfile
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_history_builder import SkaterHistoryBuilder
from api.skaters.skater_position import SkaterPosition


def _season( player_id: int, season_id: int ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id, season_id=season_id, age=18.5, games_played=40,
      goals=10, assists=20, points=30, g_pace=21.0, a_pace=42.0,
      position=SkaterPosition.CENTER, league='SHL' )


def Test_Build_TestPlayers_ExpectSeparateCompleteHistories() -> None:
   first = _season( 1, 20242025 )
   second = _season( 1, 20252026 )
   other = _season( 2, 20242025 )
   profiles = [ ProspectProfile( player_id, None, DraftPick( None ), [] ) for player_id in [ 1, 2 ] ]

   histories = SkaterHistoryBuilder.build( [ other, first, second ], profiles )

   assert [ history.player_id for history in histories ] == [ 1, 2 ]
   assert histories[ 0 ].seasons == [ first, second ]
   assert histories[ 0 ].profile is profiles[ 0 ]
   assert histories[ 1 ].profile is profiles[ 1 ]
   assert histories[ 0 ].before( 20252026 ).seasons == [ first ]
   assert histories[ 0 ].nhl_seasons() == []
   assert histories[ 0 ].other_league_seasons() == [ first, second ]
   assert histories[ 0 ].latest_prospect_source( 20262027, supported_leagues={ 'SHL' } ) is second
   assert histories[ 0 ].latest_prospect_source( 20262027, supported_leagues={ 'OHL' } ) is None


def Test_Build_TestEmpty_ExpectEmptyList() -> None:
   assert SkaterHistoryBuilder.build( [], [] ) == []


def Test_Build_TestMissingProfile_ExpectError() -> None:
   with pytest.raises( KeyError ):
      SkaterHistoryBuilder.build( [ _season( 1, 20242025 ) ], [] )
