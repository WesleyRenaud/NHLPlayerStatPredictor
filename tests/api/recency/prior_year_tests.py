from __future__ import annotations

from api.projections.scoring_paces import ScoringPaces
from api.recency.prior_year import PriorYear


def _prior( year: int, nhl_games: int, age: float ) -> PriorYear:
   return PriorYear(
      year,
      ScoringPaces( 10.0, 20.0, 0.0, 0.0, 0.0, 0.0 ),
      0.0,
      60,
      nhl_games,
      age )


def Test_Reliability_TestQualifiedSeason_ExpectFullWeight() -> None:
   assert PriorYear.reliability( PriorYear.MIN_GAMES ) == 1.0
   assert PriorYear.reliability( PriorYear.MIN_GAMES + 62 ) == 1.0


def Test_Reliability_TestShortSeason_ExpectFractionOfTheGate() -> None:
   games = PriorYear.MIN_GAMES // 2
   assert PriorYear.reliability( games ) == games / PriorYear.MIN_GAMES


def Test_AgeInYear_TestYears_ExpectCompletedAgeWithElapsedSeasons() -> None:
   prior = _prior( 2023, 60, 24.9 )

   completed_age = int( prior.age )
   assert prior.age_in_year( prior.year ) == completed_age
   assert prior.age_in_year( prior.year + 1 ) == completed_age + 1
   elapsed_seasons = 3
   assert prior.age_in_year( prior.year + elapsed_seasons ) == completed_age + elapsed_seasons
