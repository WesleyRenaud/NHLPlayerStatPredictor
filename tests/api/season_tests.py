from __future__ import annotations

from datetime import date

import pytest

from api.season import Season
from api.season_length import SeasonLength
from api.shared.enums.position import Position
from api.skaters.team import Team


@pytest.mark.parametrize( 'season_id, expected', [
   ( 20052006, '2005-06' ),
   ( 20252026, '2025-26' ),
] )
def Test_Label( season_id: int, expected: str ) -> None:
   label = Season.label( season_id )

   assert label == expected


def Test_PrimaryTeam_TestSplitSeason_ExpectLastTeam() -> None:
   members = list( Team )
   teams = [ members[ Position.FIRST ], members[ Position.SECOND ] ]

   team = Season.primary_team( teams )

   assert team == teams[ Position.LAST ]


def Test_Pace_TestHalfSeason_ExpectScaledToPace() -> None:
   value = 20
   games_played = 42
   pace_games = 84

   pace = Season.pace( value, games_played, pace_games )

   assert pace == value / games_played * pace_games


def Test_PaceGames_TestLastSeason_ExpectScheduledLength() -> None:
   seasons = [
      SeasonLength( 20252026, 82, date( 2025, 10, 7 ), date( 2026, 4, 17 ) ),
      SeasonLength( 20262027, 84, date( 2026, 9, 29 ), date( 2027, 4, 10 ) ),
   ]

   pace_games = Season.pace_games( seasons )

   assert pace_games == Season.latest( seasons ).number_of_games


def Test_Latest_TestSeasons_ExpectLastLength() -> None:
   seasons = [
      SeasonLength( 20252026, 82, date( 2025, 10, 7 ), date( 2026, 4, 17 ) ),
      SeasonLength( 20262027, 84, date( 2026, 9, 29 ), date( 2027, 4, 10 ) ),
   ]

   latest = Season.latest( seasons )

   assert latest == sorted( seasons )[ Position.LAST ]


def Test_Prior_TestSeasons_ExpectSecondLastLength() -> None:
   seasons = [
      SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      SeasonLength( 20252026, 82, date( 2025, 10, 7 ), date( 2026, 4, 17 ) ),
      SeasonLength( 20262027, 84, date( 2026, 9, 29 ), date( 2027, 4, 10 ) ),
   ]

   prior = Season.prior( seasons )

   assert prior == sorted( seasons )[ Position.SECOND_LAST ]


def Test_AgeInYear_TestLaterYear_ExpectAgePlusElapsed() -> None:
   age = 29
   from_year = 2024
   elapsed = 2

   assert Season.age_in_year( age, from_year, from_year + elapsed ) == age + elapsed


def Test_RecencyLag_TestImmediatePrior_ExpectZero() -> None:
   target_season_id = 20212022
   season_id = 20202021

   lag = Season.recency_lag( target_season_id, season_id )

   assert lag == 0


def Test_Years_TestSeasonId_ExpectBothYears() -> None:
   season_id = 20202021
   first_year = 2020
   second_year = 2021

   assert Season.years( season_id ) == ( first_year, second_year )


def Test_FromYears_TestBothYears_ExpectJoinedSeasonId() -> None:
   first_year = 2020
   second_year = 2021
   season_id = 20202021

   assert Season.from_years( first_year, second_year ) == season_id


def Test_SeasonBefore_TestProjectionSeason_ExpectSeasonBeforeIt() -> None:
   projection_season_id = 20212022
   season_before_projection = 20202021

   assert Season.season_before( projection_season_id ) == season_before_projection


def Test_RecencyLag_TestSkippedYear_ExpectOne() -> None:
   target_season_id = 20222023
   season_id = 20202021

   lag = Season.recency_lag( target_season_id, season_id )

   assert lag == 1
