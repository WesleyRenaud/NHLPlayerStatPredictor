from __future__ import annotations

from datetime import date

import pytest

import api.ingest.skater_season_builder as skater_season_builder
from api.ingest.skater_season_builder import SkaterSeasonBuilder
from api.season import Season
from api.season_length import SeasonLength
from api.shared.enums.position import Position
from api.skaters.skater_bio import SkaterBio
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_summary import SkaterSummary
from api.skaters.team import Team


def Test_BuildRows_TestRegularSeason_ExpectPacedTotals() -> None:
   player_id = 8478402
   team = list( Team )[ Position.FIRST ]
   position = SkaterPosition( 'C' )
   games_played = 82
   goals = 44
   assists = 79
   points = 123
   pace_games = 84
   season = SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) )
   summaries = [
      SkaterSummary(
         player_id,
         'Connor McDavid',
         position,
         [ team ],
         games_played,
         goals,
         assists,
         points )
   ]
   bios = [ SkaterBio( player_id, date( 1997, 1, 13 ) ) ]

   rows = SkaterSeasonBuilder.build_rows( summaries, bios, season, pace_games )
   row = rows[ Position.FIRST ]

   assert len( rows ) == 1
   assert row.g_pace == Season.pace( float( goals ), float( games_played ), pace_games )
   assert row.a_pace == Season.pace( float( assists ), float( games_played ), pace_games )
   assert row.p_pace == Season.pace( float( points ), float( games_played ), pace_games )
   assert row.pace_games == pace_games
   assert row.team == team


def Test_BuildRows_TestShortSeason_ExpectPacedTotals() -> None:
   player_id = 1
   games_played = 4
   points = 2
   pace_games = 84
   summaries = [
      SkaterSummary(
         player_id,
         'Sample Player',
         SkaterPosition( 'D' ),
         [ list( Team )[ Position.SECOND ] ],
         games_played,
         1,
         1,
         points )
   ]
   bios = [ SkaterBio( player_id, date( 1999, 1, 1 ) ) ]
   season = SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) )

   rows = SkaterSeasonBuilder.build_rows( summaries, bios, season, pace_games )

   assert rows[ Position.FIRST ].p_pace == Season.pace(
      float( points ),
      float( games_played ),
      pace_games )


def Test_BuildRows_TestMissingBio_ExpectSkipped() -> None:
   team = list( Team )[ Position.FIRST ]
   position = SkaterPosition( 'C' )
   kept_id = 1
   missing_id = 2
   games_played = 82
   pace_games = 84
   summaries = [
      SkaterSummary( kept_id, 'Has Bio', position, [ team ], games_played, 1, 1, 2 ),
      SkaterSummary( missing_id, 'No Bio', position, [ team ], games_played, 1, 1, 2 ),
   ]
   bios = [ SkaterBio( kept_id, date( 1999, 1, 1 ) ) ]
   season = SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) )

   rows = SkaterSeasonBuilder.build_rows( summaries, bios, season, pace_games )

   assert len( rows ) == 1
   assert rows[ Position.FIRST ].player_id == kept_id


def Test_Seasons_TestBeforeFirstSeason_ExpectExcluded(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   first_season_id = 20102011
   excluded = SeasonLength( 20092010, 82, date( 2009, 10, 1 ), date( 2010, 4, 15 ) )
   included_first = SeasonLength(
      first_season_id,
      82,
      date( 2010, 10, 7 ),
      date( 2011, 4, 17 ) )
   included_second = SeasonLength( 20112012, 82, date( 2011, 10, 6 ), date( 2012, 4, 10 ) )
   monkeypatch.setattr( skater_season_builder.Config, 'FIRST_SEASON_ID', first_season_id )

   meta = SkaterSeasonBuilder._seasons( [ excluded, included_first, included_second ] )

   assert [ item.season_id for item in meta ] == [
      included_first.season_id,
      included_second.season_id,
   ]
