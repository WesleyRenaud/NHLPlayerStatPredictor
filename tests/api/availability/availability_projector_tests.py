from __future__ import annotations

from datetime import date

from api.availability.availability_projector import AvailabilityProjector
from api.availability.games_share import GamesShare
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _season(
      season_id: int,
      gp_share: float | None,
      games_played: int = 82 ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub',
      position=SkaterPosition( 'D' ),
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=games_played,
      even_strength_goals=0,
      even_strength_points=0,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      gp_share=gp_share,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0,
      shots=0,
      penalty_minutes=0 )


def Test_Resolve_TestLastSeason_ExpectThatShare() -> None:
   last_share = 0.8
   older_share = 0.4
   target = 20262027
   seasons = [ _season( 20252026, last_share ), _season( 20242025, older_share ) ]

   share = AvailabilityProjector.resolve( seasons, target )

   assert share == last_share


def Test_Resolve_TestNoLastSeason_ExpectMostRecent() -> None:
   recent_share = GamesShare.FULL
   older_share = 0.4
   target = 20262027
   seasons = [ _season( 20242025, recent_share ), _season( 20232024, older_share ) ]

   resolved = AvailabilityProjector.resolve( seasons, target )

   assert resolved == recent_share


def Test_Resolve_TestEmpty_ExpectFull() -> None:
   target = 20262027
   seasons: list[ NhlSkaterSeason ] = []

   share = AvailabilityProjector.resolve( seasons, target )

   assert share == GamesShare.FULL


def Test_Resolve_TestMissingShare_ExpectFull() -> None:
   target = 20262027
   seasons = [ _season( 20252026, None ) ]

   share = AvailabilityProjector.resolve( seasons, target )

   assert share == GamesShare.FULL


def Test_Resolve_TestInjuredNhlYear_ExpectShare() -> None:
   share = 0.07
   games_played = 6
   target = 20262027
   seasons = [ _season( 20252026, share, games_played=games_played ) ]

   resolved = AvailabilityProjector.resolve( seasons, target )

   assert resolved == share
