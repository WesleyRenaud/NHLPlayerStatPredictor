from __future__ import annotations

from api.projections.scoring_paces import ScoringPaces
from api.recency.prior_year import PriorYear


def _prior( year: int, nhl_games: int, age: int ) -> PriorYear:
   return PriorYear(
      year,
      ScoringPaces( 10.0, 20.0, 0.0, 0.0, 0.0, 0.0 ),
      0.0,
      60,
      nhl_games,
      age )


def Test_AgeInYear_TestElapsedSeasons_ExpectAgePlusYears() -> None:
   age = 24
   prior = _prior( 2023, 60, age )
   elapsed_seasons = 3

   assert prior.age_in_year( prior.year ) == age
   assert prior.age_in_year( prior.year + 1 ) == age + 1
   assert prior.age_in_year( prior.year + elapsed_seasons ) == age + elapsed_seasons
