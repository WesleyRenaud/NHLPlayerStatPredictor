from __future__ import annotations

from api.projections.power_play_pace import PowerPlayPace
from api.projections.season_pace import SeasonPace
from api.recency.prior_source import PriorSource
from api.recency.prior_year import PriorYear


def _prior( year: int, nhl_games: int, age: float ) -> PriorYear:
   return PriorYear(
      year,
      SeasonPace( 10.0, 20.0 ),
      PowerPlayPace.zero(),
      60,
      nhl_games,
      age,
      SeasonPace.zero() )


def Test_Source_TestNhlGames_ExpectNhl() -> None:
   prior = _prior( 2024, PriorYear.MIN_GAMES, 24.3 )

   assert prior.source() == PriorSource.NHL


def Test_Source_TestFewNhlGames_ExpectTranslated() -> None:
   prior = _prior( 2024, PriorYear.MIN_GAMES - 1, 24.3 )

   assert prior.source() == PriorSource.TRANSLATED


def Test_TargetAge_TestFractionalAge_ExpectNextCompletedAge() -> None:
   prior = _prior( 2024, 60, 24.9 )

   assert prior.target_age() == 25


def Test_GapBefore_TestYears_ExpectMissedSeasons() -> None:
   prior = _prior( 2023, 60, 24.3 )

   assert prior.gap_before( 2024 ) == 0
   assert prior.gap_before( 2026 ) == 2
