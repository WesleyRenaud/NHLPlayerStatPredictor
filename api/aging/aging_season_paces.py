from __future__ import annotations

from ..depth.usable_nhl_ice import UsableNhlIce
from ..skaters.skater_season import SkaterSeason


class AgingSeasonPaces():
   @classmethod
   def resolve(
         cls,
         season: SkaterSeason,
         mix_from: SkaterSeason ) -> tuple[ float, float ]:
      if cls._enough_games( season ):
         return season.g_pace, season.a_pace

      if cls._has_mix( mix_from ):
         return cls._apply_mix( season, mix_from )

      return season.g_pace, season.a_pace


   @classmethod
   def _enough_games( cls, season: SkaterSeason ) -> bool:
      return season.games_played >= UsableNhlIce.MIN_GAMES


   @classmethod
   def _has_mix( cls, season: SkaterSeason ) -> bool:
      return cls._enough_games( season ) and ( season.g_pace + season.a_pace ) != 0


   @classmethod
   def _apply_mix(
         cls,
         season: SkaterSeason,
         mix_from: SkaterSeason ) -> tuple[ float, float ]:
      points = season.g_pace + season.a_pace
      share = mix_from.g_pace / ( mix_from.g_pace + mix_from.a_pace )
      return points * share, points * ( 1.0 - share )
