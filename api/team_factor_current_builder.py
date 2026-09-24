from __future__ import annotations

from .depth_chart import DepthChart
from .depth_group import DepthGroup
from .games_share import GamesShare
from .ice_pace_scaler import IcePaceScaler
from .ice_usage import IceUsage
from .projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from .projections.team_lineup import TeamLineup
from .skater_group import SkaterGroup
from .skater_ice import SkaterIce
from .slot_average import SlotAverage
from .team import Team
from .team_factor_filler import TeamFactorFiller
from .team_factor_prior_binder import TeamFactorPriorBinder
from .team_factor_rows import TeamFactorRows
from .team_factor_skater import TeamFactorSkater
from .teammate_skater import TeammateSkater


class TeamFactorCurrentBuilder():
   @classmethod
   def build(
         cls,
         lineup: TeamLineup,
         slots: list[ SlotAverage ],
         charts: dict[ tuple[ Team, SkaterGroup ], DepthChart ],
         usages: dict[ int, IceUsage ],
         season_length: int,
         ice: dict[ int, SkaterIce ],
         availabilities: dict[ int, float ] ) -> list[ TeamFactorSkater ]:
      forwards, f_extras = cls._skaters(
         lineup,
         slots,
         charts,
         usages,
         season_length,
         ice,
         availabilities,
         DepthGroup.forwards() )
      defense, extras = cls._skaters(
         lineup,
         slots,
         charts,
         usages,
         season_length,
         ice,
         availabilities,
         DepthGroup.defense() )
      return TeamFactorRows.build( forwards, f_extras, defense, extras )


   @classmethod
   def _skaters(
         cls,
         lineup: TeamLineup,
         slots: list[ SlotAverage ],
         charts: dict[ tuple[ Team, SkaterGroup ], DepthChart ],
         usages: dict[ int, IceUsage ],
         season_length: int,
         ice: dict[ int, SkaterIce ],
         availabilities: dict[ int, float ],
         group: DepthGroup ) -> tuple[
            list[ TeammateSkater ],
            list[ TeammateSkater ] ]:
      matching = [
         skater
         for skater in lineup.skaters
         if group.contains( skater.position )
      ]
      paces = {
         skater.player_id: cls._scaled( skater.contribution, skater.player_id, ice )
         for skater in matching
      }
      chart = charts.get( ( lineup.team, group.skater_group ) )

      if chart is not None:
         return cls._from_chart(
            chart,
            paces,
            slots,
            group,
            usages,
            season_length )

      return cls._from_scoring( matching, paces, slots, group, availabilities )


   @classmethod
   def _from_scoring(
         cls,
         matching: list[ CurrentSeasonNhlSkater ],
         paces: dict[ int, float ],
         slots: list[ SlotAverage ],
         group: DepthGroup,
         availabilities: dict[ int, float ] ) -> tuple[
            list[ TeammateSkater ],
            list[ TeammateSkater ] ]:
      ranked = sorted(
         matching,
         key=lambda skater: ( -paces[ skater.player_id ], skater.player_id ) )
      regulars = [
         TeammateSkater(
            skater.player_id,
            paces[ skater.player_id ],
            availabilities.get( skater.player_id, GamesShare.FULL ),
            None )
         for skater in ranked[ : group.dressed_count ]
      ]
      extras = [
         TeammateSkater(
            skater.player_id,
            paces[ skater.player_id ],
            GamesShare.FULL,
            None )
         for skater in ranked[ group.dressed_count: ]
      ]
      return regulars, TeamFactorFiller.pad( extras, slots, group.spare_slot )


   @classmethod
   def _from_chart(
         cls,
         chart: DepthChart,
         paces: dict[ int, float ],
         slots: list[ SlotAverage ],
         group: DepthGroup,
         usages: dict[ int, IceUsage ],
         season_length: int ) -> tuple[
            list[ TeammateSkater ],
            list[ TeammateSkater ] ]:
      regulars = [
         TeammateSkater(
            skater.player_id,
            paces[ skater.player_id ],
            skater.availability,
            None )
         for skater, _toi in chart.regulars
      ]
      extras = [
         TeammateSkater(
            skater.player_id,
            TeamFactorFiller.extra_pace( skater.player_id, paces, slots ),
            GamesShare.FULL,
            None )
         for skater in chart.extras
      ]
      return (
         TeamFactorPriorBinder.bind(
            regulars,
            chart,
            usages,
            season_length,
            group ),
         TeamFactorFiller.pad( extras, slots, group.spare_slot ) )


   @classmethod
   def _scaled(
         cls,
         points: float,
         player_id: int,
         ice: dict[ int, SkaterIce ] ) -> float:
      row = ice.get( player_id )

      if row is None or row.last_toi is None:
         return points

      return points * IcePaceScaler.ratio( row.last_toi, row.projected_toi )
