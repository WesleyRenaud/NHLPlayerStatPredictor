from __future__ import annotations

from datetime import date

from api.availability_projector import AvailabilityProjector
from api.games_share import GamesShare
from api.nhl_skater_season import NhlSkaterSeason
from api.recency_weight import RecencyWeight
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


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
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      gp_share=gp_share )


def Test_Resolve_TestWeightedShares_ExpectAverage() -> None:
   target = 20262027
   assert AvailabilityProjector.resolve(
      [ _season( 20252026, 1.0 ), _season( 20242025, 0.4 ) ],
      [ RecencyWeight( 0, 0.75 ), RecencyWeight( 1, 0.25 ) ],
      target ) == 0.85


def Test_Resolve_TestMissingLag_ExpectRenormalized() -> None:
   assert AvailabilityProjector.resolve(
      [ _season( 20252026, 0.5 ) ],
      [ RecencyWeight( 0, 0.75 ), RecencyWeight( 1, 0.25 ) ],
      20262027 ) == 0.5


def Test_Resolve_TestEmpty_ExpectFull() -> None:
   assert AvailabilityProjector.resolve(
      [],
      [ RecencyWeight( 0, 1.0 ) ],
      20262027 ) == GamesShare.FULL


def Test_Resolve_TestMissingShare_ExpectFull() -> None:
   assert AvailabilityProjector.resolve(
      [ _season( 20252026, None ) ],
      [ RecencyWeight( 0, 1.0 ) ],
      20262027 ) == GamesShare.FULL


def Test_Resolve_TestInjuredNhlYear_ExpectShare() -> None:
   share = 0.07
   assert AvailabilityProjector.resolve(
      [ _season( 20252026, share, games_played=6 ) ],
      [ RecencyWeight( 0, 1.0 ) ],
      20262027 ) == share
