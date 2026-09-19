from __future__ import annotations

from datetime import date

from api.position import Position
from api.season_length import SeasonLength
from api.skater_bio import SkaterBio
from api.skater_position import SkaterPosition
from api.skater_season_ingester import SkaterSeasonIngester
from api.skater_summary import SkaterSummary
from api.team import Team


def Test_BuildRows_TestRegularSeason_ExpectPacedTotals() -> None:
   rows = SkaterSeasonIngester.build_rows(
      [ SkaterSummary(
         8478402,
         'Connor McDavid',
         SkaterPosition.CENTER,
         [ Team.EDMONTON_OILERS ],
         82,
         44,
         79,
         123 ) ],
      [ SkaterBio( 8478402, date( 1997, 1, 13 ) ) ],
      SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      84 )

   assert len( rows ) == 1
   row = rows[ Position.FIRST ]
   assert row.g_pace == 44 / 82 * 84
   assert row.a_pace == 79 / 82 * 84
   assert row.p_pace == 123 / 82 * 84
   assert row.pace_games == 84
   assert row.team == Team.EDMONTON_OILERS


def Test_BuildRows_TestShortSeason_ExpectPacedTotals() -> None:
   rows = SkaterSeasonIngester.build_rows(
      [ SkaterSummary(
         1,
         'Sample Player',
         SkaterPosition.DEFENSE,
         [ Team.BUFFALO_SABRES ],
         4,
         1,
         1,
         2 ) ],
      [ SkaterBio( 1, date( 1999, 1, 1 ) ) ],
      SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      84 )

   assert rows[ Position.FIRST ].p_pace == 2 / 4 * 84


def Test_Seasons_TestBeforeFirstSeason_ExpectExcluded() -> None:
   meta = SkaterSeasonIngester._seasons(
      [
         SeasonLength( 20042005, 82, date( 2004, 10, 1 ), date( 2005, 4, 15 ) ),
         SeasonLength( 20252026, 82, date( 2025, 10, 7 ), date( 2026, 4, 17 ) ),
         SeasonLength( 20262027, 84, date( 2026, 9, 29 ), date( 2027, 4, 10 ) ),
      ] )

   assert [ item.season_id for item in meta ] == [ 20252026, 20262027 ]
