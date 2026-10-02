from __future__ import annotations

import pytest

from api.projections.scoring_component_shares import ScoringComponentShares


def Test_Split_TestTotals_ExpectComponentsSumToInputs() -> None:
   goals = 30.0
   assists = 50.0
   shares = ScoringComponentShares( 20, 0.75, 0.68, 0.2, 0.3, 0.05, 0.02 )

   scoring = shares.split( goals, assists )

   assert scoring.power_play_goals == pytest.approx( goals * shares.power_play_goals )
   assert scoring.short_handed_assists == pytest.approx( assists * shares.short_handed_assists )
   assert scoring.even_strength_goals == pytest.approx(
      goals * shares.even_strength_goals )
   assert scoring.even_strength_assists == pytest.approx( assists * shares.even_strength_assists )
   assert scoring.goals == pytest.approx( goals )
   assert scoring.assists == pytest.approx( assists )


def Test_FromRow_TestShares_ExpectRoundTrip() -> None:
   shares = ScoringComponentShares( 20, 0.75, 0.68, 0.2, 0.3, 0.05, 0.02 )

   assert ScoringComponentShares.from_row( shares.to_dict() ) == shares
