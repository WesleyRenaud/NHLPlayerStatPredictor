from __future__ import annotations

from collections import defaultdict

from ..league_factor import LeagueFactor
from ..other_league_skater_season import OtherLeagueSkaterSeason
from ..recency_weight import RecencyWeight
from ..season import Season
from .season_pace import SeasonPace
from ..skater_season import SkaterSeason
from .year_pace import YearPace


class TranslatedPaceAverager():
   GAMES_SCALE = 20


   @classmethod
   def average(
         cls,
         seasons: list[ SkaterSeason ],
         weights: list[ RecencyWeight ],
         target_season_id: int,
         factors: list[ LeagueFactor ] ) -> SeasonPace | None:
      by_lag = cls._by_lag( seasons, target_season_id )
      total = 0.0
      goals_total = 0.0
      assists_total = 0.0

      for recency in weights:
         year = cls.year( by_lag.get( recency.lag, [] ), factors )

         if year is None:
            continue

         weight = recency.weight * cls._games_weight( year.games )
         goals_total += year.pace.goals * weight
         assists_total += year.pace.assists * weight
         total += weight

      if not total:
         return None

      return SeasonPace(
         goals=goals_total / total,
         assists=assists_total / total )


   @classmethod
   def year(
         cls,
         seasons: list[ SkaterSeason ],
         factors: list[ LeagueFactor ] ) -> YearPace | None:
      games = 0
      goals = 0.0
      assists = 0.0

      for season in seasons:
         pace = cls._nhl_pace( season, factors )

         if pace is None:
            continue

         games += season.games_played
         goals += season.games_played * pace.goals
         assists += season.games_played * pace.assists

      if not games:
         return None

      return YearPace(
         SeasonPace( goals=goals / games, assists=assists / games ),
         games )


   @classmethod
   def _nhl_pace(
         cls,
         season: SkaterSeason,
         factors: list[ LeagueFactor ] ) -> SeasonPace | None:
      if isinstance( season, OtherLeagueSkaterSeason ):
         return season.nhl_pace( factors )

      return SeasonPace( season.g_pace, season.a_pace )


   @classmethod
   def _games_weight( cls, games: int ) -> float:
      return games / ( games + TranslatedPaceAverager.GAMES_SCALE )


   @classmethod
   def _by_lag(
         cls,
         seasons: list[ SkaterSeason ],
         target_season_id: int ) -> dict[ int, list[ SkaterSeason ] ]:
      by_lag: dict[ int, list[ SkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         by_lag[ Season.recency_lag( target_season_id, season.season_id ) ].append(
            season )

      return by_lag
