from __future__ import annotations

from ..aging.league_factor import LeagueFactor
from .season_pace import SeasonPace
from ..skaters.nhl_skater_season import NhlSkaterSeason
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
      power_play_goals = 0.0
      power_play_assists = 0.0

      for season in seasons:
         pace = cls._nhl_pace( season, factors )

         if pace is None:
            continue

         games += season.games_played
         goals += season.games_played * pace.goals
         assists += season.games_played * pace.assists
         if isinstance( season, NhlSkaterSeason ):
            power_play_pace = season.power_play_pace()
            power_play_goals += season.games_played * power_play_pace.goals
            power_play_assists += season.games_played * power_play_pace.assists

      if not games:
         return None

      return YearPace(
         goals=goals / games,
         assists=assists / games,
         power_play_goals=power_play_goals / games,
         power_play_assists=power_play_assists / games,
         games=games )


   @classmethod
   def _nhl_pace(
         cls,
         season: SkaterSeason,
         factors: list[ LeagueFactor ] ) -> SeasonPace | None:
      if isinstance( season, OtherLeagueSkaterSeason ):
         return season.nhl_pace( factors )

      return SeasonPace( goals=season.g_pace, assists=season.a_pace )
