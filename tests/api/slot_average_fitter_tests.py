from __future__ import annotations

from api.depth_group import DepthGroup
from api.ice_usage import IceUsage
from api.projections.season_pace import SeasonPace
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.slot_average_fitter import SlotAverageFitter
from api.team import Team


def _usage(
      player_id: int,
      toi: float,
      team: Team,
      games: int = 80 ) -> tuple[ int, IceUsage ]:
   return player_id, IceUsage(
      toi,
      games,
      team,
      SkaterPosition( 'D' ) )


def Test_Fit_TestSeventhAndEighth_ExpectLeagueMeans() -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   usages = {}
   paces = {}
   first_toi = [ 24.0, 22.0, 21.0, 20.0, 18.0, 16.0, 15.0, 13.0 ]
   second_toi = [ 23.0, 22.0, 21.0, 19.0, 18.0, 17.0, 13.0, 11.0 ]

   for index, toi in enumerate( first_toi ):
      player_id, usage = _usage( index + 1, toi, first )
      usages[ player_id ] = usage
      paces[ player_id ] = SeasonPace( float( index ), float( index ) * 2.0 )

   for index, toi in enumerate( second_toi ):
      player_id, usage = _usage( index + 11, toi, second )
      usages[ player_id ] = usage
      paces[ player_id ] = SeasonPace( float( index ), float( index ) * 2.0 )

   slots = SlotAverageFitter.fit(
      usages,
      paces,
      DepthGroup.defense().spare_slot )
   seventh = next(
      slot
      for slot in slots
      if slot.slot == DepthGroup.defense().spare_slot )
   eighth = next(
      slot
      for slot in slots
      if slot.slot == DepthGroup.defense().spare_slot + 1 )
   assert abs( seventh.toi - 14.0 ) < 0.001
   assert abs( seventh.goals - 6.0 ) < 0.001
   assert abs( seventh.assists - 12.0 ) < 0.001
   assert abs( eighth.toi - 12.0 ) < 0.001


def Test_Fit_TestLowGamesHighToi_ExpectInDepth() -> None:
   team = list( Team )[ Position.FIRST ]
   usages = {}

   for index, toi in enumerate( [ 26.0, 24.0, 22.0, 20.0, 18.0, 16.0, 14.0 ] ):
      player_id, usage = _usage(
         index + 1,
         toi,
         team,
         games=1 if index == 0 else 80 )
      usages[ player_id ] = usage

   slots = SlotAverageFitter.fit(
      usages,
      {},
      DepthGroup.defense().spare_slot )
   seventh = next(
      slot
      for slot in slots
      if slot.slot == DepthGroup.defense().spare_slot )
   assert seventh.toi == 14.0
