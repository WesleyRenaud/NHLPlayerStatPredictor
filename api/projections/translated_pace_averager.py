from __future__ import annotations

from collections import defaultdict

from .career_pace import CareerPace
from ..league_factor import LeagueFactor
from ..nhl_skater_season import NhlSkaterSeason
from ..other_league_skater_season import OtherLeagueSkaterSeason
from ..recency_weight import RecencyWeight
from ..season import Season


class TranslatedPaceAverager():
   GAMES_SCALE = 20


   @classmethod
   def average(
         cls,
         seasons: list[ NhlSkaterSeason ],
         other_seasons: list[ OtherLeagueSkaterSeason ],
         weights: list[ RecencyWeight ],
         target_season_id: int,
         factors: list[ LeagueFactor ] ) -> CareerPace:
      nhl_by_lag = cls._nhl_by_lag( seasons, target_season_id )
      others_by_lag = cls._others_by_lag( other_seasons, target_season_id )
      by_league = { factor.league: factor for factor in factors }
      total = 0.0
      goals_total = 0.0
      assists_total = 0.0

      for recency in weights:
         year = cls._year_pace(
            nhl_by_lag.get( recency.lag ),
            others_by_lag.get( recency.lag, [] ),
            by_league )

         if year is None:
            continue

         pace, games = year
         weight = recency.weight * cls._games_weight( games )
         goals_total += pace.goals * weight
         assists_total += pace.assists * weight
         total += weight

      return CareerPace(
         goals=goals_total / total,
         assists=assists_total / total )


   @classmethod
   def _games_weight( cls, games: float ) -> float:
      return games / ( games + TranslatedPaceAverager.GAMES_SCALE )


   @classmethod
   def _year_pace(
         cls,
         nhl: NhlSkaterSeason | None,
         others: list[ OtherLeagueSkaterSeason ],
         by_league: dict[ str, LeagueFactor ] ) -> tuple[ CareerPace, float ] | None:
      games = 0.0
      goals = 0.0
      assists = 0.0

      if nhl is not None:
         nhl_games = float( nhl.games_played )
         games += nhl_games
         goals += nhl_games * nhl.g_pace
         assists += nhl_games * nhl.a_pace

      for other in others:
         factor = by_league.get( other.league )

         if factor is None:
            continue

         other_games = float( other.games_played )
         games += other_games
         goals += other_games * other.g_pace * factor.goals
         assists += other_games * other.a_pace * factor.assists

      if not games:
         return None

      return CareerPace( goals=goals / games, assists=assists / games ), games


   @classmethod
   def _nhl_by_lag(
         cls,
         seasons: list[ NhlSkaterSeason ],
         target_season_id: int ) -> dict[ int, NhlSkaterSeason ]:
      by_lag: dict[ int, NhlSkaterSeason ] = {}

      for season in seasons:
         by_lag[ Season.recency_lag( target_season_id, season.season_id ) ] = season

      return by_lag


   @classmethod
   def _others_by_lag(
         cls,
         seasons: list[ OtherLeagueSkaterSeason ],
         target_season_id: int ) -> dict[ int, list[ OtherLeagueSkaterSeason ] ]:
      by_lag: dict[ int, list[ OtherLeagueSkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         by_lag[ Season.recency_lag( target_season_id, season.season_id ) ].append(
            season )

      return by_lag
