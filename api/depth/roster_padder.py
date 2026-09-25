from __future__ import annotations

from .depth_group import DepthGroup
from .league_filler import LeagueFiller
from ..projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from ..projections.season_pace import SeasonPace
from ..shared.enums.position import Position
from ..skaters.team import Team
from .slot_average import SlotAverage
from .slot_filler import SlotFiller


class RosterPadder():
   @classmethod
   def pad(
         cls,
         paces: list[ CurrentSeasonNhlSkater ],
         slot_averages: list[ SlotAverage ] ) -> list[ CurrentSeasonNhlSkater ]:
      by_team: dict[ Team, list[ CurrentSeasonNhlSkater ] ] = {}

      for skater in paces:
         by_team.setdefault( skater.team, [] ).append( skater )

      padded = []

      for skaters in by_team.values():
         padded.extend( skaters )

         for group in ( DepthGroup.forwards(), DepthGroup.defense() ):
            padded.extend( cls._spares( skaters, slot_averages, group ) )

      return padded


   @classmethod
   def _spares(
         cls,
         skaters: list[ CurrentSeasonNhlSkater ],
         slot_averages: list[ SlotAverage ],
         group: DepthGroup ) -> list[ CurrentSeasonNhlSkater ]:
      matching = [
         skater
         for skater in skaters
         if group.contains( skater.position )
      ]
      next_slot = max( len( matching ) + 1, group.spare_slot )
      spares = []

      while next_slot <= group.roster_count:
         average = SlotFiller.average( slot_averages, next_slot )

         if average is None:
            break

         spares.append(
            CurrentSeasonNhlSkater(
               LeagueFiller.player_id( next_slot ),
               SeasonPace( average.goals, average.assists ),
               skaters[ Position.FIRST ].team,
               group.skater_group.position ) )
         next_slot += 1

      return spares
