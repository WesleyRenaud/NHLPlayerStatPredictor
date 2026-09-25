from __future__ import annotations

from ..availability.games_share import GamesShare
from ..depth.depth_group import DepthGroup
from ..depth.ice_usage import IceUsage
from ..depth.last_core import LastCore
from ..depth.slot_average import SlotAverage
from ..projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from ..projections.team_lineup import TeamLineup
from .team_factor_filler import TeamFactorFiller
from .team_factor_rows import TeamFactorRows
from .team_factor_skater import TeamFactorSkater
from .teammate_skater import TeammateSkater


class TeamFactorPreviousBuilder():
   @classmethod
   def build(
         cls,
         lineup: TeamLineup,
         slots: list[ SlotAverage ],
         usages: dict[ int, IceUsage ],
         season_length: int ) -> list[ TeamFactorSkater ]:
      rows = []

      for group in ( DepthGroup.forwards(), DepthGroup.defense() ):
         regulars, extras = cls._skaters(
            lineup,
            slots,
            usages,
            season_length,
            group )
         rows.extend( TeamFactorRows.group( regulars, extras, group ) )

      return rows


   @classmethod
   def _skaters(
         cls,
         lineup: TeamLineup,
         slots: list[ SlotAverage ],
         usages: dict[ int, IceUsage ],
         season_length: int,
         group: DepthGroup ) -> tuple[
            list[ TeammateSkater ],
            list[ TeammateSkater ] ]:
      matching = [
         skater
         for skater in lineup.skaters
         if group.contains( skater.position )
      ]
      paces = {
         skater.player_id: cls._pace( skater )
         for skater in matching
      }
      regulars, extras = LastCore.teammates(
         lineup.team,
         usages,
         paces,
         season_length,
         group.dressed_count,
         group.extra_count,
         group.positions )

      if not regulars:
         regulars, extras = cls._from_scoring( matching, season_length, group )

      return regulars, TeamFactorFiller.pad( extras, slots, group.spare_slot )


   @classmethod
   def _from_scoring(
         cls,
         matching: list[ PreviousSeasonNhlSkater ],
         season_length: int,
         group: DepthGroup ) -> tuple[
            list[ TeammateSkater ],
            list[ TeammateSkater ] ]:
      ranked = sorted(
         matching,
         key=lambda skater: ( -cls._pace( skater ), skater.player_id ) )
      regulars = [
         TeammateSkater(
            skater.player_id,
            cls._pace( skater ),
            GamesShare.resolve( skater.games, season_length ),
            None )
         for skater in ranked[ : group.dressed_count ]
      ]
      extras = [
         TeammateSkater(
            skater.player_id,
            cls._pace( skater ),
            GamesShare.FULL,
            None )
         for skater in ranked[ group.dressed_count: ]
      ]
      return regulars, extras


   @classmethod
   def _pace( cls, skater: PreviousSeasonNhlSkater ) -> float:
      return skater.pace.goals + skater.pace.assists
