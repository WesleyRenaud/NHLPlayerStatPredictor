from __future__ import annotations

from datetime import date

from api.season_length import SeasonLength


def Test_FromRow_TestSeasonJson_ExpectSeasonLength() -> None:
   season = SeasonLength.from_row(
      {
         'id': 20262027,
         'startDate': '2026-09-29T17:00:00',
         'regularSeasonEndDate': '2027-04-10',
         'numberOfGames': 84,
      } )
   assert season.season_id == 20262027
   assert season.number_of_games == 84
   assert season.start_date == date( 2026, 9, 29 )
   assert season.regular_season_end_date == date( 2027, 4, 10 )


def Test_Init_TestSeasonAndGames_ExpectFields() -> None:
   season = SeasonLength( 20262027, 84, date( 2026, 9, 29 ), date( 2027, 4, 10 ) )
   assert season.season_id == 20262027
   assert season.number_of_games == 84
   assert season.start_date == date( 2026, 9, 29 )
   assert season.regular_season_end_date == date( 2027, 4, 10 )


def Test_Order_TestEarlierSeason_ExpectLessThan() -> None:
   assert SeasonLength(
      20252026,
      82,
      date( 2025, 10, 7 ),
      date( 2026, 4, 17 ) ) < SeasonLength(
      20262027,
      84,
      date( 2026, 9, 29 ),
      date( 2027, 4, 10 ) )
