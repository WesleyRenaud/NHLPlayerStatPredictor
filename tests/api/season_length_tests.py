from __future__ import annotations

from datetime import date

from api.season_length import SeasonLength


def Test_FromRow_TestSeasonJson_ExpectSeasonLength() -> None:
   season = SeasonLength( 20262027, 84, date( 2026, 9, 29 ), date( 2027, 4, 10 ) )

   loaded = SeasonLength.from_row( {
      'id': season.season_id,
      'startDate': f'{ season.start_date.isoformat() }T17:00:00',
      'regularSeasonEndDate': season.regular_season_end_date.isoformat(),
      'numberOfGames': season.number_of_games,
   } )

   assert loaded == season


def Test_Init_TestSeasonAndGames_ExpectFields() -> None:
   season_id = 20262027
   number_of_games = 84
   start_date = date( 2026, 9, 29 )
   end_date = date( 2027, 4, 10 )

   season = SeasonLength( season_id, number_of_games, start_date, end_date )

   assert season.season_id == season_id
   assert season.number_of_games == number_of_games
   assert season.start_date == start_date
   assert season.regular_season_end_date == end_date


def Test_Order_TestEarlierSeason_ExpectLessThan() -> None:
   earlier = SeasonLength(
      20252026,
      82,
      date( 2025, 10, 7 ),
      date( 2026, 4, 17 ) )
   later = SeasonLength(
      20262027,
      84,
      date( 2026, 9, 29 ),
      date( 2027, 4, 10 ) )

   is_less = earlier < later

   assert is_less
