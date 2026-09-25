from __future__ import annotations

from ..depth.depth_chart import DepthChart
from ..depth.depth_group import DepthGroup
from ..depth.ice_pace_scaler import IcePaceScaler
from ..depth.skater_ice import SkaterIce
from ..depth.slot_average import SlotAverage
from ..projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from ..projections.team_lineup import TeamLineup
from ..skaters.skater_group import SkaterGroup
from ..skaters.team import Team
from .team_factor_filler import TeamFactorFiller
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
         ice: dict[ int, SkaterIce ] ) -> list[ TeamFactorSkater ]:
      rows = []

      for group in ( DepthGroup.forwards(), DepthGroup.defense() ):
         regulars, extras = cls._skaters(
            lineup,
            slots,
            charts,
            ice,
            group )
         rows.extend( TeamFactorRows.group( regulars, extras, group ) )

      return rows


   @classmethod
   def _skaters(
         cls,
         lineup: TeamLineup,
         slots: list[ SlotAverage ],
         charts: dict[ tuple[ Team, SkaterGroup ], DepthChart ],
         ice: dict[ int, SkaterIce ],
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
      return cls._from_chart(
         charts[ ( lineup.team, group.skater_group ) ],
         paces,
         slots,
         group )


   @classmethod
   def _from_chart(
         cls,
         chart: DepthChart,
         paces: dict[ int, float ],
         slots: list[ SlotAverage ],
         group: DepthGroup ) -> tuple[
            list[ TeammateSkater ],
            list[ TeammateSkater ] ]:
      regulars = [
         TeammateSkater(
            skater.player_id,
            paces.get( skater.player_id, 0.0 ),
            skater.availability,
            None )
         for skater, _toi in chart.regulars
      ]
      extras = [
         TeammateSkater(
            skater.player_id,
            TeamFactorFiller.extra_pace( skater.player_id, paces, slots ),
            skater.availability,
            None )
         for skater in chart.extras
      ]
      return regulars, TeamFactorFiller.pad( extras, slots, group.spare_slot )


   @classmethod
   def _scaled(
         cls,
         points: float,
         player_id: int,
         ice: dict[ int, SkaterIce ] ) -> float:
      row = ice.get( player_id )

      if row is None or not row.last_toi:
         return points

      return points * IcePaceScaler.ratio( row.last_toi, row.projected_toi )
