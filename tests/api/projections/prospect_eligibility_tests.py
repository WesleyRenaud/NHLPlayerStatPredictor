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
