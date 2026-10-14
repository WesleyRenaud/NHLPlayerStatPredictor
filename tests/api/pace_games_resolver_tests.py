from __future__ import annotations

from datetime import date

import pytest

import api.pace_games_resolver as pace_games_resolver
from api.pace_games_resolver import PaceGamesResolver
from api.season import Season
from api.season_length import SeasonLength
from api.skaters.team import Team


def _seasons() -> list[ SeasonLength ]:
   return [
      SeasonLength( 20202021, 56, date( 2021, 1, 13 ), date( 2021, 5, 19 ) ),
      SeasonLength( 20212022, 82, date( 2021, 10, 12 ), date( 2022, 4, 29 ) ),
   ]


def _install(
      monkeypatch: pytest.MonkeyPatch,
      team_games: int,
      played: int ) -> SeasonLength:
   season = Season.latest( _seasons() )
   monkeypatch.setattr( pace_games_resolver.RecencyTargetResolver, 'season', lambda: season )
   monkeypatch.setattr(
      pace_games_resolver.StandingsGamesFetcher,
      'games_played',
      lambda season_id, team, on_date: team_games )
   monkeypatch.setattr(
      pace_games_resolver.SkaterGamesFetcher,
      'games_played',
      lambda season_id, player_id, on_date: played )
   return season


@pytest.mark.parametrize(
   'played, team_games',
   [
      ( 2, 5 ),
      ( 0, 4 ),
      ( 0, 0 ),
   ] )
def Test_Resolve_TestMissedGames_ExpectScheduleMinusMissed(
      monkeypatch: pytest.MonkeyPatch,
      played: int,
      team_games: int ) -> None:
   season = _install( monkeypatch, team_games, played )
   missed = team_games - played

   pace_games = PaceGamesResolver.resolve( 7, date( 2021, 10, 20 ), Team( 'CHI' ) )

   assert pace_games == season.number_of_games - missed
