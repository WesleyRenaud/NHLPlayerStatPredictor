from __future__ import annotations

from unittest.mock import Mock

import pytest

import api.projections.player_history_resolver as player_history_resolver
from api.projections.player_history_resolver import PlayerHistoryResolver
from api.skaters.skater_summary import SkaterSummary
from api.time import Time


def _summary( games: int, goals: int, shots: int, ice: float ) -> SkaterSummary:
   return SkaterSummary.from_row( {
      'playerId': 7, 'skaterFullName': 'Stub Skater', 'positionCode': 'C', 'teamAbbrevs': 'COL,EDM',
      'gamesPlayed': games, 'goals': goals, 'assists': 7, 'points': goals + 7,
      'penaltyMinutes': 4, 'evGoals': goals, 'evPoints': goals + 7,
      'ppGoals': 0, 'ppPoints': 0, 'shGoals': 0, 'shPoints': 0,
      'shots': shots, 'timeOnIcePerGame': ice,
   } )


def Test_Resolve_TestNhlHistory_ExpectNhlSeasonsAndCareerWithoutLandingFetch(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   summaries = { 20252026: _summary( 20, 5, 40, 1200.0 ), 20262027: _summary( 2, 1, 10, 1500.0 ) }
   landing_fetch = Mock()
   monkeypatch.setattr( player_history_resolver.NhlClient, 'player_landing', landing_fetch )
   monkeypatch.setattr( player_history_resolver.NhlClient, 'skater_summary',
      Mock( side_effect=lambda season_id: [ summaries[ season_id ] ] ) )
   monkeypatch.setattr( player_history_resolver.SkaterSeasonProvider, 'seasons_for_player_id',
      Mock( return_value=[ Mock( season_id=season_id ) for season_id in summaries ] ) )

   history = PlayerHistoryResolver.resolve( 7 )

   landing_fetch.assert_not_called()
   assert [ row[ 'seasonId' ] for row in history[ 'seasons' ] ] == sorted( summaries )
   for row in history[ 'seasons' ]:
      summary = summaries[ row[ 'seasonId' ] ]
      assert row[ 'team' ] == ', '.join( team.value for team in summary.team_abbrevs )
      assert row[ 'goals' ] == summary.goals
      assert row[ 'league' ] == 'NHL'
      assert row[ 'shots' ] == summary.shots
      assert row[ 'penaltyMinutes' ] == summary.penalty_minutes
   career = history[ 'career' ]
   for key in [ 'gamesPlayed', 'goals', 'assists', 'points', 'shots', 'evenStrengthGoals' ]:
      assert career[ key ] == sum( summary.stats_dict()[ key ] for summary in summaries.values() )
   assert career[ 'shootingPercentage' ] == pytest.approx( 100 * career[ 'goals' ] / career[ 'shots' ] )
   total_ice = sum( summary.time_on_ice_per_game * summary.games_played for summary in summaries.values() )
   assert career[ 'timeOnIcePerGame' ] == Time.clock_string( Time.minutes( total_ice / career[ 'gamesPlayed' ] ) )


def Test_Resolve_TestNoNhlHistory_ExpectNoNhlCareer(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr( player_history_resolver.SkaterSeasonProvider, 'seasons_for_player_id', Mock( return_value=[] ) )

   history = PlayerHistoryResolver.resolve( 7 )

   assert history[ 'seasons' ] == []
   assert history[ 'career' ] is None
