from __future__ import annotations

from datetime import date

import pytest

import api.ingest.skater_season_builder as skater_season_builder
from api.ingest.skater_season_builder import SkaterSeasonBuilder
from api.season import Season
from api.season_length import SeasonLength
from api.shared.enums.position import Position
from api.skaters.skater_bio import SkaterBio
from api.skaters.skater_game import SkaterGame
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_summary import SkaterSummary
from api.skaters.team import Team
from api.types import Types


def Test_BuildRows_TestRegularSeason_ExpectPacedTotals() -> None:
   player_id = 8478402
   team = list( Team )[ Position.FIRST ]
   position = list( SkaterPosition )[ Position.FIRST ]
   games_played = 82
   goals = 44
   assists = 79
   points = 123
   penalty_minutes = 12
   power_play_goals = 20
   power_play_points = 60
   short_handed_goals = 2
   short_handed_points = 4
   even_strength_goals = goals - power_play_goals - short_handed_goals
   even_strength_points = points - power_play_points - short_handed_points
   pace_games = 84
   shots = 250
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
         points,
         penalty_minutes,
         power_play_goals,
         power_play_points,
         short_handed_goals,
         short_handed_points,
         even_strength_goals,
         even_strength_points,
         shots,
         1280.0 )
   ]
   bios = [ SkaterBio( player_id, date( 1997, 1, 13 ) ) ]

   rows = SkaterSeasonBuilder.build_rows( summaries, bios, season, pace_games, { player_id: [] } )
   row = rows[ Position.FIRST ]

   assert len( rows ) == 1
   assert row.g_pace == Season.pace( float( goals ), float( games_played ), pace_games )
   assert row.a_pace == Season.pace( float( assists ), float( games_played ), pace_games )
   assert row.p_pace == Season.pace( float( points ), float( games_played ), pace_games )
   assert row.penalty_minutes == penalty_minutes
   assert row.power_play_goals == power_play_goals
   assert row.power_play_points == power_play_points
   assert row.short_handed_goals == short_handed_goals
   assert row.short_handed_points == short_handed_points
   assert row.even_strength_goals == even_strength_goals
   assert row.even_strength_points == even_strength_points
   assert row.shots == shots
   assert row.shots_pace() == Season.pace( shots, games_played, pace_games )
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
         list( SkaterPosition )[ Position.SECOND ],
         [ list( Team )[ Position.SECOND ] ],
         games_played,
         1,
         1,
         points,
         2,
         0,
         0,
         0,
         0,
         1,
         points,
         10,
         1200.0 )
   ]
   bios = [ SkaterBio( player_id, date( 1999, 1, 1 ) ) ]
   season = SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) )

   rows = SkaterSeasonBuilder.build_rows( summaries, bios, season, pace_games, { player_id: [] } )

   assert rows[ Position.FIRST ].p_pace == Season.pace(
      float( points ),
      float( games_played ),
      pace_games )


def Test_BuildRows_TestMissingBio_ExpectSkipped() -> None:
   team = list( Team )[ Position.FIRST ]
   position = list( SkaterPosition )[ Position.FIRST ]
   kept_id = 1
   missing_id = 2
   games_played = 82
   pace_games = 84
   summaries = [
      SkaterSummary( kept_id, 'Has Bio', position, [ team ], games_played, 1, 1, 2, 0, 0, 0, 0, 0, 1, 2, 10, 1200.0 ),
      SkaterSummary( missing_id, 'No Bio', position, [ team ], games_played, 1, 1, 2, 0, 0, 0, 0, 0, 1, 2, 10, 1200.0 ),
   ]
   bios = [ SkaterBio( kept_id, date( 1999, 1, 1 ) ) ]
   season = SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) )

   rows = SkaterSeasonBuilder.build_rows(
      summaries,
      bios,
      season,
      pace_games,
      { kept_id: [], missing_id: [] } )

   assert len( rows ) == 1
   assert rows[ Position.FIRST ].player_id == kept_id


def Test_RowsForSeason_TestGameRow_ExpectNumberedPoints(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   season_id = 20242025
   player_id = 7
   first_points = 2
   later_points = 1
   repeated_points = 9
   pace_games = 84
   position = list( SkaterPosition )[ Position.FIRST ]
   calls: list[ tuple[ int, str ] ] = []

   def fake( season: int, team: str, force: bool = False ) -> Types.JsonObjectList:
      calls.append( ( season, team ) )

      if season == season_id and team == 'TOR':
         return [
            { 'playerId': player_id, 'gameDate': '2024-10-11', 'points': later_points },
            { 'playerId': player_id, 'gameDate': '2024-10-09', 'points': first_points },
            { 'playerId': player_id, 'gameDate': '2024-10-09', 'points': repeated_points },
            { 'playerId': player_id, 'gameDate': '2024-10-13' },
         ]

      return []

   monkeypatch.setattr(
      skater_season_builder.NhlClient,
      'skater_summary',
      lambda requested_id, force=False: [
         SkaterSummary(
            player_id,
            'Stub Skater',
            position,
            [ list( Team )[ Position.FIRST ] ],
            2,
            1,
            1,
            first_points + later_points,
            0,
            0,
            0,
            0,
            0,
            1,
            2,
            4,
            1200.0 ),
      ] )
   monkeypatch.setattr(
      skater_season_builder.NhlClient,
      'skater_bios',
      lambda requested_id, force=False: [ SkaterBio( player_id, date( 1997, 1, 13 ) ) ] )
   monkeypatch.setattr( skater_season_builder.NhlClient, 'skater_games', fake )
   season = SeasonLength( season_id, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) )

   rows = SkaterSeasonBuilder._rows_for_season( season, pace_games, False )

   assert rows[ Position.FIRST ].games == [
      SkaterGame( 1, first_points ),
      SkaterGame( 2, later_points ),
   ]
   assert calls == [ ( season_id, team.value ) for team in Team ]


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
