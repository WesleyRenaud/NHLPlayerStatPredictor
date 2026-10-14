from __future__ import annotations

from datetime import date

import pytest

import api.ingest.season_games as season_games
import api.ingest.standings_games_fetcher as standings_games_fetcher
from api.ingest.standings_games_fetcher import StandingsGamesFetcher
from api.season_length import SeasonLength
from api.skaters.team import Team


def Test_GamesPlayed_TestMatchingTeam_ExpectGames(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   season_id = 20262027
   team = Team( 'CHI' )
   team_games = 6
   on_date = date( 2026, 10, 13 )
   monkeypatch.setattr( season_games.NhlClient, 'seasons', lambda: [
      SeasonLength( season_id, 84, date( 2026, 10, 7 ), date( 2027, 4, 16 ) ),
   ] )
   monkeypatch.setattr( standings_games_fetcher.NhlClient, 'standings', lambda: {
      'standings': [
         { 'seasonId': season_id, 'teamAbbrev': { 'default': 'COL' }, 'gamesPlayed': 4 },
         { 'seasonId': season_id, 'teamAbbrev': { 'default': team.value }, 'gamesPlayed': team_games },
      ],
   } )

   games = StandingsGamesFetcher.games_played( season_id, team, on_date )

   assert games == team_games
