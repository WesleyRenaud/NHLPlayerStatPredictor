from __future__ import annotations

from api.projections.scoring_paces import ScoringPaces
from api.projections.weighted_scoring import WeightedScoring


def Test_Adding_TestPlayedSeason_ExpectGamesAndWeightedScoring() -> None:
   paces = ScoringPaces( 2.0, 4.0, 0.0, 0.0, 0.0, 0.0 )

   weighted = WeightedScoring.empty().adding( 10, paces )

   assert weighted == WeightedScoring( 10, paces.scaled( 10 ) )


def Test_PerGame_TestPlayedSeasons_ExpectGamesWeightedAverage() -> None:
   first = ScoringPaces( 2.0, 4.0, 0.0, 0.0, 0.0, 0.0 )
   second = ScoringPaces( 6.0, 8.0, 0.0, 0.0, 0.0, 0.0 )

   average = WeightedScoring.empty().adding( 10, first ).adding( 30, second ).per_game()

   assert average == first.scaled( 10 ).adding( second.scaled( 30 ) ).per_game( 40 )


def Test_PerGame_TestNoGames_ExpectNoAverage() -> None:
   assert WeightedScoring.empty().per_game() is None
