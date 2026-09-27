from __future__ import annotations

from api.projections.season_pace import SeasonPace
from api.recency.prior_source import PriorSource
from api.recency.prior_year import PriorYear


def Test_Source_TestNhlGames_ExpectNhl() -> None:
   prior = PriorYear( 2024, SeasonPace( 10.0, 20.0 ), 60, PriorYear.MIN_GAMES, 24.3 )

   assert prior.source() == PriorSource.NHL


def Test_Source_TestFewNhlGames_ExpectTranslated() -> None:
   prior = PriorYear( 2024, SeasonPace( 10.0, 20.0 ), 60, PriorYear.MIN_GAMES - 1, 24.3 )

   assert prior.source() == PriorSource.TRANSLATED


def Test_TargetAge_TestFractionalAge_ExpectNextCompletedAge() -> None:
   prior = PriorYear( 2024, SeasonPace( 10.0, 20.0 ), 60, 60, 24.9 )

   assert prior.target_age() == 25


def Test_GapBefore_TestYears_ExpectMissedSeasons() -> None:
   prior = PriorYear( 2023, SeasonPace( 10.0, 20.0 ), 60, 60, 24.3 )

   assert prior.gap_before( 2024 ) == 0
   assert prior.gap_before( 2026 ) == 2
