from __future__ import annotations

from datetime import date

import pytest

from api.position import Position
from api.season_length import SeasonLength
from api.skater_bio import SkaterBio
from api.skater_position import SkaterPosition
import api.skater_season_ingester as skater_season_ingester
from api.skater_season_ingester import SkaterSeasonIngester
from api.skater_summary import SkaterSummary
from api.team import Team


def Test_BuildRows_TestRegularSeason_ExpectPacedTotals() -> None:
   team = list( Team )[ Position.FIRST ]
   rows = SkaterSeasonIngester.build_rows(
      [ SkaterSummary(
         8478402,
         'Connor McDavid',
         list( SkaterPosition )[ Position.FIRST ],
         [ team ],
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
   assert row.team == team


def Test_BuildRows_TestShortSeason_ExpectPacedTotals() -> None:
   rows = SkaterSeasonIngester.build_rows(
      [ SkaterSummary(
         1,
         'Sample Player',
         list( SkaterPosition )[ Position.SECOND ],
         [ list( Team )[ Position.SECOND ] ],
         4,
         1,
         1,
         2 ) ],
      [ SkaterBio( 1, date( 1999, 1, 1 ) ) ],
      SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      84 )

   assert rows[ Position.FIRST ].p_pace == 2 / 4 * 84


def Test_Seasons_TestBeforeFirstSeason_ExpectExcluded(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr( skater_season_ingester.Config, 'FIRST_SEASON_ID', 20102011 )
   meta = SkaterSeasonIngester._seasons(
      [
         SeasonLength( 20092010, 82, date( 2009, 10, 1 ), date( 2010, 4, 15 ) ),
         SeasonLength( 20102011, 82, date( 2010, 10, 7 ), date( 2011, 4, 17 ) ),
         SeasonLength( 20112012, 82, date( 2011, 10, 6 ), date( 2012, 4, 10 ) ),
      ] )

   assert [ item.season_id for item in meta ] == [ 20102011, 20112012 ]
