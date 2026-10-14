from __future__ import annotations

from datetime import date

from .ingest.skater_games_fetcher import SkaterGamesFetcher
from .ingest.standings_games_fetcher import StandingsGamesFetcher
from .recency_target_resolver import RecencyTargetResolver
from .skaters.team import Team


class PaceGamesResolver():
   @classmethod
   def resolve( cls, player_id: int, on_date: date, team: Team ) -> int:
      season = RecencyTargetResolver.season()
      season_games = season.number_of_games
      team_games = StandingsGamesFetcher.games_played( season.season_id, team, on_date )
      played = SkaterGamesFetcher.games_played( season.season_id, player_id, on_date )
      missed = team_games - played
      return season_games - missed
