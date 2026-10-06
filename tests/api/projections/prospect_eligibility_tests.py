from __future__ import annotations

import pytest

from api.projections.draft_pick import DraftPick
from api.projections.nhl_season_games import NhlSeasonGames
from api.projections.prospect_eligibility import ProspectEligibility
from api.projections.prospect_profile import ProspectProfile


@pytest.mark.parametrize( 'age, games, expected', [
   ( 25, 25, True ),
   ( 26, 25, False ),
   ( 25, 26, False ),
   ( 20, 0, True ),
] )
def Test_Eligible_TestBoundaries_ExpectPlayerEligibility(
      age: float, games: int, expected: bool ) -> None:
   profile = ProspectProfile( 1, 2025, DraftPick( 3 ), [
      NhlSeasonGames( 20242025, games ), NhlSeasonGames( 20262027, 80 ) ] )

   assert ProspectEligibility.eligible( profile, 20262027, age ) is expected


@pytest.mark.parametrize( 'age, nhl_games, prior_games, expected', [
   ( 25.9, 0, 25, True ),
   ( 26.0, 0, 0, False ),
   ( 25.0, 1, 0, False ),
   ( 25.0, 0, 26, False ),
] )
def Test_PreNhl_TestWindow_ExpectLatestSeasonOutsideLeague(
      age: float, nhl_games: int, prior_games: int, expected: bool ) -> None:
   assert ProspectEligibility.pre_nhl( age, nhl_games, prior_games ) is expected
