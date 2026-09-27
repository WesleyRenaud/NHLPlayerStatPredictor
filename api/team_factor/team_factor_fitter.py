from __future__ import annotations

from ..depth.ice_usage import IceUsage
from ..depth.slot_average import SlotAverage
from ..projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from ..projections.team_lineup import TeamLineup
from .team_factor import TeamFactor
from .team_factor_previous_builder import TeamFactorPreviousBuilder


class TeamFactorFitter():
   @classmethod
   def previous(
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
