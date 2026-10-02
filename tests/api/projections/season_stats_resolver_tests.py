from __future__ import annotations

from datetime import date
from unittest.mock import Mock

import pytest

import api.projections.season_stats_resolver as season_stats_resolver
from api.projections.season_stats_resolver import SeasonStatsResolver
from api.season import Season
from api.season_length import SeasonLength
from api.skaters.skater_summary import SkaterSummary


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

   stats = SeasonStatsResolver.resolve( 7, on_date )

   assert stats == {
      'seasonLabel': Season.label( expected_season_id ), **summaries[ expected_season_id ].stats_dict(),
   }
   assert stats[ 'gamesPlayed' ] == summaries[ expected_season_id ].games_played
   fetch.assert_called_once_with( expected_season_id )


def Test_Resolve_TestMissingPlayer_ExpectNoneWithoutOldSeasonFallback(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   fetch = Mock( return_value=[ _summary( 3, 1 ) ] )
   monkeypatch.setattr( season_stats_resolver.NhlClient, 'seasons', _seasons )
   monkeypatch.setattr( season_stats_resolver.NhlClient, 'skater_summary', fetch )

   assert SeasonStatsResolver.resolve( 8, date( 2026, 10, 2 ) ) is None
   fetch.assert_called_once_with( 20262027 )
