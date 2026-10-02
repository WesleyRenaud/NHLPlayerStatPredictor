from __future__ import annotations

from datetime import date
from unittest.mock import Mock

import pytest

import api.projections.season_stats_resolver as season_stats_resolver
from api.projections.season_stats_resolver import SeasonStatsResolver
from api.season import Season
from api.season_length import SeasonLength
from api.skaters.skater_summary import SkaterSummary
from api.skaters.team import Team


def _summary( games: int, goals: int ) -> SkaterSummary:
   return SkaterSummary.from_row( {
      'playerId': 7, 'skaterFullName': 'Stub Skater', 'positionCode': 'C', 'teamAbbrevs': 'COL',
      'gamesPlayed': games, 'goals': goals, 'assists': 7, 'points': goals + 7,
      'penaltyMinutes': 4, 'evGoals': goals, 'evPoints': goals + 7,
      'ppGoals': 0, 'ppPoints': 0, 'shGoals': 0, 'shPoints': 0,
      'shots': 50, 'timeOnIcePerGame': 1280.0,
   } )


def _seasons() -> list[ SeasonLength ]:
   return [
      SeasonLength( 20252026, 82, date( 2025, 10, 7 ), date( 2026, 4, 17 ) ),
      SeasonLength( 20262027, 84, date( 2026, 9, 29 ), date( 2027, 4, 10 ) ),
   ]


@pytest.mark.parametrize(
   'on_date, expected_season_id',
   [
      ( date( 2026, 9, 28 ), 20252026 ),
      ( date( 2026, 9, 29 ), 20262027 ),
      ( date( 2026, 10, 2 ), 20262027 ),
   ] )
def Test_Resolve_TestSeasonStart_ExpectCorrectObservedSeason(
      monkeypatch: pytest.MonkeyPatch,
      on_date: date,
      expected_season_id: int ) -> None:
   summaries = { 20252026: _summary( 80, 40 ), 20262027: _summary( 3, 1 ) }
   fetch = Mock( side_effect=lambda season_id: [ summaries[ season_id ] ] )
   monkeypatch.setattr( season_stats_resolver.NhlClient, 'seasons', _seasons )
   monkeypatch.setattr( season_stats_resolver.NhlClient, 'skater_summary', fetch )
   monkeypatch.setattr( season_stats_resolver.RosterSkaterProvider, 'team', Mock( return_value=Team( 'COL' ) ) )
   team_games = 5
   standings = Mock( return_value={
      'standings': [ { 'seasonId': 20262027, 'teamAbbrev': { 'default': 'COL' }, 'gamesPlayed': team_games } ],
   } )
   monkeypatch.setattr( season_stats_resolver.NhlClient, 'standings', standings )
   remaining = 0 if expected_season_id == 20252026 else _seasons()[ 1 ].number_of_games - team_games

   stats = SeasonStatsResolver.resolve( 7, on_date )

   assert stats == {
      'seasonLabel': Season.label( expected_season_id ), **summaries[ expected_season_id ].stats_dict(),
      'fullSeasonPace': summaries[ expected_season_id ].full_season_pace( remaining ),
   }
   assert stats[ 'gamesPlayed' ] == summaries[ expected_season_id ].games_played
   fetch.assert_called_once_with( expected_season_id )
   if expected_season_id == 20252026:
      standings.assert_not_called()
   else:
      assert stats[ 'fullSeasonPace' ][ 'gamesPlayed' ] == summaries[ expected_season_id ].games_played + remaining
      assert stats[ 'fullSeasonPace' ][ 'gamesPlayed' ] < _seasons()[ 1 ].number_of_games


def Test_Resolve_TestTradedPlayer_ExpectCurrentRosterTeamRemainingGames(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   summary = _summary( 3, 1 )
   current_team = Team( 'EDM' )
   team_games = 6
   monkeypatch.setattr( season_stats_resolver.NhlClient, 'seasons', _seasons )
   monkeypatch.setattr( season_stats_resolver.NhlClient, 'skater_summary', Mock( return_value=[ summary ] ) )
   monkeypatch.setattr( season_stats_resolver.RosterSkaterProvider, 'team', Mock( return_value=current_team ) )
   monkeypatch.setattr( season_stats_resolver.NhlClient, 'standings', Mock( return_value={
      'standings': [
         { 'seasonId': 20262027, 'teamAbbrev': { 'default': 'COL' }, 'gamesPlayed': 4 },
         { 'seasonId': 20262027, 'teamAbbrev': { 'default': current_team.value }, 'gamesPlayed': team_games },
      ],
   } ) )

   stats = SeasonStatsResolver.resolve( summary.player_id, date( 2026, 10, 2 ) )

   remaining = _seasons()[ 1 ].number_of_games - team_games
   assert stats is not None
   assert stats[ 'fullSeasonPace' ] == summary.full_season_pace( remaining )


def Test_Resolve_TestMissingPlayer_ExpectNoneWithoutOldSeasonFallback(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   fetch = Mock( return_value=[ _summary( 3, 1 ) ] )
   monkeypatch.setattr( season_stats_resolver.NhlClient, 'seasons', _seasons )
   monkeypatch.setattr( season_stats_resolver.NhlClient, 'skater_summary', fetch )

   assert SeasonStatsResolver.resolve( 8, date( 2026, 10, 2 ) ) is None
   fetch.assert_called_once_with( 20262027 )
