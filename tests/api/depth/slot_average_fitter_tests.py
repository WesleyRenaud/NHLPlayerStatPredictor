from __future__ import annotations

from api.depth.depth_group import DepthGroup
from api.depth.ice_usage import IceUsage
from api.depth.slot_average_fitter import SlotAverageFitter
from api.projections.season_pace import SeasonPace
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


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
   spare = DepthGroup.defense().spare_slot
   usages = {}
   paces = {}
   first_toi = [ 24.0, 22.0, 21.0, 20.0, 18.0, 16.0, 15.0, 13.0 ]
   second_toi = [ 23.0, 22.0, 21.0, 19.0, 18.0, 17.0, 13.0, 11.0 ]
   first_goals = [ float( index ) for index in range( len( first_toi ) ) ]
   second_goals = [ float( index ) for index in range( len( second_toi ) ) ]

   for index, toi in enumerate( first_toi ):
      player_id, usage = _usage( index + 1, toi, first )
      usages[ player_id ] = usage
      paces[ player_id ] = SeasonPace( first_goals[ index ], first_goals[ index ] * 2.0 )

   for index, toi in enumerate( second_toi ):
      player_id, usage = _usage( index + 11, toi, second )
      usages[ player_id ] = usage
      paces[ player_id ] = SeasonPace( second_goals[ index ], second_goals[ index ] * 2.0 )

   slots = SlotAverageFitter.fit( usages, paces, spare )

   seventh = next( slot for slot in slots if slot.slot == spare )
   eighth = next( slot for slot in slots if slot.slot == spare + 1 )
   index = spare + Position.LAST
   assert abs(
      seventh.toi - ( first_toi[ index ] + second_toi[ index ] ) / 2 ) < 0.001
   assert abs(
      seventh.goals - ( first_goals[ index ] + second_goals[ index ] ) / 2 ) < 0.001
   assert abs(
      seventh.assists
      - ( first_goals[ index ] * 2.0 + second_goals[ index ] * 2.0 ) / 2 ) < 0.001
   assert abs(
      eighth.toi
      - ( first_toi[ index + 1 ] + second_toi[ index + 1 ] ) / 2 ) < 0.001


def Test_Fit_TestLowGamesHighToi_ExpectInDepth() -> None:
   team = list( Team )[ Position.FIRST ]
   spare = DepthGroup.defense().spare_slot
   tois = [ 26.0, 24.0, 22.0, 20.0, 18.0, 16.0, 14.0 ]
   usages = {}

   for index, toi in enumerate( tois ):
      player_id, usage = _usage(
         index + 1,
         toi,
         team,
         games=1 if index == 0 else 80 )
      usages[ player_id ] = usage

   slots = SlotAverageFitter.fit( usages, {}, spare )

   seventh = next( slot for slot in slots if slot.slot == spare )
   assert seventh.toi == tois[ spare + Position.LAST ]
