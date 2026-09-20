from __future__ import annotations

from collections import defaultdict

from .career_pace import CareerPace
from ..league_factor import LeagueFactor
from ..other_league_season import OtherLeagueSeason
from ..recency_weight import RecencyWeight
from ..season import Season
from ..skater_season import SkaterSeason


class TranslatedPaceAverager():
   @classmethod
   def average(
         cls,
         seasons: list[ SkaterSeason ],
         other_seasons: list[ OtherLeagueSeason ],
         weights: list[ RecencyWeight ],
         target_season_id: int,
         factors: list[ LeagueFactor ] ) -> CareerPace:
      nhl_by_lag = cls._nhl_by_lag( seasons, target_season_id )
      others_by_lag = cls._others_by_lag( other_seasons, target_season_id )
      by_league = { factor.league: factor for factor in factors }
      total = 0.0
      goals_total = 0.0
      assists_total = 0.0

      for weight in weights:
         pace = cls._year_pace(
            nhl_by_lag.get( weight.lag ),
            others_by_lag.get( weight.lag, [] ),
            by_league )

         if pace is None:
            continue

         goals_total += pace.goals * weight.weight
         assists_total += pace.assists * weight.weight
         total += weight.weight

      return CareerPace(
         goals=goals_total / total,
         assists=assists_total / total )


   @classmethod
   def _year_pace(
         cls,
         nhl: SkaterSeason | None,
         others: list[ OtherLeagueSeason ],
         by_league: dict[ str, LeagueFactor ] ) -> CareerPace | None:
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

      return CareerPace( goals=goals / games, assists=assists / games )


   @classmethod
   def _nhl_by_lag(
         cls,
         seasons: list[ SkaterSeason ],
         target_season_id: int ) -> dict[ int, SkaterSeason ]:
      by_lag: dict[ int, SkaterSeason ] = {}

      for season in seasons:
         by_lag[ Season.recency_lag( target_season_id, season.season_id ) ] = season

      return by_lag


   @classmethod
   def _others_by_lag(
         cls,
         seasons: list[ OtherLeagueSeason ],
         target_season_id: int ) -> dict[ int, list[ OtherLeagueSeason ] ]:
      by_lag: dict[ int, list[ OtherLeagueSeason ] ] = defaultdict( list )

      for season in seasons:
         by_lag[ Season.recency_lag( target_season_id, season.season_id ) ].append(
            season )

      return by_lag
