from __future__ import annotations

from api.projections.power_play_pace import PowerPlayPace
from api.projections.season_pace import SeasonPace
from api.projections.short_handed_pace import ShortHandedPace
from api.recency.prior_source import PriorSource
from api.recency.prior_year import PriorYear


def _prior( year: int, nhl_games: int, age: float ) -> PriorYear:
   return PriorYear(
      year,
      SeasonPace( 10.0, 20.0 ),
      PowerPlayPace.zero(),
      ShortHandedPace( 0.0, 0.0 ),
      0.0,
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

   assert prior.target_age() == int( prior.age ) + 1


def Test_GapBefore_TestYears_ExpectMissedSeasons() -> None:
   prior = _prior( 2023, 60, 24.3 )

   assert prior.gap_before( 2024 ) == 0
   target_year = 2026
   assert prior.gap_before( target_year ) == target_year - prior.year - 1


def Test_AgeInYear_TestYears_ExpectCompletedAgeWithElapsedSeasons() -> None:
   prior = _prior( 2023, 60, 24.9 )

   completed_age = int( prior.age )
   assert prior.age_in_year( prior.year ) == completed_age
   assert prior.age_in_year( prior.year + 1 ) == completed_age + 1
   elapsed_seasons = 3
   assert prior.age_in_year( prior.year + elapsed_seasons ) == completed_age + elapsed_seasons
