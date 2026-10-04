from __future__ import annotations

from api.projections.draft_pick import DraftPick
from api.projections.prospect_profile import ProspectProfile
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_history import SkaterHistory
from api.skaters.skater_position import SkaterPosition


def _source( player_id: int, season_id: int ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id, season_id=season_id, age=18.5, games_played=40,
      goals=10, assists=20, points=30, g_pace=21.0, a_pace=42.0,
      position=SkaterPosition.CENTER, league='SHL' )


def Test_Before_TestFutureAndTargetSeasons_ExpectEarlierOnly() -> None:
   rows = [ _source( 1, season ) for season in [ 20232024, 20242025, 20252026 ] ]
   history = SkaterHistory( 1, rows, ProspectProfile( 1, None, DraftPick( None ), [] ) )

   assert history.before( 20242025 ).seasons == rows[ :1 ]
   assert history.before( 20232024 ).seasons == []
   assert history.seasons == rows


def Test_Seasons_TestEmpty_ExpectEmptyLists() -> None:
   history = SkaterHistory( 1, [], ProspectProfile( 1, None, DraftPick( None ), [] ) )

   assert history.nhl_seasons() == []
   assert history.other_league_seasons() == []
   assert history.latest_prospect_source( 20262027, supported_leagues={ 'SHL' } ) is None
