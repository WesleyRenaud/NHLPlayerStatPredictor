from __future__ import annotations

from .depth_chart import DepthChart
from .ice_usage import IceUsage
from .projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from .projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from .projections.team_lineup import TeamLineup
from .skater_group import SkaterGroup
from .skater_ice import SkaterIce
from .slot_average import SlotAverage
from .team import Team
from .team_factor import TeamFactor
from .team_factor_current_builder import TeamFactorCurrentBuilder
from .team_factor_previous_builder import TeamFactorPreviousBuilder


class TeamFactorFitter():
   @classmethod
   def fit(
         cls,
         current_season: int,
         previous_season_id: int,
         nhl_splits: list[ PreviousSeasonNhlSkater ],
         roster_paces: list[ CurrentSeasonNhlSkater ],
         season_length: int,
         slots: list[ SlotAverage ],
         charts: list[ DepthChart ],
         usages: dict[ int, IceUsage ],
         ice: dict[ int, SkaterIce ] ) -> list[ TeamFactor ]:
      by_chart = {
         ( chart.team, chart.skater_group ): chart
         for chart in charts
      }
      return sorted(
         [
            *cls._previous(
               previous_season_id,
               nhl_splits,
               slots,
               usages,
               season_length ),
            *cls._current(
               current_season,
               roster_paces,
               slots,
               by_chart,
               usages,
               season_length,
               ice ),
         ],
         key=lambda factor: ( factor.season, factor.team.value ) )


   @classmethod
   def _previous(
         cls,
         season: int,
         splits: list[ PreviousSeasonNhlSkater ],
         slots: list[ SlotAverage ],
         usages: dict[ int, IceUsage ],
         season_length: int ) -> list[ TeamFactor ]:
      return cls._rated(
         [
            TeamFactor(
               season,
               group.team,
               0.0,
               TeamFactorPreviousBuilder.build(
                  group,
                  slots,
                  usages,
                  season_length ) )
            for group in TeamLineup.group( splits )
         ] )


   @classmethod
   def _current(
         cls,
         season: int,
         roster_paces: list[ CurrentSeasonNhlSkater ],
         slots: list[ SlotAverage ],
         charts: dict[ tuple[ Team, SkaterGroup ], DepthChart ],
         usages: dict[ int, IceUsage ],
         season_length: int,
         ice: dict[ int, SkaterIce ] ) -> list[ TeamFactor ]:
      return cls._rated(
         [
            TeamFactor(
               season,
               lineup.team,
               0.0,
               TeamFactorCurrentBuilder.build(
                  lineup,
                  slots,
                  charts,
                  usages,
                  season_length,
                  ice ) )
            for lineup in TeamLineup.group( roster_paces )
         ] )


   @classmethod
   def _rated( cls, factors: list[ TeamFactor ] ) -> list[ TeamFactor ]:
      league = sum( factor.dressed_total() for factor in factors ) / len( factors )
      return [
         TeamFactor(
            factor.season,
            factor.team,
            factor.dressed_total() / league,
            factor.skaters )
         for factor in factors
      ]
