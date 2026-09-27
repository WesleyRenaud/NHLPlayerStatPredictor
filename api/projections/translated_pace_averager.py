from __future__ import annotations

from ..aging.league_factor import LeagueFactor
from .season_pace import SeasonPace
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater_season import SkaterSeason
from .year_pace import YearPace


class TranslatedPaceAverager():
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
