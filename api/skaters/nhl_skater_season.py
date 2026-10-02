from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..projections.power_play_pace import PowerPlayPace
from ..projections.scoring_paces import ScoringPaces
from ..projections.season_pace import SeasonPace
from ..projections.short_handed_pace import ShortHandedPace
from ..season import Season
from ..shared.enums.position import Position
from .skater_position import SkaterPosition
from .skater_season import SkaterSeason
from .skater_season_key import SkaterSeasonKey
from .team import Team
from ..types import Types


@dataclass( frozen=True )
class NhlSkaterSeason( SkaterSeason ):
   player_name: str
   birth_date: date
   team: Team
   schedule_games: int
   pace_games: int
   p_pace: float
   penalty_minutes: int
   gp_share: float | None
   playoff_games: int
   playoff_goals: int
   playoff_assists: int
   power_play_goals: int
   power_play_points: int
   short_handed_goals: int
   short_handed_points: int
   even_strength_goals: int
   even_strength_points: int
   shots: int


   @classmethod
   def from_row( cls, row: Types.JsonObject | Types.Row ) -> NhlSkaterSeason:
      gp_share = row[ 'GP_SHARE' ]
      return cls(
         player_id=int( row[ 'PLAYER_ID' ] ),
         season_id=int( row[ 'SEASON_ID' ] ),
         age=float( row[ 'AGE' ] ),
         games_played=int( row[ 'GAMES_PLAYED' ] ),
         goals=int( row[ 'GOALS' ] ),
         assists=int( row[ 'ASSISTS' ] ),
         points=int( row[ 'POINTS' ] ),
         g_pace=float( row[ 'G_PACE' ] ),
         a_pace=float( row[ 'A_PACE' ] ),
         player_name=str( row[ 'PLAYER_NAME' ] ),
         position=SkaterPosition( str( row[ 'POSITION' ] ) ),
         birth_date=date.fromisoformat(
            str( row[ 'BIRTH_DATE' ] ).split( 'T' )[ Position.FIRST ] ),
         team=Team( str( row[ 'TEAM' ] ) ),
         schedule_games=int( row[ 'SCHEDULE_GAMES' ] ),
         pace_games=int( row[ 'PACE_GAMES' ] ),
         p_pace=float( row[ 'P_PACE' ] ),
         penalty_minutes=int( row[ 'PIM' ] ),
         gp_share=None if gp_share is None else float( gp_share ),
         playoff_games=int( row[ 'PLAYOFF_GAMES' ] ),
         playoff_goals=int( row[ 'PLAYOFF_GOALS' ] ),
         playoff_assists=int( row[ 'PLAYOFF_ASSISTS' ] ),
         power_play_goals=int( row[ 'PP_GOALS' ] ),
         power_play_points=int( row[ 'PP_POINTS' ] ),
         short_handed_goals=int( row[ 'SHORT_HANDED_GOALS' ] ),
         short_handed_points=int( row[ 'SHORT_HANDED_POINTS' ] ),
         even_strength_goals=int( row[ 'EV_GOALS' ] ),
         even_strength_points=int( row[ 'EV_POINTS' ] ),
         shots=int( row[ 'SHOTS' ] ) )


   def key( self ) -> SkaterSeasonKey:
      return SkaterSeasonKey( self.player_id, self.season_id )


   def scoring_paces( self ) -> ScoringPaces:
      even_strength = self.even_strength_pace()
      power_play = self.power_play_pace()
      short_handed = self.short_handed_pace()
      return ScoringPaces(
         even_strength.goals,
         even_strength.assists,
         power_play.goals,
         power_play.assists,
         short_handed.goals,
         short_handed.assists )


   def power_play_pace( self ) -> PowerPlayPace:
      return PowerPlayPace(
         goals=Season.pace(
            self.power_play_goals,
            self.games_played,
            self.pace_games ),
         assists=Season.pace(
            self.power_play_points - self.power_play_goals,
            self.games_played,
            self.pace_games ) )


   def short_handed_pace( self ) -> ShortHandedPace:
      return ShortHandedPace(
         goals=Season.pace(
            self.short_handed_goals,
            self.games_played,
            self.pace_games ),
         assists=Season.pace(
            self.short_handed_points - self.short_handed_goals,
            self.games_played,
            self.pace_games ) )


   def penalty_minutes_pace( self ) -> float:
      return Season.pace(
         self.penalty_minutes,
         self.games_played,
         self.pace_games )


   def shots_pace( self ) -> float:
      return Season.pace( self.shots, self.games_played, self.pace_games )


   def even_strength_pace( self ) -> SeasonPace:
      return SeasonPace(
         Season.pace( self.even_strength_goals, self.games_played, self.pace_games ),
         Season.pace(
            self.even_strength_points - self.even_strength_goals,
            self.games_played,
            self.pace_games ) )


   def playoff_surplus( self ) -> SeasonPace:
      share = self.playoff_games / self.games_played
      return SeasonPace(
         goals=max( self.playoff_goals - share * self.goals, 0.0 ),
         assists=max( self.playoff_assists - share * self.assists, 0.0 ) )
