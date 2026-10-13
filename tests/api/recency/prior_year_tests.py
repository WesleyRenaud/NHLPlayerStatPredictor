from __future__ import annotations

import pytest

from api.projections.scoring_paces import ScoringPaces
from api.recency.games_reliability import GamesReliability
from api.recency.prior_year import PriorYear


def _prior( year: int, nhl_games: int, age: int ) -> PriorYear:
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


def Test_Reliability_TestMidpoint_ExpectCurveWeight() -> None:
   curve = GamesReliability.from_full_season( PriorYear.MIN_GAMES )
   games = curve.midpoint
   steps = ( curve.midpoint - games ) / curve.reach
   expected = 1 / ( 1 + curve.odds ** steps )

   assert PriorYear.reliability( games ) == pytest.approx( expected )


def Test_Reliability_TestReachBelowMidpoint_ExpectCurveWeight() -> None:
   curve = GamesReliability.from_full_season( PriorYear.MIN_GAMES )
   games = curve.midpoint - curve.reach
   steps = ( curve.midpoint - games ) / curve.reach
   expected = 1 / ( 1 + curve.odds ** steps )

   assert PriorYear.reliability( games ) == pytest.approx( expected )


def Test_Reliability_TestReachAboveMidpoint_ExpectCurveWeight() -> None:
   curve = GamesReliability.from_full_season( PriorYear.MIN_GAMES )
   games = curve.midpoint + curve.reach
   steps = ( curve.midpoint - games ) / curve.reach
   expected = 1 / ( 1 + curve.odds ** steps )

   assert PriorYear.reliability( games ) == pytest.approx( expected )


def Test_AgeInYear_TestElapsedSeasons_ExpectAgePlusYears() -> None:
   age = 24
   prior = _prior( 2023, 60, age )
   elapsed_seasons = 3

   assert prior.age_in_year( prior.year ) == age
   assert prior.age_in_year( prior.year + 1 ) == age + 1
   assert prior.age_in_year( prior.year + elapsed_seasons ) == age + elapsed_seasons
