from __future__ import annotations

from .availability_state import AvailabilityState
from ..depth.ice_available import IceAvailable


class AvailabilityEnumerator():
   @classmethod
   def resolve(
         cls,
         skaters: list[ IceAvailable ] ) -> list[ AvailabilityState ]:
      states = [
         AvailabilityState( share=1.0, playing=[], regulars_out=0 )
      ]

      for skater in skaters:
         states = cls._expand( states, skater )

      return states


   @classmethod
   def _expand(
         cls,
         states: list[ AvailabilityState ],
         skater: IceAvailable ) -> list[ AvailabilityState ]:
      expanded = []

      for state in states:
         available = state.share * skater.availability

         if available > 0.0:
            expanded.append(
               AvailabilityState(
                  share=available,
                  playing=[ *state.playing, skater ],
                  regulars_out=state.regulars_out ) )

         unavailable = state.share * ( 1.0 - skater.availability )

         if unavailable > 0.0:
            expanded.append(
               AvailabilityState(
                  share=unavailable,
                  playing=list( state.playing ),
                  regulars_out=state.regulars_out + 1 ) )

      return expanded
