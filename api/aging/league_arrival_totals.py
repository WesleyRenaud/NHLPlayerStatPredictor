from __future__ import annotations

from dataclasses import dataclass

from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason


@dataclass( frozen=True )
class LeagueArrivalTotals():
   league: str
   age: int
   nhl_points: float
   other_points: float
   arrival_count: int


   @classmethod
   def from_seasons(
         cls,
         other: OtherLeagueSkaterSeason,
         following: NhlSkaterSeason ) -> LeagueArrivalTotals:
      return cls.empty( other.league, other.age ).adding( other, following )


   @classmethod
   def empty( cls, league: str, age: int ) -> LeagueArrivalTotals:
      return cls( league, age, 0.0, 0.0, 0 )


   def adding(
         self,
         other: OtherLeagueSkaterSeason,
         following: NhlSkaterSeason ) -> LeagueArrivalTotals:
      games = following.games_played
      return LeagueArrivalTotals(
         self.league,
         self.age,
         self.nhl_points + games * ( following.g_pace + following.a_pace ),
         self.other_points + games * ( other.g_pace + other.a_pace ),
         self.arrival_count + 1 )


   def matches( self, other: OtherLeagueSkaterSeason ) -> bool:
      return self.league == other.league and self.age == other.age


   def rate( self ) -> float | None:
      if self.other_points == 0.0:
         return None

      return self.nhl_points / self.other_points
