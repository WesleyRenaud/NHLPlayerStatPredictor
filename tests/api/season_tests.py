from __future__ import annotations

from datetime import date

import pytest

from api.season import Season
from api.season_length import SeasonLength
from api.shared.enums.position import Position
from api.team import Team
from api.types import Types


def _lengths( seasons: Types.JsonObjectList ) -> list[ SeasonLength ]:
   return SeasonLength.from_rows( seasons )


@pytest.mark.parametrize( 'season_id, expected', [
   ( 20052006, '2005-06' ),
   ( 20252026, '2025-26' ),
] )
def Test_Label( season_id: int, expected: str ) -> None:
   assert Season.label( season_id ) == expected


def Test_PrimaryTeam_TestSplitSeason_ExpectLastTeam() -> None:
   members = list( Team )
   teams = [ members[ Position.FIRST ], members[ Position.SECOND ] ]
   assert Season.primary_team( teams ) == teams[ Position.LAST ]


def Test_Pace_TestHalfSeason_ExpectScaledToPace() -> None:
   assert Season.pace( 20, 42, 84 ) == 40.0


def Test_AgeOn_TestKnownBirthday_ExpectFractionalAge() -> None:
   age = Season.age_on( date( 1997, 1, 13 ), date( 2025, 10, 7 ) )
   assert 28.7 < age < 28.8


def Test_PaceGames_TestLastSeason_ExpectScheduledLength() -> None:
   seasons = _lengths(
      [
         {
            'id': 20252026,
            'startDate': '2025-10-07T00:00:00',
            'regularSeasonEndDate': '2026-04-17',
            'numberOfGames': 82,
         },
         {
            'id': 20262027,
            'startDate': '2026-09-29T17:00:00',
            'regularSeasonEndDate': '2027-04-10',
            'numberOfGames': 84,
         },
      ] )
   assert Season.pace_games( seasons ) == sorted( seasons )[ Position.LAST ].number_of_games


def Test_RecencyLag_TestImmediatePrior_ExpectZero() -> None:
   assert Season.recency_lag( 20212022, 20202021 ) == 0


def Test_RecencyLag_TestSkippedYear_ExpectOne() -> None:
   assert Season.recency_lag( 20222023, 20202021 ) == 1
