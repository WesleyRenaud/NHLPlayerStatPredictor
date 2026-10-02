from __future__ import annotations


class SkaterStatRates():
   @staticmethod
   def time_on_ice_per_game( total_ice: float, games_played: int ) -> float:
      """Return average ice time in the same unit as total_ice."""
      return total_ice / games_played


   @classmethod
   def shooting_percentage( cls, goals: int, shots: int | None ) -> float | None:
      return cls.shooting_percentage_from_paces( goals, shots )


   @staticmethod
   def shooting_percentage_from_paces( goals_pace: float, shots_pace: float | None ) -> float | None:
      return None if shots_pace is None or shots_pace == 0 else 100 * goals_pace / shots_pace
